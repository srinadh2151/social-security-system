"""
Backend Configuration

Configuration settings for the Social Security Application Backend.
"""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings."""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Social Security Application Backend"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database Settings
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "social_security_system")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components."""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # File Upload Settings
    UPLOAD_DIR: Path = Path("backend/uploads")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [
        "application/pdf",
        "image/jpeg", 
        "image/png",
        "image/jpg",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "text/plain",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    
    # Document Types
    DOCUMENT_TYPES: dict = {
        "emirates_id": "Emirates ID",
        "resume": "Resume",
        "bank_statement": "Bank Statement",
        "credit_report": "Etihad Bureau Credit Report",
        "assets": "Assets/Liabilities",
        "passport": "Passport",
        "salary_certificate": "Salary Certificate",
        # "employment_contract": "Employment Contract",
        # "medical_report": "Medical Report",
        # "family_book": "Family Book",
        # "birth_certificate": "Birth Certificate",
        # "marriage_certificate": "Marriage Certificate",
        "other": "Other Document"
    }
    
    # Application Status
    APPLICATION_STATUSES: List[str] = [
        "draft",
        "submitted", 
        "under_review",
        "approved",
        "rejected",
        "pending_documents"
    ]
    
    # AI Chatbot Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    CHATBOT_MODEL: str = os.getenv("CHATBOT_MODEL", "gpt-3.5-turbo")
    CHATBOT_TEMPERATURE: float = float(os.getenv("CHATBOT_TEMPERATURE", "0.7"))
    
    # Security Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "backend/logs/app.log")

# Create settings instance
settings = Settings()

# Create necessary directories
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
Path("backend/logs").mkdir(parents=True, exist_ok=True)