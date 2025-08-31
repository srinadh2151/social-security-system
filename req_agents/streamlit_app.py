"""
Streamlit Web Interface for Social Security Chatbot

This module provides a user-friendly web interface for the chatbot using Streamlit.
"""

import streamlit as st
import os
import sys
from datetime import datetime
import json

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from req_agents.chatbot_agent import SocialSecurityChatbot


def initialize_chatbot():
    """Initialize the chatbot with session state."""
    if 'chatbot' not in st.session_state:
        # Check if user wants to use OpenAI or local model
        use_openai = st.sidebar.checkbox("Use OpenAI GPT (requires API key)", value=False)
        
        if use_openai:
            openai_key = st.sidebar.text_input("OpenAI API Key", type="password")
            if openai_key:
                os.environ['OPENAI_API_KEY'] = openai_key
                st.session_state.chatbot = SocialSecurityChatbot(use_openai=True)
            else:
                st.warning("Please enter your OpenAI API key to use GPT models.")
                return None
        else:
            # Use local Ollama model
            model_name = st.sidebar.selectbox(
                "Select Local Model",
                ["llama3.1", "llama2", "mistral", "codellama"],
                index=0
            )
            try:
                st.session_state.chatbot = SocialSecurityChatbot(use_openai=False, model_name=model_name)
            except Exception as e:
                st.error(f"Error initializing local model: {str(e)}")
                st.info("Make sure Ollama is installed and the model is available. Run: `ollama pull llama3.1`")
                return None
    
    return st.session_state.chatbot


def initialize_session_state():
    """Initialize session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False


def display_welcome_message():
    """Display the welcome message and instructions."""
    st.markdown("""
    ## 🤖 Welcome to the Social Security Application Chatbot!
    
    I'm here to help you with:
    
    📋 **Application Queries**
    - Check your application status
    - Get detailed application information
    - View approval details and amounts
    
    🔍 **Job Search Assistance**
    - Find job opportunities based on your skills
    - Get recommendations for positions matching your experience
    
    💡 **Career Guidance**
    - Get course recommendations for skill development
    - Find training programs and certifications
    
    ### 🚀 Sample Application IDs to try:
    - `APP-2025-000001` (Ahmed Al Mansouri - Family Support)
    - `APP-2025-000002` (Fatima Al Zahra - Regular Support)
    - `APP-2025-000003` (Mohammed Al Rashid - Emergency Support)
    - `APP-2025-000004` (Aisha Al Maktoum - Regular Support - Approved)
    - `APP-2025-000005` (Omar Al Nahyan - Elderly Support - Approved)
    
    Just type your application ID or ask me anything! 😊
    """)


def display_chat_message(role: str, content: str):
    """Display a chat message with proper formatting."""
    with st.chat_message(role):
        if role == "assistant":
            # Format the assistant's response with better styling
            st.markdown(content)
        else:
            st.write(content)


def main():
    """Main Streamlit application."""
    
    # Page configuration
    st.set_page_config(
        page_title="Social Security Chatbot",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
    }
    .stTextInput > div > div > input {
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("<h1 class='main-header'>🇦🇪 UAE Social Security Application Chatbot</h1>", unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar configuration
    st.sidebar.title("⚙️ Configuration")
    
    # Initialize chatbot
    chatbot = initialize_chatbot()
    
    if not chatbot:
        st.stop()
    
    # Sidebar information
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 System Status")
    st.sidebar.success("✅ Chatbot Ready")
    st.sidebar.info(f"💬 Messages: {len(st.session_state.messages)}")
    
    # Clear conversation button
    if st.sidebar.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.conversation_started = False
        chatbot.reset_conversation()
        st.rerun()
    
    # Sample queries
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 Quick Actions")
    
    sample_queries = [
        "Show me help menu",
        "APP-2025-000001",
        "APP-2025-000004",
        "Help me find jobs",
        "I need career guidance"
    ]
    
    for query in sample_queries:
        if st.sidebar.button(f"📝 {query}", key=f"sample_{query}"):
            st.session_state.messages.append({"role": "user", "content": query})
            with st.spinner("Processing..."):
                response = chatbot.chat(query)
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Display welcome message if no conversation started
        if not st.session_state.conversation_started and not st.session_state.messages:
            display_welcome_message()
        
        # Display chat messages
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                display_chat_message(message["role"], message["content"])
        
        # Chat input
        if prompt := st.chat_input("Type your message here... (e.g., 'APP-2025-000001' or 'help')"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.conversation_started = True
            
            # Display user message
            display_chat_message("user", prompt)
            
            # Get bot response
            with st.spinner("🤖 Thinking..."):
                try:
                    response = chatbot.chat(prompt)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    display_chat_message("assistant", response)
                except Exception as e:
                    error_msg = f"I apologize, but I encountered an error: {str(e)}"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    display_chat_message("assistant", error_msg)
            
            st.rerun()
    
    with col2:
        # Statistics and information panel
        st.markdown("### 📈 Chat Statistics")
        
        if st.session_state.messages:
            user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
            bot_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
            
            st.metric("User Messages", user_messages)
            st.metric("Bot Responses", bot_messages)
            
            # Show last query time
            if st.session_state.messages:
                st.write("**Last Activity:**")
                st.write(datetime.now().strftime("%H:%M:%S"))
        
        st.markdown("---")
        
        # Quick help
        st.markdown("### 🆘 Quick Help")
        st.markdown("""
        **Application Query:**
        - Type your application ID
        - Example: `APP-2025-000001`
        
        **Job Search:**
        - "Help me find jobs"
        - "Search for jobs based on my experience"
        
        **Career Guidance:**
        - "I need career guidance"
        - "Recommend courses for me"
        
        **General:**
        - "help" - Show all options
        - "menu" - Display main menu
        """)
        
        # Export conversation
        if st.session_state.messages:
            st.markdown("---")
            if st.button("📥 Export Conversation"):
                conversation_data = {
                    "timestamp": datetime.now().isoformat(),
                    "messages": st.session_state.messages
                }
                st.download_button(
                    label="💾 Download Chat History",
                    data=json.dumps(conversation_data, indent=2),
                    file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )


if __name__ == "__main__":
    main()