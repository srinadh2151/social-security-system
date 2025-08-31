"""
Pydantic Models

Data models for the Social Security Application Backend API.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum

# Enums
class ApplicationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING_DOCUMENTS = "pending_documents"

class DocumentType(str, Enum):
    EMIRATES_ID = "emirates_id"
    RESUME = "resume"
    BANK_STATEMENT = "bank_statement"
    CREDIT_REPORT = "credit_report"
    ASSETS = "assets"
    PASSPORT = "passport"
    SALARY_CERTIFICATE = "salary_certificate"
    EMPLOYMENT_CONTRACT = "employment_contract"
    MEDICAL_REPORT = "medical_report"
    FAMILY_BOOK = "family_book"
    BIRTH_CERTIFICATE = "birth_certificate"
    MARRIAGE_CERTIFICATE = "marriage_certificate"
    OTHER = "other"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

class MaritalStatus(str, Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"

class EducationLevel(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    DIPLOMA = "diploma"
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"

# Base Models
class BaseResponse(BaseModel):
    """Base response model."""
    success: bool = True
    message: str = "Operation completed successfully"
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    error: str
    message: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.now)

# Application Models
class PersonalInfo(BaseModel):
    """Personal information model."""
    first_name: str = Field(..., min_length=2, max_length=50)
    middle_name: Optional[str] = Field(None, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    emirates_id: str = Field(..., pattern=r"^\d{15}$")
    passport_number: Optional[str] = Field(None, max_length=20)
    date_of_birth: date
    gender: Gender
    nationality: str = Field(..., min_length=2, max_length=50)
    marital_status: MaritalStatus
    phone_number: str = Field(..., pattern=r"^\+971[0-9]{8,9}$")
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    
    @validator('date_of_birth')
    def validate_age(cls, v):
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError('Applicant must be at least 18 years old')
        if age > 100:
            raise ValueError('Invalid date of birth')
        return v

class AddressInfo(BaseModel):
    """Address information model."""
    street_address: str = Field(..., min_length=5, max_length=200)
    city: str = Field(..., min_length=2, max_length=50)
    emirate: str = Field(..., min_length=2, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=10)
    country: str = Field(default="UAE", max_length=50)

class EmploymentInfo(BaseModel):
    """Employment information model."""
    employer_name: str = Field(..., min_length=2, max_length=100)
    job_title: str = Field(..., min_length=2, max_length=100)
    employment_start_date: date
    monthly_salary: float = Field(..., gt=0, le=1000000)
    employment_type: str = Field(..., max_length=50)  # full-time, part-time, contract
    work_permit_number: Optional[str] = Field(None, max_length=50)
    
    @validator('employment_start_date')
    def validate_employment_date(cls, v):
        if v > date.today():
            raise ValueError('Employment start date cannot be in the future')
        return v

class EducationInfo(BaseModel):
    """Education information model."""
    highest_education: EducationLevel
    institution_name: str = Field(..., min_length=2, max_length=100)
    graduation_year: int = Field(..., ge=1950, le=2024)
    field_of_study: str = Field(..., min_length=2, max_length=100)
    
    @validator('graduation_year')
    def validate_graduation_year(cls, v):
        current_year = datetime.now().year
        if v > current_year:
            raise ValueError('Graduation year cannot be in the future')
        return v

class FamilyMember(BaseModel):
    """Family member model."""
    name: str = Field(..., min_length=2, max_length=100)
    relationship: str = Field(..., min_length=2, max_length=50)
    emirates_id: Optional[str] = Field(None, pattern=r"^\d{15}$")
    date_of_birth: date
    is_dependent: bool = False

class FinancialInfo(BaseModel):
    """Financial information model."""
    monthly_income: float = Field(..., gt=0, le=1000000)
    monthly_expenses: float = Field(..., ge=0, le=1000000)
    bank_name: str = Field(..., min_length=2, max_length=100)
    account_number: str = Field(..., min_length=5, max_length=50)
    has_other_income: bool = False
    other_income_details: Optional[str] = Field(None, max_length=500)
    
    @validator('monthly_expenses')
    def validate_expenses(cls, v, values):
        if 'monthly_income' in values and v > values['monthly_income'] * 2:
            raise ValueError('Monthly expenses seem unusually high compared to income')
        return v

class ApplicationCreate(BaseModel):
    """Application creation model."""
    personal_info: PersonalInfo
    address_info: AddressInfo
    employment_info: EmploymentInfo
    education_info: EducationInfo
    family_members: List[FamilyMember] = []
    financial_info: FinancialInfo
    additional_notes: Optional[str] = Field(None, max_length=1000)

class ApplicationUpdate(BaseModel):
    """Application update model."""
    personal_info: Optional[PersonalInfo] = None
    address_info: Optional[AddressInfo] = None
    employment_info: Optional[EmploymentInfo] = None
    education_info: Optional[EducationInfo] = None
    family_members: Optional[List[FamilyMember]] = None
    financial_info: Optional[FinancialInfo] = None
    additional_notes: Optional[str] = None
    status: Optional[ApplicationStatus] = None

class ApplicationResponse(BaseModel):
    """Application response model."""
    application_id: str
    status: ApplicationStatus
    personal_info: PersonalInfo
    address_info: AddressInfo
    employment_info: EmploymentInfo
    education_info: EducationInfo
    family_members: List[FamilyMember]
    financial_info: FinancialInfo
    additional_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    documents: List[str] = []  # Document IDs

# Document Models
class DocumentInfo(BaseModel):
    """Document information model."""
    document_id: str
    filename: str
    document_type: DocumentType
    size: int
    content_type: str
    upload_date: datetime
    processing_status: str = "uploaded"
    validation_score: Optional[float] = None
    issues: List[str] = []
    application_id: Optional[str] = None

class DocumentUploadResponse(BaseModel):
    """Document upload response model."""
    documents: List[DocumentInfo]
    total_uploaded: int
    success: bool = True
    message: str = "Documents uploaded successfully"

# Chatbot Models
class ChatMessage(BaseModel):
    """Chat message model."""
    message: str = Field(..., min_length=1, max_length=1000)
    application_id: Optional[str] = None
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    conversation_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    tool_used: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None

# Search and Filter Models
class ApplicationFilter(BaseModel):
    """Application filter model."""
    status: Optional[ApplicationStatus] = None
    emirate: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    search_term: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)

class ApplicationListResponse(BaseModel):
    """Application list response model."""
    applications: List[ApplicationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

# Statistics Models
class ApplicationStats(BaseModel):
    """Application statistics model."""
    total_applications: int
    by_status: Dict[str, int]
    by_emirate: Dict[str, int]
    recent_submissions: int
    average_processing_time: Optional[float] = None