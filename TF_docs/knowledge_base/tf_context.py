# tf_context.py
"""
TF (Tracks & Fields) Agent System Context
Project: Music licensing workflow automation
Key APIs: Spotify, Chartmetric, AIMS, Odoo, TF Platform
See ~/Desktop/TF_workflows/docs/ for full analysis

This file contains all project constants and shared context
that agents can import to maintain consistency.
"""

# Project Types with thresholds and workflows
PROJECT_TYPES = {
    'SYNCH_A': {
        'threshold': 100000,
        'workflow': 'full',
        'features': ['custom_mailouts', 'management_oversight', 'extensive_clearance']
    },
    'SYNCH_B': {
        'threshold': 25000,  # or 10000, TBD
        'workflow': 'standard',
        'features': ['playlist_or_request', 'custom_mailouts', 'team_collaboration']
    },
    'SYNCH_C': {
        'threshold': 0,
        'workflow': 'simplified',
        'features': ['request_first', 'tbc_checking']
    },
    'PRODUCTION': {
        'workflow': 'custom',
        'features': ['mood_playlists', 'composer_selection', 'singer_casting']
    }
}

# Margin Structure (budget_min, budget_max, margin_percentage)
MARGIN_STRUCTURE = [
    (0, 1500, 1.0),           # 100% - Library Blanket Deals
    (1500, 30000, 0.5),       # 50%
    (30000, 100000, 0.25),    # 25%
    (100000, 250000, 0.20),   # 20%
    (500000, float('inf'), 0.10),  # 10%
]

# Custom Client Arrangements
CUSTOM_CLIENTS = {
    'Client 1': {'type': 'percentage', 'value': 0.15},
    'Client 2': {'type': 'flat_fee', 'value': 10000},
    'Client 3': {'type': 'hourly', 'value': 'with_estimates'},
    'Client 4': {'type': 'custom', 'value': 'TBD'},
}

# Brief Types and Required Fields
BRIEF_TYPES = {
    'business': {
        'required': ['media', 'term', 'territory', 'budget'],
        'optional': ['scripts', 'lengths', 'extras', 'options']
    },
    'creative': {
        'required': ['keywords', 'descriptions'],
        'optional': ['reference_tracks', 'lyrics', 'structure', 'instruments', 'genres']
    },
    'contextual': {
        'required': ['brand'],
        'optional': ['brand_category', 'story', 'music_performance', 'audience_preferences']
    },
    'technical': {
        'required': ['length'],
        'optional': ['musical_attributes', 'process']
    },
    'deliverables': {
        'required': ['submission_deadline'],
        'optional': ['general_deadlines']
    },
    'competitive': {
        'optional': ['alternatives', 'competitor_analysis']
    }
}

# Member Tiers (for search prioritization)
MEMBER_TIERS = [
    'Featured Tracks',
    'One2One Rep',
    'Elevated Partner',
    'Standard Member'
]

# Price Filters
PRICE_TIERS = {
    '$': (0, 5000),
    '$$': (5000, 15000),
    '$$$': (15000, 50000),
    '$$$$': (50000, float('inf'))
}

# Workflow States
WORKFLOW_STATES = {
    'NEW': 'New project received',
    'BRIEF_EXTRACTED': 'Brief data extracted',
    'STRATEGY_DEFINED': 'Project strategy determined',
    'SEARCHING': 'Conducting searches',
    'SHORTLISTING': 'Creating shortlist',
    'CLIENT_REVIEW': 'Awaiting client feedback',
    'CLEARANCE': 'Clearing rights',
    'CONTRACTED': 'Contracts in progress',
    'DELIVERED': 'Assets delivered',
    'COMPLETE': 'Project complete'
}

# Search Types
SEARCH_TYPES = [
    'lyrics',
    'reference',
    'free_text',
    'context_stats',
    'similarity',
    'prompt'
]

# Integration Endpoints (to be updated after client meeting)
INTEGRATIONS = {
    'spotify': {
        'base_url': 'https://api.spotify.com/v1',
        'auth_type': 'oauth2'
    },
    'chartmetric': {
        'status': 'already_developed',
        'auth_type': 'api_key'
    },
    'aims': {
        'status': 'pending_info',
        'auth_type': 'unknown'
    },
    'tf_platform': {
        'base_url': 'tracksandfields.com/api',  # TBD
        'auth_type': 'unknown'
    },
    'odoo': {
        'auth_type': 'api_key',
        'modules': ['project', 'crm', 'account']
    }
}

# File Storage Platforms
FILE_STORAGE_PLATFORMS = [
    'Box',
    'Nextcloud',
    'Disco',
    'Transfer'
]

# Email Templates (to be defined)
EMAIL_TEMPLATES = {
    'missing_brief_info': 'Template for requesting missing brief information',
    'project_update': 'Template for project status updates',
    'clearance_request': 'Template for rights clearance requests',
    'newsletter': 'Template for member newsletters'
}

# Knowledge Base Configuration
KNOWLEDGE_BASE = {
    'path': 'knowledge_base',
    'structure': {
        'briefs': 'Historical project briefs with outcomes',
        'templates': 'Email and communication templates',
        'clearances': 'Rights clearance history and pricing',
        'search_patterns': 'Successful search strategies',
        'client_prefs': 'Client-specific preferences'
    },
    'analyzer': 'knowledge_base/brief_analyzer.py',
    'features': [
        'Similar brief matching',
        'Fee estimation based on history',
        'Search strategy suggestions',
        'Client preference tracking'
    ]
}

def get_project_type(budget):
    """Determine project type based on budget."""
    if budget >= PROJECT_TYPES['SYNCH_A']['threshold']:
        return 'SYNCH_A'
    elif budget >= PROJECT_TYPES['SYNCH_B']['threshold']:
        return 'SYNCH_B'
    else:
        return 'SYNCH_C'

def calculate_payout(budget, client=None):
    """Calculate payout based on budget and margin structure."""
    if client and client in CUSTOM_CLIENTS:
        custom = CUSTOM_CLIENTS[client]
        if custom['type'] == 'percentage':
            return budget * (1 - custom['value'])
        elif custom['type'] == 'flat_fee':
            return budget - custom['value']
        else:
            return None  # Requires manual calculation
    
    for min_budget, max_budget, margin in MARGIN_STRUCTURE:
        if min_budget <= budget < max_budget:
            return budget * (1 - margin)
    
    return budget * 0.9  # Default 10% margin if not in structure

# Agent Communication Patterns
AGENT_OUTPUTS = {
    1: {
        'name': 'Search Module',
        'input': 'Search brief of any type',
        'output': 'List of songs with Spotify track ID and TF.com track ID'
    },
    2: {
        'name': 'Playlist/Request Creation',
        'input': 'Project executor brief',
        'output': 'Playlist/request created, shortlisted, message to Account Manager'
    },
    3: {
        'name': 'Clearance Module',
        'input': 'Song and buyout details',
        'output': 'Email to rights holders with recipients listed'
    }
}