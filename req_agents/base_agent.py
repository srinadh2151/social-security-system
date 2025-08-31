"""
Base Agent for LangChain-based AI Agents

This module provides the base agent class using LangChain LLM interface.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from abc import ABC, abstractmethod

try:
    from req_agents.llm_interface import LangChainLLMInterface
except ImportError:
    from llm_interface import LangChainLLMInterface

logger = logging.getLogger(__name__)


class LangChainBaseAgent(ABC):
    """Base class for all LangChain-based AI agents."""
    
    def __init__(
        self,
        name: str,
        llm_interface: Optional[LangChainLLMInterface] = None,
        model: str = "gpt-4",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ):
        """Initialize base agent."""
        self.name = name
        self.llm = llm_interface or LangChainLLMInterface(
            default_model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Agent state
        self.conversation_history = []
        self.tools = {}
        self.memory = {}
        
        # Agent metadata
        self.agent_id = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.created_at = datetime.now()
        self.execution_count = 0
        
        logger.info(f"Initialized {self.__class__.__name__}: {self.name}")
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main task."""
        pass
    
    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None
    ) -> str:
        """Generate response using LLM."""
        try:
            response = await self.llm.generate_response(
                prompt=prompt,
                model=model or self.model,
                system_prompt=system_prompt or self.system_prompt,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            self.execution_count += 1
            return response
            
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            raise
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Complete a chat conversation."""
        try:
            response = await self.llm.chat_completion(
                messages=messages,
                model=model or self.model,
                temperature=temperature or self.temperature
            )
            
            self.execution_count += 1
            return response
            
        except Exception as e:
            logger.error(f"Chat completion failed: {str(e)}")
            raise
    
    async def generate_structured_response(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate structured response following a schema."""
        try:
            response = await self.llm.generate_structured_response(
                prompt=prompt,
                schema=schema,
                model=model or self.model,
                system_prompt=system_prompt or self.system_prompt
            )
            
            self.execution_count += 1
            return response
            
        except Exception as e:
            logger.error(f"Structured response generation failed: {str(e)}")
            raise
    
    async def think(self, context: str, question: str) -> str:
        """Generate thoughts about a given context and question."""
        thinking_prompt = f"""
Context: {context}

Question: {question}

Please think through this step by step and provide your reasoning.
"""
        
        return await self.generate_response(thinking_prompt)
    
    async def reason(self, observations: List[str], goal: str) -> str:
        """Reason about observations to achieve a goal."""
        reasoning_prompt = f"""
Goal: {goal}

Observations:
{chr(10).join(f"- {obs}" for obs in observations)}

Based on these observations, what should be the next action to achieve the goal?
Provide your reasoning and recommended action.
"""
        
        return await self.generate_response(reasoning_prompt)
    
    async def reflect(self, action: str, result: str, goal: str) -> str:
        """Reflect on an action and its result."""
        reflection_prompt = f"""
Goal: {goal}
Action taken: {action}
Result: {result}

Please reflect on this action and result:
1. Was the action effective in moving toward the goal?
2. What could be improved?
3. What should be the next step?

Provide your reflection and recommendations.
"""
        
        return await self.generate_response(reflection_prompt)
    
    def add_tool(self, name: str, tool_func: Callable, description: str):
        """Add a tool that the agent can use."""
        self.tools[name] = {
            "function": tool_func,
            "description": description
        }
        logger.info(f"Added tool '{name}' to agent {self.name}")
    
    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """Use a tool."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not available")
        
        tool = self.tools[tool_name]
        try:
            if asyncio.iscoroutinefunction(tool["function"]):
                return await tool["function"](**kwargs)
            else:
                return tool["function"](**kwargs)
        except Exception as e:
            logger.error(f"Tool '{tool_name}' execution failed: {str(e)}")
            raise
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return list(self.tools.keys())
    
    def get_tool_description(self, tool_name: str) -> str:
        """Get description of a tool."""
        if tool_name in self.tools:
            return self.tools[tool_name]["description"]
        return "Tool not found"
    
    def update_memory(self, key: str, value: Any):
        """Update agent memory."""
        self.memory[key] = {
            "value": value,
            "timestamp": datetime.now(),
            "access_count": self.memory.get(key, {}).get("access_count", 0) + 1
        }
    
    def get_memory(self, key: str) -> Any:
        """Get value from agent memory."""
        if key in self.memory:
            self.memory[key]["access_count"] += 1
            return self.memory[key]["value"]
        return None
    
    def add_to_conversation(self, role: str, content: str):
        """Add message to conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        })
        
        # Keep only last 20 messages to manage memory
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def get_conversation_context(self, last_n: int = 5) -> str:
        """Get recent conversation context."""
        recent_messages = self.conversation_history[-last_n:] if self.conversation_history else []
        
        context_parts = []
        for msg in recent_messages:
            context_parts.append(f"{msg['role']}: {msg['content']}")
        
        return "\n".join(context_parts)
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get agent status information."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "model": self.model,
            "created_at": self.created_at.isoformat(),
            "execution_count": self.execution_count,
            "available_tools": list(self.tools.keys()),
            "memory_keys": list(self.memory.keys()),
            "conversation_length": len(self.conversation_history),
            "llm_model": self.llm.default_model
        }
    
    def reset_conversation(self):
        """Reset conversation history."""
        self.conversation_history = []
        logger.info(f"Conversation history reset for agent {self.name}")
    
    def reset_memory(self):
        """Reset agent memory."""
        self.memory = {}
        logger.info(f"Memory reset for agent {self.name}")
    
    def export_state(self) -> Dict[str, Any]:
        """Export agent state for persistence."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "model": self.model,
            "system_prompt": self.system_prompt,
            "conversation_history": [
                {
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp": msg["timestamp"].isoformat()
                }
                for msg in self.conversation_history
            ],
            "memory": {
                k: {
                    "value": v["value"],
                    "timestamp": v["timestamp"].isoformat(),
                    "access_count": v["access_count"]
                }
                for k, v in self.memory.items()
            },
            "execution_count": self.execution_count,
            "created_at": self.created_at.isoformat(),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
    
    def import_state(self, state: Dict[str, Any]):
        """Import agent state from persistence."""
        self.agent_id = state.get("agent_id", self.agent_id)
        self.name = state.get("name", self.name)
        self.model = state.get("model", self.model)
        self.system_prompt = state.get("system_prompt", self.system_prompt)
        self.execution_count = state.get("execution_count", 0)
        self.temperature = state.get("temperature", self.temperature)
        self.max_tokens = state.get("max_tokens", self.max_tokens)
        
        # Import conversation history
        self.conversation_history = []
        for msg in state.get("conversation_history", []):
            self.conversation_history.append({
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": datetime.fromisoformat(msg["timestamp"])
            })
        
        # Import memory
        self.memory = {}
        for k, v in state.get("memory", {}).items():
            self.memory[k] = {
                "value": v["value"],
                "timestamp": datetime.fromisoformat(v["timestamp"]),
                "access_count": v["access_count"]
            }
        
        # Import timestamps
        created_at_str = state.get("created_at")
        if created_at_str:
            self.created_at = datetime.fromisoformat(created_at_str)
        
        logger.info(f"State imported for agent {self.name}")


# Test implementation
if __name__ == "__main__":
    import asyncio
    
    class TestAgent(LangChainBaseAgent):
        """Simple test implementation of LangChainBaseAgent."""
        
        async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
            """Test execution method."""
            task_description = task.get("description", "")
            
            response = await self.generate_response(
                f"Please help with this task: {task_description}",
                system_prompt="You are a helpful assistant."
            )
            
            return {
                "status": "completed",
                "response": response,
                "task": task,
                "agent": self.name
            }
    
    async def test_base_agent():
        """Test the base agent."""
        print("🧪 Testing LangChain Base Agent...")
        
        # Create test agent
        agent = TestAgent(
            name="test_agent",
            model="gpt-4",
            system_prompt="You are a helpful test assistant."
        )
        
        # Test basic functionality
        print(f"Agent created: {agent.name}")
        print(f"Agent ID: {agent.agent_id}")
        print(f"Model: {agent.model}")
        
        # Test task execution
        task = {
            "description": "Explain what artificial intelligence is in simple terms",
            "context": "Educational explanation needed"
        }
        
        try:
            result = await agent.execute(task)
            print(f"\n✅ Task executed successfully!")
            print(f"Status: {result['status']}")
            print(f"Response: {result['response'][:200]}...")
            
            # Test agent status
            status = agent.get_agent_status()
            print(f"\n📊 Agent Status:")
            print(f"Executions: {status['execution_count']}")
            print(f"Tools: {status['available_tools']}")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
    
    # Run test
    asyncio.run(test_base_agent())