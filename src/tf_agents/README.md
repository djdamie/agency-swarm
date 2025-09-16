# TF Agents Package

Scaffolding for migrating the Tracks & Fields supervisor workflow onto
Agency Swarm v1. Modules are intentionally light-weight for now and will be
populated as we port the legacy LangGraph implementation.

```
src/tf_agents/
├── agents/          # Agent factories and orchestration logic
Agents:
- `create_brief_analyzer_agent()`
- `create_project_strategist_agent()`
- `create_tf_agency()`

├── tools/           # Chartmetric/Spotify tooling adapters
├── utils/           # Shared helpers (auth, parsing, etc.)
├── services/        # External service wrappers (optional)
├── config.py        # Domain constants bridged from legacy context files
├── prompts.py       # Prompt strings imported from legacy workflow
└── state.py         # MasterContext helpers for workflow state
```

Refer to `integration_plan.md` for the full migration roadmap.
