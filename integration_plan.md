# TF Supervisor Migration Plan

## Objectives
- Port LangGraph-based supervisor workflow into Agency Swarm v1 orchestration with minimal behavioral drift
- Support client self-hosting with local LLMs while keeping external-tool agents (e.g., Chartmetric) functional via OpenAI for now
- Prepare for AG-UI driven operator experience and optional MCP server tooling

## Legacy Assets To Reuse
- `Previous Agents/tf_supervisor_workflow/` for brief analysis, strategy logic, HITL patterns
- `Previous Agents/Previous_Chartmetric_Tools/` for Chartmetric APIs (now backed by refreshed `helpers.py` token flow)
- Domain constants and business rules in `TF_docs/knowledge_base/tf_context.py`
- Knowledge base docs and briefs under `TF_docs/knowledge_base/` for testing and validation scenarios

## Integration Roadmap
1. **Framework Alignment**
   - Map LangGraph state/agents to Agency Swarm agent + tool abstractions
   - Identify required context/state models and consolidate shared config imports
2. **Environment & Deployment**
   - Define self-hosted runtime: local model endpoints, secret management, external API usage policy
   - Document `.env` expectations and per-client overrides
3. **Tooling Migration**
   - Repackage Chartmetric tools as Agency Swarm tools or MCP services; ensure `helpers.get_access_token` is wired into new infra
   - Validate rate limiting and error handling match repo conventions
4. **Workflow Implementation**
   - Rebuild supervisor, brief analyzer, and strategist agents within Agency Swarm, incorporating HITL loops
   - Add unit/integration tests leveraging existing briefs to confirm extraction and strategy parity
5. **Interface Layer**
   - Prototype AG-UI configuration (see `examples/interactive/copilot_demo.py`) for operator workflows
   - Evaluate MCP server approach for cross-tool reuse and decide if/when to adopt
6. **Validation & Handoff**
   - Run targeted pytest suites, then `make ci`
   - Prepare deployment notes for client server migration and local model configuration

## Framework Alignment Findings
| Legacy component | Agency Swarm mapping | Notes / gaps |
| --- | --- | --- |
| `AgentState` / `EnhancedAgentState` (`Previous Agents/tf_supervisor_workflow/models.py:6`, `123`) | Persist structured data in `MasterContext.user_context` with helper accessors; initialize per-run payload via agency hooks | Need context bootstrap so every run seeds keys (`brief_analysis`, `project_strategy`, `missing_info`, `session_id`) and persists HITL counters for AG-UI resume |
| `BriefAnalyzerAgent.analyze` (`Previous Agents/tf_supervisor_workflow/agent.py:179`) | Instantiate an `Agent` with `BRIEF_ANALYZER_PROMPT` plus a `function_tool` that calls the local LLM, normalizes JSON, and stores output via context setters | Must recreate JSON cleanup/metrics logic (lines 95-177) inside the tool or a shared utility; consider `output_type` guardrails for schema enforcement |
| `ProjectStrategyAgent.strategize` (`Previous Agents/tf_supervisor_workflow/project_strategy_agent.py:1`, `agent.py:386`) | Define a strategist `Agent` using `PROJECT_STRATEGIST_PROMPT` and a tool that reads the stored brief analysis, runs the LLM (local or OpenAI), and saves strategy results | Need deterministic fallback behavior from legacy code (lines 60-107) and margin helpers from `TF_docs/knowledge_base/tf_context.py:12` exposed to the tool |
| `EnhancedSupervisorAgent.route_enhanced` (`Previous Agents/tf_supervisor_workflow/agent.py:397`) | Model workflow with `Agency` communication flows (`brief_analyzer > strategist`, etc.) and optional coordination tool to gate when HITL review is required | Agency Swarm lacks a native `hitl_request` pause; we must implement a custom send_message variant or context flag that signals UI to request human input before continuing |
| HITL utilities (`Previous Agents/tf_supervisor_workflow/enhanced_nodes.py:9`) | Convert `MissingInfoDetector`, `ConfidenceScorer`, `BriefEnhancer`, and parser nodes into reusable context utilities / `function_tool`s triggered after analysis steps | Ensure tools write back to context consistently and emit user-facing summaries for AG-UI; message parsing must move to dedicated tool to inspect latest user reply |
| Chartmetric tools (`Previous Agents/Previous_Chartmetric_Tools/*.py`) | Keep existing `BaseTool` subclasses, register them in new agents’ `tools_folder`, and rely on refreshed `helpers.get_access_token` (`Previous Agents/Previous_Chartmetric_Tools/helpers.py:1`) | Need to wire token helper into Agency Swarm loading path and audit rate limiting to comply with repo conventions; consider MCP packaging later |

## Environment & Deployment Plan

