# 🏗️ Social Security Application Backend

## 🌟 **Complete FastAPI Backend for Social Security Application System**

A comprehensive backend API built with FastAPI that handles application submissions, document uploads, and AI chatbot integration for the UAE Social Security Application System.

## 🎯 **Features**

### ✅ **Core Functionality**
- **Application Management**: Create, read, update, delete applications
- **Document Upload**: Secure file upload with validation and storage
- **AI Chatbot Integration**: Career counseling, job search, course recommendations
- **Database Integration**: PostgreSQL with async operations
- **RESTful API**: Clean, documented API endpoints
- **File Management**: Local file storage with metadata tracking

### 🔧 **Technical Features**
- **FastAPI Framework**: Modern, fast, async Python web framework
- **Pydantic Models**: Data validation and serialization
- **CORS Support**: Configured for Streamlit frontend integration
- **Error Handling**: Comprehensive error handling and logging
- **Background Tasks**: Async processing for long-running operations
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

## 📁 **Project Structure**

```
backend/
├── __init__.py                 # Package initialization
├── main.py                     # FastAPI application entry point
├── config.py                   # Configuration settings
├── models.py                   # Pydantic data models
├── start_backend.py           # Server startup script
├── test_backend.py            # Backend testing script
├── README.md                  # This documentation
├── database/
│   ├── __init__.py
│   └── connection.py          # Database connection manager
├── routers/
│   ├── __init__.py
│   ├── applications.py        # Application endpoints
│   ├── documents.py           # Document upload endpoints
│   └── chatbot.py            # AI chatbot endpoints
├── uploads/                   # Document storage directory
└── logs/                      # Application logs
```

## 🚀 **Quick Start**

### 1. **Install Dependencies**
```bash
# Activate virtual environment
source .venv/bin/activate

# Install requirements (if not already installed)
pip install fastapi uvicorn python-multipart aiofiles asyncpg
```

### 2. **Configure Environment**
```bash
# Copy environment template
cp .env.template .env

# Edit .env file with your settings
DATABASE_URL=postgresql://postgres:password@localhost:5432/social_security_db
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. **Start the Backend**
```bash
# Method 1: Using startup script
cd backend
python start_backend.py

# Method 2: Direct uvicorn
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. **Test the Backend**
```bash
# Run comprehensive tests
python backend/test_backend.py

# Or test individual endpoints
curl http://localhost:8000/health
```

## 📡 **API Endpoints**

### **Core Endpoints**
- `GET /` - API information and status
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative API documentation

### **Applications API** (`/api/v1/applications`)
- `POST /` - Create new application
- `GET /{application_id}` - Get application by ID
- `PUT /{application_id}` - Update application
- `DELETE /{application_id}` - Delete application
- `GET /` - List applications with filtering
- `GET /stats/overview` - Application statistics

### **Documents API** (`/api/v1/documents`)
- `POST /upload` - Upload documents
- `GET /application/{application_id}` - Get application documents
- `GET /{document_id}/download` - Download document
- `GET /{document_id}/info` - Get document information
- `DELETE /{document_id}` - Delete document
- `GET /types/list` - Get supported document types

### **Chatbot API** (`/api/v1/chatbot`)
- `POST /chat` - Chat with AI assistant
- `GET /conversation/{conversation_id}/history` - Get chat history
- `DELETE /conversation/{conversation_id}` - Clear conversation
- `GET /tools/available` - Get available chatbot tools
- `POST /quick-query` - Quick single query
- `GET /status` - Chatbot service status

## 💾 **Data Models**

### **Application Data Structure**
```python
{
    "personal_info": {
        "first_name": "Ahmed",
        "last_name": "Al Mansouri",
        "emirates_id": "784199012345678",
        "date_of_birth": "1984-05-15",
        "gender": "male",
        "nationality": "UAE",
        "marital_status": "married",
        "phone_number": "+971501234567",
        "email": "ahmed@email.com"
    },
    "address_info": {
        "street_address": "123 Sheikh Zayed Road",
        "city": "Dubai",
        "emirate": "Dubai",
        "country": "UAE"
    },
    "employment_info": {
        "employer_name": "Tech Solutions LLC",
        "job_title": "Senior Engineer",
        "employment_start_date": "2020-01-15",
        "monthly_salary": 15000.0,
        "employment_type": "full-time"
    },
    "education_info": {
        "highest_education": "bachelor",
        "institution_name": "American University of Sharjah",
        "graduation_year": 2008,
        "field_of_study": "Computer Engineering"
    },
    "family_members": [...],
    "financial_info": {...}
}
```

### **Document Upload Structure**
```python
{
    "files": [file1, file2, ...],
    "application_id": "APP-2024-123456",
    "document_types": ["emirates_id", "salary_certificate"]
}
```

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/db_name

# API Settings
DEBUG=false
SECRET_KEY=your-secret-key-here

# File Upload
MAX_FILE_SIZE=10485760  # 10MB in bytes

# AI Chatbot
OPENAI_API_KEY=your_openai_api_key
CHATBOT_MODEL=gpt-3.5-turbo
CHATBOT_TEMPERATURE=0.7

