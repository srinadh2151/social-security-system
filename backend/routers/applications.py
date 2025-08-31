"""
Applications Router

FastAPI router for handling Social Security application operations.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import uuid

from backend.models import (
    ApplicationCreate, ApplicationResponse, ApplicationUpdate,
    ApplicationFilter, ApplicationListResponse, ApplicationStats,
    BaseResponse, ErrorResponse
)
from backend.database_manager import BackendDatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def get_database_manager(request: Request) -> BackendDatabaseManager:
    """Dependency to get database manager from app state."""
    if not hasattr(request.app.state, 'database_manager') or request.app.state.database_manager is None:
        raise HTTPException(status_code=503, detail="Database not available")
    db_manager = request.app.state.database_manager
    if not db_manager.connected:
        raise HTTPException(status_code=503, detail="Database not connected")
    return db_manager

@router.post("/", response_model=Dict[str, Any])
async def create_application(
    application: ApplicationCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db_manager: BackendDatabaseManager = Depends(get_database_manager)
):
    """
    Create a new Social Security application.
    
    This endpoint accepts application data from the Streamlit frontend
    and stores it in the database.
    """
    try:
        logger.info(f"Creating new application for {application.personal_info.first_name} {application.personal_info.last_name}")
        
        # Create application in database
        application_id = await db_manager.create_application(application)
        
        # Add background task for processing
        background_tasks.add_task(process_application, application_id, db_manager)
        
        logger.info(f"Application created successfully: {application_id}")
        
        return {
            "success": True,
            "message": "Application submitted successfully",
            "application_id": application_id,
            "status": "submitted",
            "created_at": datetime.now().isoformat(),
            "next_steps": [
                "Upload required documents",
                "Wait for initial review",
                "Check status using application ID"
            ]
        }
        
    except Exception as e:
        logger.error(f"Application creation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create application: {str(e)}"
        )

@router.get("/{application_id}", response_model=Dict[str, Any])
async def get_application(
    application_id: str,
    request: Request,
    db_manager: BackendDatabaseManager = Depends(get_database_manager)
):
    """
    Get application details by ID.
    
    Returns complete application information including personal details,
    family members, financial information, and document status.
    """
    try:
        logger.info(f"Retrieving application: {application_id}")
        
        application_data = await db_manager.get_application(application_id)
        
        if not application_data:
            raise HTTPException(
                status_code=404,
                detail=f"Application {application_id} not found"
            )
        
        # Get associated documents
        documents = await db_manager.get_application_documents(application_id)
        application_data["documents"] = documents
        
        logger.info(f"Application retrieved successfully: {application_id}")
        return {
            "success": True,
            "application": application_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve application {application_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve application: {str(e)}"
        )

@router.put("/{application_id}", response_model=BaseResponse)
async def update_application(
    application_id: str,
    application_update: ApplicationUpdate,
    request: Request,
    db_manager: BackendDatabaseManager = Depends(get_database_manager)
):
    """
    Update an existing application.
    
    Allows partial updates to application data.
    """
    try:
        logger.info(f"Updating application: {application_id}")
        
        # Check if application exists
        existing_app = await db_manager.get_application(application_id)
        if not existing_app:
            raise HTTPException(
                status_code=404,
                detail=f"Application {application_id} not found"
            )
        
        # Update status if provided
        if application_update.status:
            await db_manager.update_application_status(
                application_id, 
                application_update.status.value
            )
        
        logger.info(f"Application updated successfully: {application_id}")
        return BaseResponse(message=f"Application {application_id} updated successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update application {application_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update application: {str(e)}"
        )

@router.get("/", response_model=ApplicationListResponse)
async def list_applications(
    status: Optional[str] = Query(None, description="Filter by application status"),
    search_term: Optional[str] = Query(None, description="Search by name or Emirates ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    request: Request = None,
    db_manager: BackendDatabaseManager = Depends(get_database_manager)
):
    """
    List applications with optional filtering and pagination.
    
    Supports filtering by status and searching by name or Emirates ID.
    """
    try:
        logger.info(f"Listing applications - page: {page}, size: {page_size}")
        
        filters = {
            "status": status,
            "search_term": search_term,
            "page": page,
            "page_size": page_size
        }
        
        applications = await db_manager.list_applications(filters)
        
        # Get total count for pagination
        total_filters = {k: v for k, v in filters.items() if k not in ["page", "page_size"] and v is not None}
        total_applications = await db_manager.list_applications(total_filters)
        total = len(total_applications)
        
        total_pages = (total + page_size - 1) // page_size
        
        logger.info(f"Retrieved {len(applications)} applications")
        
        return ApplicationListResponse(
            applications=applications,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Failed to list applications: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list applications: {str(e)}"
        )

@router.get("/stats/overview", response_model=ApplicationStats)
async def get_application_statistics(
    request: Request,
    db_manager: BackendDatabaseManager = Depends(get_database_manager)
):
    """
    Get application statistics and overview.
    
    Returns counts by status, recent submissions, and other metrics.
    """
    try:
        logger.info("Retrieving application statistics")
        
        stats = await db_manager.get_application_stats()
        
        logger.info("Statistics retrieved successfully")
        return ApplicationStats(**stats)
        
    except Exception as e:
        logger.error(f"Failed to retrieve statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )

@router.delete("/{application_id}", response_model=BaseResponse)
async def delete_application(
    application_id: str,
    request: Request,
    db_manager: BackendDatabaseManager = Depends(get_database_manager)
):
    """
    Delete an application (soft delete by updating status).
    
    Note: This is typically used for draft applications only.
    """
    try:
        logger.info(f"Deleting application: {application_id}")
        
        # Check if application exists
        existing_app = await db_manager.get_application(application_id)
        if not existing_app:
            raise HTTPException(
                status_code=404,
                detail=f"Application {application_id} not found"
            )
        
        # Soft delete by updating status
        await db_manager.update_application_status(application_id, "deleted")
        
        logger.info(f"Application deleted successfully: {application_id}")
        return BaseResponse(message=f"Application {application_id} deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete application {application_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete application: {str(e)}"
        )

async def process_application(application_id: str, db_manager: BackendDatabaseManager):
    """
    Background task to process application.
    
    This can include validation, document verification, etc.
    """
    try:
        logger.info(f"Processing application: {application_id}")
        
        # Simulate processing time
        import asyncio
        await asyncio.sleep(2)
        
        # Update status to under review
        await db_manager.update_application_status(application_id, "under_review")
        
        logger.info(f"Application processing completed: {application_id}")
        
    except Exception as e:
        logger.error(f"Application processing failed for {application_id}: {str(e)}")
        # Update status to indicate processing error
        try:
            await db_manager.update_application_status(application_id, "processing_error")
        except:
            pass