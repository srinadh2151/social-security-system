"""
Database Operations for Social Security Application System

This module provides database operations and utilities for the application system.
"""

import psycopg2
import psycopg2.extras
from psycopg2.pool import SimpleConnectionPool
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date
import uuid
from contextlib import contextmanager
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str = "localhost"
    port: int = 5432
    database: str = "social_security_system"
    username: str = "postgres"
    password: str = ""
    min_connections: int = 1
    max_connections: int = 20


class DatabaseManager:
    """Database manager for handling all database operations."""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize database manager."""
        self.config = config
        self.connection_pool = None
        self._initialize_connection_pool()
    
    def _initialize_connection_pool(self):
        """Initialize connection pool."""
        try:
            self.connection_pool = SimpleConnectionPool(
                self.config.min_connections,
                self.config.max_connections,
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {str(e)}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool."""
        connection = None
        try:
            connection = self.connection_pool.getconn()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database operation failed: {str(e)}")
            raise
        finally:
            if connection:
                self.connection_pool.putconn(connection)
    
    def close_all_connections(self):
        """Close all connections in the pool."""
        if self.connection_pool:
            self.connection_pool.closeall()


class ApplicationRepository:
    """Repository for application-related database operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize repository."""
        self.db_manager = db_manager
    
    def create_applicant(self, applicant_data: Dict[str, Any]) -> str:
        """Create a new applicant and return the ID."""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Insert applicant
                cursor.execute("""
                    INSERT INTO applicants (
                        emirates_id, first_name, last_name, date_of_birth, 
                        gender, nationality, phone_number, email, education_level
                    ) VALUES (
                        %(emirates_id)s, %(first_name)s, %(last_name)s, %(date_of_birth)s,
                        %(gender)s, %(nationality)s, %(phone_number)s, %(email)s, %(education_level)s
                    ) RETURNING id
                """, applicant_data)
                
                applicant_id = cursor.fetchone()['id']
                
                # Insert address
                if 'address' in applicant_data:
                    address_data = applicant_data['address'].copy()
                    address_data['applicant_id'] = applicant_id
                    
                    cursor.execute("""
                        INSERT INTO addresses (
                            applicant_id, emirate, city, area, po_box, address_line
                        ) VALUES (
                            %(applicant_id)s, %(emirate)s, %(city)s, %(area)s, %(po_box)s, %(address_line)s
                        )
                    """, address_data)
                
                # Insert employment info
                if 'employment' in applicant_data:
                    employment_data = applicant_data['employment'].copy()
                    employment_data['applicant_id'] = applicant_id
                    
                    cursor.execute("""
                        INSERT INTO employment_info (
                            applicant_id, employment_status, employer_name, job_title,
                            monthly_income, years_of_experience
                        ) VALUES (
                            %(applicant_id)s, %(status)s, %(employer_name)s, %(job_title)s,
                            %(monthly_income)s, %(years_of_experience)s
                        )
                    """, employment_data)
                
                conn.commit()
                return str(applicant_id)
    
    def create_application(self, application_data: Dict[str, Any]) -> str:
        """Create a new application and return the ID."""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Create applicant first
                applicant_id = self.create_applicant(application_data['applicant'])
                
                # Insert application
                cursor.execute("""
                    INSERT INTO applications (
                        applicant_id, application_type, priority_level, requested_amount,
                        support_duration, reason_for_application, additional_notes,
                        application_status, submitted_at
                    ) VALUES (
                        %(applicant_id)s, %(application_type)s, %(priority_level)s, %(requested_amount)s,
                        %(support_duration)s, %(reason_for_application)s, %(additional_notes)s,
                        'submitted', CURRENT_TIMESTAMP
                    ) RETURNING id, application_number
                """, {
                    'applicant_id': applicant_id,
                    **application_data
                })
                
                result = cursor.fetchone()
                application_id = result['id']
                application_number = result['application_number']
                
                # Insert family members
                if 'family_members' in application_data:
                    for member in application_data['family_members']:
                        member_data = member.copy()
                        member_data['applicant_id'] = applicant_id
                        
                        cursor.execute("""
                            INSERT INTO family_members (
                                applicant_id, name, relationship, age, emirates_id,
                                has_income, monthly_income, is_dependent
                            ) VALUES (
                                %(applicant_id)s, %(name)s, %(relationship)s, %(age)s, %(emirates_id)s,
                                %(has_income)s, %(monthly_income)s, %(is_dependent)s
                            )
                        """, member_data)
                
                # Insert financial info if provided
                if 'financial_situation' in application_data:
                    financial_data = application_data['financial_situation'].copy()
                    financial_data['application_id'] = application_id
                    
                    cursor.execute("""
                        INSERT INTO financial_info (
                            application_id, total_household_income, monthly_expenses,
                            existing_debts, savings_amount, property_value, other_assets
                        ) VALUES (
                            %(application_id)s, %(total_household_income)s, %(monthly_expenses)s,
                            %(existing_debts)s, %(savings_amount)s, %(property_value)s, %(other_assets)s
                        )
                    """, financial_data)
                
                # Insert banking info if provided
                if 'banking' in application_data:
                    banking_data = application_data['banking'].copy()
                    banking_data['application_id'] = application_id
                    
                    cursor.execute("""
                        INSERT INTO banking_info (
                            application_id, bank_name, account_number, iban, has_bank_loan
                        ) VALUES (
                            %(application_id)s, %(bank_name)s, %(account_number)s, %(iban)s, %(has_bank_loan)s
                        )
                    """, banking_data)
                
                # Insert emergency contact if provided
                if 'emergency_contact' in application_data:
                    emergency_data = application_data['emergency_contact'].copy()
                    emergency_data['application_id'] = application_id
                    
                    cursor.execute("""
                        INSERT INTO emergency_contacts (
                            application_id, name, relationship, phone, email
                        ) VALUES (
                            %(application_id)s, %(name)s, %(relationship)s, %(phone)s, %(email)s
                        )
                    """, emergency_data)
                
                # Insert status history
                cursor.execute("""
                    INSERT INTO application_status_history (
                        application_id, old_status, new_status, changed_by, change_reason
                    ) VALUES (
                        %(application_id)s, 'draft', 'submitted', 'applicant', 'Application submitted'
                    )
                """, {'application_id': application_id})
                
                conn.commit()
                return str(application_id)
    
    def get_application_by_id(self, application_id: str) -> Optional[Dict[str, Any]]:
        """Get application by ID with all related data."""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Get main application data
                cursor.execute("""
                    SELECT 
                        a.*,
                        ap.first_name, ap.last_name, ap.emirates_id, ap.phone_number, ap.email,
                        ap.date_of_birth, ap.gender, ap.nationality, ap.education_level,
                        addr.emirate, addr.city, addr.area, addr.po_box, addr.address_line,
                        emp.employment_status, emp.employer_name, emp.job_title, 
                        emp.monthly_income, emp.years_of_experience
                    FROM applications a
                    JOIN applicants ap ON a.applicant_id = ap.id
                    LEFT JOIN addresses addr ON ap.id = addr.applicant_id AND addr.is_current = TRUE
                    LEFT JOIN employment_info emp ON ap.id = emp.applicant_id AND emp.is_current = TRUE
                    WHERE a.id = %s
                """, (application_id,))
                
                application = cursor.fetchone()
                if not application:
                    return None
                
                # Get family members
                cursor.execute("""
                    SELECT * FROM family_members WHERE applicant_id = %s
                """, (application['applicant_id'],))
                family_members = cursor.fetchall()
                
                # Get financial info
                cursor.execute("""
                    SELECT * FROM financial_info WHERE application_id = %s
                """, (application_id,))
                financial_info = cursor.fetchone()
                
                # Get banking info
                cursor.execute("""
                    SELECT * FROM banking_info WHERE application_id = %s
                """, (application_id,))
                banking_info = cursor.fetchone()
                
                # Get emergency contact
                cursor.execute("""
                    SELECT * FROM emergency_contacts WHERE application_id = %s
                """, (application_id,))
                emergency_contact = cursor.fetchone()
                
                # Get documents
                cursor.execute("""
                    SELECT * FROM documents WHERE application_id = %s ORDER BY upload_date DESC
                """, (application_id,))
                documents = cursor.fetchall()
                
                # Get assessment results
                cursor.execute("""
                    SELECT * FROM assessment_results WHERE application_id = %s ORDER BY created_at DESC
                """, (application_id,))
                assessments = cursor.fetchall()
                
                # Combine all data
                result = dict(application)
                result['family_members'] = [dict(fm) for fm in family_members]
                result['financial_info'] = dict(financial_info) if financial_info else None
                result['banking_info'] = dict(banking_info) if banking_info else None
                result['emergency_contact'] = dict(emergency_contact) if emergency_contact else None
                result['documents'] = [dict(doc) for doc in documents]
                result['assessments'] = [dict(assessment) for assessment in assessments]
                
                return result
    
    def get_application_by_number(self, application_number: str) -> Optional[Dict[str, Any]]:
        """Get application by application number."""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id FROM applications WHERE application_number = %s
                """, (application_number,))
                
                result = cursor.fetchone()
                if result:
                    return self.get_application_by_id(str(result['id']))
                return None
    
    def update_application_status(self, application_id: str, new_status: str, 
                                changed_by: str = 'system', reason: str = '') -> bool:
        """Update application status."""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Get current status
                cursor.execute("""
                    SELECT application_status FROM applications WHERE id = %s
                """, (application_id,))
                
                current = cursor.fetchone()
                if not current:
                    return False
                
                old_status = current['application_status']
                
                # Update status
                cursor.execute("""
                    UPDATE applications 
                    SET application_status = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (new_status, application_id))
                
                # Insert status history
                cursor.execute("""
                    INSERT INTO application_status_history (
                        application_id, old_status, new_status, changed_by, change_reason
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (application_id, old_status, new_status, changed_by, reason))
                
                conn.commit()
                return True
    
    def add_document(self, application_id: str, document_data: Dict[str, Any]) -> str:
        """Add a document to an application."""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                document_data['application_id'] = application_id
                
                cursor.execute("""
                    INSERT INTO documents (
                        application_id, document_type, document_purpose, file_name,
                        file_path, file_size, mime_type, processing_status, confidence_score
                    ) VALUES (
                        %(application_id)s, %(document_type)s, %(document_purpose)s, %(file_name)s,
                        %(file_path)s, %(file_size)s, %(mime_type)s, %(processing_status)s, %(confidence_score)s
                    ) RETURNING id
                """, document_data)
                
                document_id = cursor.fetchone()['id']
                conn.commit()
                return str(document_id)
    
    def update_document_processing(self, document_id: str, processing_data: Dict[str, Any]) -> bool:
        """Update document processing results."""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE documents 
                    SET processing_status = %(processing_status)s,
                        processing_date = CURRENT_TIMESTAMP,
                        extracted_data = %(extracted_data)s,
                        confidence_score = %(confidence_score)s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %(document_id)s
                """, {**processing_data, 'document_id': document_id})
                
                conn.commit()
                return cursor.rowcount > 0
    
    def add_assessment_result(self, application_id: str, assessment_data: Dict[str, Any]) -> str:
        """Add assessment result."""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                assessment_data['application_id'] = application_id
                
                cursor.execute("""
                    INSERT INTO assessment_results (
                        application_id, assessment_type, assessment_score,
                        assessment_details, recommendations, risk_factors
                    ) VALUES (
                        %(application_id)s, %(assessment_type)s, %(assessment_score)s,
                        %(assessment_details)s, %(recommendations)s, %(risk_factors)s
                    ) RETURNING id
                """, assessment_data)
                
                assessment_id = cursor.fetchone()['id']
                conn.commit()
                return str(assessment_id)
    
    def update_ai_assessment(self, application_id: str, assessment_data: Dict[str, Any]) -> bool:
        """Update AI assessment results in application."""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE applications 
                    SET ai_assessment_score = %(score)s,
                        ai_assessment_status = %(status)s,
                        ai_assessment_date = CURRENT_TIMESTAMP,
                        human_review_required = %(human_review_required)s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %(application_id)s
                """, {**assessment_data, 'application_id': application_id})
                
                conn.commit()
                return cursor.rowcount > 0
    
    def get_applications_by_status(self, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get applications by status."""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM application_summary 
                    WHERE application_status = %s 
                    ORDER BY submitted_at DESC 
                    LIMIT %s
                """, (status, limit))
                
                return [dict(row) for row in cursor.fetchall()]
    
    def search_applications(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search applications with various filters."""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                where_clauses = []
                params = []
                
                if 'emirates_id' in search_params:
                    where_clauses.append("emirates_id = %s")
                    params.append(search_params['emirates_id'])
                
                if 'application_number' in search_params:
                    where_clauses.append("application_number = %s")
                    params.append(search_params['application_number'])
                
                if 'status' in search_params:
                    where_clauses.append("application_status = %s")
                    params.append(search_params['status'])
                
                if 'emirate' in search_params:
                    where_clauses.append("emirate = %s")
                    params.append(search_params['emirate'])
                
                if 'date_from' in search_params:
                    where_clauses.append("submitted_at >= %s")
                    params.append(search_params['date_from'])
                
                if 'date_to' in search_params:
                    where_clauses.append("submitted_at <= %s")
                    params.append(search_params['date_to'])
                
                where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
                
                query = f"""
                    SELECT * FROM application_summary 
                    WHERE {where_clause}
                    ORDER BY submitted_at DESC 
                    LIMIT 100
                """
                
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
    
    def get_workflow_log(self, application_id: str) -> List[Dict[str, Any]]:
        """Get workflow logs for an application."""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM workflow_logs 
                    WHERE application_id = %s 
                    ORDER BY start_time DESC
                """, (application_id,))
                
                return [dict(row) for row in cursor.fetchall()]
    
    def add_workflow_log(self, workflow_data: Dict[str, Any]) -> str:
        """Add workflow log entry."""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO workflow_logs (
                        application_id, workflow_id, workflow_status, start_time,
                        end_time, duration_seconds, documents_processed, 
                        errors_count, warnings_count, workflow_data
                    ) VALUES (
                        %(application_id)s, %(workflow_id)s, %(workflow_status)s, %(start_time)s,
                        %(end_time)s, %(duration_seconds)s, %(documents_processed)s,
                        %(errors_count)s, %(warnings_count)s, %(workflow_data)s
                    ) RETURNING id
                """, workflow_data)
                
                log_id = cursor.fetchone()['id']
                conn.commit()
                return str(log_id)


