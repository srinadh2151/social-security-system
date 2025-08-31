"""
Social Security Application - Streamlit Frontend

A comprehensive Streamlit application for UAE Social Security benefit applications
with document upload and AI chatbot integration.
"""

import streamlit as st
import requests
import json
from datetime import datetime, date
from typing import Dict, Any, List, Optional
import io
import base64

# Configuration
BACKEND_URL = "http://localhost:8000/api/v1"
PAGE_CONFIG = {
    "page_title": "UAE Social Security Application",
    "page_icon": "🇦🇪",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Initialize Streamlit
st.set_page_config(**PAGE_CONFIG)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background-color: #1e3c72;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #2a5298;
    }
</style>
""", unsafe_allow_html=True)

# Utility Functions
def check_backend_health() -> bool:
    """Check if backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL.replace('/api/v1', '')}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def display_success(message: str):
    """Display success message."""
    st.markdown(f'<div class="success-box">✅ {message}</div>', unsafe_allow_html=True)

def display_error(message: str):
    """Display error message."""
    st.markdown(f'<div class="error-box">❌ {message}</div>', unsafe_allow_html=True)

def display_info(message: str):
    """Display info message."""
    st.markdown(f'<div class="info-box">ℹ️ {message}</div>', unsafe_allow_html=True)

# Session State Initialization
if 'application_id' not in st.session_state:
    st.session_state.application_id = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = None
if 'page' not in st.session_state:
    st.session_state.page = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 Home"

# Main Application
def main():
    """Main application function."""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🇦🇪 UAE Social Security Application System</h1>
        <p>Apply for social security benefits with AI-powered assistance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check backend status
    if not check_backend_health():
        st.error("🚨 Backend server is not running! Please start the backend first.")
        st.code("uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
        st.stop()
    
    # Sidebar Navigation
    st.sidebar.title("📋 Navigation")
    
    # Initialize current page in session state if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "🏠 Home"
    
    # Check if page was set programmatically
    if 'page' in st.session_state and st.session_state.page:
        st.session_state.current_page = st.session_state.page
        # Clear the programmatic page setting
        st.session_state.page = None
    
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Home", "📝 New Application", "📄 Upload Documents", "🔄 Process Documents", "🤖 AI Assistant", "📊 Application Status"],
        index=["🏠 Home", "📝 New Application", "📄 Upload Documents", "🔄 Process Documents", "🤖 AI Assistant", "📊 Application Status"].index(st.session_state.current_page) if st.session_state.current_page in ["🏠 Home", "📝 New Application", "📄 Upload Documents", "🔄 Process Documents", "🤖 AI Assistant", "📊 Application Status"] else 0,
        key="page_selector"
    )
    
    # Update current page when selectbox changes
    if page != st.session_state.current_page:
        st.session_state.current_page = page
    
    # Page Routing
    if page == "🏠 Home":
        show_home_page()
    elif page == "📝 New Application":
        show_application_form()
    elif page == "📄 Upload Documents":
        show_document_upload()
    elif page == "🔄 Process Documents":
        show_document_processing()
    elif page == "🤖 AI Assistant":
        show_chatbot()
    elif page == "📊 Application Status":
        show_application_status()

def show_home_page():
    """Display home page."""
    st.header("Welcome to UAE Social Security Application System")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📝 Apply for Benefits")
        st.write("Submit your social security benefit application with our easy-to-use form.")
        if st.button("Start New Application", key="start_app"):
            st.session_state.page = "📝 New Application"
            st.rerun()
    
    with col2:
        st.subheader("📄 Upload Documents")
        st.write("Upload required documents to support your application.")
        if st.button("Upload Documents", key="upload_docs"):
            st.session_state.page = "📄 Upload Documents"
            st.rerun()
    
    with col3:
        st.subheader("🔄 Process Documents")
        st.write("Process uploaded documents and generate assessment.")
        if st.button("Process Documents", key="process_docs"):
            st.session_state.page = "🔄 Process Documents"
            st.rerun()
    
    # Second row for additional features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🤖 AI Assistant")
        st.write("Get help with career guidance, job search, and course recommendations.")
        if st.button("Chat with AI", key="chat_ai"):
            st.session_state.page = "🤖 AI Assistant"
            st.rerun()
    
    with col2:
        st.subheader("📊 Application Status")
        st.write("Check the status of your submitted applications.")
        if st.button("Check Status", key="check_status"):
            st.session_state.page = "📊 Application Status"
            st.rerun()
    
    # System Status
    st.subheader("🔧 System Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Backend Status", "🟢 Online")
    
    with col2:
        try:
            response = requests.get(f"{BACKEND_URL}/chatbot/status")
            if response.status_code == 200:
                data = response.json()
                status = "🟢 Available" if data.get("service_available") else "🟡 Limited"
            else:
                status = "🔴 Offline"
        except:
            status = "🔴 Offline"
        st.metric("AI Assistant", status)
    
    with col3:
        response = requests.get(f"{BACKEND_URL}/applications/0d2fa831-02c0-4c9a-961e-882934bf7ffe")
        if response.status_code == 200:
            status = "🟢 Connected"
        else:
            status = "🔴 Offline"       
        st.metric("Database", status)

