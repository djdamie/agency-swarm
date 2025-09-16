"""
Project Strategy Agent for TF Supervisor Workflow - LLM-BASED VERSION
====================================================================

Completely rewritten to use LLM for intelligent analysis instead of manual calculations.
This mirrors the BriefAnalyzer pattern and leverages the LLM's natural language understanding.
"""

import json
import re
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from models import AgentState
from prompts import PROJECT_STRATEGIST_PROMPT


class ProjectStrategyAgent:
    """LLM-powered Project Strategy Agent that mirrors Brief Analyzer pattern"""
    
    def __init__(self, llm):
        self.llm = llm
        
    def clean_json_response(self, raw_content: str) -> str:
        """Clean JSON from markdown and other formatting - mirrors Brief Analyzer"""
        content = raw_content.strip()
        
        # First try: Extract JSON from markdown code blocks
        json_pattern = r'```json\s*([\s\S]*?)\s*```'
        json_match = re.search(json_pattern, content)
        
        if json_match:
            return json_match.group(1).strip()
        
        # Second try: Remove markdown indicators manually
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        
        # Third try: Find JSON-like structure
        brace_start = content.find('{')
        brace_end = content.rfind('}')
        
        if brace_start != -1 and brace_end != -1:
            return content[brace_start:brace_end + 1]
        
        return content.strip()
        
    def strategize(self, state: AgentState) -> AgentState:
        """LLM-powered project strategy analysis - mirrors Brief Analyzer pattern"""
        
        brief_analysis = state.get("brief_analysis", {})
        if not brief_analysis:
            # Fallback for missing brief analysis
            state["project_strategy"] = {
                "project_type": "SYNCH_UNKNOWN",
                "budget_status": "MISSING",
                "estimated_budget": "Unknown",
                "estimated_payout": "Cannot calculate",
                "margin_percentage": "TBD",
                "immediate_actions": ["Complete brief analysis first"]
            }
            return state
        
        # Prepare LLM messages - same pattern as Brief Analyzer
        messages = [
            SystemMessage(content=PROJECT_STRATEGIST_PROMPT),
            HumanMessage(content=f"Analyze this brief and create comprehensive project strategy:\n\n{json.dumps(brief_analysis, indent=2)}")
        ]
        
        # Call LLM for strategy analysis
        response = self.llm.invoke(messages)
        
        try:
            # Clean the response content using Brief Analyzer logic
            cleaned_content = self.clean_json_response(response.content)
            
            # Parse JSON response
            strategy = json.loads(cleaned_content)
            
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            print(f"LLM strategy analysis failed: {e}")
            
            # Fallback strategy with basic analysis
            strategy = {
                "project_type": "SYNCH_UNKNOWN",
                "budget_status": "UNCLEAR", 
                "estimated_budget": "Requires clarification",
                "estimated_payout": "Cannot calculate",
                "margin_percentage": "TBD",
                "complexity_assessment": {
                    "scores": {"creative": 5, "clearance": 5, "timeline": 5, "budget": 8},
                    "overall": 6,
                    "level": "MEDIUM",
                    "assessment": "Medium complexity due to LLM parsing failure",
                    "breakdown": {
                        "creative": "Unable to assess - LLM analysis failed",
                        "clearance": "Unable to assess - LLM analysis failed", 
                        "timeline": "Unable to assess - LLM analysis failed",
                        "budget": "High complexity - LLM could not parse budget"
                    }
                },
                "search_strategies": ["free_text_search", "context_search"],
                "workflow_recommendations": ["⚠️ LLM analysis failed - manual review required"],
                "resource_requirements": ["Strategy Lead", "Senior Supervisor"],
                "risk_factors": ["LLM strategy analysis failed", "Requires manual assessment"],
                "opportunities": [],
                "mitigation_strategies": {"LLM failure": "Manual strategy review required"},
                "confidence_level": "LOW",
                "alternative_approaches": ["Manual strategy development", "Simplified workflow"],
                "immediate_actions": ["URGENT: Manual strategy review required"],
                "success_criteria": ["Complete manual strategy assessment"]
            }
        
        # Store strategy in state
        state["project_strategy"] = strategy
        
        # Create status message - extract key info from strategy
        project_type = strategy.get("project_type", "UNKNOWN")
        budget_info = strategy.get("estimated_budget", "Unknown")
        complexity_level = strategy.get("complexity_assessment", {}).get("level", "UNKNOWN")
        
        state["messages"].append(AIMessage(
            content=f"Project strategy completed. Type: {project_type}, Budget: {budget_info}, Complexity: {complexity_level}",
            name="project_strategist"
        ))
        
        return state 