"""
TF Supervisor Workflow Package

Music licensing workflow automation system with enhanced brief extraction
and multi-agent orchestration for Tracks & Fields.
"""

__version__ = "1.0.0"
__author__ = "TF Team"

from .agent import graph, process_brief

__all__ = ["graph", "process_brief"]