### Runtime Targets
- Deploy Agency Swarm API + agents on client-managed VM (Linux, Python 3.12+) with GPU/accelerator for local LLMs.
- Run local inference stack through LiteLLM proxy or direct OpenAI-compatible endpoint (e.g., vLLM/Ollama) exposed on an internal network port.
- Package Chartmetric/Spotify integrations alongside agency so credentialed HTTP calls remain inside trusted network; optionally continue hosting MCP services for cross-project reuse.

### Secrets & Configuration
| Key | Purpose | Notes |
| --- | --- | --- |
| `OPENAI_API_KEY` | Fallback/complementary hosted model usage (Chartmetric agents, emergency overrides) | Store in client secret manager; only required if external models remain enabled. |
| `LOCAL_LLM_BASE_URL` | URL for LiteLLM/vLLM/Ollama gateway | Use http(s) endpoint reachable from agency host; pair with `LOCAL_LLM_API_KEY` if proxy enforces auth. |
| `LOCAL_LLM_MODEL` | Default model identifier for supervisor/brief agents | Matches model name configured in proxy (e.g., `gpt-4o-mini`, `llama3.1-70b`). |
| `CHARTMETRIC_REFRESH_TOKEN` | Token exchange for all Chartmetric tools | Required by `helpers.get_access_token`; rotate via client vault and inject at runtime. |
| `SPOTIFY_CLIENT_ID/SECRET`, `SPOTIFY_REDIRECT_URI`, `SPOTIFY_SCOPE` | Spotify playlist tooling | Persist in secure store; redirect URI must stay consistent with deployed OAuth callback. |
| `TF_PLATFORM_API_KEY`, `AIMS_API_KEY`, `ODOO_TOKEN` | Future workflow integrations | Define placeholders now; wire into tool loaders when APIs are available. |
| `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT` | Optional tracing when debugging | Disable in production if telemetry not permitted. |
| `AGENCY_SHARED_DIR` | Absolute path to shared files/knowledge base | Mount read-only copy of `TF_docs/knowledge_base` for agents and UI. |

### Local Model Strategy
- Stand up LiteLLM proxy (or direct vLLM endpoint) with configured budget-friendly models sized for on-prem hardware; ensure JSON mode and 8k+ context support for brief parsing.
- Expose two tiers: **analysis** (deterministic mid-size model) for supervisor/brief extraction and **narrative** (higher-quality) for client-facing summaries when needed.
- Configure Agency agents via `OpenAIChatCompletionsModel` or `LitellmModel` pointing to the proxy; set retry/timeouts aligned with on-prem performance.
- Maintain OpenAI-hosted access only for Chartmetric/Spotify tool agents (per client approval) so throughput-sensitive analytics remain reliable.

### Deployment Checklist
1. Provision Python environment (uv/venv) and install project dependencies (`make install` or `uv sync`).
2. Load `.env` from client secret manager; never commit secrets—use templated `.env.example`.
3. Start local LLM service and verify health (`curl $LOCAL_LLM_BASE_URL/v1/models`).
4. Run `make check` + targeted pytest (brief + tool integrations) before promoting builds.
5. Configure persistence callbacks (`load_threads_callback`, `save_threads_callback`) to back agency sessions with client datastore.
6. Expose AG-UI frontend (e.g., via FastAPI/AGUI adapter) behind HTTPS; ensure CORS allows internal operator access only.
7. Set up logging/monitoring (structured logs, token usage, tool latency) and rotate refresh tokens on schedule.


## Tooling Migration Strategy

### Chartmetric Tooling
- Keep Python implementations in `Previous Agents/Previous_Chartmetric_Tools/` as authoritative source code; migrate into `src/tf_agents/tools/chartmetric/` to align with Agency Swarm tooling layout.
- Each module subclasses `BaseTool`; use `ToolFactory.adapt_base_tool` via agent `tools_folder` to auto-register. Group rate-limited tools in a dedicated folder and set `one_call_at_a_time=True` for endpoints that must serialize (e.g., fan metrics iterating requests).
- Centralize token handling by exposing `get_access_token` through a shared helper (e.g., `src/tf_agents/utils/chartmetric_auth.py`); load `CHARTMETRIC_REFRESH_TOKEN` from `.env`/secret manager at startup and reuse cached token.
- Add lightweight integration tests that stub HTTP responses to confirm adapter wiring, and document required env vars in `.env.example`.
- Optionally mirror functionality as MCP server later; initial milestone keeps direct BaseTool usage for faster integration.
- ✅ Updated validators to Pydantic `@field_validator`.

### Spotify Tooling
- Convert OpenAPI schemas in `Previous Agents/Agent_Schemas/Spotify_schema.json` into Agent `schemas_folder`; leverage `ToolFactory.from_openapi_schema` to auto-generate tools.
- For OAuth flow, ensure callback host matches client deployment; implement token exchange helper (persistent refresh token or user login) and store session IDs in agency context.
- Create agent-specific wrapper to orchestrate playlist fetch/add flows while respecting rate limits (`one_call_at_a_time`).

