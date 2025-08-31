from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Query, Form, Body, Response
# from werkzeug.datastructures import FileStorage
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import Depends, Request
import datetime
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import hashlib
import logging
from typing import List, Dict, Any, Union, Optional, Dict, Any
import urllib
import io
# from azure.storage.blob import BlobServiceClient
import json
from pydantic import BaseModel
import mimetypes
import requests
# from app import utils
# from email_sender.workflow import Workflow
import ast

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

router = APIRouter()
# wf = Workflow()

class DocumentInfo(BaseModel):
    """Document information model."""
    document_id: str
    filename: str
    document_type: str
    size: int
    content_type: str
    upload_date: str
    processing_status: str
    validation_score: Optional[float] = None
    issues: List[str] = []

def get_database_manager(request: Request):
    """Dependency to get database manager from app state."""
    if not hasattr(request.app.state, 'database_manager'):
        raise HTTPException(status_code=503, detail="Database not available")
    return request.app.state.database_manager

@router.get("/user-authorization/", tags=["User Access"])
def check_authorization(user_mail:str):
    try:
        return JSONResponse(content={"user": { "Access": False, 
                                                  "message":"User not found"}}, status_code=404)

    except Exception as e:
        logger.error(f"Error checking authorization for user {user_mail}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", response_model=List[DocumentInfo])
async def upload_documents(
    files: List[UploadFile] = File(...),
    application_id: Optional[str] = None,
    request: Request = None,
    db_manager = Depends(get_database_manager)
):
    """Upload documents for processing."""
    logger.info(f"Uploading {len(files)} documents")
    
    try:
        uploaded_documents = []
        
        for file in files:
            # Validate file
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise HTTPException(
                    status_code=400, 
                    detail=f"File {file.filename} exceeds 10MB size limit"
                )
            
            # Check file type
            allowed_types = [
                'application/pdf',
                'image/jpeg',
                'image/png',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'application/vnd.ms-excel',
                'text/plain'
            ]
            
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type {file.content_type} not supported"
                )
            
            # Generate document ID
            document_id = str(uuid.uuid4())
            
            # Read file content
            content = await file.read()
            
            # Determine document type
            doc_type = _determine_document_type(file.filename, file.content_type)
            
            # Store document
            document_info = {
                "document_id": document_id,
                "filename": file.filename,
                "content": content,
                "document_type": doc_type,
                "size": file.size,
                "content_type": file.content_type,
                "application_id": application_id
            }
            
            await db_manager.store_document(document_id, document_info)
            
            uploaded_documents.append(DocumentInfo(
                document_id=document_id,
                filename=file.filename,
                document_type=doc_type,
                size=file.size,
                content_type=file.content_type,
                upload_date= datetime.now(),  #"2024-01-01T00:00:00Z",
                processing_status="uploaded"
            ))
        
        return uploaded_documents
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Document upload failed")
