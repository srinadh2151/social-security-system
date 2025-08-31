"""
LangChain-Enhanced Social Security Chatbot

An intelligent chatbot using LangChain framework for tool routing and conversation management.
"""

import re
from typing import Dict, Any, Optional, List
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_database_tools import SimpleApplicationQuery
from search_tools import JobSearchTool, CourseRecommendationTool
import json
import os

# Load environment variables (with fallback)
try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# LangChain imports (with fallback for missing dependencies)
try:
    from langchain.tools import Tool
    from langchain.schema import BaseMessage, HumanMessage, AIMessage
    from langchain.prompts import PromptTemplate
    
    # Try newer imports first, fallback to older ones
    try:
        from langchain_openai import ChatOpenAI
        from langchain_community.llms import OpenAI
    except ImportError:
        from langchain.chat_models import ChatOpenAI
        from langchain.llms import OpenAI
    
    # Try newer chain approach, fallback to LLMChain
    try:
        from langchain.chains import LLMChain
    except ImportError:
        pass
    
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # Fallback classes for when LangChain is not available
    class Tool:
        def __init__(self, name, description, func):
            self.name = name
            self.description = description
            self.func = func
    
    class BaseMessage:
        pass
    
    class HumanMessage(BaseMessage):
        def __init__(self, content):
            self.content = content
    
    class AIMessage(BaseMessage):
        def __init__(self, content):
            self.content = content
    
    LANGCHAIN_AVAILABLE = False


