"""
Social Security Application Backend

FastAPI backend for handling application submissions, document uploads,
and integration with the database and AI chatbot services.
"""

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from backend.routers.applications import router as applications_router
from backend.routers.documents import router as documents_router
from backend.database_manager import BackendDatabaseManager
from backend.config import settings
from backend.models import ChatMessage, ChatResponse, BaseResponse

# Import LangChain chatbot from req_agents
try:
    from req_agents.simple_chatbot import LangChainChatbot
    CHATBOT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Chatbot not available: {e}")
    CHATBOT_AVAILABLE = False

# Import document processing service
try:
    from req_agents.document_processing_service import DocumentProcessingService
    DOCUMENT_PROCESSING_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Document processing service not available: {e}")
    DOCUMENT_PROCESSING_AVAILABLE = False

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime

# Models are imported from backend.models

# Initialize FastAPI app
app = FastAPI(
    title="Social Security Application Backend",
    description="Backend API for Social Security Application System with AI Chatbot",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],  # Streamlit default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("backend/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files for document access
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Database manager instance
database_manager = None

# Global chatbot sessions (in production, use proper session management)
chatbot_sessions = {}

# Document processing service instance
document_processing_service = None

def get_or_create_chatbot(conversation_id: str) -> 'LangChainChatbot':
    """Get existing chatbot session or create new one."""
    if not CHATBOT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Chatbot service is not available"
        )
    
    if conversation_id not in chatbot_sessions:
        chatbot_sessions[conversation_id] = LangChainChatbot()
    
    return chatbot_sessions[conversation_id]

@app.on_event("startup")
async def startup_event():
    """Initialize database connection and services on startup."""
    global database_manager, document_processing_service
    
    # Initialize database
    try:
        database_manager = BackendDatabaseManager()
        await database_manager.connect()
        app.state.database_manager = database_manager
        print("✅ Database connected successfully")
        print(f"   Connected: {database_manager.connected}")
        print(f"   Config: {database_manager.config.host}:{database_manager.config.port}/{database_manager.config.database}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        # Set a dummy database manager for development
        app.state.database_manager = None
    
    # Initialize document processing service
    if DOCUMENT_PROCESSING_AVAILABLE:
        try:
            document_processing_service = DocumentProcessingService(
                uploads_dir=str(UPLOAD_DIR),
                outputs_dir="./workflow_outputs"
            )
            app.state.document_processing_service = document_processing_service
            print("✅ Document processing service initialized")
        except Exception as e:
            print(f"❌ Document processing service initialization failed: {e}")
            app.state.document_processing_service = None
    else:
        app.state.document_processing_service = None

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    if database_manager:
        await database_manager.disconnect()
        print("✅ Database disconnected")

# Include routers
app.include_router(applications_router, prefix="/api/v1/applications", tags=["Applications"])
app.include_router(documents_router, prefix="/api/v1/documents", tags=["Documents"])

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Social Security Application Backend API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "applications": "/api/v1/applications",
            "documents": "/api/v1/documents", 
            "chatbot": "/api/v1/chatbot",
            "docs": "/docs"
        },
        "chatbot_framework": "LangChain"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_status = "connected" if database_manager else "disconnected"
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

# Chatbot endpoints using LangChain from req_agents
@app.post("/api/v1/chatbot/chat", response_model=ChatResponse)
async def chat_with_bot(message: ChatMessage, request: Request):
    """Chat with the AI assistant using LangChain framework."""
    try:
        # Generate conversation ID if not provided
        conversation_id = message.conversation_id or str(uuid.uuid4())
        
        # Get or create chatbot session
        chatbot = get_or_create_chatbot(conversation_id)
        
        # Process the message using LangChain
        response_text = chatbot.chat(message.message)
        
        # Determine which tool was used based on response content
        tool_used = None
        if "APPLICATION SUMMARY" in response_text:
            tool_used = "Application_Query"
        elif "JOB SEARCH RESULTS" in response_text:
            tool_used = "Job_Search"
        elif "COURSE RECOMMENDATIONS" in response_text:
            tool_used = "Career_Guidance"
        elif "CAREER COUNSELING SESSION" in response_text:
            tool_used = "Career_Counseling"
        
        # Get conversation history for context
        history = chatbot.get_conversation_history()
        context_data = {
            "conversation_length": len(history),
            "application_id": message.application_id,
            "has_applicant_context": bool(chatbot.router.current_applicant_data)
        }
        
        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            tool_used=tool_used,
            context_data=context_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )

