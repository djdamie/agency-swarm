# TF Supervisor Workflow

A multi-agent system for Tracks & Fields music supervision workflow using LangGraph's supervisor pattern.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your API keys:
```
GROQ_API_KEY=your-groq-api-key
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=tf_supervisor_workflow
```

3. Run the test:
```bash
python test_workflow.py
```

## Structure

- `agent.py` - Main agent implementation
- `models.py` - Pydantic models for structured data
- `prompts.py` - System prompts for each agent
- `test_workflow.py` - Test cases and examples
- `langgraph.json` - LangGraph deployment configuration

## Agents

1. **Supervisor** - Orchestrates the workflow
2. **Brief Analyzer** - Extracts and structures brief information
3. **Project Strategist** - Develops project strategy based on brief analysis

## Deployment

To deploy to LangGraph Platform:
```bash
langgraph deploy
```