class CareerCounselingTool:
    """AI-powered career counseling tool using OpenAI LLM."""
    
    def __init__(self):
        """Initialize the career counseling tool with OpenAI LLM."""
        self.available = False
        
        if not LANGCHAIN_AVAILABLE:
            print("Info: LangChain not available - using intelligent counseling fallback")
            return
        
        try:
            # Check for OpenAI API key
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("Info: OpenAI API key not found - using intelligent counseling fallback")
                return
            
            # Initialize OpenAI LLM
            self.llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.7,
                openai_api_key=api_key
            )
            
            # Create counseling prompt template
            self.counseling_prompt = PromptTemplate(
                input_variables=["user_query", "applicant_context", "conversation_history"],
                template="""
You are a professional career counselor with expertise in UAE job market and career development. 
You provide personalized, empathetic, and actionable career advice.

APPLICANT CONTEXT:
{applicant_context}

CONVERSATION HISTORY:
{conversation_history}

USER QUERY:
{user_query}

COUNSELING GUIDELINES:
- Be empathetic and supportive in your tone
- Provide specific, actionable advice tailored to UAE job market
- Consider the applicant's background, education, and experience
- Ask clarifying questions when needed
- Offer both short-term and long-term career strategies
- Include cultural considerations for UAE workplace
- Be encouraging while being realistic about challenges
- Suggest concrete next steps

Respond as a caring, professional career counselor would:
"""
            )
            
            # Create LLM chain
            self.counseling_chain = LLMChain(
                llm=self.llm,
                prompt=self.counseling_prompt
            )
            
            self.available = True
            print("✅ OpenAI career counselor initialized successfully")
            
        except Exception as e:
            print(f"Info: OpenAI not available for career counseling: {str(e)}")
            self.available = False
    
    def provide_counseling(self, user_query: str, applicant_context: dict = None, conversation_history: list = None) -> str:
        """Provide AI-powered career counseling."""
        if not self.available:
            return self._fallback_counseling(user_query, applicant_context)
        
        try:
            # Format applicant context
            context_str = self._format_applicant_context(applicant_context)
            
            # Format conversation history
            history_str = self._format_conversation_history(conversation_history)
            
            # Generate counseling response
            response = self.counseling_chain.run(
                user_query=user_query,
                applicant_context=context_str,
                conversation_history=history_str
            )
            
            return f"""
🧠 **CAREER COUNSELING SESSION**
{'=' * 50}

{response}

💡 **Next Steps:**
• Reflect on the advice provided
• Consider scheduling a follow-up discussion
• Take action on the specific recommendations
• Feel free to ask more detailed questions

🤝 **Remember:** Career development is a journey, and I'm here to support you every step of the way.
"""
        
        except Exception as e:
            print(f"Error in career counseling: {str(e)}")
            return self._fallback_counseling(user_query, applicant_context)
    
    def _format_applicant_context(self, applicant_context: dict) -> str:
        """Format applicant context for the prompt."""
        if not applicant_context:
            return "No specific applicant information available."
        
        context_parts = []
        if applicant_context.get('name'):
            context_parts.append(f"Name: {applicant_context['name']}")
        if applicant_context.get('current_job'):
            context_parts.append(f"Current Role: {applicant_context['current_job']}")
        if applicant_context.get('education'):
            context_parts.append(f"Education: {applicant_context['education']}")
        if applicant_context.get('experience_years'):
            context_parts.append(f"Experience: {applicant_context['experience_years']} years")
        if applicant_context.get('age'):
            context_parts.append(f"Age: {applicant_context['age']}")
        
        return "\n".join(context_parts) if context_parts else "General career counseling request."
    
    def _format_conversation_history(self, conversation_history: list) -> str:
        """Format conversation history for context."""
        if not conversation_history or len(conversation_history) < 2:
            return "This is the start of our conversation."
        
        # Get last few exchanges for context
        recent_history = conversation_history[-6:]  # Last 3 exchanges
        formatted = []
        
        for entry in recent_history:
            role = "User" if entry.get('role') == 'user' else "Counselor"
            content = entry.get('content', '')[:200]  # Limit length
            formatted.append(f"{role}: {content}")
        
        return "\n".join(formatted)
    
    def _fallback_counseling(self, user_query: str, applicant_context: dict = None) -> str:
        """Intelligent fallback counseling when OpenAI is not available."""
        # Create a more intelligent fallback based on query analysis
        query_lower = user_query.lower()
        
        # Analyze the type of career concern
        if any(word in query_lower for word in ['stuck', 'confused', 'lost', 'direction']):
            advice_type = "career_direction"
        elif any(word in query_lower for word in ['change', 'switch', 'transition']):
            advice_type = "career_change"
        elif any(word in query_lower for word in ['growth', 'promotion', 'advance']):
            advice_type = "career_growth"
        elif any(word in query_lower for word in ['skills', 'learn', 'develop']):
            advice_type = "skill_development"
        else:
            advice_type = "general"
        
        # Get applicant context
        name = applicant_context.get('name', 'there') if applicant_context else 'there'
        current_job = applicant_context.get('current_job', 'your current role') if applicant_context else 'your current role'
        experience = applicant_context.get('experience_years', 0) if applicant_context else 0
        
        # Generate contextual advice
        advice = self._generate_contextual_advice(advice_type, name, current_job, experience, user_query)
        
        return f"""
� ***CAREER COUNSELING SESSION**
{'=' * 50}

Hello {name}! I understand you're asking: "{user_query}"

{advice}

💡 **Immediate Next Steps:**
• Reflect on the guidance provided above
• Consider your personal values and long-term goals
• Take one small action today toward your career development
• Feel free to ask more specific questions

🤝 **Additional Support Available:**
• 🔍 **Job Search**: "find jobs for {current_job}" - Get real opportunities
• 📚 **Skill Development**: "recommend courses" - Find training programs
• 📋 **Application Review**: Provide your application ID for personalized advice

**Remember:** Every career journey has challenges, but with the right strategy and persistence, you can achieve your goals. I'm here to support you every step of the way.
"""
    
    def _generate_contextual_advice(self, advice_type: str, name: str, current_job: str, experience: int, query: str) -> str:
        """Generate contextual career advice based on the situation."""
        
        if advice_type == "career_direction":
            return f"""
**Finding Your Career Direction:**

It's completely normal to feel uncertain about your career path, especially in today's rapidly changing job market. Here's my guidance:

🎯 **Self-Assessment:**
• Reflect on what energizes you in your current role as {current_job}
• Identify your core strengths and natural talents
• Consider what impact you want to make in the UAE market

🔍 **Exploration Strategy:**
• Research growth sectors in UAE (technology, renewable energy, healthcare, finance)
• Network with professionals in fields that interest you
• Consider informational interviews to learn about different paths

📈 **With {experience} years of experience, you have valuable insights to offer. Use this as a foundation to explore adjacent opportunities.**
"""
        
        elif advice_type == "career_change":
            return f"""
**Career Transition Guidance:**

Career changes can be both exciting and challenging. Here's a strategic approach:

⚖️ **Assessment Phase:**
• Evaluate your transferable skills from {current_job}
• Research the UAE job market in your target field
• Assess financial implications and timeline for transition

🛤️ **Transition Strategy:**
• Consider gradual transition vs. complete career pivot
• Build relevant skills through courses or certifications
• Start networking in your target industry
• Update your personal brand (LinkedIn, CV) to reflect new direction

💪 **With {experience} years of experience, you have a strong foundation. Many skills are transferable across industries.**
"""
        
        elif advice_type == "career_growth":
            return f"""
**Career Advancement Strategy:**

Growth opportunities exist even in challenging times. Here's how to position yourself:

🚀 **Advancement Tactics:**
• Identify key skills needed for the next level in your field
• Seek stretch assignments and additional responsibilities
• Build relationships with senior leaders and mentors
• Document your achievements and impact quantitatively

🌟 **Leadership Development:**
• Develop both technical and soft skills
• Consider management training or leadership courses
• Look for opportunities to lead projects or mentor others

📊 **In the UAE market, professionals with {experience} years of experience are well-positioned for senior roles. Focus on demonstrating business impact.**
"""
        
        elif advice_type == "skill_development":
            return f"""
**Skill Development Strategy:**

Continuous learning is essential in today's economy. Here's your development plan:

🎓 **Learning Priorities:**
• Identify in-demand skills in your industry and the UAE market
• Focus on both technical skills and soft skills (communication, leadership)
• Consider digital skills that are increasingly important

📚 **Learning Approach:**
• Mix formal education (certifications) with practical application
• Join professional associations and attend industry events
• Find a mentor who can guide your development

🔧 **Given your background in {current_job}, focus on skills that complement your existing expertise while opening new opportunities.**
"""
        
        else:  # general advice
            return f"""
**General Career Guidance:**

Career development is a journey, not a destination. Here's my holistic advice:

🎯 **Career Foundation:**
• Define your personal mission and values
• Set both short-term (1-2 years) and long-term (5-10 years) goals
• Build a strong professional network in the UAE

💼 **Professional Excellence:**
• Continuously improve in your current role as {current_job}
• Stay updated with industry trends and market changes
• Maintain a growth mindset and embrace challenges

🌍 **UAE Market Considerations:**
• Understand cultural nuances in the workplace
• Build relationships across diverse backgrounds
• Consider the unique opportunities in the UAE's growing economy

**Your {experience} years of experience give you a solid foundation. Focus on leveraging this while remaining open to new opportunities.**
"""