# Utility functions
def create_database_config_from_env() -> DatabaseConfig:
    """Create database config from environment variables."""
    return DatabaseConfig(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '5432')),
        database=os.getenv('DB_NAME', 'social_security_system'),
        username=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres'),  # Default demo password
        min_connections=int(os.getenv('DB_MIN_CONNECTIONS', '1')),
        max_connections=int(os.getenv('DB_MAX_CONNECTIONS', '20'))
    )


def serialize_for_json(obj):
    """Serialize objects for JSON storage."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_for_json(item) for item in obj]
    return obj


# Example usage
if __name__ == "__main__":
    # Example of how to use the database operations
    config = create_database_config_from_env()
    db_manager = DatabaseManager(config)
    repo = ApplicationRepository(db_manager)
    
    # Example application data (matching the form structure)
    sample_application = {
        "applicant": {
            "emirates_id": "784199999999999",
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "1990-01-01",
            "gender": "Male",
            "nationality": "UAE",
            "phone_number": "+971501234567",
            "email": "test@example.com",
            "education_level": "Bachelor's",
            "address": {
                "emirate": "Dubai",
                "city": "Dubai",
                "area": "Downtown",
                "po_box": "12345",
                "address_line": "Test Address"
            },
            "employment": {
                "status": "Employed",
                "employer_name": "Test Company",
                "job_title": "Developer",
                "monthly_income": 10000.00,
                "years_of_experience": 5
            }
        },
        "family_members": [
            {
                "name": "Test Spouse",
                "relationship": "Spouse",
                "age": 28,
                "emirates_id": "784199999999998",
                "has_income": False,
                "monthly_income": 0.0,
                "is_dependent": False
            }
        ],
        "application_type": "Regular Support",
        "priority_level": "Normal",
        "requested_amount": 3000.00,
        "support_duration": "6 months",
        "reason_for_application": "Test application",
        "additional_notes": "This is a test"
    }
    
    try:
        # Create application
        app_id = repo.create_application(sample_application)
        print(f"Created application with ID: {app_id}")
        
        # Retrieve application
        app_data = repo.get_application_by_id(app_id)
        print(f"Retrieved application: {app_data['application_number']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        db_manager.close_all_connections()