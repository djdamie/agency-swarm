from datetime import datetime
from typing import Dict, Any, List

from models import (
    EnhancedAgentState, MissingInfoRequest
)


class MissingInfoDetector:
    """Detect missing critical information from brief analysis"""
    
    # Critical field mappings with user-friendly descriptions
    CRITICAL_FIELDS = {
        "business_brief.budget": {
            "description": "Budget amount for the project",
            "priority": "critical",
            "suggested_values": ["Under $5,000", "$5,000-$50,000", "Over $50,000", "TBD"]
        },
        "business_brief.territory": {
            "description": "Geographic territories where music will be used",
            "priority": "critical", 
            "suggested_values": ["United States", "Germany", "United Kingdom", "Global", "Europe"]
        },
        "business_brief.media": {
            "description": "Media channels where music will be used",
            "priority": "critical",
            "suggested_values": ["TV Commercial", "Online Video", "Radio", "Cinema", "Social Media"]
        },
        "business_brief.term": {
            "description": "Duration of music license",
            "priority": "important",
            "suggested_values": ["1 year", "2 years", "3 years", "In perpetuity", "TBD"]
        },
        "creative_brief.genres": {
            "description": "Musical genres or styles needed",
            "priority": "important",
            "suggested_values": ["Pop", "Rock", "Electronic", "Classical", "Hip-Hop", "Folk"]
        },
        "deliverables.submission_deadline": {
            "description": "When music submissions are due",
            "priority": "critical",
            "suggested_values": []
        }
    }
    
    def detect_missing_fields(self, analysis: Dict[str, Any]) -> List[str]:
        """Detect which critical fields are missing from analysis"""
        missing_fields = []
        
        for field_path, field_info in self.CRITICAL_FIELDS.items():
            if self._is_field_missing(analysis, field_path):
                missing_fields.append(field_path)
        
        return missing_fields
    
    def _is_field_missing(self, analysis: Dict[str, Any], field_path: str) -> bool:
        """Check if a specific field path is missing or empty"""
        parts = field_path.split('.')
        current_data = analysis
        
        try:
            for part in parts:
                current_data = current_data.get(part, {})
                if current_data is None:
                    return True
            
            # Check if field is empty
            if isinstance(current_data, list):
                return len(current_data) == 0
            elif isinstance(current_data, str):
                return current_data.strip() == ""
            elif current_data is None:
                return True
            
            return False
            
        except (AttributeError, TypeError):
            return True
    
    def create_missing_info_request(
        self, 
        session_id: str, 
        missing_fields: List[str]
    ) -> MissingInfoRequest:
        """Create structured request for missing information"""
        
        field_descriptions = {}
        suggested_values = {}
        critical_count = 0
        
        for field in missing_fields:
            if field in self.CRITICAL_FIELDS:
                field_config = self.CRITICAL_FIELDS[field]
                field_descriptions[field] = field_config["description"]
                suggested_values[field] = field_config["suggested_values"]
                
                if field_config["priority"] == "critical":
                    critical_count += 1
        
        # Determine overall priority
        if critical_count >= 2:
            priority = "critical"
        elif critical_count >= 1:
            priority = "important"
        else:
            priority = "optional"
        
        return MissingInfoRequest(
            session_id=session_id,
            missing_fields=missing_fields,
            field_descriptions=field_descriptions,
            priority=priority,
            suggested_values=suggested_values,
            request_message=self._generate_request_message(missing_fields, priority),
            created_at=datetime.now().isoformat()
        )
    
    def _generate_request_message(self, missing_fields: List[str], priority: str) -> str:
        """Generate user-friendly message requesting missing information"""
        
        field_names = []
        for field in missing_fields:
            if field in self.CRITICAL_FIELDS:
                field_names.append(self.CRITICAL_FIELDS[field]["description"].lower())
        
        if priority == "critical":
            return f"To provide the best music recommendations, we need some additional information: {', '.join(field_names)}. This information is critical for accurate project scoping."
        elif priority == "important": 
            return f"We found most of the key details, but could use clarification on: {', '.join(field_names)}. This will help us provide more targeted recommendations."
        else:
            return f"Optional: If available, additional details on {', '.join(field_names)} would help refine our recommendations."