class IntelligentRouter:
    """Intelligent router for determining which tool to use based on user input."""
    
    def __init__(self):
        """Initialize the router with tools."""
        self.db_tool = SimpleApplicationQuery()
        self.job_tool = JobSearchTool()
        self.course_tool = CourseRecommendationTool()
        self.counseling_tool = CareerCounselingTool()
        self.current_applicant_data = None
    
    def route_query(self, user_input: str, conversation_history: list = None) -> str:
        """Route user query to appropriate tool and return response."""
        user_input_lower = user_input.lower()
        
        # Check for application ID pattern (both APP-YYYY-XXXXXX and UUID formats)
        app_id_match = re.search(r'APP-\d{4}-\d{6}', user_input, re.IGNORECASE)
        uuid_match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', user_input, re.IGNORECASE)
        
        if app_id_match:
            return self._handle_application_query(app_id_match.group().upper())
        elif uuid_match:
            return self._handle_application_query(uuid_match.group().lower())
        
        # Check for job search intent
        job_keywords = ['find job', 'job search', 'employment', 'work opportunities', 'career opportunities', 'looking for', 'positions']
        if any(keyword in user_input_lower for keyword in job_keywords):
            return self._handle_job_search(user_input)
        
        # Check for career counseling intent (more personal/advice-oriented)
        counseling_keywords = [
            'career advice', 'career counseling', 'career counselor', 'what should i do',
            'career path', 'career change', 'career direction', 'career planning',
            'feeling stuck', 'career confusion', 'career goals', 'professional advice',
            'career transition', 'next step in career', 'career development advice',
            'career strategy', 'career mentor', 'career coach', 'risks of switching',
            'should i change', 'transition while working', 'prepare for transition',
            'at my age', 'career switch', 'changing fields', 'new career'
        ]
        if any(keyword in user_input_lower for keyword in counseling_keywords):
            return self._handle_career_counseling(user_input, conversation_history)
        
        # Check for career guidance intent (course/training focused)
        career_keywords = ['course recommendation', 'training', 'skill development', 'what should i study', 'courses', 'learn', 'certification']
        if any(keyword in user_input_lower for keyword in career_keywords):
            return self._handle_career_guidance(user_input)
        
        # Help and general queries
        if any(word in user_input_lower for word in ['help', 'menu', 'options', 'what can you do']):
            return self._show_help_menu()
        
        # Context-aware follow-up handling
        if self.current_applicant_data:
            # Check for counseling-related follow-ups first (more specific)
            if any(phrase in user_input_lower for phrase in [
                'advice', 'counseling', 'what should', 'confused', 'stuck', 'risks', 
                'transition', 'switch', 'change', 'prepare', 'at my age', 'how can i'
            ]):
                return self._handle_career_counseling_for_applicant(user_input, conversation_history)
            elif any(phrase in user_input_lower for phrase in ['job', 'work', 'employment', 'opportunities']):
                return self._handle_job_search_for_applicant()
            elif any(phrase in user_input_lower for phrase in ['course', 'training', 'study', 'learn', 'certification']):
                return self._handle_career_guidance_for_applicant()
        
        # Default response
        return self._generate_contextual_response(user_input)
    
    def _handle_application_query(self, app_id: str) -> str:
        """Handle application status queries."""
        result = self.db_tool.query_application(app_id)
        
        if "No application found" in result:
            return f"""
❌ {result}

💡 **Please check:**
• Make sure the application ID is correct (format: APP-YYYY-XXXXXX)
• Try these sample IDs:
  - APP-2025-000001 (Ahmed Al Mansouri)
  - APP-2025-000004 (Aisha Al Maktoum - Approved)

{self._show_help_menu()}
"""
        
        # Store applicant data for context
        try:
            skills_data = self.db_tool.extract_skills(app_id)
            self.current_applicant_data = json.loads(skills_data)
        except:
            self.current_applicant_data = None
        
        # Check for document processing status
        processing_status = self._check_document_processing_status(app_id)
        if processing_status:
            result += "\n\n" + processing_status
        
        return result + self._add_follow_up_options()
    
    def _check_document_processing_status(self, app_id: str) -> str:
        """Check document processing status for an application."""
        try:
            import json
            from pathlib import Path
            
            # Look for processing status file
            status_file = Path(f"./workflow_outputs/application_status_{app_id}.json")
            
            if status_file.exists():
                with open(status_file, 'r') as f:
                    status_data = json.load(f)
                
                processing_status = status_data.get('processing_status', 'unknown')
                final_decision = status_data.get('final_decision', 'pending')
                overall_score = status_data.get('overall_score', 0)
                processing_duration = status_data.get('processing_duration', 'N/A')
                documents_processed = status_data.get('documents_processed', 0)
                
                # Get judgment summary if available
                judgment = status_data.get('judgment_summary', {})
                confidence_level = judgment.get('confidence_level', 'medium')
                risk_level = judgment.get('risk_level', 'medium')
                support_types = judgment.get('recommended_support_types', [])
                support_amount = judgment.get('estimated_support_amount', 'To be determined')
                
                status_emoji = {
                    'completed': '✅',
                    'processing': '🔄',
                    'failed': '❌',
                    'pending': '⏳'
                }.get(processing_status, '📋')
                
                decision_emoji = {
                    'approved': '✅',
                    'conditionally_approved': '⚠️',
                    'pending_review': '🔍',
                    'rejected': '❌'
                }.get(final_decision, '📋')
                
                result = f"""
📊 **DOCUMENT PROCESSING STATUS**
{status_emoji} **Processing Status:** {processing_status.title()}
{decision_emoji} **Final Decision:** {final_decision.replace('_', ' ').title()}
📈 **Overall Score:** {overall_score:.2f}/1.0
⏱️ **Processing Duration:** {processing_duration}
📄 **Documents Processed:** {documents_processed}
🎯 **Confidence Level:** {confidence_level.title()}
⚠️ **Risk Level:** {risk_level.title()}
"""
                
                if support_types:
                    result += f"\n💰 **Recommended Support:** {', '.join(support_types)}"
                    result += f"\n💵 **Estimated Amount:** {support_amount}"
                
                # Add key findings if available
                key_findings = judgment.get('key_findings', [])
                if key_findings:
                    result += f"\n\n🔍 **Key Findings:**"
                    for finding in key_findings[:3]:  # Show top 3 findings
                        result += f"\n• {finding}"
                
                # Add next steps if available
                next_steps = judgment.get('next_steps', [])
                if next_steps:
                    result += f"\n\n📋 **Next Steps:**"
                    for step in next_steps[:3]:  # Show top 3 steps
                        result += f"\n• {step}"
                
                return result
            
            else:
                # Check if there are any workflow outputs for this application
                workflow_dir = Path("./workflow_outputs")
                if workflow_dir.exists():
                    app_workflows = list(workflow_dir.glob(f"*{app_id}*"))
                    if app_workflows:
                        return f"""
📊 **DOCUMENT PROCESSING STATUS**
🔄 **Status:** Processing completed - results available
📁 **Workflow Directory:** {app_workflows[0].name}
💡 **Note:** Detailed processing results have been generated
"""
                
                return f"""
📊 **DOCUMENT PROCESSING STATUS**
⏳ **Status:** No document processing found for this application
💡 **Note:** Documents may not have been uploaded or processed yet
"""
        
        except Exception as e:
            return f"""
📊 **DOCUMENT PROCESSING STATUS**
❌ **Error:** Could not retrieve processing status
💡 **Details:** {str(e)}
"""
    
    def _handle_job_search(self, user_input: str) -> str:
        """Handle job search requests."""
        skills = self._extract_skills_from_input(user_input)
        
        if not skills and self.current_applicant_data:
            skills = self.current_applicant_data.get('current_job', 'general')
        elif not skills:
            skills = "general"
        
        return self.job_tool._run(skills, "UAE", "")
    
    def _handle_career_guidance(self, user_input: str) -> str:
        """Handle career guidance requests."""
        current_skills = self._extract_skills_from_input(user_input)
        
        if not current_skills and self.current_applicant_data:
            current_skills = f"{self.current_applicant_data.get('current_job', '')} with {self.current_applicant_data.get('education', '')} education"
        elif not current_skills:
            current_skills = "general background"
        
        return self.course_tool._run(current_skills, "", "")
    
    def _handle_job_search_for_applicant(self) -> str:
        """Handle job search for current applicant."""
        if not self.current_applicant_data:
            return "Please provide your application ID first so I can understand your background."
        
        skills = self.current_applicant_data.get('current_job', 'general')
        experience_level = "senior" if self.current_applicant_data.get('experience_years', 0) > 5 else "mid"
        
        return self.job_tool._run(skills, "UAE", experience_level)
    
    def _handle_career_guidance_for_applicant(self) -> str:
        """Handle career guidance for current applicant."""
        if not self.current_applicant_data:
            return "Please provide your application ID first so I can understand your background."
        
        current_skills = f"{self.current_applicant_data.get('current_job', '')} with {self.current_applicant_data.get('education', '')} education"
        
        return self.course_tool._run(current_skills, "", self.current_applicant_data.get('education', ''))
    
    def _handle_career_counseling(self, user_input: str, conversation_history: list = None) -> str:
        """Handle career counseling requests using AI counselor."""
        return self.counseling_tool.provide_counseling(
            user_query=user_input,
            applicant_context=self.current_applicant_data,
            conversation_history=conversation_history
        )
    
    def _handle_career_counseling_for_applicant(self, user_input: str, conversation_history: list = None) -> str:
        """Handle career counseling for current applicant."""
        if not self.current_applicant_data:
            return "Please provide your application ID first so I can understand your background for personalized counseling."
        
        return self.counseling_tool.provide_counseling(
            user_query=user_input,
            applicant_context=self.current_applicant_data,
            conversation_history=conversation_history
        )
    
    def _extract_skills_from_input(self, user_input: str) -> str:
        """Extract skills or job titles from user input."""
        keywords = ['engineer', 'manager', 'consultant', 'supervisor', 'developer', 'analyst', 'coordinator', 'data scientist', 'software engineer']
        
        for keyword in keywords:
            if keyword in user_input.lower():
                return keyword
        
        return ""
    
    def _add_follow_up_options(self) -> str:
        """Add follow-up options after showing application details."""
        return """

🎯 **WHAT WOULD YOU LIKE TO DO NEXT?**

a) 🔍 **Job Search**: Find job opportunities based on your experience
b) 📚 **Career Guidance**: Get course recommendations and training advice
c) 🧠 **Career Counseling**: Get personalized career advice and planning
d) ❓ **Other Questions**: Ask me anything else about your application

Just tell me what you'd like to do! 😊
"""
    
    def _show_help_menu(self) -> str:
        """Show the help menu with available options."""
        return """
🤖 **HOW CAN I HELP YOU?**

📋 **APPLICATION QUERIES:**
• Check your application status and details
• View approval information and amounts
• See your complete profile information

Just provide your Application ID (e.g., "APP-2025-000001")

🔍 **JOB SEARCH ASSISTANCE:**
• Find job opportunities based on your skills
• Get salary ranges and company information
• Receive application tips and advice

💡 **CAREER GUIDANCE:**
• Get course recommendations for skill development
• Find training programs and certifications
• Receive career advancement advice

🧠 **CAREER COUNSELING:**
• Get personalized career advice from AI counselor
• Discuss career transitions and planning
• Receive strategic career development guidance

🎯 **SAMPLE APPLICATION IDs:**
• APP-2025-000001 (Ahmed - Family Support)
• APP-2025-000004 (Aisha - Approved ✅)
"""
    
    def _generate_contextual_response(self, user_input: str) -> str:
        """Generate contextual response for general queries."""
        if self.current_applicant_data:
            name = self.current_applicant_data.get('name', 'there')
            return f"Hello {name}! I understand you're asking about: '{user_input}'. How can I specifically help you with your application, job search, or career development?"
        else:
            return f"""
🤔 I understand you're asking about: "{user_input}"

{self._show_help_menu()}

💡 **Try these examples:**
• "APP-2025-000001" - Check application status
• "Help me find jobs" - Job search assistance
• "I need career guidance" - Course recommendations
"""