def show_application_form():
    """Display application form."""
    st.header("📝 New Social Security Application")
    
    with st.form("application_form"):
        st.subheader("👤 Personal Information")
        
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name *", placeholder="Ahmed")
            middle_name = st.text_input("Middle Name", placeholder="Mohammed")
            emirates_id = st.text_input("Emirates ID *", placeholder="784199012345678", max_chars=15)
            date_of_birth = st.date_input("Date of Birth *", min_value=date(1920, 1, 1), max_value=date.today())
            nationality = st.text_input("Nationality *", value="UAE")
        
        with col2:
            last_name = st.text_input("Last Name *", placeholder="Al Mansouri")
            passport_number = st.text_input("Passport Number", placeholder="A1234567")
            gender = st.selectbox("Gender *", ["male", "female"])
            marital_status = st.selectbox("Marital Status *", ["single", "married", "divorced", "widowed"])
            phone_number = st.text_input("Phone Number *", placeholder="+971501234567")
        
        email = st.text_input("Email Address *", placeholder="ahmed@email.com")
        
        st.subheader("🏠 Address Information")
        col1, col2 = st.columns(2)
        with col1:
            street_address = st.text_area("Street Address *", placeholder="123 Sheikh Zayed Road")
            emirate = st.selectbox("Emirate *", ["Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain"])
        
        with col2:
            city = st.text_input("City *", placeholder="Dubai")
            postal_code = st.text_input("Postal Code", placeholder="12345")
        
        st.subheader("💼 Employment Information")
        col1, col2 = st.columns(2)
        with col1:
            employer_name = st.text_input("Employer Name *", placeholder="Tech Solutions LLC")
            employment_start_date = st.date_input("Employment Start Date *", max_value=date.today())
            employment_type = st.selectbox("Employment Type *", ["full-time", "part-time", "contract"])
        
        with col2:
            job_title = st.text_input("Job Title *", placeholder="Senior Engineer")
            monthly_salary = st.number_input("Monthly Salary (AED) *", min_value=0.0, step=100.0, value=15000.0)
            work_permit_number = st.text_input("Work Permit Number", placeholder="WP123456")
        
        st.subheader("🎓 Education Information")
        col1, col2 = st.columns(2)
        with col1:
            highest_education = st.selectbox("Highest Education *", ["primary", "secondary", "diploma", "bachelor", "master", "phd"])
            graduation_year = st.number_input("Graduation Year *", min_value=1950, max_value=2024, value=2010)
        
        with col2:
            institution_name = st.text_input("Institution Name *", placeholder="American University of Sharjah")
            field_of_study = st.text_input("Field of Study *", placeholder="Computer Engineering")
        
        st.subheader("👨‍👩‍👧‍👦 Family Members")
        num_family_members = st.number_input("Number of Family Members", min_value=0, max_value=10, value=0)
        
        family_members = []
        for i in range(num_family_members):
            st.write(f"**Family Member {i+1}**")
            col1, col2, col3 = st.columns(3)
            with col1:
                member_name = st.text_input(f"Name", key=f"family_name_{i}")
                member_relationship = st.text_input(f"Relationship", key=f"family_rel_{i}")
            with col2:
                member_emirates_id = st.text_input(f"Emirates ID", key=f"family_eid_{i}")
                member_dob = st.date_input(f"Date of Birth", key=f"family_dob_{i}")
            with col3:
                member_dependent = st.checkbox(f"Is Dependent", key=f"family_dep_{i}")
            
            if member_name and member_relationship:
                family_members.append({
                    "name": member_name,
                    "relationship": member_relationship,
                    "emirates_id": member_emirates_id if member_emirates_id else None,
                    "date_of_birth": member_dob.isoformat(),
                    "is_dependent": member_dependent
                })
        
        st.subheader("💰 Financial Information")
        col1, col2 = st.columns(2)
        with col1:
            monthly_income = st.number_input("Monthly Income (AED) *", min_value=0.0, step=100.0, value=monthly_salary)
            bank_name = st.text_input("Bank Name *", placeholder="Emirates NBD")
            has_other_income = st.checkbox("Do you have other sources of income?")
        
        with col2:
            monthly_expenses = st.number_input("Monthly Expenses (AED) *", min_value=0.0, step=100.0, value=8000.0)
            account_number = st.text_input("Account Number *", placeholder="1234567890")
            if has_other_income:
                other_income_details = st.text_area("Other Income Details")
            else:
                other_income_details = None
        
        st.subheader("📝 Additional Information")
        additional_notes = st.text_area("Additional Notes", placeholder="Any additional information you'd like to provide...")
        
        # Submit button
        submitted = st.form_submit_button("🚀 Submit Application", use_container_width=True)
        
        if submitted:
            # Validate required fields
            required_fields = {
                "First Name": first_name,
                "Last Name": last_name,
                "Emirates ID": emirates_id,
                "Phone Number": phone_number,
                "Email": email,
                "Street Address": street_address,
                "City": city,
                "Emirate": emirate,
                "Employer Name": employer_name,
                "Job Title": job_title,
                "Institution Name": institution_name,
                "Field of Study": field_of_study,
                "Bank Name": bank_name,
                "Account Number": account_number
            }
            
            missing_fields = [field for field, value in required_fields.items() if not value]
            
            if missing_fields:
                display_error(f"Please fill in the following required fields: {', '.join(missing_fields)}")
                return
            
            # Validate Emirates ID format
            if not emirates_id.isdigit() or len(emirates_id) != 15:
                display_error("Emirates ID must be exactly 15 digits")
                return
            
            # Validate phone number format
            if not phone_number.startswith("+971") or len(phone_number) < 12:
                display_error("Phone number must be in UAE format (+971XXXXXXXXX)")
                return
            
            # Prepare application data
            application_data = {
                "personal_info": {
                    "first_name": first_name,
                    "middle_name": middle_name if middle_name else None,
                    "last_name": last_name,
                    "emirates_id": emirates_id,
                    "passport_number": passport_number if passport_number else None,
                    "date_of_birth": date_of_birth.isoformat(),
                    "gender": gender,
                    "nationality": nationality,
                    "marital_status": marital_status,
                    "phone_number": phone_number,
                    "email": email
                },
                "address_info": {
                    "street_address": street_address,
                    "city": city,
                    "emirate": emirate,
                    "postal_code": postal_code if postal_code else None,
                    "country": "UAE"
                },
                "employment_info": {
                    "employer_name": employer_name,
                    "job_title": job_title,
                    "employment_start_date": employment_start_date.isoformat(),
                    "monthly_salary": monthly_salary,
                    "employment_type": employment_type,
                    "work_permit_number": work_permit_number if work_permit_number else None
                },
                "education_info": {
                    "highest_education": highest_education,
                    "institution_name": institution_name,
                    "graduation_year": graduation_year,
                    "field_of_study": field_of_study
                },
                "family_members": family_members,
                "financial_info": {
                    "monthly_income": monthly_income,
                    "monthly_expenses": monthly_expenses,
                    "bank_name": bank_name,
                    "account_number": account_number,
                    "has_other_income": has_other_income,
                    "other_income_details": other_income_details
                },
                "additional_notes": additional_notes if additional_notes else None
            }
            print('***application_data - \n', application_data)
            print('Type', type(application_data))
            # Submit to backend
            submit_application(application_data)

