# CivicRelay

**CivicRelay is a consent-first coordination agent for small nonprofits.** It turns a pile of volunteer updates into a ranked, source-linked review queue, then drafts outreach for a coordinator to approve.

It was built for the *Good Neighbor Agents* track of the AWS Agents for Humans Hackathon. The project never sends messages, modifies schedules, or commits volunteers. Those remain deliberate human actions.

## What it does

- Reads a small batch of volunteer updates.
- Detects coverage-risk language such as unavailable, urgent, cancelled, or broken transport.
- Sorts the updates into an action queue with a clear reason for each action.
- Creates a short outreach draft for each item, ready for a human to review.
- Can run a Strands Agent path with three constrained, inspectable tools.

## Run it

The frontend works directly by opening `index.html`; it automatically falls back to a local demo planner. For the API and Strands path:

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app:app --reload --port 8000
```

Open `index.html` in a browser and use **Build the review queue**.

To enable a configured Strands model, provide your normal AWS Bedrock credential chain, set `CIVICRELAY_USE_STRANDS=1`, and add `"use_strands": true` to a `/api/plan` request.

## Technical design

See [ARCHITECTURE.md](ARCHITECTURE.md). The tool boundaries are intentionally narrow:

- `extract_volunteer_signals`
- `build_action_queue`
- `draft_human_approved_outreach`

No tool is able to send an email, create a calendar event, or mutate a third-party system.

## Demo story

Harbor Mutual Aid needs to cover an evening food pickup. Four volunteers send status updates: one transport cancellation, one backup driver, one pickup volunteer, and one supply drop-off. CivicRelay finds the transport gap, ranks it first, and prepares a draft question to confirm the handoff.

## License

[MIT](LICENSE)
