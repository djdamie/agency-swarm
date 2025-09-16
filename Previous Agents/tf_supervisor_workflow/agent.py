import os
import json
import uuid
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv


from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, AIMessage
from langgraph.graph import StateGraph, END

from models import (
    AgentState, BriefAnalysis, ProjectStrategy,
    BusinessBrief, CreativeBrief, ContextualBrief,
    TechnicalBrief, Deliverables, CompetitiveBrief,
    EnhancedAgentState, MissingInfoRequest, AnalysisSession
)
from prompts import SUPERVISOR_PROMPT, BRIEF_ANALYZER_PROMPT, PROJECT_STRATEGIST_PROMPT
from project_strategy_agent import ProjectStrategyAgent
from enhanced_nodes import (
    MissingInfoDetector, ConfidenceScorer, BriefEnhancer,
    missing_info_collector, brief_enhancer_node, analysis_validator, message_parser_node
)

# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatGroq(
    temperature=0.1,
    model=os.getenv("LLM_MODEL", "openai/gpt-oss-20b"),
    groq_api_key=os.getenv("GROQ_API_KEY")
)

class BriefAnalyzerAgent:
    """Agent responsible for extracting and structuring brief information"""
    
    def __init__(self, llm):
        self.llm = llm
        
    def clean_json_response(self, raw_content: str) -> str:
        """Clean JSON from markdown and other formatting"""
        import re
        
        content = raw_content.strip()
        
        # First try: Extract JSON from markdown code blocks
        json_pattern = r'```json\s*([\s\S]*?)\s*```'
        json_match = re.search(json_pattern, content)
        
        if json_match:
            content = json_match.group(1).strip()
        else:
            # Second try: Remove markdown indicators manually
            if content.startswith("```json"):
                content = content[7:].strip()
            
            if content.endswith("```"):
                content = content[:-3].strip()
            
            # Third try: Find JSON block by looking for opening and closing braces
            # This handles cases where there's text before/after JSON
            brace_start = content.find('{')
            if brace_start != -1:
                # Find the matching closing brace
                brace_count = 0
                for i, char in enumerate(content[brace_start:], brace_start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            content = content[brace_start:i+1]
                            break
        
        # Fix common Unicode escape issues for German and other international characters
        unicode_fixes = {
            r'\\u00df': 'ß',  # German sharp s
            r'\\u00e4': 'ä',  # German a-umlaut  
            r'\\u00f6': 'ö',  # German o-umlaut
            r'\\u00fc': 'ü',  # German u-umlaut
            r'\\u00c4': 'Ä',  # German A-umlaut
            r'\\u00d6': 'Ö',  # German O-umlaut
            r'\\u00dc': 'Ü',  # German U-umlaut
            r'\\u00ab': 'ß',  # Common LLM mistake: \\u00ab should be ß in German context
            r'\\u00bb': '»',  # Right guillemet
        }
        
        for bad_escape, good_char in unicode_fixes.items():
            content = re.sub(bad_escape, good_char, content, flags=re.IGNORECASE)
        
        return content.strip()

    def validate_extraction_fields(self, analysis_dict: dict) -> dict:
        """Validate and ensure all required fields exist with proper structure"""
        
        # Ensure business_brief structure
        business_brief = analysis_dict.get("business_brief", {})
        business_brief.setdefault("client", None)
        business_brief.setdefault("agency", None)
        business_brief.setdefault("brand", None)
        business_brief.setdefault("media", [])
        business_brief.setdefault("term", None)
        business_brief.setdefault("territory", [])
        business_brief.setdefault("scripts", None)
        business_brief.setdefault("lengths", [])
        business_brief.setdefault("cutdowns", [])
        business_brief.setdefault("extras", [])
        business_brief.setdefault("options", [])
        business_brief.setdefault("budget", None)
        
        # Ensure creative_brief structure with enhanced_interpretation
        creative_brief = analysis_dict.get("creative_brief", {})
        creative_brief.setdefault("keywords", [])
        creative_brief.setdefault("reference_tracks", [])
        creative_brief.setdefault("descriptions", None)
        creative_brief.setdefault("lyrics_requirements", None)
        creative_brief.setdefault("structure", None)
        creative_brief.setdefault("instruments", [])
        creative_brief.setdefault("genres", [])
        creative_brief.setdefault("storyboard", None)
        creative_brief.setdefault("mood", None)
        
        # Ensure enhanced_interpretation exists
        enhanced = creative_brief.setdefault("enhanced_interpretation", {})
        enhanced.setdefault("search_keywords", [])
        enhanced.setdefault("mood_descriptors", [])
        enhanced.setdefault("genre_suggestions", [])
        enhanced.setdefault("reference_analysis", None)
        
        # Ensure other brief sections exist
        analysis_dict.setdefault("contextual_brief", {})
        analysis_dict.setdefault("technical_brief", {})
        analysis_dict.setdefault("deliverables", {})
        analysis_dict.setdefault("competitive_brief", {})
        
        # Set defaults
        analysis_dict.setdefault("extraction_status", "partial")
        analysis_dict.setdefault("brief_quality", "poor")
        analysis_dict.setdefault("missing_information", [])
        analysis_dict.setdefault("extraction_notes", "")
        
        return analysis_dict

    def calculate_extraction_metrics(self, analysis: dict) -> dict:
        """Calculate extraction quality metrics similar to n8n workflow"""
        
        business = analysis.get("business_brief", {})
        creative = analysis.get("creative_brief", {})
        
        # Count extracted fields
        business_fields = sum(1 for key in ["client", "agency", "brand", "budget", "territory", "media"] 
                            if business.get(key))
        creative_fields = sum(1 for key in ["keywords", "genres", "mood", "reference_tracks"]
                            if creative.get(key))
        
        # Enhanced interpretation check
        enhanced = creative.get("enhanced_interpretation", {})
        enhanced_quality = "good" if any(enhanced.get(key) for key in 
                                       ["search_keywords", "mood_descriptors", "genre_suggestions"]) else "poor"
        
        # Calculate completion rates
        total_critical_fields = 6  # client, budget, creative direction, etc.
        extracted_critical = business_fields + (1 if creative_fields > 0 else 0)
        completion_rate = round((extracted_critical / total_critical_fields) * 100, 1)
        
        return {
            "business_fields_extracted": business_fields,
            "creative_fields_extracted": creative_fields,
            "enhanced_interpretation_quality": enhanced_quality,
            "completion_rate": completion_rate,
            "critical_field_success": extracted_critical >= 3,
            "production_ready": (completion_rate >= 70 and 
                               analysis.get("json_structure_valid", False) and
                               analysis.get("extraction_status") == "complete")
        }

    def analyze(self, state: AgentState) -> AgentState:
        """Extract and structure information from the brief"""
        
        # Get brief content from either raw_brief field or chat messages
        brief_content = state.get("raw_brief", "")
        
        # If no raw_brief, extract from chat messages (Chat interface mode)
        if not brief_content and "messages" in state and state["messages"]:
            # Find the human message with the brief content
            for message in state["messages"]:
                if hasattr(message, 'type') and message.type == "human":
                    # Extract text content from message
                    if hasattr(message, 'content'):
                        if isinstance(message.content, str):
                            brief_content = message.content
                        elif isinstance(message.content, list):
                            # Handle multi-part content (like from Chat interface)
                            for part in message.content:
                                if isinstance(part, dict) and part.get("type") == "text":
                                    brief_content = part.get("text", "")
                                    break
                    # Preserve original brief content when coming from chat
                    state["original_brief_content"] = brief_content
                    break
        
        messages = [
            SystemMessage(content=BRIEF_ANALYZER_PROMPT),
            HumanMessage(content=f"Please analyze and extract the brief information from the provided email text and return ONLY valid JSON:\n\n{brief_content}\n\nReturn the extraction as pure JSON in the exact format specified. No markdown, no extra text, just JSON.")
        ]
        
        response = self.llm.invoke(messages)
        
        extraction_valid = False
        try:
            # Clean the response content using n8n logic
            cleaned_content = self.clean_json_response(response.content)
            
            # Parse JSON
            analysis_dict = json.loads(cleaned_content)
            
            # Validate and ensure proper structure
            analysis = self.validate_extraction_fields(analysis_dict)
            
            extraction_valid = True
            
        except Exception as e:
            # Enhanced fallback structure matching n8n pattern
            analysis = {
                "extraction_status": "failed",
                "brief_quality": "poor",
                "business_brief": {
                    "client": None,
                    "agency": None, 
                    "brand": None,
                    "media": [],
                    "term": None,
                    "territory": [],
                    "scripts": None,
                    "lengths": [],
                    "cutdowns": [],
                    "extras": [],
                    "options": [],
                    "budget": None
                },
                "creative_brief": {
                    "keywords": [],
                    "reference_tracks": [],
                    "descriptions": None,
                    "lyrics_requirements": None,
                    "structure": None,
                    "instruments": [],
                    "genres": [],
                    "storyboard": None,
                    "mood": None,
                    "enhanced_interpretation": {
                        "search_keywords": [],
                        "mood_descriptors": [],
                        "genre_suggestions": [],
                        "reference_analysis": None
                    }
                },
                "contextual_brief": {},
                "technical_brief": {},
                "deliverables": {},
                "competitive_brief": {},
                "missing_information": ["Unable to parse brief automatically", f"Parsing error: {str(e)}"],
                "extraction_notes": f"Automatic extraction failed. Manual review required. Error: {str(e)}",
                "error": str(e),
                "raw_output": response.content
            }
        
        # Add extraction metadata and basic metrics
        analysis["json_structure_valid"] = extraction_valid
        analysis["extraction_metrics"] = self.calculate_extraction_metrics(analysis)
        
        state["brief_analysis"] = analysis
        state["messages"].append(AIMessage(
            content=f"Brief analysis completed. Status: {analysis.get('extraction_status', 'unknown')}, Valid JSON: {extraction_valid}",
            name="brief_analyzer"
        ))
        
        return state

class EnhancedBriefAnalyzerAgent(BriefAnalyzerAgent):
    """Enhanced Brief Analyzer with HITL support"""
    
    def __init__(self, llm):
        super().__init__(llm)
        self.missing_info_detector = MissingInfoDetector()
        self.confidence_scorer = ConfidenceScorer()
        self.brief_enhancer = BriefEnhancer()
    
    def analyze_with_session(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Enhanced analysis with session tracking and HITL support"""
        
        # Store original brief content
        if not state.get("original_brief_content"):
            state["original_brief_content"] = state.get("raw_brief", "")
        
        # Perform standard analysis
        analyzed_state = self.analyze(state)
        
        # Convert to EnhancedAgentState if needed
        if not isinstance(state, dict) or "session_id" not in state:
            enhanced_state = {
                "messages": analyzed_state.get("messages", []),
                "brief_analysis": analyzed_state.get("brief_analysis"),
                "project_strategy": analyzed_state.get("project_strategy"),
                "next_agent": analyzed_state.get("next_agent", ""),
                "current_task": analyzed_state.get("current_task", ""),
                "raw_brief": analyzed_state.get("raw_brief", ""),
                # Ensure original_brief_content is preserved or set from raw_brief
                "original_brief_content": state.get("original_brief_content") or state.get("raw_brief", ""),
                "additional_user_info": None,
                "analysis_sessions": [],
                "missing_info_requests": [],
                "session_id": str(uuid.uuid4()),
                "hitl_status": "pending",
                "current_confidence_score": 0.0,
                "requires_user_input": False,
                "hitl_iteration_count": 0,
                "max_hitl_iterations": 3
            }
        else:
            enhanced_state = state
            
        # Apply missing info detection
        enhanced_state = missing_info_collector(enhanced_state)
        
        return enhanced_state
    
    def update_with_missing_info(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Update analysis with user-provided missing information"""
        
        if not state.get("additional_user_info"):
            return state
        
        # Enhance brief with additional info
        state = brief_enhancer_node(state)
        
        # Re-analyze with enhanced brief
        state = self.analyze_with_session(state)
        
        # Validate results
        state = analysis_validator(state)
        
        return state
    
    def create_missing_info_request(self, analysis: dict, session_id: str) -> dict:
        """Create structured request for missing information"""
        
        missing_fields = self.missing_info_detector.detect_missing_fields(analysis)
        
        if not missing_fields:
            return None
        
        request = self.missing_info_detector.create_missing_info_request(
            session_id, missing_fields
        )
        
        return request.model_dump()
    
    def calculate_analysis_quality(self, analysis: dict) -> dict:
        """Calculate comprehensive analysis quality metrics"""
        
        confidence_score = self.confidence_scorer.calculate_confidence_score(analysis)
        confidence_level = self.confidence_scorer.get_confidence_level(confidence_score)
        
        missing_fields = self.missing_info_detector.detect_missing_fields(analysis)
        
        # Count critical missing fields
        critical_missing = 0
        for field in missing_fields:
            if field in self.missing_info_detector.CRITICAL_FIELDS:
                if self.missing_info_detector.CRITICAL_FIELDS[field]["priority"] == "critical":
                    critical_missing += 1
        
        return {
            "confidence_score": confidence_score,
            "confidence_level": confidence_level,
            "missing_fields_count": len(missing_fields),
            "critical_missing_count": critical_missing,
            "analysis_complete": len(missing_fields) == 0,
            "production_ready": confidence_score >= 0.8 and critical_missing == 0
        }


class ProjectStrategistAgent:
    """Wrapper for the dedicated Project Strategy Agent"""
    
    def __init__(self, llm):
        # Initialize the dedicated strategy agent
        self.strategy_agent = ProjectStrategyAgent(llm)
    
    def strategize(self, state: AgentState) -> AgentState:
        """Use the dedicated strategy agent for comprehensive analysis"""
        return self.strategy_agent.strategize(state)

class EnhancedSupervisorAgent:
    """Enhanced supervisor with HITL workflow support"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def route_enhanced(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Enhanced routing with HITL workflow logic"""
        
        # Check HITL status first - but allow message parsing and brief enhancement
        if state.get("requires_user_input", False) and not state.get('additional_user_info'):
            # Check if we have new human messages to parse first
            messages = state.get('messages', [])
            has_new_human_message = False
            for message in reversed(messages):
                if hasattr(message, 'type') and message.type == "human":
                    # Found a human message - check if it's not the original brief
                    if len(messages) > 3:  # Original brief + initial AI responses
                        has_new_human_message = True
                    break
            
            if has_new_human_message:
                # Let the workflow continue to parse the message
                pass
            else:
                state["next_agent"] = "hitl_request"
                return state
        
        # Standard workflow routing
        current_state_summary = f"""
        Brief Analysis: {'Present' if state.get('brief_analysis') else 'Missing'}
        Project Strategy: {'Present' if state.get('project_strategy') else 'Missing'}
        HITL Status: {state.get('hitl_status', 'pending')}
        Confidence Score: {state.get('current_confidence_score', 0.0)}
        Messages: {len(state.get('messages', []))}
        """
        
        # Routing logic
        if not state.get('brief_analysis'):
            next_agent = 'enhanced_brief_analyzer'
        elif state.get('hitl_status') == 'pending' and not state.get('additional_user_info'):
            # Check if we have new human messages to parse
            messages = state.get('messages', [])
            has_new_human_message = False
            for message in reversed(messages):
                if hasattr(message, 'type') and message.type == "human":
                    # Found a human message - check if it's not the original brief
                    if len(messages) > 3:  # Original brief + initial AI responses
                        has_new_human_message = True
                    break
            next_agent = 'message_parser' if has_new_human_message else 'hitl_request'
        elif state.get('hitl_status') == 'pending' and state.get('additional_user_info'):
            next_agent = 'brief_enhancer'
        elif not state.get('project_strategy') and state.get('hitl_status') == 'completed':
            next_agent = 'project_strategist'
        else:
            next_agent = 'end'
            
        state["next_agent"] = next_agent
        state["messages"].append(AIMessage(
            content=f"Enhanced routing to: {next_agent}",
            name="enhanced_supervisor"
        ))
        
        return state


class SupervisorAgent:
    """Agent responsible for orchestrating the workflow"""
    
    def __init__(self, llm):
        self.llm = llm
        
    def route(self, state: AgentState) -> AgentState:
        """Decide which agent should act next"""
        
        current_state_summary = f"""
        Brief Analysis: {'Present' if state.get('brief_analysis') else 'Missing'}
        Project Strategy: {'Present' if state.get('project_strategy') else 'Missing'}
        Messages: {len(state.get('messages', []))}
        """
        
        messages = [
            SystemMessage(content=SUPERVISOR_PROMPT),
            HumanMessage(content=f"Current state:\n{current_state_summary}\n\nWhich agent should act next?")
        ]
        
        response = self.llm.invoke(messages)
        next_agent = response.content.strip().lower()
        
        # Ensure valid routing
        if not state.get('brief_analysis'):
            next_agent = 'brief_analyzer'
        elif not state.get('project_strategy'):
            next_agent = 'project_strategist'
        else:
            next_agent = 'end'
            
        state["next_agent"] = next_agent
        state["messages"].append(AIMessage(
            content=f"Routing to: {next_agent}",
            name="supervisor"
        ))
        
        return state

# Create the enhanced workflow graph with HITL support
def create_enhanced_workflow():
    """Create and compile the enhanced TF workflow graph with HITL"""
    
    # Initialize agents
    enhanced_brief_analyzer = EnhancedBriefAnalyzerAgent(llm)
    strategist = ProjectStrategistAgent(llm)
    enhanced_supervisor = EnhancedSupervisorAgent(llm)
    
    # Create the graph with Enhanced state
    workflow = StateGraph(EnhancedAgentState)
    
    # Add nodes
    workflow.add_node("enhanced_supervisor", enhanced_supervisor.route_enhanced)
    workflow.add_node("enhanced_brief_analyzer", enhanced_brief_analyzer.analyze_with_session)
    workflow.add_node("brief_enhancer", enhanced_brief_analyzer.update_with_missing_info)
    workflow.add_node("project_strategist", strategist.strategize)
    
    # Add HITL workflow nodes
    workflow.add_node("missing_info_collector", missing_info_collector)
    workflow.add_node("analysis_validator", analysis_validator)
    workflow.add_node("message_parser", message_parser_node)
    
    # Add edges
    workflow.add_edge("enhanced_brief_analyzer", "enhanced_supervisor")
    workflow.add_edge("brief_enhancer", "enhanced_supervisor") 
    workflow.add_edge("project_strategist", "enhanced_supervisor")
    workflow.add_edge("missing_info_collector", "enhanced_supervisor")
    workflow.add_edge("analysis_validator", "enhanced_supervisor")
    workflow.add_edge("message_parser", "enhanced_supervisor")
    
    # Conditional routing from enhanced supervisor
    def route_enhanced_supervisor(state):
        return state.get("next_agent", "end")
    
    workflow.add_conditional_edges(
        "enhanced_supervisor",
        route_enhanced_supervisor,
        {
            "enhanced_brief_analyzer": "enhanced_brief_analyzer",
            "brief_enhancer": "brief_enhancer",
            "project_strategist": "project_strategist",
            "missing_info_collector": "missing_info_collector",
            "analysis_validator": "analysis_validator",
            "message_parser": "message_parser",
            "hitl_request": END,  # Pause for user input
            "end": END
        }
    )
    
    # Set entry point
    workflow.set_entry_point("enhanced_supervisor")
    
    # Compile
    return workflow.compile()


# Create the workflow graph
def create_workflow():
    """Create and compile the TF workflow graph"""
    
    # Initialize agents
    brief_analyzer = BriefAnalyzerAgent(llm)
    strategist = ProjectStrategistAgent(llm)
    supervisor = SupervisorAgent(llm)
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor.route)
    workflow.add_node("brief_analyzer", brief_analyzer.analyze)
    workflow.add_node("project_strategist", strategist.strategize)
    
    # Add edges
    workflow.add_edge("brief_analyzer", "supervisor")
    workflow.add_edge("project_strategist", "supervisor")
    
    # Conditional routing from supervisor
    def route_supervisor(state):
        return state.get("next_agent", "end")
    
    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "brief_analyzer": "brief_analyzer",
            "project_strategist": "project_strategist",
            "end": END
        }
    )
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Compile
    return workflow.compile()