class ConfidenceScorer:
    """Calculate confidence scores for brief analysis quality"""
    
    def calculate_confidence_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall confidence score (0.0 to 1.0)"""
        
        # Get extraction metrics if available
        metrics = analysis.get("extraction_metrics", {})
        
        # Base score from existing metrics
        base_score = 0.0
        
        # JSON structure validity (20% weight)
        if analysis.get("json_structure_valid", False):
            base_score += 0.2
        
        # Completion rate (30% weight)
        completion_rate = metrics.get("completion_rate", 0)
        base_score += (completion_rate / 100) * 0.3
        
        # Critical field success (25% weight)  
        if metrics.get("critical_field_success", False):
            base_score += 0.25
        
        # Enhanced interpretation quality (25% weight)
        enhanced_quality = metrics.get("enhanced_interpretation_quality", "poor")
        if enhanced_quality == "good":
            base_score += 0.25
        elif enhanced_quality == "fair":
            base_score += 0.15
        
        return min(max(base_score, 0.0), 1.0)
    
    def get_confidence_level(self, score: float) -> str:
        """Convert confidence score to human-readable level"""
        if score >= 0.8:
            return "high"
        elif score >= 0.6:
            return "medium"
        elif score >= 0.4:
            return "low"
        else:
            return "very_low"


class BriefEnhancer:
    """Enhance original brief with additional user-provided information"""
    
    def enhance_brief_content(
        self, 
        original_brief: str, 
        additional_info: Dict[str, Any]
    ) -> str:
        """Combine original brief with user-provided information"""
        
        enhancement_text = "\n\n=== ADDITIONAL INFORMATION PROVIDED ===\n"
        
        for field_path, value in additional_info.items():
            field_name = self._get_field_display_name(field_path)
            enhancement_text += f"{field_name}: {value}\n"
        
        return original_brief + enhancement_text
    
    def _get_field_display_name(self, field_path: str) -> str:
        """Convert field path to display name"""
        field_mappings = {
            "business_brief.budget": "Budget",
            "business_brief.territory": "Territory",
            "business_brief.media": "Media Usage",
            "business_brief.term": "License Term",
            "creative_brief.genres": "Musical Genres",
            "deliverables.submission_deadline": "Submission Deadline"
        }
        
        return field_mappings.get(field_path, field_path.replace("_", " ").title())
    
    def merge_analysis_with_additional_info(
        self, 
        original_analysis: Dict[str, Any], 
        additional_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge user-provided info into analysis structure"""
        
        enhanced_analysis = original_analysis.copy()
        
        for field_path, value in additional_info.items():
            self._set_nested_field(enhanced_analysis, field_path, value)
        
        # Update extraction status
        enhanced_analysis["extraction_status"] = "enhanced"
        enhanced_analysis["extraction_notes"] = enhanced_analysis.get("extraction_notes", "") + " | Enhanced with user-provided information"
        
        # Recalculate missing information
        detector = MissingInfoDetector()
        missing_fields = detector.detect_missing_fields(enhanced_analysis)
        enhanced_analysis["missing_information"] = missing_fields
        
        return enhanced_analysis
    
    def _set_nested_field(self, data: Dict[str, Any], field_path: str, value: Any):
        """Set value at nested field path"""
        parts = field_path.split('.')
        current = data
        
        # Navigate to parent
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set final value
        final_key = parts[-1]
        current[final_key] = value


