# 🇦🇪 UAE Social Security Application System

A comprehensive AI-powered social security application system built with Streamlit, FastAPI, and advanced document processing capabilities.

## 🌟 Features

### 🖥️ **Frontend (Streamlit)**

- **Interactive Application Form** - Complete social security benefit application
- **Document Upload System** - Support for multiple document types (PDF, DOCX, XLSX)
- **AI Chatbot Assistant** - Intelligent help with job search, career guidance, and application status
- **Application Status Tracking** - Real-time status updates and processing results
- **Document Processing Interface** - One-click document analysis and assessment

### 🔧 **Backend (FastAPI)**

- **RESTful API** - Complete CRUD operations for applications and documents
- **Database Integration** - PostgreSQL with comprehensive schema
- **Document Processing Pipeline** - AI-powered document analysis and assessment
- **Authentication System** - Secure user management
- **Real-time Status Updates** - WebSocket support for live updates

### 🤖 **AI-Powered Features**

- **Multi-Agent System** - Specialized agents for different tasks
- **Document Processing** - OCR, text extraction, and intelligent analysis
- **Financial Assessment** - Comprehensive evaluation across 5 dimensions
- **Career Guidance** - Job search integration with LinkedIn API
- **Course Recommendations** - Udemy API integration for skill development
- **Intelligent Chatbot** - LangChain-powered conversational AI

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │    FastAPI      │    │   PostgreSQL    │
│   Frontend      │◄──►│    Backend      │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                        │
        │               ┌─────────────────┐              │
        └──────────────►│  AI Agents      │◄─────────────┘
                        │  - Document     │
                        │  - Assessment   │
                        │  - Chatbot      │
                        │  - Workflow     │
                        └─────────────────┘
```

## 📋 Supported Document Types

- **Emirates ID** (PDF) - Personal information extraction
- **Resume/CV** (PDF, DOCX) - Employment history and skills analysis
- **Bank Statements** (PDF, TXT) - Financial behavior assessment
- **Credit Reports** (PDF, TXT) - Credit history and risk analysis
- **Assets/Liabilities** (XLSX) - Net worth and financial position

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- OpenAI API Key

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/srinadh2151/social-security-system.git
   cd social-security-system
   ```

2. **Create virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**

   ```bash
   cd database
   python setup.py
   ```

6. **Start the backend**

   ```bash
   python backend/main.py
   ```

7. **Start the frontend**
   ```bash
   streamlit run streamlit_app.py
   ```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=social_security_system
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# API Keys (Optional)
LINKEDIN_API_KEY=your_linkedin_api_key
UDEMY_API_KEY=your_udemy_api_key
```

## 📊 Assessment Criteria

The system evaluates applications across 5 key dimensions:

1. **Income Assessment** (35%) - Income stability and sources
2. **Employment Assessment** (30%) - Job status and career progression
3. **Family Assessment** (15%) - Family composition and needs
4. **Wealth Assessment** (15%) - Assets, liabilities, and credit score
5. **Demographic Assessment** (5%) - Age, education, and location factors

## 🤖 AI Agents

### Document Processing Agent

- Extracts structured data from various document types
- Uses OCR for image-based documents
- Validates and cross-references information

### Assessment Agent

- Evaluates applications using AI-powered scoring
- Generates risk assessments and recommendations
- Provides detailed reasoning for decisions

### Chatbot Agent

- Handles user queries about applications
- Provides job search assistance via LinkedIn API
- Offers course recommendations via Udemy API
- Delivers personalized career counseling

### Workflow Orchestrator

- Manages the complete processing pipeline
- Coordinates between different agents
- Generates comprehensive reports and audit trails

## 📱 API Endpoints

### Applications

- `POST /api/v1/applications/` - Create new application
- `GET /api/v1/applications/{id}` - Get application details
- `PUT /api/v1/applications/{id}` - Update application
- `GET /api/v1/applications/` - List applications

### Documents

- `POST /api/v1/documents/upload` - Upload documents
- `POST /api/v1/documents/process-uploads` - Process uploaded documents
- `GET /api/v1/documents/workflows` - List processing workflows
- `GET /api/v1/documents/workflow/{id}/status` - Get workflow status

### Chatbot

- `POST /api/v1/chatbot/chat` - Send message to chatbot
- `GET /api/v1/chatbot/conversation/{id}/history` - Get chat history
- `DELETE /api/v1/chatbot/conversation/{id}` - Clear conversation

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_backend.py
pytest tests/test_agents.py
pytest tests/test_integration.py
```