@app.get("/api/v1/chatbot/conversation/{conversation_id}/history")
async def get_conversation_history(conversation_id: str):
    """Get conversation history for a specific conversation."""
    try:
        if conversation_id not in chatbot_sessions:
            return {
                "conversation_id": conversation_id,
                "history": [],
                "message": "No conversation found"
            }
        
        chatbot = chatbot_sessions[conversation_id]
        history = chatbot.get_conversation_history()
        
        return {
            "conversation_id": conversation_id,
            "history": history,
            "total_messages": len(history)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve conversation history: {str(e)}"
        )

@app.delete("/api/v1/chatbot/conversation/{conversation_id}", response_model=BaseResponse)
async def clear_conversation(conversation_id: str):
    """Clear conversation history for a specific conversation."""
    try:
        if conversation_id in chatbot_sessions:
            chatbot_sessions[conversation_id].reset_conversation()
            del chatbot_sessions[conversation_id]
        
        return BaseResponse(
            message=f"Conversation {conversation_id} cleared successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear conversation: {str(e)}"
        )

@app.get("/api/v1/chatbot/tools/available")
async def get_available_tools():
    """Get list of available LangChain chatbot tools."""
    try:
        if not CHATBOT_AVAILABLE:
            return {
                "available": False,
                "message": "Chatbot service is not available",
                "tools": []
            }
        
        # Create temporary chatbot to get tool info
        temp_chatbot = LangChainChatbot()
        tools = temp_chatbot.get_available_tools()
        descriptions = temp_chatbot.get_tool_descriptions()
        
        tool_info = []
        for tool_name in tools:
            tool_info.append({
                "name": tool_name,
                "description": descriptions.get(tool_name, "No description available")
            })
        
        return {
            "available": True,
            "tools": tool_info,
            "capabilities": [
                "Application status queries",
                "Job search with LinkedIn API",
                "Course recommendations with Udemy API", 
                "AI-powered career counseling",
                "Context-aware conversations"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get available tools: {str(e)}"
        )

class QuickQueryRequest(BaseModel):
    query: str
    application_id: Optional[str] = None

@app.post("/api/v1/chatbot/quick-query")
async def quick_query(request: QuickQueryRequest):
    """Quick query endpoint for simple LangChain chatbot interactions."""
    try:
        if not CHATBOT_AVAILABLE:
            return {
                "success": False,
                "message": "Chatbot service is not available",
                "response": "I'm sorry, but the AI assistant is currently unavailable. Please try again later."
            }
        
        # Create temporary chatbot session
        chatbot = LangChainChatbot()
        
        # Process the query using LangChain
        response = chatbot.chat(request.query)
        
        return {
            "success": True,
            "query": request.query,
            "response": response,
            "application_id": request.application_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "query": request.query,
            "response": f"I encountered an error processing your request: {str(e)}",
            "error": str(e)
        }

@app.get("/api/v1/chatbot/status")
async def get_chatbot_status():
    """Get LangChain chatbot service status."""
    try:
        status_info = {
            "service_available": CHATBOT_AVAILABLE,
            "active_conversations": len(chatbot_sessions),
            "framework": "LangChain",
            "timestamp": datetime.now().isoformat()
        }
        
        if CHATBOT_AVAILABLE:
            # Test chatbot functionality
            try:
                temp_chatbot = LangChainChatbot()
                tools = temp_chatbot.get_available_tools()
                status_info.update({
                    "tools_available": len(tools),
                    "tools": tools,
                    "openai_configured": hasattr(temp_chatbot.router.counseling_tool, 'available') and temp_chatbot.router.counseling_tool.available
                })
            except Exception as e:
                status_info["initialization_error"] = str(e)
        
        return status_info
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get chatbot status: {str(e)}"
        )

# Document Processing Endpoints

class ProcessDocumentsRequest(BaseModel):
    applicant_info: Optional[Dict[str, Any]] = None
    workflow_id: Optional[str] = None

class ProcessSpecificDocumentsRequest(BaseModel):
    document_paths: List[str]
    applicant_info: Optional[Dict[str, Any]] = None
    workflow_id: Optional[str] = None

