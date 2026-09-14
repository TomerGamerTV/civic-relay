"""CivicRelay: a consent-first volunteer-coordination agent.

Run locally with:
    python -m uvicorn app:app --reload --port 8000

Set CIVICRELAY_USE_STRANDS=1 and configure an AWS Bedrock credential chain to
let the Strands Agent write its own briefing narrative. The safe deterministic
planner remains available for offline demos and never sends outreach itself.
"""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from strands import Agent, tool

    STRANDS_AVAILABLE = True
except ImportError:  # The browser demo is still useful before dependencies install.
    STRANDS_AVAILABLE = False

    def tool(func):  # type: ignore[misc]
        return func


class RelayRequest(BaseModel):
    organization: str = Field(min_length=2, max_length=120)
    goal: str = Field(min_length=8, max_length=500)
    messages: list[str] = Field(min_length=1, max_length=30)
    use_strands: bool = False


PRIORITY_WORDS = {
    "urgent": 4,
    "asap": 4,
    "today": 3,
    "tomorrow": 3,
    "cannot": 2,
    "can’t": 2,
    "cancel": 2,
    "need": 2,
    "help": 1,
}


def _score(message: str) -> int:
    lowered = message.lower()
    return sum(weight for word, weight in PRIORITY_WORDS.items() if word in lowered)


def _name(message: str, index: int) -> str:
    match = re.search(r"(?:^|[,.\-—]\s*)([A-Z][a-z]{1,20})(?:\s+[A-Z][a-z]{1,20})?", message)
    return match.group(1) if match else f"Volunteer {index + 1}"


@tool
def extract_volunteer_signals(messages_json: str) -> str:
    """Extract availability, risks, and commitments from a JSON list of volunteer messages.

    This tool does not contact anyone or expose personal information. It returns only
    a short, reviewable coordination summary for the planner.
    """
    messages = json.loads(messages_json)
    signals = []
    for index, message in enumerate(messages):
        signals.append(
            {
                "label": _name(message, index),
                "priority": _score(message),
                "mentions_unavailability": bool(re.search(r"can't|cannot|unavailable|cancel", message, re.I)),
                "summary": message[:220],
            }
        )
    return json.dumps(signals)


@tool
def build_action_queue(signals_json: str, goal: str) -> str:
    """Turn reviewed volunteer signals into a small ordered queue of human-approved actions."""
    signals = json.loads(signals_json)
    ranked = sorted(signals, key=lambda signal: signal["priority"], reverse=True)
    queue = []
    for signal in ranked[:5]:
        action = "Confirm availability" if signal["mentions_unavailability"] else "Acknowledge update"
        queue.append(
            {
                "owner": "Coordinator",
                "action": f"{action} with {signal['label']} for {goal}",
                "why": signal["summary"],
                "approval_required": True,
            }
        )
    return json.dumps(queue)


@tool
def draft_human_approved_outreach(person: str, action: str) -> str:
    """Draft a short outreach message. The draft is never sent by this agent."""
    return f"Hi {person}, thanks for the update. Before we change anything, could you confirm: {action}?"


def deterministic_plan(payload: RelayRequest) -> dict[str, Any]:
    entries = []
    for index, message in enumerate(payload.messages):
        entries.append(
            {
                "name": _name(message, index),
                "message": message.strip(),
                "score": _score(message),
                "unavailable": bool(re.search(r"can't|cannot|unavailable|cancel", message, re.I)),
            }
        )
    entries.sort(key=lambda item: item["score"], reverse=True)
    coverage_risk = sum(item["unavailable"] for item in entries)
    themes = Counter()
    for item in entries:
        for label, words in {
            "availability": ("available", "shift", "cover", "can", "can't", "cannot"),
            "supplies": ("supply", "food", "kit", "stock", "deliver"),
            "transport": ("ride", "drive", "transport", "pickup"),
            "safety": ("urgent", "safe", "risk", "medical"),
        }.items():
            if any(word in item["message"].lower() for word in words):
                themes[label] += 1

    actions = []
    for item in entries[:5]:
        label = "Coverage check" if item["unavailable"] else "Confirm and route"
        actions.append(
            {
                "priority": "NOW" if item["score"] >= 3 else "NEXT",
                "title": f"{label}: {item['name']}",
                "detail": item["message"],
                "approval": "Draft only — coordinator approval required",
                "draft": draft_human_approved_outreach(item["name"], f"the next step for {payload.goal}"),
            }
        )
    if not actions:
        actions.append(
            {
                "priority": "NEXT",
                "title": "Review incoming updates",
                "detail": "No urgent signals were detected.",
                "approval": "Draft only — coordinator approval required",
                "draft": "",
            }
        )

    return {
        "mode": "deterministic-reviewable-planner",
        "brief": {
            "organization": payload.organization,
            "goal": payload.goal,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "messages_reviewed": len(entries),
            "coverage_risk": coverage_risk,
            "themes": themes.most_common(4),
        },
        "actions": actions,
        "guardrails": [
            "No message is sent without a human review.",
            "No volunteer data is sold, exported, or used for training.",
            "Every recommendation is linked to a source update.",
        ],
    }


def strands_narrative(payload: RelayRequest, plan: dict[str, Any]) -> str | None:
    if not STRANDS_AVAILABLE or os.getenv("CIVICRELAY_USE_STRANDS") != "1":
        return None
    system_prompt = """You are CivicRelay, a consent-first coordination agent for a small nonprofit.
Use the provided tools to inspect the messages and prepare a short operational brief.
Never claim to send a message, alter a schedule, or make a commitment. Clearly flag all actions that need human approval."""
    agent = Agent(
        system_prompt=system_prompt,
        tools=[extract_volunteer_signals, build_action_queue, draft_human_approved_outreach],
    )
    prompt = json.dumps(
        {
            "organization": payload.organization,
            "goal": payload.goal,
            "messages": payload.messages,
            "deterministic_plan": plan,
        }
    )
    return str(agent(prompt))


app = FastAPI(title="CivicRelay API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"ok": True, "strands_available": STRANDS_AVAILABLE}


@app.post("/api/plan")
def plan(payload: RelayRequest) -> dict[str, Any]:
    result = deterministic_plan(payload)
    if payload.use_strands:
        narrative = strands_narrative(payload, result)
        if narrative:
            result["strands_narrative"] = narrative
            result["mode"] = "strands-agent-plus-reviewable-planner"
    return result
