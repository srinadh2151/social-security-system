"""
Simplified Database Tools for Social Security Application Chatbot

This module provides simplified tools for querying the database without complex inheritance.
"""

import os
import psycopg2
import psycopg2.extras
from typing import Dict, Any, Optional, List
import json
from datetime import datetime


class DatabaseConfig:
    """Database configuration."""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '5432'))
        self.database = os.getenv('DB_NAME', 'social_security_system')
        self.user = os.getenv('DB_USER', 'srinadh.nidadana-c')
        self.password = os.getenv('DB_PASSWORD', '')


class SimpleApplicationQuery:
    """Simple application query tool."""
    
    def __init__(self):
        self.db_config = DatabaseConfig()
    
    def get_connection(self):
        """Get database connection."""
        return psycopg2.connect(
            host=self.db_config.host,
            port=self.db_config.port,
            database=self.db_config.database,
            user=self.db_config.user,
            password=self.db_config.password
        )
    
    def query_application(self, application_id: str) -> str:
        """Query application information."""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    # Main application query with applicant details
                    main_query = """
                    SELECT 
                        a.id as application_id,
                        a.application_number,
                        a.application_type,
                        a.priority_level,
                        a.requested_amount,
                        a.approved_amount,
                        a.support_duration,
                        a.approved_duration,
                        a.reason_for_application,
                        a.additional_notes,
                        a.application_status,
                        a.ai_assessment_score,
                        a.ai_assessment_status,
                        a.human_review_required,
                        a.submitted_at,
                        a.updated_at,
                        
                        -- Applicant details
                        ap.emirates_id,
                        ap.first_name,
                        ap.last_name,
                        ap.date_of_birth,
                        ap.gender,
                        ap.nationality,
                        ap.phone_number,
                        ap.email,
                        ap.education_level,
                        
                        -- Address
                        addr.emirate,
                        addr.city,
                        addr.area,
                        addr.address_line,
                        
                        -- Employment
                        emp.employment_status,
                        emp.employer_name,
                        emp.job_title,
                        emp.monthly_income,
                        emp.years_of_experience,
                        
                        -- Financial info
                        fin.total_household_income,
                        fin.monthly_expenses,
                        fin.existing_debts,
                        fin.savings_amount,
                        fin.property_value,
                        fin.other_assets,
                        
                        -- Banking info
                        bank.bank_name,
                        bank.account_number,
                        bank.has_bank_loan
                        
                    FROM applications a
                    JOIN applicants ap ON a.applicant_id = ap.id
                    LEFT JOIN addresses addr ON ap.id = addr.applicant_id
                    LEFT JOIN employment_info emp ON ap.id = emp.applicant_id
                    LEFT JOIN financial_info fin ON a.id = fin.application_id
                    LEFT JOIN banking_info bank ON a.id = bank.application_id
                    WHERE a.application_number = %s OR a.id::text = %s
                    """
                    
                    cursor.execute(main_query, (application_id, application_id))
                    main_result = cursor.fetchone()
                    
                    if not main_result:
                        return f"No application found with ID: {application_id}"
                    
                    # Get family members
                    family_query = """
                    SELECT name, relationship, age, has_income, monthly_income, is_dependent
                    FROM family_members 
                    WHERE applicant_id = %s
                    """
                    cursor.execute(family_query, (main_result['application_id'],))
                    family_members = cursor.fetchall()
                    
                    # Get assessment results
                    assessment_query = """
                    SELECT assessment_type, assessment_score, assessment_details, 
                           recommendations, risk_factors
                    FROM assessment_results 
                    WHERE application_id = %s
                    """
                    cursor.execute(assessment_query, (main_result['application_id'],))
                    assessments = cursor.fetchall()
                    
                    # Get status history
                    status_query = """
                    SELECT old_status, new_status, changed_by, change_reason, created_at
                    FROM application_status_history 
                    WHERE application_id = %s
                    ORDER BY created_at DESC
                    LIMIT 5
                    """
                    cursor.execute(status_query, (main_result['application_id'],))
                    status_history = cursor.fetchall()
                    
                    # Get documents
                    docs_query = """
                    SELECT document_type, document_purpose, processing_status, 
                           confidence_score, upload_date
                    FROM documents 
                    WHERE application_id = %s
                    """
                    cursor.execute(docs_query, (main_result['application_id'],))
                    documents = cursor.fetchall()
                    
                    # Format the response
                    result = {
                        "application_info": dict(main_result),
                        "family_members": [dict(fm) for fm in family_members],
                        "assessments": [dict(a) for a in assessments],
                        "status_history": [dict(sh) for sh in status_history],
                        "documents": [dict(d) for d in documents]
                    }
                    
                    return self.format_application_summary(result)
                    
        except Exception as e:
            return f"Error querying database: {str(e)}"
    
    def format_application_summary(self, data: Dict[str, Any]) -> str:
        """Format the application data into a readable summary."""
        app = data["application_info"]
        
        # Calculate age
        birth_date = app.get('date_of_birth')
        age = ""
        if birth_date:
            today = datetime.now().date()
            age = f" (Age: {today.year - birth_date.year})"
        
        summary = f"""
📋 APPLICATION SUMMARY
{'='*50}

👤 APPLICANT INFORMATION:
• Name: {app['first_name']} {app['last_name']}{age}
• Emirates ID: {app['emirates_id']}
• Gender: {app['gender']}
• Nationality: {app['nationality']}
• Education: {app['education_level']}
• Phone: {app['phone_number']}
• Email: {app['email']}

📍 ADDRESS:
• Location: {app['area']}, {app['city']}, {app['emirate']}
• Address: {app['address_line']}

🏢 EMPLOYMENT:
• Status: {app['employment_status']}
• Employer: {app['employer_name'] or 'N/A'}
• Position: {app['job_title'] or 'N/A'}
• Monthly Income: AED {app['monthly_income'] or 0:,.2f}
• Experience: {app['years_of_experience'] or 0} years

📄 APPLICATION DETAILS:
• Application Number: {app['application_number']}
• Type: {app['application_type']}
• Status: {app['application_status'].upper()}
• Priority: {app['priority_level']}
• Requested Amount: AED {app['requested_amount']:,.2f}
• Support Duration: {app['support_duration']}
• Reason: {app['reason_for_application']}
• Submitted: {app['submitted_at'].strftime('%Y-%m-%d %H:%M') if app['submitted_at'] else 'N/A'}

🤖 AI ASSESSMENT:
• Score: {app['ai_assessment_score'] or 'N/A'}%
• Status: {app['ai_assessment_status'] or 'Pending'}
• Human Review Required: {'Yes' if app['human_review_required'] else 'No'}
"""

        # Add approval information if approved
        if app['application_status'] in ['approved'] and app['approved_amount']:
            summary += f"""
✅ APPROVAL DETAILS:
• Approved Amount: AED {app['approved_amount']:,.2f}
• Approved Duration: {app['approved_duration']}
• You can expect to receive your support payment soon!
"""

        # Add financial information
        if app['total_household_income']:
            summary += f"""
💰 FINANCIAL INFORMATION:
• Total Household Income: AED {app['total_household_income']:,.2f}
• Monthly Expenses: AED {app['monthly_expenses']:,.2f}
• Existing Debts: AED {app['existing_debts']:,.2f}
• Savings: AED {app['savings_amount']:,.2f}
• Property Value: AED {app['property_value']:,.2f}
"""

        # Add family information
        if data["family_members"]:
            summary += f"\n👨‍👩‍👧‍👦 FAMILY MEMBERS:\n"
            for member in data["family_members"]:
                income_info = f"(Income: AED {member['monthly_income']:,.2f})" if member['has_income'] else "(No income)"
                dependent = "Dependent" if member['is_dependent'] else "Independent"
                summary += f"• {member['name']} - {member['relationship']}, Age {member['age']} - {dependent} {income_info}\n"

        # Add recent status changes
        if data["status_history"]:
            summary += f"\n📈 RECENT STATUS CHANGES:\n"
            for status in data["status_history"][:3]:
                summary += f"• {status['old_status']} → {status['new_status']} ({status['created_at'].strftime('%Y-%m-%d')})\n"

        # Add documents status
        if data["documents"]:
            summary += f"\n📎 DOCUMENTS STATUS:\n"
            for doc in data["documents"]:
                confidence = f"({doc['confidence_score']:.0%} confidence)" if doc['confidence_score'] else ""
                summary += f"• {doc['document_type'].upper()}: {doc['processing_status']} {confidence}\n"

        return summary

    def extract_skills(self, application_id: str) -> str:
        """Extract applicant skills and background."""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    query = """
                    SELECT 
                        ap.first_name,
                        ap.last_name,
                        ap.education_level,
                        emp.employment_status,
                        emp.employer_name,
                        emp.job_title,
                        emp.years_of_experience,
                        emp.monthly_income,
                        a.application_type,
                        a.reason_for_application
                    FROM applications a
                    JOIN applicants ap ON a.applicant_id = ap.id
                    LEFT JOIN employment_info emp ON ap.id = emp.applicant_id
                    WHERE a.application_number = %s OR a.id::text = %s
                    """
                    
                    cursor.execute(query, (application_id, application_id))
                    result = cursor.fetchone()
                    
                    if not result:
                        return f"No application found with ID: {application_id}"
                    
                    # Format skills and background information
                    skills_info = {
                        "name": f"{result['first_name']} {result['last_name']}",
                        "education": result['education_level'],
                        "employment_status": result['employment_status'],
                        "current_job": result['job_title'],
                        "employer": result['employer_name'],
                        "experience_years": result['years_of_experience'],
                        "income_level": "High" if (result['monthly_income'] or 0) > 15000 else "Medium" if (result['monthly_income'] or 0) > 8000 else "Low",
                        "application_reason": result['reason_for_application']
                    }
                    
                    return json.dumps(skills_info, indent=2)
                    
        except Exception as e:
            return f"Error extracting skills: {str(e)}"


# Test the simple tools
def test_simple_tools():
    """Test the simplified database tools."""
    print("🧪 Testing Simplified Database Tools")
    print("=" * 40)
    
    db_tool = SimpleApplicationQuery()
    
    # Test application query
    print("\n1. Testing Application Query:")
    test_app_ids = ["APP-2025-000001", "APP-2025-000004"]
    
    for app_id in test_app_ids:
        print(f"\n📋 Querying: {app_id}")
        print("-" * 30)
        try:
            result = db_tool.query_application(app_id)
            if "APPLICATION SUMMARY" in result:
                print("✅ Success! Application found and formatted correctly")
                print(result[:300] + "..." if len(result) > 300 else result)
            else:
                print(f"⚠️  Result: {result}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    # Test skills extraction
    print("\n\n2. Testing Skills Extraction:")
    print(f"\n🔍 Extracting skills for: APP-2025-000001")
    print("-" * 30)
    try:
        skills_result = db_tool.extract_skills("APP-2025-000001")
        if "name" in skills_result.lower():
            print("✅ Success! Skills extracted correctly")
            print(skills_result)
        else:
            print(f"⚠️  Result: {skills_result}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    test_simple_tools()