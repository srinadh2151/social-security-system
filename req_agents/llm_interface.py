"""
LangChain-based LLM Interface for AI Agents

This module provides a unified interface to LLM models using LangChain framework.
Supports both Ollama (llama3.2) and OpenAI (GPT-4/4o) models.
"""

import logging
import os
import asyncio
from typing import Dict, Any, List, Optional, Union, AsyncGenerator
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# LangChain imports
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama

# For structured output
# from langchain_core.pydantic_v1 import BaseModel, Field
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

logger = logging.getLogger(__name__)

class LangChainLLMInterface:
    """LangChain-based interface for LLM models."""
    
    def __init__(
        self,
        default_model: str = "gpt-4o",
        openai_api_key: Optional[str] = None,
        openai_base_url: Optional[str] = None,
        ollama_base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        max_tokens: int = 2048
    ):
        """Initialize LangChain LLM interface."""
        self.default_model = default_model
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.openai_base_url = openai_base_url or os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.ollama_base_url = ollama_base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Model configurations
        self.model_configs = {
            # OpenAI Models
            "gpt-4": {
                "provider": "openai",
                "model_name": "gpt-4",
                "context_length": 8192,
                "supports_streaming": True,
                "supports_functions": True
            },
            "gpt-4o": {
                "provider": "openai", 
                "model_name": "gpt-4o",
                "context_length": 128000,
                "supports_streaming": True,
                "supports_functions": True
            },
            "gpt-4-turbo": {
                "provider": "openai",
                "model_name": "gpt-4-turbo",
                "context_length": 128000,
                "supports_streaming": True,
                "supports_functions": True
            },
            # Ollama Models
            "llama3.2": {
                "provider": "ollama",
                "model_name": "llama3.2",
                "context_length": 8192,
                "supports_streaming": True,
                "supports_functions": False
            },
            "llama3.2:3b": {
                "provider": "ollama",
                "model_name": "llama3.2:3b", 
                "context_length": 8192,
                "supports_streaming": True,
                "supports_functions": False
            },
            "llama3.2:1b": {
                "provider": "ollama",
                "model_name": "llama3.2:1b",
                "context_length": 8192,
                "supports_streaming": True,
                "supports_functions": False
            }
        }
        
        # Cache for initialized models
        self._model_cache = {}
        
        # Initialize default model
        self._initialize_default_model()
    
    def _initialize_default_model(self):
        """Initialize the default model."""
        try:
            self.get_model(self.default_model)
            logger.info(f"Default model '{self.default_model}' initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize default model '{self.default_model}': {str(e)}")
    
    def get_model(self, model_name: Optional[str] = None) -> Union[ChatOpenAI, ChatOllama]:
        """Get or create a model instance."""
        model_name = model_name or self.default_model
        
        # Check cache first
        if model_name in self._model_cache:
            return self._model_cache[model_name]
        
        # Get model config
        config = self.model_configs.get(model_name)
        if not config:
            raise ValueError(f"Unknown model: {model_name}")
        
        # Create model instance based on provider
        if config["provider"] == "openai":
            if not self.openai_api_key:
                raise ValueError("OpenAI API key not provided")
            
            model = ChatOpenAI(
                model=config["model_name"],
                openai_api_key=self.openai_api_key,
                openai_api_base=self.openai_base_url,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                streaming=True
            )
            
        elif config["provider"] == "ollama":
            model = ChatOllama(
                model=config["model_name"],
                base_url=self.ollama_base_url,
                temperature=self.temperature,
                num_predict=self.max_tokens
            )
            
        else:
            raise ValueError(f"Unknown provider: {config['provider']}")
        
        # Cache the model
        self._model_cache[model_name] = model
        return model
    
    async def generate_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """Generate response from LLM."""
        try:
            # Get model instance
            llm = self.get_model(model)
            
            # Override parameters if provided
            if temperature is not None:
                llm.temperature = temperature
            if max_tokens is not None and hasattr(llm, 'max_tokens'):
                llm.max_tokens = max_tokens
            
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))
            
            # Generate response
            if stream:
                response_chunks = []
                async for chunk in llm.astream(messages):
                    if hasattr(chunk, 'content'):
                        response_chunks.append(chunk.content)
                return "".join(response_chunks)
            else:
                response = await llm.ainvoke(messages)
                return response.content
                
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            return f"I apologize, but I'm unable to process your request at the moment due to a technical issue: {str(e)}"
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """Complete a chat conversation."""
        try:
            # Get model instance
            llm = self.get_model(model)
            
            # Override parameters if provided
            if temperature is not None:
                llm.temperature = temperature
            if max_tokens is not None and hasattr(llm, 'max_tokens'):
                llm.max_tokens = max_tokens
            
            # Convert messages to LangChain format
            langchain_messages = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if role == "system":
                    langchain_messages.append(SystemMessage(content=content))
                elif role == "user":
                    langchain_messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    langchain_messages.append(AIMessage(content=content))
            
            # Generate response
            if stream:
                response_chunks = []
                async for chunk in llm.astream(langchain_messages):
                    if hasattr(chunk, 'content'):
                        response_chunks.append(chunk.content)
                return "".join(response_chunks)
            else:
                response = await llm.ainvoke(langchain_messages)
                return response.content
                
        except Exception as e:
            logger.error(f"Chat completion failed: {str(e)}")
            return f"I apologize, but I'm unable to process your request at the moment: {str(e)}"
    
    async def generate_structured_response(
        self,
        prompt: str,
        schema: Dict[str, Any],
        model: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate structured response following a JSON schema."""
        try:
            # Create a Pydantic model from schema (simplified)
            class ResponseModel(BaseModel):
                response: Dict[str, Any] = Field(description="Structured response")
            
            # Create parser
            parser = JsonOutputParser()
            
            # Create prompt template
            format_instructions = parser.get_format_instructions()
            
            structured_prompt = f"""
{system_prompt or "You are a helpful assistant."}

Please respond with a valid JSON object that follows this schema:
{schema}

User request: {prompt}

{format_instructions}
"""
            
            # Generate response
            response = await self.generate_response(
                structured_prompt,
                model=model,
                temperature=0.3  # Lower temperature for structured output
            )
            
            # Parse response
            try:
                return parser.parse(response)
            except Exception as parse_error:
                logger.warning(f"Failed to parse structured response: {parse_error}")
                # Try to extract JSON manually
                import json
                import re
                
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except json.JSONDecodeError:
                        pass
                
                # Fallback
                return {"error": "Could not parse structured response", "raw_response": response}
                
        except Exception as e:
            logger.error(f"Structured response generation failed: {str(e)}")
            return {"error": str(e)}
    
    async def create_chain(
        self,
        prompt_template: str,
        model: Optional[str] = None,
        output_parser: Optional[Any] = None
    ):
        """Create a LangChain chain for reusable workflows."""
        try:
            # Get model
            llm = self.get_model(model)
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_template(prompt_template)
            
            # Create chain
            if output_parser:
                chain = prompt | llm | output_parser
            else:
                chain = prompt | llm | StrOutputParser()
            
            return chain
            
        except Exception as e:
            logger.error(f"Chain creation failed: {str(e)}")
            raise
    
    async def batch_generate(
        self,
        prompts: List[str],
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> List[str]:
        """Generate responses for multiple prompts in batch."""
        try:
            # Get model
            llm = self.get_model(model)
            
            # Override parameters if provided
            if temperature is not None:
                llm.temperature = temperature
            
            # Prepare all message sets
            message_sets = []
            for prompt in prompts:
                messages = []
                if system_prompt:
                    messages.append(SystemMessage(content=system_prompt))
                messages.append(HumanMessage(content=prompt))
                message_sets.append(messages)
            
            # Batch generate
            responses = await llm.abatch(message_sets)
            return [response.content for response in responses]
            
        except Exception as e:
            logger.error(f"Batch generation failed: {str(e)}")
            return [f"Error: {str(e)}" for _ in prompts]
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return list(self.model_configs.keys())
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a model."""
        config = self.model_configs.get(model_name, {})
        return {
            "model": model_name,
            "provider": config.get("provider", "unknown"),
            "context_length": config.get("context_length", 0),
            "supports_streaming": config.get("supports_streaming", False),
            "supports_functions": config.get("supports_functions", False),
            "available": model_name in self._model_cache or self._check_model_availability(model_name)
        }
    
    def _check_model_availability(self, model_name: str) -> bool:
        """Check if a model is available."""
        try:
            self.get_model(model_name)
            return True
        except Exception:
            return False
    
    async def stream_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Stream response from LLM."""
        try:
            # Get model
            llm = self.get_model(model)
            
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))
            
            # Stream response
            async for chunk in llm.astream(messages):
                if hasattr(chunk, 'content') and chunk.content:
                    yield chunk.content
                    
        except Exception as e:
            logger.error(f"Streaming failed: {str(e)}")
            yield f"Error: {str(e)}"
    
    def set_default_model(self, model_name: str):
        """Set the default model."""
        if model_name not in self.model_configs:
            raise ValueError(f"Unknown model: {model_name}")
        
        self.default_model = model_name
        logger.info(f"Default model set to: {model_name}")
    
    def clear_cache(self):
        """Clear the model cache."""
        self._model_cache.clear()
        logger.info("Model cache cleared")


# Convenience functions for common use cases
async def quick_generate(
    prompt: str,
    model: str = "gpt-4o",
    system_prompt: Optional[str] = None
) -> str:
    """Quick generation function."""
    interface = LangChainLLMInterface(default_model=model)
    return await interface.generate_response(prompt, system_prompt=system_prompt)


async def quick_chat(
    messages: List[Dict[str, str]],
    model: str = "gpt-4"
) -> str:
    """Quick chat completion function."""
    interface = LangChainLLMInterface(default_model=model)
    return await interface.chat_completion(messages)


# Test implementation
if __name__ == "__main__":
    import asyncio
    
    async def test_langchain_interface():
        """Test the LangChain LLM interface."""
        print("🧪 Testing LangChain LLM Interface...")
        
        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️  OPENAI_API_KEY not found. Testing with Ollama...")
            interface = LangChainLLMInterface(default_model="llama3.2")
        else:
            print("✅ Found OpenAI API key. Testing with GPT-4o...")
            interface = LangChainLLMInterface(default_model="gpt-4o")
        
        # Test 1: Simple generation
        print("\n1️⃣ Testing simple generation...")
        try:
            response = await interface.generate_response(
                # "What is 2 + 2? Explain your reasoning.",
                # "What is the weather in Abu Dhabi now? Give me more details",
                "I have 100 thousand dollars and I need to make sure it is invested in a firm that gives me 15% return per annum. \
                If invest in this company for 4 years what is the return on investment by end of 4th year? Give me details as well.",
                # system_prompt="You are a helpful weather agent who googles and gives me answer."
                # system_prompt="You are a math tutor."
                system_prompt="You are an analyst that can actually look at investment opportuinites and calculates how much is the overall return on investment."
            )
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 2: Chat completion
        print("\n2️⃣ Testing chat completion...")
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! How are you?"},
                {"role": "assistant", "content": "I'm doing well, thank you!"},
                {"role": "user", "content": "Can you help me with Python?"}
            ]
            response = await interface.chat_completion(messages)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 3: Structured response
        print("\n3️⃣ Testing structured response...")
        try:
            schema = {
                "type": "object",
                "properties": {
                    "answer": {"type": "number"},
                    "explanation": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                }
            }
            response = await interface.generate_structured_response(
                "What is 15 * 7?",
                schema
            )
            print(f"Structured response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 4: Model info
        print("\n4️⃣ Available models:")
        for model in interface.get_available_models():
            info = interface.get_model_info(model)
            print(f"  {model}: {info['provider']} - Context: {info['context_length']}")
        
        print("\n✅ Testing completed!")
    
    # Run test
    asyncio.run(test_langchain_interface())