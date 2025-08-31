"""
Social Security Application Chatbot Package

This package contains all the components for the Social Security Application Chatbot:
- Database tools for querying application information
- Search tools for job search and career guidance
- Main chatbot agent with LangChain integration
- Web interface using Streamlit
- Command-line interface for testing

Usage:
    from req_agents.chatbot_agent import SocialSecurityChatbot, ChatbotInterface
    from req_agents.database_tools import ApplicationQueryTool
    from req_agents.search_tools import JobSearchTool, CourseRecommendationTool
"""

from .chatbot_agent import SocialSecurityChatbot, ChatbotInterface
from .database_tools import ApplicationQueryTool, ApplicantSkillsExtractorTool
from .search_tools import JobSearchTool, CourseRecommendationTool

__version__ = "1.0.0"
__author__ = "Social Security System Team"

__all__ = [
    "SocialSecurityChatbot",
    "ChatbotInterface", 
    "ApplicationQueryTool",
    "ApplicantSkillsExtractorTool",
    "JobSearchTool",
    "CourseRecommendationTool"
]