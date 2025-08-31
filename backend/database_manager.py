"""
Database Manager for Backend

This module provides a bridge between the FastAPI backend and the database operations.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# Add database directory to path
sys.path.append(str(Path(__file__).parent.parent / "database"))

from database_operations import DatabaseManager as DBManager, DatabaseConfig, ApplicationRepository
from backend.config import settings

logger = logging.getLogger(__name__)


class BackendDatabaseManager:
    """Database manager for the backend API."""
    
    def __init__(self):
        """Initialize the database manager."""
        self.config = DatabaseConfig(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            username=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        self.db_manager = None
        self.repository = None
        self.connected = False
    
    async def connect(self):
        """Connect to the database."""
        try:
            # Test the connection first
            import psycopg2
            test_conn = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password
            )
            test_conn.close()
            
            # Initialize the database manager and repository
            self.db_manager = DBManager(self.config)
            self.repository = ApplicationRepository(self.db_manager)
            self.connected = True
            logger.info("✅ Database connection established")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            self.connected = False
            raise
    
    async def disconnect(self):
        """Disconnect from the database."""
        if self.db_manager:
            self.db_manager.close_all_connections()
            self.connected = False
            logger.info("✅ Database connection closed")
    
    def _convert_application_data(self, application_data) -> Dict[str, Any]:
        """Convert FastAPI application model to database format."""
        # Convert the Pydantic model to dictionary format expected by database
        personal_info = application_data.personal_info
        address_info = application_data.address_info
        employment_info = application_data.employment_info
        financial_info = application_data.financial_info
        education_info = application_data.education_info
        
        # Map education levels from frontend to database enum
        education_mapping = {
            "primary": "Primary",
            "secondary": "Secondary", 
            "diploma": "Diploma",
            "bachelor": "Bachelor's",
            "master": "Master's",
            "phd": "PhD"
        }
        
        # Build applicant data
        applicant_data = {
            "emirates_id": personal_info.emirates_id,
            "first_name": personal_info.first_name,
            "last_name": personal_info.last_name,
            "date_of_birth": personal_info.date_of_birth,
            "gender": personal_info.gender.value.capitalize(),  # Convert "male" -> "Male", "female" -> "Female"
            "nationality": personal_info.nationality,
            "phone_number": personal_info.phone_number,
            "email": personal_info.email,
            "education_level": education_mapping.get(education_info.highest_education.value, "Bachelor's"),
            "address": {
                "emirate": address_info.emirate,
                "city": address_info.city,
                "area": address_info.city,  # Use city as area since area not provided in frontend
                "po_box": address_info.postal_code if address_info.postal_code else None,
                "address_line": address_info.street_address
            },
            "employment": {
                "status": "Employed",  # Database enum value
                "employer_name": employment_info.employer_name or "",
                "job_title": employment_info.job_title or "",
                "monthly_income": float(employment_info.monthly_salary or 0),
                "years_of_experience": 0  # Not provided in frontend model
            }
        }
        
        # Build application data
        app_data = {
            "applicant": applicant_data,
            "application_type": "Regular Support",  # Database enum value
            "priority_level": "Normal",  # Database enum value
            "requested_amount": float(financial_info.monthly_expenses or 3000),
            "support_duration": "6 months",  # Database enum value
            "reason_for_application": "Financial assistance needed",  # Default reason
            "additional_notes": application_data.additional_notes or ""
        }
        
        # Add family members if any
        if application_data.family_members:
            app_data["family_members"] = []
            for member in application_data.family_members:
                # Calculate age from date_of_birth
                from datetime import datetime, date
                if isinstance(member.date_of_birth, str):
                    birth_date = datetime.fromisoformat(member.date_of_birth).date()
                else:
                    birth_date = member.date_of_birth
                today = date.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                
                # Map relationship to database enum format
                relationship_mapping = {
                    "spouse": "Spouse",
                    "child": "Child", 
                    "parent": "Parent",
                    "sibling": "Sibling",
                    "other": "Other"
                }
                
                app_data["family_members"].append({
                    "name": member.name,
                    "relationship": relationship_mapping.get(member.relationship.lower(), "Other"),
                    "age": age,
                    "emirates_id": member.emirates_id if member.emirates_id else None,  # Use None instead of empty string
                    "has_income": False,
                    "monthly_income": 0.0,
                    "is_dependent": member.is_dependent
                })
        
        # Add financial situation
        app_data["financial_situation"] = {
            "total_household_income": float(financial_info.monthly_income or 0),
            "monthly_expenses": float(financial_info.monthly_expenses or 0),
            "existing_debts": 0.0,
            "savings_amount": 0.0,
            "property_value": 0.0,
            "other_assets": 0.0
        }
        
        # Add banking info
        app_data["banking"] = {
            "bank_name": financial_info.bank_name or "",
            "account_number": financial_info.account_number or "",
            "iban": None,  # Use None instead of empty string for IBAN constraint
            "has_bank_loan": False
        }
        
        return app_data
    
    async def create_application(self, application_data) -> str:
        """Create a new application."""
        if not self.connected:
            raise Exception("Database not connected")
        
        try:
            # Convert application data to database format
            db_data = self._convert_application_data(application_data)
            
            # Create application using repository
            application_id = self.repository.create_application(db_data)
            
            return application_id
            
        except Exception as e:
            logger.error(f"Failed to create application: {str(e)}")
            raise
    
    async def get_application(self, application_id: str) -> Optional[Dict[str, Any]]:
        """Get application by ID."""
        if not self.connected:
            raise Exception("Database not connected")
        
        try:
            return self.repository.get_application_by_id(application_id)
        except Exception as e:
            logger.error(f"Failed to get application {application_id}: {str(e)}")
            raise
    
    async def update_application_status(self, application_id: str, status: str) -> bool:
        """Update application status."""
        if not self.connected:
            raise Exception("Database not connected")
        
        try:
            return self.repository.update_application_status(application_id, status)
        except Exception as e:
            logger.error(f"Failed to update application status {application_id}: {str(e)}")
            raise
    
    async def list_applications(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List applications with filters."""
        if not self.connected:
            raise Exception("Database not connected")
        
        try:
            if not filters:
                filters = {}
            
            # Convert filters to database format
            search_params = {}
            if filters.get("status"):
                search_params["status"] = filters["status"]
            if filters.get("search_term"):
                # For now, we'll search by Emirates ID if it looks like one
                search_term = filters["search_term"]
                if search_term.isdigit() and len(search_term) >= 10:
                    search_params["emirates_id"] = search_term
            
            return self.repository.search_applications(search_params)
            
        except Exception as e:
            logger.error(f"Failed to list applications: {str(e)}")
            raise
    
    async def get_application_documents(self, application_id: str) -> List[Dict[str, Any]]:
        """Get documents for an application."""
        if not self.connected:
            raise Exception("Database not connected")
        
        try:
            # Get application data which includes documents
            app_data = self.repository.get_application_by_id(application_id)
            if app_data and "documents" in app_data:
                return app_data["documents"]
            return []
        except Exception as e:
            logger.error(f"Failed to get application documents {application_id}: {str(e)}")
            raise
    
    async def store_document(self, document_id: str, document_info: Dict[str, Any]):
        """Store document information."""
        if not self.connected:
            raise Exception("Database not connected")
        
        try:
            return self.repository.add_document(
                document_info.get("application_id"),
                {
                    "document_type": document_info.get("document_type", "other"),
                    "document_purpose": document_info.get("document_type", "other"),
                    "file_name": document_info["filename"],
                    "file_path": f"backend/uploads/{document_id}_{document_info['filename']}",
                    "file_size": document_info["size"],
                    "mime_type": document_info["content_type"],
                    "processing_status": "uploaded",
                    "confidence_score": 1.0
                }
            )
        except Exception as e:
            logger.error(f"Failed to store document: {str(e)}")
            raise
    
    async def get_application_stats(self) -> Dict[str, Any]:
        """Get application statistics."""
        if not self.connected:
            raise Exception("Database not connected")
        
        try:
            # Get basic stats using search
            all_apps = self.repository.search_applications({})
            
            # Count by status
            status_counts = {}
            for app in all_apps:
                status = app.get("application_status", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count recent submissions (simplified)
            recent_count = len([app for app in all_apps if app.get("submitted_at")])
            
            return {
                "total_applications": len(all_apps),
                "by_status": status_counts,
                "recent_submissions": recent_count
            }
            
        except Exception as e:
            logger.error(f"Failed to get application stats: {str(e)}")
            raise