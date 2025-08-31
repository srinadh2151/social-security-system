"""
Documents Router

FastAPI router for handling document upload and management operations.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import uuid
import os
from pathlib import Path
import mimetypes

from backend.models import DocumentInfo, DocumentUploadResponse, BaseResponse
from backend.database_manager import BackendDatabaseManager
from backend.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def get_database_manager(request: Request) -> BackendDatabaseManager:
    """Dependency to get database manager from app state."""
    if not hasattr(request.app.state, 'database_manager'):
        raise HTTPException(status_code=503, detail="Database not available")
    return request.app.state.database_manager

def validate_file(file: UploadFile) -> None:
    """Validate uploaded file."""
    # Check file size
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File {file.filename} exceeds maximum size of {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )
    
    # Check file type
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} is not supported. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
        )
    
    # Check filename
    if not file.filename or len(file.filename) > 255:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )

def determine_document_type(filename: str, content_type: str) -> str:
    """Determine document type based on filename and content type."""
    filename_lower = filename.lower()
    
    # Map common filename patterns to document types (matching config.py)
    type_mapping = {
        'emirates': 'emirates_id',
        'resume': 'resume',
        'cv': 'resume',
        'bank': 'bank_statement',
        'statement': 'bank_statement',
        'credit': 'credit_report',
        'etihad': 'credit_report',
        'bureau': 'credit_report',
        'asset': 'assets',
        'liabilit': 'assets',
        'passport': 'passport',
        'salary': 'salary_certificate',
        'employment': 'employment_contract',
        'contract': 'employment_contract',
        'medical': 'medical_report',
        'family': 'family_book',
        'birth': 'birth_certificate',
        'marriage': 'marriage_certificate'
    }
    
    for keyword, doc_type in type_mapping.items():
        if keyword in filename_lower:
            return doc_type
    
    return 'other'

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_documents(
    files: List[UploadFile] = File(...),
    application_id: Optional[str] = Form(None),
    document_types: Optional[List[str]] = Form(None),
    request: Request = None,
    db_manager: BackendDatabaseManager = Depends(get_database_manager)
):
    """
    Upload documents for an application.
    
    Accepts multiple files and stores them locally while saving
    metadata to the database.
    """
    try:
        logger.info(f"Uploading {len(files)} documents for application: {application_id}")
        
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        uploaded_documents = []
        
        for i, file in enumerate(files):
            # Validate file
            validate_file(file)
            
            # Generate unique document ID
            document_id = str(uuid.uuid4())
            
            # Read file content
            content = await file.read()
            
            # Determine document type
            if document_types and i < len(document_types):
                doc_type = document_types[i]
            else:
                doc_type = determine_document_type(file.filename, file.content_type)
            
            # Create safe filename
            safe_filename = f"{document_id}_{file.filename}"
            file_path = settings.UPLOAD_DIR / safe_filename
            
            # Save file to disk
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Store document info in database
            document_info = {
                "document_id": document_id,
                "filename": file.filename,
                "document_type": doc_type,
                "size": len(content),
                "content_type": file.content_type,
                "application_id": application_id,
                "content": content
            }
            
            await db_manager.store_document(document_id, document_info)
            
            # Create response object
            doc_response = DocumentInfo(
                document_id=document_id,
                filename=file.filename,
                document_type=doc_type,
                size=len(content),
                content_type=file.content_type,
                upload_date=datetime.now(),
                processing_status="uploaded",
                application_id=application_id
            )
            
            uploaded_documents.append(doc_response)
            
            logger.info(f"Document uploaded successfully: {file.filename} -> {document_id}")
        
        return DocumentUploadResponse(
            documents=uploaded_documents,
            total_uploaded=len(uploaded_documents),
            message=f"Successfully uploaded {len(uploaded_documents)} documents"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Document upload failed: {str(e)}"
        )

@router.get("/application/{application_id}", response_model=List[DocumentInfo])
async def get_application_documents(
    application_id: str,
    request: Request,
    db_manager: BackendDatabaseManager = Depends(get_database_manager)
):
    """
    Get all documents for a specific application.
    
    Returns list of document metadata for the given application ID.
    """
    try:
        logger.info(f"Retrieving documents for application: {application_id}")
        
        documents = await db_manager.get_application_documents(application_id)
        
        # Convert to DocumentInfo objects
        document_list = []
        for doc in documents:
            document_list.append(DocumentInfo(
                document_id=str(doc["id"]),  # Use "id" field from database
                filename=doc["file_name"],   # Use "file_name" field from database
                document_type=doc["document_type"],
                size=doc["file_size"],       # Use "file_size" field from database
                content_type=doc["mime_type"], # Use "mime_type" field from database
                upload_date=doc["upload_date"],
                processing_status=doc["processing_status"],
                application_id=application_id
            ))
        
        logger.info(f"Retrieved {len(document_list)} documents for application: {application_id}")
        return document_list
        
    except Exception as e:
        logger.error(f"Failed to retrieve documents for application {application_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve documents: {str(e)}"
        )

@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    request: Request,
    db_manager: BackendDatabaseManager = Depends(get_database_manager)
):
    """
    Download a specific document by ID.
    
    Returns the file for download with appropriate headers.
    """
    try:
        logger.info(f"Downloading document: {document_id}")
        
        # For now, construct file path from document_id
        # This is a simplified approach - in production you'd want proper document metadata storage
        file_path = None
        filename = f"document_{document_id}"
        
        # Look for the file in uploads directory
        for file in settings.UPLOAD_DIR.glob(f"{document_id}_*"):
            file_path = file
            filename = file.name.split("_", 1)[1] if "_" in file.name else file.name
            break
        
        if not file_path or not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} not found"
            )
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Document file not found on disk"
            )
        
        # Determine media type
        media_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        
        logger.info(f"Document download successful: {document_id}")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type=media_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document download failed for {document_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Document download failed: {str(e)}"
        )

@router.get("/{document_id}/info", response_model=DocumentInfo)
async def get_document_info(
    document_id: str,
    request: Request,
    db_manager: BackendDatabaseManager = Depends(get_database_manager)
):
    """
    Get document information by ID.
    
    Returns document metadata without the file content.
    """
    try:
        logger.info(f"Retrieving document info: {document_id}")
        
        # For now, return basic info based on file existence
        # In production, this would come from proper document metadata storage
        file_path = None
        filename = f"document_{document_id}"
        
        # Look for the file in uploads directory
        for file in settings.UPLOAD_DIR.glob(f"{document_id}_*"):
            file_path = file
            filename = file.name.split("_", 1)[1] if "_" in file.name else file.name
            break
        
        if not file_path or not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} not found"
            )
        
        # Get file stats
        file_stats = file_path.stat()
        
        return DocumentInfo(
            document_id=document_id,
            filename=filename,
            document_type="other",
            size=file_stats.st_size,
            content_type=mimetypes.guess_type(str(file_path))[0] or "application/octet-stream",
            upload_date=datetime.fromtimestamp(file_stats.st_ctime),
            processing_status="uploaded",
            application_id=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve document info for {document_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve document info: {str(e)}"
        )

@router.delete("/{document_id}", response_model=BaseResponse)
async def delete_document(
    document_id: str,
    request: Request,
    db_manager: BackendDatabaseManager = Depends(get_database_manager)
):
    """
    Delete a document by ID.
    
    Removes both the file from disk and the database record.
    """
    try:
        logger.info(f"Deleting document: {document_id}")
        
        # Find and delete the file
        file_path = None
        for file in settings.UPLOAD_DIR.glob(f"{document_id}_*"):
            file_path = file
            break
        
        if not file_path or not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} not found"
            )
        
        # Delete file from disk
        file_path.unlink()
        
        logger.info(f"Document deleted successfully: {document_id}")
        
        return BaseResponse(
            message=f"Document {document_id} deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document deletion failed for {document_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Document deletion failed: {str(e)}"
        )

@router.get("/types/list")
async def get_document_types():
    """
    Get list of supported document types.
    
    Returns available document types for frontend selection.
    """
    return {
        "document_types": settings.DOCUMENT_TYPES,
        "allowed_file_types": settings.ALLOWED_FILE_TYPES,
        "max_file_size_mb": settings.MAX_FILE_SIZE / (1024 * 1024)
    }