# Workflow Node Functions
def missing_info_collector(state: EnhancedAgentState) -> EnhancedAgentState:
    """Node to collect missing information and generate HITL request"""
    
    brief_analysis = state.get("brief_analysis", {})
    detector = MissingInfoDetector()
    
    # Detect missing fields
    missing_fields = detector.detect_missing_fields(brief_analysis)
    
    if missing_fields:
        # Create missing info request
        request = detector.create_missing_info_request(
            state["session_id"], 
            missing_fields
        )
        
        # Add to state
        state["missing_info_requests"].append(request.model_dump())
        state["requires_user_input"] = True
        state["hitl_status"] = "pending"
        
        # Calculate confidence score
        scorer = ConfidenceScorer()
        confidence = scorer.calculate_confidence_score(brief_analysis)
        state["current_confidence_score"] = confidence
        
    else:
        state["hitl_status"] = "completed"
        state["requires_user_input"] = False
    
    return state


def brief_enhancer_node(state: EnhancedAgentState) -> EnhancedAgentState:
    """Node to enhance brief with additional user information"""
    
    if not state.get("additional_user_info"):
        return state
    
    enhancer = BriefEnhancer()
    
    # Enhance brief content
    # Always build from the original brief content to avoid duplicating addenda
    original_brief = state.get("original_brief_content") or state.get("raw_brief", "")
    enhanced_brief_content = enhancer.enhance_brief_content(
        original_brief, 
        state["additional_user_info"]
    )
    
    # Update state with enhanced content
    state["raw_brief"] = enhanced_brief_content
    
    # If we have an existing analysis, merge the additional info
    if state.get("brief_analysis"):
        enhanced_analysis = enhancer.merge_analysis_with_additional_info(
            state["brief_analysis"],
            state["additional_user_info"]
        )
        state["brief_analysis"] = enhanced_analysis
    
    # Track iteration
    state["hitl_iteration_count"] += 1
    
    # Create analysis session record
    session_record = {
        "session_id": state["session_id"],
        "iteration": state["hitl_iteration_count"],
        "timestamp": datetime.now().isoformat(),
        "analysis_result": state.get("brief_analysis", {}),
        "confidence_score": state.get("current_confidence_score", 0.0),
        "missing_info_detected": [],
        "user_input_provided": state["additional_user_info"]
    }
    
    state["analysis_sessions"].append(session_record)
    
    # Clear additional info to prevent repeated re-enhancement loops
    state["additional_user_info"] = None
    
    return state


def analysis_validator(state: EnhancedAgentState) -> EnhancedAgentState:
    """Node to validate analysis quality and determine if more HITL needed"""
    
    brief_analysis = state.get("brief_analysis", {})
    scorer = ConfidenceScorer()
    
    # Calculate current confidence
    confidence = scorer.calculate_confidence_score(brief_analysis)
    state["current_confidence_score"] = confidence
    
    # Check if we should continue HITL process
    detector = MissingInfoDetector()
    remaining_missing = detector.detect_missing_fields(brief_analysis)
    
    # Decision logic
    max_iterations_reached = state["hitl_iteration_count"] >= state["max_hitl_iterations"]
    confidence_acceptable = confidence >= 0.6
    critical_fields_resolved = len([f for f in remaining_missing 
                                   if f in detector.CRITICAL_FIELDS and 
                                   detector.CRITICAL_FIELDS[f]["priority"] == "critical"]) == 0
    
    if max_iterations_reached or confidence_acceptable or critical_fields_resolved:
        state["hitl_status"] = "completed"
        state["requires_user_input"] = False
    else:
        state["hitl_status"] = "pending"
        state["requires_user_input"] = True
        
        # Generate new missing info request for remaining fields
        if remaining_missing:
            detector = MissingInfoDetector()
            request = detector.create_missing_info_request(
                state["session_id"],
                remaining_missing
            )
            state["missing_info_requests"].append(request.model_dump())
    
    return state