class LangChainChatbot:
    """LangChain-enhanced chatbot for Social Security Application System."""
    
    def __init__(self):
        """Initialize the LangChain chatbot with intelligent routing."""
        self.router = IntelligentRouter()
        self.conversation_history = []
        
        # Create LangChain tools for structured access
        self.tools = self._create_langchain_tools()
    
    def _create_langchain_tools(self) -> List[Tool]:
        """Create LangChain tools for structured access."""
        return [
            Tool(
                name="Application_Query",
                description="Query application status and details using application ID (format: APP-YYYY-XXXXXX)",
                func=self.router._handle_application_query
            ),
            Tool(
                name="Job_Search", 
                description="Search for job opportunities based on skills and location",
                func=self.router._handle_job_search
            ),
            Tool(
                name="Career_Guidance",
                description="Provide career guidance and course recommendations for skill development",
                func=self.router._handle_career_guidance
            ),
            Tool(
                name="Career_Counseling",
                description="Provide personalized career counseling and advice using AI counselor for career planning, transitions, and strategic guidance",
                func=self._handle_career_counseling_with_history
            )
        ]
    
    def _create_tools(self) -> List[Tool]:
        """Create LangChain tools for the agent."""
        return [
            Tool(
                name="Application_Query",
                description="Use this tool when user provides an application ID (format: APP-YYYY-XXXXXX) or asks about their application status. Input should be the application ID.",
                func=self._handle_application_query
            ),
            Tool(
                name="Job_Search",
                description="Use this tool when user asks about finding jobs, employment opportunities, or work. Input should be the job title or skills to search for.",
                func=self._handle_job_search
            ),
            Tool(
                name="Career_Guidance",
                description="Use this tool when user asks for career advice, course recommendations, training, or skill development. Input should be their current background or skills.",
                func=self._handle_career_guidance
            )
        ]
    
    def _handle_application_query(self, app_id: str) -> str:
        """Handle application queries through LangChain tool."""
        # Extract application ID if not in correct format
        app_id_match = re.search(r'APP-\d{4}-\d{6}', app_id, re.IGNORECASE)
        uuid_match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', app_id, re.IGNORECASE)
        
        if app_id_match:
            app_id = app_id_match.group().upper()
        elif uuid_match:
            app_id = uuid_match.group().lower()
        
        result = self.router.db_tool.query_application(app_id)
        
        # Store applicant data for context
        try:
            skills_data = self.router.db_tool.extract_skills(app_id)
            self.router.current_applicant_data = json.loads(skills_data)
        except:
            self.router.current_applicant_data = None
        
        return result
    
    def _handle_job_search(self, skills: str) -> str:
        """Handle job search through LangChain tool."""
        # Use current applicant data if available
        if not skills and self.router.current_applicant_data:
            skills = self.router.current_applicant_data.get('current_job', 'general')
        elif not skills:
            skills = "general"
        
        return self.router.job_tool._run(skills, "UAE", "")
    
    def _handle_career_guidance(self, background: str) -> str:
        """Handle career guidance through LangChain tool."""
        # Use current applicant data if available
        if not background and self.router.current_applicant_data:
            background = f"{self.router.current_applicant_data.get('current_job', '')} with {self.router.current_applicant_data.get('education', '')} education"
        elif not background:
            background = "general background"
        
        return self.router.course_tool._run(background, "", "")
    
    def _handle_career_counseling_with_history(self, user_query: str) -> str:
        """Handle career counseling with conversation history."""
        return self.router._handle_career_counseling(user_query, self.conversation_history)
    
    def chat(self, user_input: str) -> str:
        """Process user input using intelligent routing."""
        user_input = user_input.strip()
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        try:
            # Use intelligent router to process the input
            response = self.router.route_query(user_input, self.conversation_history)
            
            # Add to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
            
        except Exception as e:
            error_response = f"I apologize, but I encountered an error: {str(e)}\n\n" + self.router._show_help_menu()
            self.conversation_history.append({"role": "assistant", "content": error_response})
            return error_response
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history."""
        return self.conversation_history
    
    def reset_conversation(self):
        """Reset the conversation history and applicant data."""
        self.conversation_history = []
        self.router.current_applicant_data = None
    
    def get_available_tools(self) -> List[str]:
        """Get list of available LangChain tools."""
        return [tool.name for tool in self.tools]
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """Get descriptions of available tools."""
        return {tool.name: tool.description for tool in self.tools}


# Backward compatibility - alias for the enhanced chatbot
SimpleChatbot = LangChainChatbot


class SimpleChatInterface:
    """Simple command-line interface for the chatbot."""
    
    def __init__(self):
        """Initialize the chat interface."""
        self.chatbot = LangChainChatbot()
    
    def start_chat_session(self):
        """Start an interactive chat session."""
        self._print_banner()
        
        print("🤖 Welcome! I'm your Social Security Application Assistant.")
        print("Type 'help' to see what I can do, or 'quit' to exit.")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                    print("\n🤖 Thank you for using the Social Security Chatbot! Have a great day! 👋")
                    break
                
                if user_input.lower() == 'clear':
                    self.chatbot.reset_conversation()
                    print("\n🤖 Conversation cleared! How can I help you?")
                    continue
                
                # Get response from chatbot
                print("\n🤖 Assistant:")
                print("-" * 50)
                response = self.chatbot.chat(user_input)
                print(response)
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\n\n🤖 Goodbye! 👋")
                break
            except Exception as e:
                print(f"\n🤖 I encountered an error: {str(e)}")
                print("Please try again or type 'help' for assistance.")
    
    def single_query(self, query: str) -> str:
        """Process a single query and return the response."""
        return self.chatbot.chat(query)
    
    def _print_banner(self):
        """Print the application banner."""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🇦🇪 UAE SOCIAL SECURITY APPLICATION CHATBOT 🤖            ║
║                                                              ║
║    Your AI Assistant for Application Queries,               ║
║    Job Search, and Career Guidance                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(banner)


def main():
    """Main function for testing."""
    interface = SimpleChatInterface()
    interface.start_chat_session()


if __name__ == "__main__":
    main()