@app.post("/api/v1/documents/process-uploads")
async def process_uploaded_documents(
    request: ProcessDocumentsRequest,
    background_tasks: BackgroundTasks
):
    """Process all documents in the uploads directory and generate assessment."""
    try:
        if not DOCUMENT_PROCESSING_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Document processing service is not available"
            )
        
        service = app.state.document_processing_service
        if not service:
            raise HTTPException(
                status_code=503,
                detail="Document processing service is not initialized"
            )
        
        # Process documents asynchronously
        result = await service.process_uploaded_documents(
            applicant_info=request.applicant_info,
            workflow_id=request.workflow_id
        )
        
        return {
            "success": True,
            "message": "Document processing completed",
            "workflow_id": result.get("workflow_id"),
            "status": result.get("status"),
            "processing_duration": result.get("duration"),
            "documents_processed": len(result.get("processed_documents", [])),
            "final_decision": result.get("assessment_result", {}).get("status"),
            "overall_score": result.get("assessment_result", {}).get("overall_score", 0),
            "judgment_summary": result.get("judgment_summary"),
            "errors": result.get("errors", []),
            "warnings": result.get("warnings", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(e)}"
        )

@app.post("/api/v1/documents/process-specific")
async def process_specific_documents(request: ProcessSpecificDocumentsRequest):
    """Process specific documents by their paths."""
    try:
        if not DOCUMENT_PROCESSING_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Document processing service is not available"
            )
        
        service = app.state.document_processing_service
        if not service:
            raise HTTPException(
                status_code=503,
                detail="Document processing service is not initialized"
            )
        
        # Validate document paths
        for doc_path in request.document_paths:
            if not os.path.exists(doc_path):
                raise HTTPException(
                    status_code=404,
                    detail=f"Document not found: {doc_path}"
                )
        
        # Process specific documents
        result = await service.process_specific_documents(
            document_paths=request.document_paths,
            applicant_info=request.applicant_info,
            workflow_id=request.workflow_id
        )
        
        return {
            "success": True,
            "message": "Specific document processing completed",
            "workflow_id": result.get("workflow_id"),
            "status": result.get("status"),
            "processing_duration": result.get("duration"),
            "documents_processed": len(result.get("processed_documents", [])),
            "final_decision": result.get("assessment_result", {}).get("status"),
            "overall_score": result.get("assessment_result", {}).get("overall_score", 0),
            "judgment_summary": result.get("judgment_summary"),
            "errors": result.get("errors", []),
            "warnings": result.get("warnings", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Specific document processing failed: {str(e)}"
        )

@app.get("/api/v1/documents/workflow/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """Get the status and results of a specific workflow."""
    try:
        if not DOCUMENT_PROCESSING_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Document processing service is not available"
            )
        
        service = app.state.document_processing_service
        if not service:
            raise HTTPException(
                status_code=503,
                detail="Document processing service is not initialized"
            )
        
        status = await service.get_processing_status(workflow_id)
        
        if "error" in status:
            raise HTTPException(
                status_code=404,
                detail=status["error"]
            )
        
        return {
            "success": True,
            "workflow_status": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get workflow status: {str(e)}"
        )

@app.get("/api/v1/documents/workflows")
async def list_all_workflows():
    """List all processed workflows."""
    try:
        if not DOCUMENT_PROCESSING_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Document processing service is not available"
            )
        
        service = app.state.document_processing_service
        if not service:
            raise HTTPException(
                status_code=503,
                detail="Document processing service is not initialized"
            )
        
        workflows = await service.list_all_workflows()
        
        return {
            "success": True,
            "total_workflows": len(workflows),
            "workflows": workflows
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list workflows: {str(e)}"
        )

@app.get("/api/v1/documents/processing-status")
async def get_document_processing_status():
    """Get document processing service status."""
    try:
        uploads_path = Path("./backend/uploads")
        outputs_path = Path("./workflow_outputs")
        
        # Count files in uploads directory
        uploaded_files = 0
        if uploads_path.exists():
            uploaded_files = len([f for f in uploads_path.iterdir() if f.is_file()])
        
        # Count processed workflows
        processed_workflows = 0
        if outputs_path.exists():
            processed_workflows = len([d for d in outputs_path.iterdir() if d.is_dir()])
        
        return {
            "service_available": DOCUMENT_PROCESSING_AVAILABLE,
            "service_initialized": app.state.document_processing_service is not None,
            "uploads_directory": str(uploads_path),
            "outputs_directory": str(outputs_path),
            "uploaded_files_count": uploaded_files,
            "processed_workflows_count": processed_workflows,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get processing status: {str(e)}"
        )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )