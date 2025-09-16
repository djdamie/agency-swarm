from typing import TypedDict, Annotated, List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState
import uuid

# State definition for the workflow
class AgentState(MessagesState):
    """Enhanced state with LangGraph compatibility"""
    brief_analysis: Optional[Dict[str, Any]] = None
    project_strategy: Optional[Dict[str, Any]] = None
    next_agent: str = ""
    current_task: str = ""
    raw_brief: str = ""

# Brief Analysis Models
class BusinessBrief(BaseModel):
    client: Optional[str] = None
    agency: Optional[str] = None
    brand: Optional[str] = None
    media: List[str] = Field(default_factory=list)
    term: Optional[str] = None
    territory: List[str] = Field(default_factory=list)
    scripts: Optional[str] = None
    lengths: List[str] = Field(default_factory=list)
    cutdowns: List[str] = Field(default_factory=list)
    extras: List[str] = Field(default_factory=list)
    options: List[str] = Field(default_factory=list)
    budget: Optional[str] = None

class EnhancedInterpretation(BaseModel):
    search_keywords: List[str] = Field(default_factory=list)
    mood_descriptors: List[str] = Field(default_factory=list)
    genre_suggestions: List[str] = Field(default_factory=list)
    reference_analysis: Optional[str] = None

class CreativeBrief(BaseModel):
    keywords: List[str] = Field(default_factory=list)
    reference_tracks: List[str] = Field(default_factory=list)
    descriptions: Optional[str] = None
    lyrics_requirements: Optional[str] = None
    structure: Optional[str] = None
    instruments: List[str] = Field(default_factory=list)
    genres: List[str] = Field(default_factory=list)
    storyboard: Optional[str] = None
    mood: Optional[str] = None
    enhanced_interpretation: Optional[EnhancedInterpretation] = None

class ContextualBrief(BaseModel):
    brand: Optional[str] = None
    brand_category: Optional[str] = None
    story: Optional[str] = None
    music_performance: Optional[str] = None
    brand_attributes: List[str] = Field(default_factory=list)
    audience_preferences: Optional[str] = None

class TechnicalBrief(BaseModel):
    lengths: List[str] = Field(default_factory=list)
    musical_attributes: Dict[str, Optional[str]] = Field(
        default_factory=lambda: {"bpm": None, "key": None, "time_signature": None}
    )
    special_processes: Optional[str] = None
    stem_requirements: Optional[str] = None
    format_specs: Optional[str] = None

class Deliverables(BaseModel):
    submission_deadline: Optional[str] = None
    ppm_date: Optional[str] = None
    shoot_date: Optional[str] = None
    offline_date: Optional[str] = None
    online_date: Optional[str] = None
    air_date: Optional[str] = None

class CompetitiveBrief(BaseModel):
    competitor_activity: Optional[str] = None
    alternative_approaches: List[str] = Field(default_factory=list)
    stakeholders: List[str] = Field(default_factory=list)
    pitch_situation: Optional[str] = None

class BriefAnalysis(BaseModel):
    extraction_status: Literal["complete", "partial"]
    brief_quality: Literal["excellent", "good", "poor"]
    business_brief: BusinessBrief
    creative_brief: CreativeBrief
    contextual_brief: ContextualBrief
    technical_brief: TechnicalBrief
    deliverables: Deliverables
    competitive_brief: CompetitiveBrief
    missing_information: List[str] = Field(default_factory=list)
    extraction_notes: str

# Project Strategy Models
class ProjectStrategy(BaseModel):
    project_type: Literal["Synch A-Type", "Synch B-Type", "Synch C-Type", "Production", "Unknown"]
    estimated_payout: float
    margin_percentage: float
    workflow_recommendations: List[str] = Field(default_factory=list)
    resource_requirements: List[str] = Field(default_factory=list)
    risk_factors: List[str] = Field(default_factory=list)
    alternative_approaches: List[str] = Field(default_factory=list)
    immediate_actions: List[str] = Field(default_factory=list)

# Enhanced HITL Models
class MissingInfoRequest(BaseModel):
    """Structured missing information request for HITL workflows"""
    session_id: str
    missing_fields: List[str]
    field_descriptions: Dict[str, str]
    priority: Literal["critical", "important", "optional"]
    suggested_values: Dict[str, List[str]] = Field(default_factory=dict)
    request_message: Optional[str] = None
    created_at: Optional[str] = None

class AnalysisSession(BaseModel):
    """Track analysis iterations within a session"""
    session_id: str
    iteration: int
    timestamp: str
    analysis_result: Dict[str, Any]
    confidence_score: float
    missing_info_detected: List[str]
    user_input_provided: Optional[Dict[str, Any]] = None

class EnhancedAgentState(MessagesState):
    """Enhanced state with HITL support"""
    # Original fields
    brief_analysis: Optional[Dict[str, Any]] = None
    project_strategy: Optional[Dict[str, Any]] = None
    next_agent: str = ""
    current_task: str = ""
    raw_brief: str = ""
    
    # HITL Enhancement fields
    original_brief_content: str = ""
    additional_user_info: Optional[Dict[str, Any]] = None
    analysis_sessions: List[Dict[str, Any]] = Field(default_factory=list)
    missing_info_requests: List[Dict[str, Any]] = Field(default_factory=list)
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hitl_status: Literal["pending", "completed", "skipped"] = "pending"
    current_confidence_score: float = 0.0
    
    # Workflow control
    requires_user_input: bool = False
    hitl_iteration_count: int = 0
    max_hitl_iterations: int = 3
    # Internal guard to avoid re-parsing the same message
    last_parsed_human_message_id: Optional[str] = None