def submit_application(application_data: Dict[str, Any]):
    """Submit application to backend."""
    try:
        with st.spinner("Submitting your application..."):
            response = requests.post(
                f"{BACKEND_URL}/applications/",
                json=application_data,
                headers={"Content-Type": "application/json"}
            )
        
        if response.status_code == 200:
            data = response.json()
            application_id = data.get("application_id")
            st.session_state.application_id = application_id
            
            display_success(f"Application submitted successfully!")
            
            st.balloons()
            
            # Display application details
            st.subheader("📋 Application Details")
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Application ID:** {application_id}")
                st.info(f"**Status:** {data.get('status', 'submitted').title()}")
            with col2:
                st.info(f"**Submitted:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                st.info(f"**Reference:** Keep this ID for tracking")
            
            # Next steps
            st.subheader("📋 Next Steps")
            next_steps = data.get("next_steps", [])
            for i, step in enumerate(next_steps, 1):
                st.write(f"{i}. {step}")
            
            # Quick actions
            st.subheader("🚀 Quick Actions")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📄 Upload Documents"):
                    st.session_state.page = "📄 Upload Documents"
                    st.rerun()
            with col2:
                if st.button("🤖 Get Career Advice"):
                    st.session_state.page = "🤖 AI Assistant"
                    st.rerun()
            with col3:
                if st.button("📊 Check Status"):
                    st.session_state.page = "📊 Application Status"
                    st.rerun()
        
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
            error_message = error_data.get("detail", f"HTTP {response.status_code}")
            display_error(f"Application submission failed: {error_message}")
    
    except requests.exceptions.ConnectionError:
        display_error("Could not connect to backend server. Please ensure the backend is running.")
    except Exception as e:
        display_error(f"An error occurred: {str(e)}")

def show_document_upload():
    """Display document upload page."""
    st.header("📄 Upload Documents")
    
    # Application ID input
    if not st.session_state.application_id:
        st.subheader("🔍 Enter Application ID")
        application_id = st.text_input("Application ID", placeholder="APP-2024-123456")
        if application_id:
            st.session_state.application_id = application_id
    else:
        application_id = st.session_state.application_id
        st.success(f"📋 Application ID: {application_id}")
    
    if not application_id:
        display_info("Please enter your application ID to upload documents.")
        return
    
    # Get supported document types
    try:
        response = requests.get(f"{BACKEND_URL}/documents/types/list")
        if response.status_code == 200:
            doc_types_data = response.json()
            document_types = doc_types_data.get("document_types", {})
            max_file_size = doc_types_data.get("max_file_size_mb", 10)
        else:
            document_types = {"other": "Other Document"}
            max_file_size = 10
    except:
        document_types = {"other": "Other Document"}
        max_file_size = 10
    
    st.subheader("📎 Select Documents to Upload")
    
    # File uploader
    uploaded_files = st.file_uploader(
        f"Choose files (Max {max_file_size}MB each)",
        accept_multiple_files=True,
        type=['pdf', 'jpg', 'jpeg', 'png', 'xlsx', 'xls', 'docx', 'doc', 'txt']
    )
    
    if uploaded_files:
        st.subheader("📋 Document Classification")
        
        document_classifications = []
        for i, file in enumerate(uploaded_files):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"**{file.name}**")
                st.write(f"Size: {file.size / 1024:.1f} KB")
            
            with col2:
                doc_type = st.selectbox(
                    "Document Type",
                    options=list(document_types.keys()),
                    format_func=lambda x: document_types[x],
                    key=f"doc_type_{i}"
                )
                document_classifications.append(doc_type)
            
            with col3:
                st.write("📄")
        
        # Upload button
        if st.button("🚀 Upload Documents", use_container_width=True):
            upload_documents(uploaded_files, application_id, document_classifications)