## 📈 Processing Workflow

1. **Document Upload** - Users upload required documents
2. **Classification** - AI automatically classifies document types
3. **Extraction** - Structured data extraction using OCR and NLP
4. **Assessment** - Multi-dimensional evaluation and scoring
5. **Decision** - Final approval/rejection with detailed reasoning
6. **Notification** - Real-time status updates to users

## 🔒 Security Features

- **Data Encryption** - All sensitive data encrypted at rest
- **API Authentication** - JWT-based authentication system
- **Input Validation** - Comprehensive input sanitization
- **Audit Logging** - Complete audit trail for all operations
- **Privacy Protection** - GDPR-compliant data handling

## 🌍 Localization

- **Multi-language Support** - English and Arabic
- **Cultural Adaptation** - UAE-specific business rules and requirements
- **Local Integration** - Emirates ID validation and local bank support

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Database Schema](database/schema.sql) - Complete database structure
- [Agent Documentation](req_agents/README.md) - AI agent specifications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🚀 Future Enhancements

### 🔌 **Integration & Interoperability**

1. **Model Context Protocol (MCP) Integration**

   - Convert API endpoints to MCP servers using FastMCP package
   - Add OAuth2/JWT authentication for enhanced security
   - Support for real-time data streaming and context sharing

2. **Advanced A2A (Application-to-Application) Interactions**

   - Implement GraphQL APIs for more flexible data querying
   - Add webhook support for real-time notifications to external systems
   - Create SDK packages for popular programming languages (Python, JavaScript, Java)
   - Support for batch processing and bulk operations

3. **Government System Integration**
   - Direct integration with UAE Pass for identity verification
   - Real-time connectivity with Emirates ID Authority
   - Integration with Ministry of Human Resources databases
   - Automated data sync with Central Bank of UAE for financial verification

### 🤖 **AI & Machine Learning Enhancements**

4. **Intelligent Assessment Scoring**

   - Replace heuristic weightage with ML-trained models using historical approval data
   - Implement dynamic scoring that adapts based on economic conditions
   - Add explainable AI features for transparent decision-making
   - Develop predictive models for application success probability

5. **Advanced Document Processing**

   - Multi-modal AI for processing handwritten documents and signatures
   - Automated document quality assessment and enhancement

6. **Personalized AI Assistant**
   - Proactive notifications and reminders for application requirements
   - Integration with popular messaging platforms (WhatsApp, Telegram)

7. **Advanced Analytics Dashboard**
   - Real-time processing metrics and system performance monitoring
   - Predictive analytics for application volume forecasting
   - Fraud detection patterns and risk assessment visualization
   - Demographic analysis and trend identification

8. **Business Intelligence Integration**
   - Automated report generation for government stakeholders
   - Data warehouse implementation for historical analysis
   - Machine learning insights for policy optimization

### 🌐 **Scalability & Performance**

9. **Cloud-Native Architecture**

    - Microservices architecture with Kubernetes orchestration
    - Auto-scaling based on demand patterns
    - Multi-region deployment for disaster recovery
    - Edge computing for faster document processing

12. **Performance Optimization**
    - Implement caching strategies (Redis, CDN)
    - Database optimization with read replicas and sharding
    - Asynchronous processing for heavy workloads
    - Real-time monitoring and alerting systems