### Folder & Agent Layout
- Introduce namespace `src/tf_agents/` housing: `agents/` (supervisor, strategist), `tools/chartmetric/`, `tools/spotify/`, `utils/`.
- Define `tools_folder` / `schemas_folder` per agent in code so Agency auto-loads relevant tools.
- Maintain README in new package outlining tool prerequisites, environment vars, and testing instructions.

### MCP Considerations
- After core migration, evaluate wrapping Chartmetric endpoints into an MCP server to enable sharing across agencies.
- Reuse `helpers.py` logic but ensure server enforces auth and mirrors BaseTool behavior.

## Workflow Implementation Plan

### Package Structure
- Create `src/tf_agents/` with submodules:
  - `agents/` – definitions for supervisor, brief analyzer, strategist, any coordination agents.
  - `tools/` – Chartmetric + Spotify loaders (per Tooling Strategy) plus utility tools (HITL detectors, brief enhancer).
  - `state.py` – helper dataclasses/functions to read/write workflow data from `MasterContext`.
  - `prompts.py` – ported prompts from legacy workflow, trimmed to Agency Swarm format.
  - `config.py` – surface constants and helpers from `TF_docs/knowledge_base/tf_context.py` for runtime use.
  - `services/` (optional) – wrappers for external integrations (e.g., Spotify auth flow) shared across tools.

### Agent Definitions
- `agents/brief_analyzer.py`: instantiate `Agent` with analyzer instructions, attach tools: brief extraction function (LLM call), missing-info detector, context loggers. Ensure tool writes structured result to context via `state` helpers and records metrics.
- `agents/strategist.py`: agent using strategist prompt and tool that reads stored brief analysis, invokes model, writes strategy payload and confidence metadata.
- `agents/supervisor.py`: configure entry agent that orchestrates analyzer → strategy → HITL loops; leverage context flags to pause/resume when human input required. Provide convenience factory that returns `Agency` instance.
- Provide AG-UI friendly metadata (descriptions, `send_message_tool_class` if needed).

### HITL Utilities
- Convert legacy `MissingInfoDetector`, `ConfidenceScorer`, `BriefEnhancer`, `message_parser` into `tools/hitl.py` with pure functions + `function_tool`s.
- Implement context helper to append HITL requests and track iterations; expose them to AG-UI so operators see outstanding questions.

### Context Management
- `state.py` exports getters/setters for `brief_analysis`, `project_strategy`, `missing_info_requests`, `session_id`, etc.
- Provide initialization helper invoked before each run (Agency `user_context` seed or pre-run hook) to ensure keys exist.
- Include serialization helpers to convert between Pydantic models (if reused) and dicts stored in context.

### Tests
- Unit tests under `tests/tf_agents/test_state.py` verifying context helpers (seed, read/write).
- Integration tests using sample brief email to ensure analyzer tool produces expected structure (mock LLM).
- Tests for HITL detection logic (given partial brief, expect missing-field list).
- Validate Agency wiring: instantiate agency factory with stub models/tools and run minimal scenario.

### Migration Notes
- Keep legacy LangGraph files intact for reference until new solution is validated; update README once replacement is functional.
- Document how to switch between local and hosted models via env vars in new package README.

## Interface & Validation Plan

### AG-UI / Frontend Integration
- Leverage `CopilotDemoLauncher` as reference to embed Agency into client-facing UI; replace demo agents with TF Supervisor agency factory. ✅ `tf_agents.ui.copilot.launch_copilot()` now launches the tailored Copilot experience.
- Extend UI to surface HITL requests from context (display missing info prompts, allow user input to feed back into agency). ✅ `show_missing_info` tool available for Copilot to display outstanding fields.
- Serve UI behind existing Caddy reverse proxy; reuse Open-WebUI or dedicate AG-UI port (e.g., 8009).
- Use `Agency.get_agency_structure()` to provide ReactFlow data for visualizing workflow inside Open-WebUI panels if desired.
- Ensure websocket/API endpoints honor client auth (Supabase session or internal SSO).

### MCP Integration
- Defer MCP server for Chartmetric until core agents stable; evaluate converting tools into MCP once Agency in production to enable cross-project use.
- If adopted, host MCP server alongside existing stack (Docker service) and configure agents with `mcp_servers` pointing to internal URL.

### Validation & Handoff
- Establish CI target: `pytest tests/tf_agents`, `pytest tests/integration/tf_workflow` (new) plus `make check`.
- Add smoke test script to exercise agency end-to-end using sample brief (mock LLM).
- Document deployment steps referencing docker-compose stack: environment variables, service dependencies, health checks.
- Provide operator runbook covering AG-UI usage, HITL process, and troubleshooting (LLM availability, tool errors).

## Tracking & Updates
- Keep this document synchronized as milestones complete (mark sections with dates/notes)
- Reference AGENTS.md when refining rules or adding new processes
