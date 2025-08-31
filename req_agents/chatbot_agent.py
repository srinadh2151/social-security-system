"""
Social Security Application Chatbot Agent

This module implements the main chatbot agent that handles user queries about applications,
provides job search assistance, and offers career guidance.
"""

import os
from typing import Dict, Any, List, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain.agents.react.base import DocstoreExplorer
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage
import json

from .database_tools import ApplicationQueryTool, ApplicantSkillsExtractorTool
from .search_tools import JobSearchTool, CourseRecommendationTool


class SocialSecurityChatbot:
    """Main chatbot agent for Social Security Application System."""
    
    def __init__(self, use_openai: bool = False, model_name: str = "llama3.1"):
        """Initialize the chatbot with LLM and tools."""
        self.use_openai = use_openai
        self.model_name = model_name
        
        # Initialize LLM
        self.llm = self._initialize_llm()
        
        # Initialize tools
        self.tools = self._initialize_tools()
        
        # Initialize memory
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=10  # Keep last 10 exchanges
        )
        
        # Create agent
        self.agent = self._create_agent()
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
    
    def _initialize_llm(self):
        """Initialize the language model."""
        if self.use_openai:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI")
            return ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.1,
                api_key=api_key
            )
        else:
            # Use Ollama for local LLM
            return Ollama(
                model=self.model_name,
                temperature=0.1
            )
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize all available tools."""
        
        # Database tools
        app_query_tool = ApplicationQueryTool()
        skills_extractor_tool = ApplicantSkillsExtractorTool()
        
        # Search tools
        job_search_tool = JobSearchTool()
        course_recommendation_tool = CourseRecommendationTool()
        
        # Convert to LangChain Tools
        tools = [
            Tool(
                name=app_query_tool.name,
                description=app_query_tool.description,
                func=app_query_tool._run
            ),
            Tool(
                name=skills_extractor_tool.name,
                description=skills_extractor_tool.description,
                func=skills_extractor_tool._run
            ),
            Tool(
                name=job_search_tool.name,
                description=job_search_tool.description,
                func=lambda query: job_search_tool._run(query, "UAE", "")
            ),
            Tool(
                name=course_recommendation_tool.name,
                description=course_recommendation_tool.description,
                func=lambda skills: course_recommendation_tool._run(skills, "", "")
            )
        ]
        
        return tools
    
    def _create_agent(self):
        """Create the ReAct agent with custom prompt."""
        
        prompt_template = """
You are a helpful assistant for the UAE Social Security Application System. You help applicants:

1. Query their application status and get detailed information
2. Find job opportunities based on their skills and experience  
3. Get career guidance and course recommendations

Available tools:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

IMPORTANT GUIDELINES:
- Always be polite, helpful, and professional
- When showing application information, format it clearly and highlight important details
- If an application is approved, congratulate the user and clearly show the approved amount
- After showing application details, ALWAYS offer additional help options:
  a) Job search assistance based on their experience
  b) Career guidance and course recommendations
- For job searches, use the applicant's actual skills and experience from their application
- Provide practical, actionable advice
- Use emojis to make responses more friendly and readable
- If you can't find an application, suggest they check their application number

Begin!

Previous conversation history:
{chat_history}

Question: {input}
Thought: {agent_scratchpad}
"""
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["input", "chat_history", "agent_scratchpad"],
            partial_variables={
                "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools]),
                "tool_names": ", ".join([tool.name for tool in self.tools])
            }
        )
        
        return create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
    
    def chat(self, user_input: str) -> str:
        """Process user input and return response."""
        try:
            # Check if user is asking for help or menu
            if any(word in user_input.lower() for word in ['help', 'menu', 'options', 'what can you do']):
                return self._show_help_menu()
            
            # Process the input through the agent
            response = self.agent_executor.invoke({"input": user_input})
            
            # Extract the final answer
            final_answer = response.get("output", "I'm sorry, I couldn't process your request.")
            
            # Add follow-up options if this was an application query
            if any(word in user_input.lower() for word in ['application', 'app-', 'status']):
                final_answer += self._add_follow_up_options()
            
            return final_answer
            
        except Exception as e:
            error_msg = f"I apologize, but I encountered an error: {str(e)}"
            error_msg += "\n\n" + self._show_help_menu()
            return error_msg
    
    def _show_help_menu(self) -> str:
        """Show the help menu with available options."""
        return """
