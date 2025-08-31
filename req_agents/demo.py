"""
Demo Script for Social Security Application Chatbot

This script demonstrates all the chatbot capabilities with sample interactions.
"""

from simple_chatbot import SimpleChatInterface
import time


def print_demo_header():
    """Print demo header."""
    print("🚀 SOCIAL SECURITY APPLICATION CHATBOT - DEMO")
    print("=" * 60)
    print("This demo shows all the chatbot capabilities:")
    print("1. Application Status Queries")
    print("2. Job Search Assistance")
    print("3. Career Guidance")
    print("=" * 60)


def demo_interaction(bot, query, description):
    """Demo a single interaction."""
    print(f"\n🎯 {description}")
    print(f"👤 User: {query}")
    print("\n🤖 Assistant:")
    print("-" * 50)
    
    response = bot.single_query(query)
    print(response)
    print("-" * 50)
    
    input("\nPress Enter to continue...")


def main():
    """Run the complete demo."""
    print_demo_header()
    
    # Initialize chatbot
    bot = SimpleChatInterface()
    
    # Demo 1: Application Query
    demo_interaction(
        bot,
        "APP-2025-000001",
        "DEMO 1: Application Status Query"
    )
    
    # Demo 2: Job Search after Application Query
    demo_interaction(
        bot,
        "Help me find jobs",
        "DEMO 2: Job Search Based on Applicant Profile"
    )
    
    # Demo 3: Career Guidance after Application Query
    demo_interaction(
        bot,
        "I need career guidance",
        "DEMO 3: Career Guidance Based on Applicant Background"
    )
    
    # Demo 4: Approved Application
    demo_interaction(
        bot,
        "APP-2025-000004",
        "DEMO 4: Approved Application with Amount"
    )
    
    # Demo 5: General Job Search
    demo_interaction(
        bot,
        "find jobs for manager",
        "DEMO 5: General Job Search"
    )
    
    # Demo 6: Help Menu
    demo_interaction(
        bot,
        "help",
        "DEMO 6: Help Menu and Available Options"
    )
    
    print("\n🎉 DEMO COMPLETED!")
    print("=" * 60)
    print("✅ All chatbot features demonstrated successfully!")
    print("\n🚀 To use the chatbot interactively:")
    print("   python req_agents/simple_chatbot.py")
    print("\n📊 Key Features Shown:")
    print("• ✅ Database queries with comprehensive application information")
    print("• ✅ Job search with personalized recommendations")
    print("• ✅ Career guidance with course suggestions")
    print("• ✅ Context-aware follow-up suggestions")
    print("• ✅ User-friendly formatting and emojis")
    print("• ✅ Error handling and help system")


if __name__ == "__main__":
    main()