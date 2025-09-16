# Previous Projects Context

This document contains the context of the previous projects that I have been trying to build.

TF_supervisor_workflow is a music licensing workflow automation system using LangGraph to orchestrate intelligent agents that handle email processing, music searches, rights clearance, and project management. The system automates workflows from client briefs to final music delivery.

## Architecture

### Multi-Agent System

The system follows a supervisor pattern with specialized agents:

1. **Supervisor** - Orchestrates workflow and routes tasks
2. **Brief Analyzer** - Extracts structured data from client briefs (PDFs, emails)
3. **Project Strategist** - Determines project type (Synch A/B/C, Production) and strategy
4. **Search Agents** (Phase 2):
   - Spotify Agent - Track analysis and playlist search
   - TF Platform Agent - Internal catalog search
   - Lyrics Agent - Lyric-based search
   - A&R Agent - Genre/vibe matching

### Project Classification

- **Synch A**: $50k+ (30% margin, full workflow)
- **Synch B**: $5k-$50k (40% margin, standard workflow)  
- **Synch C**: $0-$5k (50% margin, simplified workflow)
- **Production**: Custom pricing and workflow

### Key Files

- `/tf_context.py` - Central configuration, constants, and business rules
- `/tf_supervisor_workflow/agent.py` - Main LangGraph agent implementation
- `/tf_supervisor_workflow/models.py` - Pydantic models for structured data
- `/tf_supervisor_workflow/prompts.py` - System prompts for each agent
- `tf_docs/knowledge_base/` - PDFs, contracts, clearance docs, email templates
- `/n8n_workflows/` - n8n workflow definitions and setup (will include later when relevant)

## Current Status

**Phase 1 Complete**: Brief extraction with 100% test success rate using local models (currently testing gpt-oss-20b, but facing difficulties with speed using ollama on client's server. Need to try vllm instead.)

**Next Steps**:

1. Implement remaining search agents (Spotify, TF Platform, Lyrics)
2. Add Email Handler agent for complete pipeline
3. Connect to n8n workflows for execution
4. Integrate actual APIs (Spotify, TF Platform, Gmail, Chartmetric, AIMS)

Required API credentials (store in `.env`):

- `GROQ_API_KEY` - LLM provider
- `LANGCHAIN_API_KEY` - LangSmith tracing
- `SPOTIFY_CLIENT_ID/SECRET` - Music search
- `CHARTMETRIC_API_TOKEN` - Music analytics
- `TF_PLATFORM_API_KEY` - Internal catalog
- Gmail OAuth - Email processing

## Knowledge Base

The `/knowledge_base/` directory contains:

- **briefs/** - Sample client briefs in PDF format
- **clearances/** - Rights and licensing documentation
- **contracts_and_deals/** - Pricing and deal structures
- **email_briefs_txt/** - Extracted email content
- **processes/** - Workflow documentation

## Tracks & Fields Business Context

- the best files to start with are:
  - `tf_docs/knowledge_base/tf-workflow-analysis.md`
  - `tf_docs/T&F Summit 2024 - Projects.pdf`
  - `tf_docs/knowledge_base/tf_context.py`
  