🤖 SOCIAL SECURITY CHATBOT - HOW CAN I HELP YOU?
{'='*55}

I can assist you with the following:

📋 APPLICATION QUERIES:
• Check your application status
• Get detailed application information
• View approval details and amounts
• See your personal and financial information

Just provide your Application ID (e.g., "APP-2025-000001") or ask:
• "What's the status of my application APP-2025-000001?"
• "Show me details for application APP-2025-000002"

🔍 JOB SEARCH ASSISTANCE:
• Find job opportunities based on your skills
• Get recommendations for positions matching your experience
• Discover career opportunities in the UAE

💡 CAREER GUIDANCE:
• Get course recommendations for skill development
• Find training programs and certifications
• Receive career advancement advice

📞 SAMPLE QUERIES:
• "Show me my application status for APP-2025-000001"
• "Help me find jobs based on my experience"
• "What courses should I take to improve my career?"
• "I need career guidance"

Just type your question or application ID to get started! 🚀
"""
    
    def _add_follow_up_options(self) -> str:
        """Add follow-up options after showing application details."""
        return """

🎯 WHAT WOULD YOU LIKE TO DO NEXT?

a) 🔍 **Job Search**: Find job opportunities based on your experience and skills
   Just say: "Help me find jobs" or "Search for jobs based on my experience"

b) 📚 **Career Guidance**: Get course recommendations and career development advice
   Just say: "I need career guidance" or "Recommend courses for me"

c) ❓ **Other Questions**: Ask me anything else about your application or need help

Type your choice or ask me anything else! 😊
"""
    
    def reset_conversation(self):
        """Reset the conversation memory."""
        self.memory.clear()
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """Get the current conversation history."""
        return self.memory.chat_memory.messages


class ChatbotInterface:
    """Simple interface for interacting with the chatbot."""
    
    def __init__(self, use_openai: bool = False, model_name: str = "llama3.1"):
        """Initialize the chatbot interface."""
        self.chatbot = SocialSecurityChatbot(use_openai=use_openai, model_name=model_name)
        self.session_active = True
    
    def start_chat_session(self):
        """Start an interactive chat session."""
        print("🤖 Social Security Application Chatbot")
        print("=" * 50)
        print("Welcome! I'm here to help you with your social security application.")
        print("Type 'help' to see what I can do, or 'quit' to exit.")
        print("=" * 50)
        
        while self.session_active:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                    print("\n🤖 Chatbot: Thank you for using the Social Security Chatbot! Have a great day! 👋")
                    break
                
                if user_input.lower() == 'clear':
                    self.chatbot.reset_conversation()
                    print("\n🤖 Chatbot: Conversation history cleared! How can I help you?")
                    continue
                
                # Get response from chatbot
                print("\n🤖 Chatbot: ", end="")
                response = self.chatbot.chat(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n🤖 Chatbot: Goodbye! 👋")
                break
            except Exception as e:
                print(f"\n🤖 Chatbot: I encountered an error: {str(e)}")
                print("Please try again or type 'help' for assistance.")
    
    def single_query(self, query: str) -> str:
        """Process a single query and return the response."""
        return self.chatbot.chat(query)


# Example usage and testing functions
def test_chatbot():
    """Test the chatbot with sample queries."""
    
    print("🧪 Testing Social Security Chatbot")
    print("=" * 40)
    
    # Initialize chatbot
    chatbot = ChatbotInterface(use_openai=False, model_name="llama3.1")
    
    # Test queries
    test_queries = [
        "help",
        "Show me details for application APP-2025-000001",
        "What's the status of my application APP-2025-000002?",
        "Help me find jobs based on my experience",
        "I need career guidance"
    ]
    
    for query in test_queries:
        print(f"\n👤 Test Query: {query}")
        print("🤖 Response:")
        response = chatbot.single_query(query)
        print(response)
        print("-" * 50)


if __name__ == "__main__":
    # You can run this for testing
    # test_chatbot()
    
    # Or start interactive session
    interface = ChatbotInterface(use_openai=False, model_name="llama3.1")
    interface.start_chat_session()