def message_parser_node(state: EnhancedAgentState) -> EnhancedAgentState:
    """Parse follow-up human messages to extract missing information"""
    
    # Don't parse if we already have additional_user_info
    if state.get("additional_user_info"):
        return state
    
    # Check if we're in HITL mode with missing info requests
    if not state.get("missing_info_requests") or state.get("hitl_status") != "pending":
        return state
    
    messages = state.get("messages", [])
    if not messages:
        return state
    
    # Find the last human message
    last_human_message = None
    for message in reversed(messages):
        if hasattr(message, 'type') and message.type == "human":
            last_human_message = message
            break
    
    if not last_human_message:
        return state
    
    # Avoid re-parsing the same human message in a loop
    last_id = getattr(last_human_message, 'id', None)
    if last_id and state.get("last_parsed_human_message_id") == last_id:
        return state
    
    # Extract text content from the message
    message_text = ""
    if hasattr(last_human_message, 'content'):
        if isinstance(last_human_message.content, str):
            message_text = last_human_message.content
        elif isinstance(last_human_message.content, list):
            for part in last_human_message.content:
                if isinstance(part, dict) and part.get("type") == "text":
                    message_text = part.get("text", "")
                    break
    
    if not message_text:
        return state
    
    # Get missing fields from the most recent request
    latest_request = state["missing_info_requests"][-1]
    missing_fields = latest_request.get("missing_fields", [])
    
    # Simple parsing logic for common patterns
    additional_info = {}
    
    # Parse submission deadline
    if "deliverables.submission_deadline" in missing_fields:
        import re
        # Look for date patterns
        date_patterns = [
            r'submission deadline is (.+?)(?:\.|$)',
            r'deadline is (.+?)(?:\.|$)',
            r'due (.+?)(?:\.|$)',
            r'by (.+?)(?:\.|$)',
            r'(\w+ \d{1,2},? \d{4})',  # January 25, 2025
            r'(\d{1,2}/\d{1,2}/\d{4})', # 1/25/2025
            r'(\d{4}-\d{2}-\d{2})'     # 2025-01-25
        ]
        
        message_lower = message_text.lower()
        for pattern in date_patterns:
            match = re.search(pattern, message_lower, re.IGNORECASE)
            if match:
                date_value = match.group(1).strip()
                # Clean up common phrases
                date_value = re.sub(r'^(on|at|the)\s+', '', date_value, flags=re.IGNORECASE)
                date_value = re.sub(r'\s*(please|thanks?|thank you)\s*$', '', date_value, flags=re.IGNORECASE)
                additional_info["deliverables.submission_deadline"] = date_value.strip()
                break
    
    # Parse budget if missing
    if "business_brief.budget" in missing_fields:
        import re
        budget_patterns = [
            r'budget is (.+?)(?:\.|$)',
            r'(\$[\d,]+)',
            r'(\d+k?)\s*euros?',
            r'(\d+)\s*thousand'
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, message_text, re.IGNORECASE)
            if match:
                budget_value = match.group(1).strip()
                additional_info["business_brief.budget"] = budget_value
                break
    
    # Parse territory if missing
    if "business_brief.territory" in missing_fields:
        import re
        territory_patterns = [
            r'territory is (.+?)(?:\.|$)',
            r'in (.+?)(?:\.|$)',
            r'(United States|Germany|UK|France|Global|Europe)',
        ]
        
        for pattern in territory_patterns:
            match = re.search(pattern, message_text, re.IGNORECASE)
            if match:
                territory_value = match.group(1).strip()
                additional_info["business_brief.territory"] = territory_value
                break
    
    # If we extracted any information, add it to state
    if additional_info:
        state["additional_user_info"] = additional_info
        
        # Add a message to show what was parsed
        from langchain_core.messages import AIMessage
        parsed_fields = list(additional_info.keys())
        state["messages"].append(AIMessage(
            content=f"Parsed additional information: {', '.join(parsed_fields)}",
            name="message_parser"
        ))
    
    # Mark this human message as consumed for parsing to prevent loops
    if last_id:
        state["last_parsed_human_message_id"] = last_id
    
    return state