def upload_documents(files, application_id: str, document_types: List[str]):
    """Upload documents to backend."""
    try:
        with st.spinner("Uploading documents..."):
            # Prepare files for upload
            files_data = []
            form_data = {"application_id": application_id}
            
            # Prepare files and form data for multipart upload
            files_for_upload = []
            for file in files:
                files_for_upload.append(("files", (file.name, file.getvalue(), file.type)))
            
            # Prepare form data with document types as separate entries
            form_data_list = [("application_id", application_id)]
            for doc_type in document_types:
                form_data_list.append(("document_types", doc_type))
            
            response = requests.post(
                f"{BACKEND_URL}/documents/upload",
                files=files_for_upload,
                data=form_data_list
            )
        
        if response.status_code == 200:
            data = response.json()
            total_uploaded = data.get("total_uploaded", 0)
            
            display_success(f"Successfully uploaded {total_uploaded} documents!")
            
            # Display uploaded documents
            st.subheader("📋 Uploaded Documents")
            documents = data.get("documents", [])
            
            for doc in documents:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"📄 **{doc['filename']}**")
                with col2:
                    st.write(f"Type: {doc['document_type']}")
                with col3:
                    st.write(f"Status: {doc['processing_status']}")
        
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
            error_message = error_data.get("detail", f"HTTP {response.status_code}")
            display_error(f"Document upload failed: {error_message}")
    
    except requests.exceptions.ConnectionError:
        display_error("Could not connect to backend server. Please ensure the backend is running.")
    except Exception as e:
        display_error(f"An error occurred during upload: {str(e)}")

