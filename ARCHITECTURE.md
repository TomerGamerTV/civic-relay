# CivicRelay architecture

```mermaid
flowchart LR
  A[Volunteer updates] --> B[Privacy-first intake]
  B --> C[Strands Agent]
  C --> D[extract_volunteer_signals tool]
  D --> E[build_action_queue tool]
  E --> F[draft_human_approved_outreach tool]
  F --> G[Review queue]
  G --> H{Coordinator approves?}
  H -->|Yes, outside CivicRelay| I[Human sends or schedules]
  H -->|No| J[Revise or discard]
```

The agent does not own a mail, calendar, chat, or scheduling credential. Its output is a reviewable recommendation and a draft, each linked to the incoming update that produced it.

## Strands execution

`app.py` imports `Agent` and `tool` from `strands`, giving the agent three narrow tools:

1. `extract_volunteer_signals` identifies availability and urgent constraints.
2. `build_action_queue` orders a small, reviewable coordination queue.
3. `draft_human_approved_outreach` prepares wording without sending it.

The default deterministic mode lets the complete project run without a cloud credential. To invoke a configured Strands model, set `CIVICRELAY_USE_STRANDS=1` and send `use_strands: true` to the API.