# Logging
LOG_LEVEL=INFO
LOG_FILE=backend/logs/app.log
```

### **Supported File Types**
- PDF documents (`application/pdf`)
- Images (`image/jpeg`, `image/png`)
- Excel files (`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`)
- Word documents (`application/vnd.openxmlformats-officedocument.wordprocessingml.document`)
- Text files (`text/plain`)

### **Document Types**
- Emirates ID
- Passport
- Salary Certificate
- Bank Statement
- Employment Contract
- Medical Report
- Family Book
- Birth Certificate
- Marriage Certificate
- Other Documents

## 🧪 **Testing**

### **Run All Tests**
```bash
python backend/test_backend.py
```

### **Manual Testing Examples**

#### **Create Application**
```bash
curl -X POST "http://localhost:8000/api/v1/applications/" \
  -H "Content-Type: application/json" \
  -d @sample_application.json
```

#### **Upload Document**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "files=@document.pdf" \
  -F "application_id=APP-2024-123456"
```

#### **Chat with AI**
```bash
curl -X POST "http://localhost:8000/api/v1/chatbot/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "I need career advice"}'
```

## 🔗 **Integration with Streamlit**

### **Frontend Integration Points**

#### **1. Application Submission**
```python
# Streamlit frontend code
import requests

def submit_application(application_data):
    response = requests.post(
        "http://localhost:8000/api/v1/applications/",
        json=application_data
    )
    return response.json()
```

#### **2. Document Upload**
```python
def upload_documents(files, application_id):
    files_data = [("files", file) for file in files]
    data = {"application_id": application_id}
    
    response = requests.post(
        "http://localhost:8000/api/v1/documents/upload",
        files=files_data,
        data=data
    )
    return response.json()
```

#### **3. Chatbot Integration**
```python
def chat_with_assistant(message, conversation_id=None):
    data = {
        "message": message,
        "conversation_id": conversation_id
    }
    
    response = requests.post(
        "http://localhost:8000/api/v1/chatbot/chat",
        json=data
    )
    return response.json()
```

## 📊 **Monitoring and Logging**

### **Health Monitoring**
- Health check endpoint: `GET /health`
- Application statistics: `GET /api/v1/applications/stats/overview`
- Chatbot status: `GET /api/v1/chatbot/status`

### **Logging**
- Application logs: `backend/logs/app.log`
- Request/response logging
- Error tracking and reporting
- Performance monitoring

## 🔒 **Security Features**

### **File Upload Security**
- File type validation
- File size limits (10MB default)
- Secure filename handling
- Virus scanning ready (extensible)

### **Data Validation**
- Pydantic model validation
- Emirates ID format validation
- Email and phone number validation
- Date range validation

### **API Security**
- CORS configuration
- Request rate limiting ready
- Input sanitization
- Error message sanitization

## 🚀 **Production Deployment**

### **Docker Deployment** (Optional)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ ./backend/
COPY req_agents/ ./req_agents/

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Environment Setup**
```bash
# Production environment variables
export DATABASE_URL="postgresql://prod_user:prod_pass@db_host:5432/prod_db"
export DEBUG=false
export LOG_LEVEL=WARNING
```

## 📈 **Performance Considerations**

### **Database Optimization**
- Connection pooling (asyncpg)
- Query optimization
- Index usage
- Async operations

### **File Storage**
- Local storage for development
- Cloud storage ready (S3, Azure Blob)
- CDN integration ready
- File compression options

### **Caching**
- Response caching ready
- Database query caching
- Static file caching
- Redis integration ready

## 🛠️ **Development**

### **Adding New Endpoints**
1. Define Pydantic models in `models.py`
2. Create router in `routers/`
3. Add database operations in `database/connection.py`
4. Include router in `main.py`
5. Add tests in `test_backend.py`

### **Database Schema Updates**
1. Update database schema
2. Update Pydantic models
3. Update database operations
4. Test with sample data

## 📞 **Support and Troubleshooting**

### **Common Issues**

#### **Database Connection Failed**
```bash
# Check database status
pg_isready -h localhost -p 5432

# Check connection string
echo $DATABASE_URL
```

#### **File Upload Issues**
```bash
# Check upload directory permissions
ls -la backend/uploads/

# Check file size limits
curl -X GET "http://localhost:8000/api/v1/documents/types/list"
```

#### **Chatbot Not Working**
```bash
# Check chatbot status
curl -X GET "http://localhost:8000/api/v1/chatbot/status"

# Check OpenAI API key
echo $OPENAI_API_KEY
```

## 🎉 **Ready for Production!**

The Social Security Application Backend is **production-ready** with:

- ✅ **Complete API Coverage**: All required endpoints implemented
- ✅ **Data Validation**: Comprehensive input validation and sanitization
- ✅ **Error Handling**: Robust error handling and logging
- ✅ **Documentation**: Auto-generated API documentation
- ✅ **Testing**: Comprehensive test suite
- ✅ **Security**: File upload security and data validation
- ✅ **Integration**: Ready for Streamlit frontend integration
- ✅ **AI Features**: Advanced chatbot with career counseling
- ✅ **Scalability**: Async operations and connection pooling

**Start building your Social Security Application System today!** 🚀