def show_document_processing():
    """Display document processing interface."""
    st.header("🔄 Document Processing & Assessment")
    st.write("Process uploaded documents and generate financial support assessment.")
    
    # Check processing service status
    try:
        response = requests.get(f"{BACKEND_URL}/documents/processing-status")
        if response.status_code == 200:
            status = response.json()
            service_available = status.get("service_available", False)
            uploaded_files_count = status.get("uploaded_files_count", 0)
            processed_workflows_count = status.get("processed_workflows_count", 0)
            
            # Display status
            col1, col2, col3 = st.columns(3)
            with col1:
                if service_available:
                    st.success("✅ Processing Service Available")
                else:
                    st.error("❌ Processing Service Unavailable")
            
            with col2:
                st.metric("📁 Uploaded Files", uploaded_files_count)
            
            with col3:
                st.metric("📊 Processed Workflows", processed_workflows_count)
            
            if not service_available:
                st.warning("Document processing service is not available. Please contact support.")
                return
            
            if uploaded_files_count == 0:
                st.info("No documents found in uploads directory. Please upload documents first.")
                if st.button("📄 Go to Upload Documents"):
                    st.session_state.page = "📄 Upload Documents"
                    st.rerun()
                return
            
        else:
            st.error("Could not check processing service status.")
            return
    
    except Exception as e:
        st.error(f"Error checking service status: {str(e)}")
        return
    
    # Processing options
    st.subheader("🚀 Processing Options")
    
    # Applicant information
    with st.expander("👤 Applicant Information (Optional)", expanded=False):
        applicant_name = st.text_input("Full Name", placeholder="Enter applicant's full name")
        applicant_email = st.text_input("Email", placeholder="applicant@example.com")
        applicant_phone = st.text_input("Phone", placeholder="+971-50-123-4567")
        processing_notes = st.text_area("Processing Notes", placeholder="Any additional notes for processing...")
    
    # Processing buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Process All Uploaded Documents", use_container_width=True, type="primary"):
            process_uploaded_documents(
                applicant_name=applicant_name,
                applicant_email=applicant_email,
                applicant_phone=applicant_phone,
                processing_notes=processing_notes
            )
    
    with col2:
        if st.button("📊 View Processing History", use_container_width=True):
            show_processing_history()
    
    # Display recent workflows
    st.subheader("📋 Recent Processing Results")
    display_recent_workflows()

def process_uploaded_documents(applicant_name="", applicant_email="", applicant_phone="", processing_notes=""):
    """Process all uploaded documents."""
    try:
        # Prepare applicant info
        applicant_info = {
            "processing_timestamp": datetime.now().isoformat(),
            "processing_method": "streamlit_interface"
        }
        
        if applicant_name:
            applicant_info["name"] = applicant_name
        if applicant_email:
            applicant_info["email"] = applicant_email
        if applicant_phone:
            applicant_info["phone"] = applicant_phone
        if processing_notes:
            applicant_info["notes"] = processing_notes
        
        # Show processing status
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔄 Initializing document processing...")
        progress_bar.progress(10)
        
        # Make API call
        payload = {
            "applicant_info": applicant_info
        }
        
        status_text.text("📄 Processing documents...")
        progress_bar.progress(30)
        
        response = requests.post(
            f"{BACKEND_URL}/documents/process-uploads",
            json=payload,
            timeout=300  # 5 minutes timeout
        )
        
        progress_bar.progress(80)
        status_text.text("📊 Generating assessment...")
        
        if response.status_code == 200:
            result = response.json()
            progress_bar.progress(100)
            status_text.text("✅ Processing completed!")
            
            # Display results
            display_processing_results(result)
            
        else:
            progress_bar.empty()
            status_text.empty()
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
            error_message = error_data.get("detail", f"HTTP {response.status_code}")
            st.error(f"Processing failed: {error_message}")
    
    except requests.exceptions.Timeout:
        progress_bar.empty()
        status_text.empty()
        st.warning("⏰ Processing timed out. This may be normal for large documents. Check processing history for results.")
    
    except requests.exceptions.ConnectionError:
        progress_bar.empty()
        status_text.empty()
        st.error("Could not connect to backend server. Please ensure the backend is running.")
    
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"An error occurred during processing: {str(e)}")

