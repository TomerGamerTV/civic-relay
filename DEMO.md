# CivicRelay demo and submission copy

## 90-second demo outline

**0:00–0:12 — The problem**

Small volunteer groups coordinate in fast-moving message threads. A missed cancellation can leave an essential pickup uncovered. Coordinators need a compact, explainable handoff before they send anything.

**0:12–0:28 — Intake**

Show the Harbor Mutual Aid scenario. Four status updates arrive: a driver has a breakdown, another volunteer can drive an extra route, one person can cover pickup, and a supply drop-off is ready.

**0:28–0:52 — Agent path**

Click **Build the review queue**. Explain that CivicRelay runs three constrained Strands tools: it extracts volunteer signals, builds a ranked queue, and drafts human-approved outreach. It does not have messaging, calendar, or scheduling tools.

**0:52–1:12 — Review output**

Open the first action card. The transport failure is prioritized and the proposed outreach is traceable to Luis's incoming update. Show that the coordinator can copy a draft, but CivicRelay does not send it.

**1:12–1:30 — Why it matters**

The agent makes the moment before a good deed falls through more reliable. It reduces coordination load while keeping commitments and communication with the humans who own them.

## Devpost project description

### Inspiration

Community groups often run on a fragile stream of messages: a driver cancels, a volunteer offers a backup route, supplies appear, and someone must connect the dots quickly. We wanted to help coordinators avoid a missed handoff without giving an agent authority to make promises on their behalf.

### What it does

CivicRelay turns volunteer updates into a ranked, source-linked review queue. It flags coverage risks, explains what each recommendation comes from, and writes short outreach drafts for a coordinator to approve. It never sends messages, changes schedules, or commits a volunteer.

### How we built it

The backend is FastAPI and uses the Strands Agents SDK. A Strands Agent works through three narrow, inspectable tools: `extract_volunteer_signals`, `build_action_queue`, and `draft_human_approved_outreach`. The interface is a dependency-free HTML, CSS, and JavaScript workspace designed for quick review. A deterministic local path keeps the scenario runnable without cloud credentials; a configured AWS Bedrock credential chain enables the Strands execution path.

### Challenges we ran into

The design challenge was useful restraint. A coordination system becomes risky when it silently sends, schedules, or commits people. We scoped CivicRelay around interpretation and drafting, then made every outbound step visibly human-owned.

### Accomplishments that we're proud of

We built a complete, locally runnable demo with a clear agent boundary, a traceable action queue, and a readable interface for a realistic volunteer handoff. The project has a public MIT-licensed repository and architecture diagram.

### What we learned

Human-centered agents are more credible when their limits are part of the product. Narrow tools, explicit provenance, and a visible review gate make a system easier to trust and easier to correct.

### What's next

Next we would add configurable signal rules, locally encrypted organization profiles, and an optional coordinator-approved integration layer that requires a final explicit action for every send or scheduling change.

## Disclosure

Use this wording if Devpost asks about assistance: "The project was created during the event with AI coding assistance. The final architecture, scope, and review-gate behavior were directed and reviewed by the entrant. No pre-existing project code was used."