# Create graph instances for LangGraph deployment
# Align with BRIEF_AGENT_DEVELOPMENT_PLAN.md naming
original = create_workflow()
agent = create_enhanced_workflow()

# Backward compatibility exports
graph = original
enhanced_graph = agent

# Helper function for testing
def process_brief(brief_text: str) -> Dict[str, Any]:
    """Process a brief through the TF workflow"""
    
    initial_state = {
        "messages": [],
        "brief_analysis": None,
        "project_strategy": None,
        "next_agent": "",
        "current_task": "analyze_brief",
        "raw_brief": brief_text
    }
    
    final_state = graph.invoke(initial_state)
    
    return {
        "brief_analysis": final_state.get("brief_analysis"),
        "project_strategy": final_state.get("project_strategy"),
        "messages": final_state.get("messages", [])
    }

# Enhanced helper function with HITL support
def process_brief_enhanced(brief_text: str, session_id: str = None) -> Dict[str, Any]:
    """Process a brief through the enhanced TF workflow with HITL support"""
    
    initial_state = {
        "messages": [],
        "brief_analysis": None,
        "project_strategy": None,
        "next_agent": "",
        "current_task": "analyze_brief_enhanced",
        "raw_brief": brief_text,
        "original_brief_content": brief_text,
        "additional_user_info": None,
        "analysis_sessions": [],
        "missing_info_requests": [],
        "session_id": session_id or str(uuid.uuid4()),
        "hitl_status": "pending",
        "current_confidence_score": 0.0,
        "requires_user_input": False,
        "hitl_iteration_count": 0,
        "max_hitl_iterations": 3
    }
    
    final_state = enhanced_graph.invoke(initial_state)
    
    return {
        "brief_analysis": final_state.get("brief_analysis"),
        "project_strategy": final_state.get("project_strategy"),
        "session_id": final_state.get("session_id"),
        "hitl_status": final_state.get("hitl_status"),
        "requires_user_input": final_state.get("requires_user_input", False),
        "missing_info_requests": final_state.get("missing_info_requests", []),
        "current_confidence_score": final_state.get("current_confidence_score", 0.0),
        "analysis_sessions": final_state.get("analysis_sessions", []),
        "messages": final_state.get("messages", [])
    }