def display_processing_results(result):
    """Display processing results."""
    st.success("🎉 Document processing completed successfully!")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Overall Score", f"{result.get('overall_score', 0):.2f}")
    
    with col2:
        decision = result.get('final_decision', 'N/A')
        st.metric("🎯 Decision", decision)
    
    with col3:
        duration = result.get('processing_duration', 'N/A')
        st.metric("⏱️ Duration", duration)
    
    with col4:
        docs_processed = result.get('documents_processed', 0)
        st.metric("📄 Documents", docs_processed)
    
    # Workflow information
    workflow_id = result.get('workflow_id')
    if workflow_id:
        st.info(f"🆔 Workflow ID: `{workflow_id}`")
    
    # Judgment summary
    judgment_summary = result.get('judgment_summary')
    if judgment_summary:
        st.subheader("📋 Assessment Summary")
        
        final_judgment = judgment_summary.get('final_judgment', {})
        support_recommendation = judgment_summary.get('support_recommendation', {})
        risk_profile = judgment_summary.get('risk_profile', {})
        
        # Final judgment
        with st.expander("🎯 Final Judgment", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Decision:** {final_judgment.get('decision', 'N/A').title()}")
                st.write(f"**Priority Level:** {final_judgment.get('priority_level', 'N/A').title()}")
            with col2:
                st.write(f"**Confidence Level:** {final_judgment.get('confidence_level', 'N/A').title()}")
                st.write(f"**Overall Score:** {final_judgment.get('overall_score', 0):.2f}/1.0")
        
        # Support recommendations
        with st.expander("💰 Support Recommendations"):
            support_types = support_recommendation.get('recommended_support_types', [])
            if support_types:
                st.write("**Recommended Support Types:**")
                for support_type in support_types:
                    st.write(f"• {support_type}")
            
            support_amount = support_recommendation.get('estimated_support_amount', 'To be determined')
            st.write(f"**Estimated Support Amount:** {support_amount}")
            
            conditions = support_recommendation.get('conditions', [])
            if conditions:
                st.write("**Conditions:**")
                for condition in conditions:
                    st.write(f"• {condition}")
        
        # Risk assessment
        with st.expander("⚠️ Risk Assessment"):
            risk_level = risk_profile.get('risk_level', 'N/A')
            if risk_level.lower() == 'high':
                st.error(f"**Risk Level:** {risk_level.title()}")
            elif risk_level.lower() == 'medium':
                st.warning(f"**Risk Level:** {risk_level.title()}")
            else:
                st.success(f"**Risk Level:** {risk_level.title()}")
            
            risk_factors = risk_profile.get('key_risk_factors', [])
            if risk_factors:
                st.write("**Key Risk Factors:**")
                for factor in risk_factors:
                    st.write(f"• {factor}")
    
    # Errors and warnings
    errors = result.get('errors', [])
    warnings = result.get('warnings', [])
    
    if errors:
        with st.expander("❌ Processing Errors", expanded=False):
            for error in errors:
                st.error(error)
    
    if warnings:
        with st.expander("⚠️ Processing Warnings", expanded=False):
            for warning in warnings:
                st.warning(warning)

def display_recent_workflows():
    """Display recent processing workflows."""
    try:
        response = requests.get(f"{BACKEND_URL}/documents/workflows")
        if response.status_code == 200:
            workflows_data = response.json()
            workflows = workflows_data.get('workflows', [])
            
            if workflows:
                # Display recent workflows in a table
                recent_workflows = workflows[:5]  # Show last 5
                
                workflow_data = []
                for wf in recent_workflows:
                    workflow_data.append({
                        "Workflow ID": wf.get('workflow_id', 'N/A')[:20] + "...",
                        "Status": wf.get('status', 'N/A').title(),
                        "Applicant": wf.get('applicant_name', 'N/A'),
                        "Decision": wf.get('final_decision', 'N/A').title(),
                        "Score": f"{wf.get('overall_score', 0):.2f}",
                        "Duration": wf.get('processing_time', 'N/A')
                    })
                
                st.dataframe(workflow_data, use_container_width=True)
                
                # Workflow details
                if st.button("🔍 View Detailed Results"):
                    show_processing_history()
            else:
                st.info("No processing workflows found.")
    
    except Exception as e:
        st.error(f"Error loading recent workflows: {str(e)}")

def show_processing_history():
    """Show detailed processing history."""
    st.subheader("📊 Processing History")
    
    try:
        response = requests.get(f"{BACKEND_URL}/documents/workflows")
        if response.status_code == 200:
            workflows_data = response.json()
            workflows = workflows_data.get('workflows', [])
            
            if workflows:
                # Workflow selector
                workflow_options = {}
                for wf in workflows:
                    workflow_id = wf.get('workflow_id', 'Unknown')
                    applicant = wf.get('applicant_name', 'Unknown')
                    status = wf.get('status', 'Unknown')
                    display_name = f"{workflow_id[:15]}... - {applicant} ({status})"
                    workflow_options[display_name] = workflow_id
                
                selected_workflow_display = st.selectbox(
                    "Select workflow to view details:",
                    options=list(workflow_options.keys())
                )
                
                if selected_workflow_display:
                    selected_workflow_id = workflow_options[selected_workflow_display]
                    
                    # Get detailed workflow status
                    detail_response = requests.get(
                        f"{BACKEND_URL}/documents/workflow/{selected_workflow_id}/status"
                    )
                    
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        workflow_status = detail_data.get('workflow_status', {})
                        
                        # Display detailed information
                        st.json(workflow_status)
                    else:
                        st.error("Could not load detailed workflow information.")
            else:
                st.info("No processing workflows found.")
    
    except Exception as e:
        st.error(f"Error loading processing history: {str(e)}")

def show_chatbot():
    """Display AI chatbot interface."""
    st.header("🤖 AI Assistant")
    st.write("Get help with career guidance, job search, and course recommendations.")
    
    # Chat interface
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about careers, jobs, or courses..."):
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        st.chat_message("user").write(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_chatbot_response(prompt)
                st.write(response)
        
        # Add AI response to history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Quick action buttons
    st.subheader("🚀 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💼 Career Advice"):
            quick_query("I need career advice")
    
    with col2:
        if st.button("🔍 Find Jobs"):
            quick_query("Help me find jobs")
    
    with col3:
        if st.button("📚 Course Recommendations"):
            quick_query("What courses should I take?")
    
    with col4:
        if st.button("🔄 Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Application context
    if st.session_state.application_id:
        st.sidebar.success(f"📋 Application: {st.session_state.application_id}")
        if st.sidebar.button("🔍 Use My Application Data"):
            quick_query(st.session_state.application_id)

def get_chatbot_response(message: str) -> str:
    """Get response from AI chatbot."""
    try:
        data = {
            "message": message,
            "application_id": st.session_state.application_id,
            "conversation_id": st.session_state.conversation_id
        }

        print(f"chat session details \n", f"application_id:{data.get('application_id')}", 
              f"conversation_id:{data.get('conversation_id')}")
        
        response = requests.post(
            f"{BACKEND_URL}/chatbot/chat",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Update conversation ID
            if not st.session_state.conversation_id:
                st.session_state.conversation_id = result.get("conversation_id")
            
            return result.get("response", "I'm sorry, I couldn't process your request.")
        else:
            return f"I encountered an error (HTTP {response.status_code}). Please try again."
    
    except requests.exceptions.ConnectionError:
        return "I'm sorry, I can't connect to the AI service right now. Please check if the backend is running."
    except Exception as e:
        return f"I encountered an error: {str(e)}"

def quick_query(query: str):
    """Process a quick query and add to chat history."""
    st.session_state.chat_history.append({"role": "user", "content": query})
    response = get_chatbot_response(query)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()
    st.rerun()

def show_application_status():
    """Display application status page."""
    st.header("📊 Application Status")
    
    # Application ID input
    application_id = st.text_input(
        "Enter Application ID",
        value=st.session_state.application_id or "",
        placeholder="APP-2024-123456"
    )
    
    if st.button("🔍 Check Status") and application_id:
        check_application_status(application_id)
    
    # Recent applications (if any)
    if st.session_state.application_id:
        st.subheader("📋 Your Recent Application")
        check_application_status(st.session_state.application_id)

def check_application_status(application_id: str):
    """Check and display application status."""
    try:
        with st.spinner("Checking application status..."):
            response = requests.get(f"{BACKEND_URL}/applications/{application_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f'*** Data - for Application ID - {application_id}\n', data)
            application = data.get("application", {})
            
            # Display application summary
            st.subheader("📋 Application Summary")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Application ID", application_id)
            with col2:
                status = application.get("application_status", "unknown").title()
                st.metric("Status", status)
            with col3:
                created_date = application.get("created_at", "")[:10] if application.get("created_at") else "Unknown"
                st.metric("Submitted", created_date)
            
            # Personal information
            st.subheader("👤 Applicant Information")
            col1, col2 = st.columns(2)
            with col1:
                full_name = f"{application.get('first_name', '')} {application.get('last_name', '')}".strip()
                st.write(f"**Name:** {full_name if full_name else 'N/A'}")
                st.write(f"**Emirates ID:** {application.get('emirates_id', 'N/A')}")
                st.write(f"**Phone:** {application.get('phone_number', 'N/A')}")
            with col2:
                st.write(f"**Email:** {application.get('email', 'N/A')}")
                st.write(f"**Job Title:** {application.get('job_title', 'N/A')}")
                monthly_income = float(application.get('monthly_income', 0))
                st.write(f"**Monthly Salary:** AED {monthly_income:,.2f}")
            
            # Additional details
            st.subheader("📍 Address Information")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Emirate:** {application.get('emirate', 'N/A')}")
                st.write(f"**City:** {application.get('city', 'N/A')}")
                st.write(f"**Address:** {application.get('address_line', 'N/A')}")
            with col2:
                st.write(f"**P.O. Box:** {application.get('po_box', 'N/A')}")
                st.write(f"**Nationality:** {application.get('nationality', 'N/A')}")
                st.write(f"**Education:** {application.get('education_level', 'N/A')}")
            
            # Employment Information
            st.subheader("💼 Employment Information")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Employer:** {application.get('employer_name', 'N/A')}")
                st.write(f"**Employment Status:** {application.get('employment_status', 'N/A')}")
            with col2:
                st.write(f"**Experience:** {application.get('years_of_experience', 0)} years")
                st.write(f"**Date of Birth:** {application.get('date_of_birth', 'N/A')}")
            
            # Family Members
            family_members = application.get("family_members", [])
            if family_members:
                st.subheader("👨‍👩‍👧‍👦 Family Members")
                for i, member in enumerate(family_members, 1):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**{i}. {member.get('name', 'N/A')}**")
                    with col2:
                        st.write(f"Relationship: {member.get('relationship', 'N/A')}")
                    with col3:
                        st.write(f"Age: {member.get('age', 'N/A')}")
            
            # Financial Information
            financial_info = application.get("financial_info")
            if financial_info:
                st.subheader("💰 Financial Information")
                col1, col2 = st.columns(2)
                with col1:
                    household_income = float(financial_info.get('total_household_income', 0))
                    monthly_expenses = float(financial_info.get('monthly_expenses', 0))
                    st.write(f"**Household Income:** AED {household_income:,.2f}")
                    st.write(f"**Monthly Expenses:** AED {monthly_expenses:,.2f}")
                with col2:
                    net_worth = float(financial_info.get('net_worth', 0))
                    st.write(f"**Net Worth:** AED {net_worth:,.2f}")
                    st.write(f"**Requested Amount:** AED {float(application.get('requested_amount', 0)):,.2f}")
            
            # Banking Information
            banking_info = application.get("banking_info")
            if banking_info:
                st.subheader("🏦 Banking Information")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Bank:** {banking_info.get('bank_name', 'N/A')}")
                with col2:
                    st.write(f"**Account:** {banking_info.get('account_number', 'N/A')}")
            
            # Application Details
            st.subheader("📋 Application Details")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Application Type:** {application.get('application_type', 'N/A')}")
                st.write(f"**Priority:** {application.get('priority_level', 'N/A')}")
            with col2:
                st.write(f"**Support Duration:** {application.get('support_duration', 'N/A')}")
                st.write(f"**Reason:** {application.get('reason_for_application', 'N/A')}")
            
            if application.get('additional_notes'):
                st.write(f"**Additional Notes:** {application.get('additional_notes')}")
            
            # Documents
            documents = application.get("documents", [])
            if documents:
                st.subheader("📄 Uploaded Documents")
                for i, doc in enumerate(documents, 1):
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    with col1:
                        filename = doc.get('file_name', doc.get('filename', 'Unknown'))
                        st.write(f"📄 **{filename}**")
                    with col2:
                        doc_type = doc.get('document_type', 'Unknown').replace('_', ' ').title()
                        st.write(f"Type: {doc_type}")
                    with col3:
                        file_size = doc.get('file_size', doc.get('size', 0))
                        if file_size:
                            size_mb = file_size / (1024 * 1024)
                            if size_mb >= 1:
                                st.write(f"Size: {size_mb:.1f}MB")
                            else:
                                size_kb = file_size / 1024
                                st.write(f"Size: {size_kb:.1f}KB")
                        else:
                            st.write("Size: Unknown")
                    with col4:
                        status = doc.get('processing_status', 'Unknown').title()
                        if status == 'Uploaded':
                            st.write("✅ Uploaded")
                        elif status == 'Processing':
                            st.write("⏳ Processing")
                        elif status == 'Processed':
                            st.write("✅ Processed")
                        else:
                            st.write(f"Status: {status}")
                
                st.write(f"**Total Documents:** {len(documents)}")
            else:
                st.info("No documents uploaded yet.")
        
        elif response.status_code == 404:
            display_error(f"Application {application_id} not found. Please check the ID and try again.")
        else:
            display_error(f"Failed to retrieve application status (HTTP {response.status_code})")
    
    except requests.exceptions.ConnectionError:
        display_error("Could not connect to backend server. Please ensure the backend is running.")
    except Exception as e:
        display_error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()