"""
Ocean Analysis Agents Package
Contains all agent implementations for the system
"""

from .parser_agent import ParserAgent
from .qa_agent import QAAgent
from .analyst_agent import AnalystAgent
from .stats_agent import StatsAgent
from .water_mass_agent import WaterMassAgent
from .poster_agent import PosterAgent
from .report_agent import ReportAgent
from .supervisor_agent import SupervisorAgent
from .researcher_agent import ResearcherAgent

__all__ = [
    'ParserAgent',
    'QAAgent',
    'AnalystAgent',
    'StatsAgent',
    'WaterMassAgent',
    'PosterAgent',
    'ReportAgent',
    'SupervisorAgent',
    'ResearcherAgent'
] 