# Helper function to continue HITL workflow with user input
def continue_brief_analysis_with_input(
    session_id: str, 
    additional_info: Dict[str, Any],
    current_state: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Continue enhanced brief analysis with user-provided information"""
    
    if current_state:
        # Resume from existing state
        enhanced_state = current_state.copy()
    else:
        # Create minimal state (would typically be stored/retrieved)
        enhanced_state = {
            "messages": [],
            "brief_analysis": None,
            "project_strategy": None,
            "next_agent": "",
            "current_task": "enhance_brief",
            "raw_brief": "",
            "original_brief_content": "",
            "additional_user_info": None,
            "analysis_sessions": [],
            "missing_info_requests": [],
            "session_id": session_id,
            "hitl_status": "pending",
            "current_confidence_score": 0.0,
            "requires_user_input": False,
            "hitl_iteration_count": 0,
            "max_hitl_iterations": 3
        }
    
    # Add user input
    enhanced_state["additional_user_info"] = additional_info
    enhanced_state["current_task"] = "enhance_brief"
    
    # Continue workflow
    final_state = enhanced_graph.invoke(enhanced_state)
    
    return {
        "brief_analysis": final_state.get("brief_analysis"),
        "project_strategy": final_state.get("project_strategy"),
        "session_id": final_state.get("session_id"),
        "hitl_status": final_state.get("hitl_status"),
        "requires_user_input": final_state.get("requires_user_input", False),
        "missing_info_requests": final_state.get("missing_info_requests", []),
        "current_confidence_score": final_state.get("current_confidence_score", 0.0),
        "analysis_sessions": final_state.get("analysis_sessions", []),
        "messages": final_state.get("messages", [])
    }