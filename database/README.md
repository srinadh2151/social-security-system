# Social Security Application System - Database

This directory contains all database-related files for the Social Security Application System, including schema definitions, sample data, and database operations.

## 📁 Files Overview

- **`schema.sql`** - Complete PostgreSQL database schema with tables, indexes, triggers, and functions
- **`sample_data.sql`** - Sample data for testing and development
- **`database_operations.py`** - Python module for database operations and repository pattern
- **`setup.py`** - Database setup and initialization script
- **`README.md`** - This documentation file

## 🗄️ Database Schema

### Core Tables

#### **Applicants**
- Stores personal information of applicants
- Primary key: `id` (UUID)
- Unique constraint on `emirates_id`
- Includes personal details, contact info, and education level

#### **Applications**
- Main application records
- Links to applicants via foreign key
- Tracks application status, type, amounts, and AI assessment results
- Auto-generates application numbers

#### **Family Members**
- Stores information about applicant's family members
- Links to applicants
- Tracks dependents and their income

#### **Financial Info**
- Financial situation details per application
- Includes income, expenses, debts, assets
- Auto-calculates net worth

#### **Employment Info**
- Employment history and current status
- Links to applicants
- Tracks job details and income

#### **Documents**
- Uploaded document metadata and processing results
- Stores file paths, processing status, and extracted data
- Links to applications

#### **Assessment Results**
- AI assessment results and scores
- Multiple assessment types per application
- Stores recommendations and risk factors

### Supporting Tables

- **`addresses`** - Applicant addresses
- **`banking_info`** - Banking and account details
- **`emergency_contacts`** - Emergency contact information
- **`application_status_history`** - Status change tracking
- **`workflow_logs`** - Workflow execution logs
- **`audit_log`** - System audit trail

### Views

- **`application_summary`** - Consolidated application view
- **`family_summary`** - Family information summary

## 🚀 Setup Instructions

### Prerequisites

1. **PostgreSQL 12+** installed and running
2. **Python 3.8+** with required packages:
   ```bash
   pip install psycopg2-binary
   ```

### Environment Variables

For demo purposes, the setup uses simple defaults. You can optionally set:

```bash
# Optional (defaults shown)
export DB_HOST='localhost'
export DB_PORT='5432'
export DB_NAME='social_security_system'
export DB_USER='postgres'
export DB_PASSWORD='postgres'
```

### Quick Setup

1. **Make sure PostgreSQL is running** with default settings (user: postgres, password: postgres)

2. **Navigate to database directory:**
   ```bash
   cd database
   ```

3. **Run setup script:**
   ```bash
   python setup.py
   ```

4. **Verify setup:**
   The script will automatically verify the setup and show sample data.

### Manual Setup

If you prefer manual setup:

1. **Create database:**
   ```sql
   CREATE DATABASE social_security_system;
   ```

2. **Connect to database:**
   ```bash
   psql -h localhost -U postgres -d social_security_system
   ```

3. **Run schema:**
   ```sql
   \i schema.sql
   ```

4. **Load sample data:**
   ```sql
   \i sample_data.sql
   ```

## 🔧 Database Operations

### Using the Python Module

```python
from database.database_operations import DatabaseManager, ApplicationRepository, create_database_config_from_env

# Initialize
config = create_database_config_from_env()
db_manager = DatabaseManager(config)
repo = ApplicationRepository(db_manager)

# Create application
application_data = {
    "applicant": {
        "emirates_id": "784199999999999",
        "first_name": "John",
        "last_name": "Doe",
        # ... other fields
    },
    "application_type": "Regular Support",
    "requested_amount": 3000.00,
    # ... other fields
}

app_id = repo.create_application(application_data)

# Retrieve application
application = repo.get_application_by_id(app_id)

# Update status
repo.update_application_status(app_id, "approved", "admin", "Meets all criteria")
```

### Key Operations

- **`create_application()`** - Create new application with all related data
- **`get_application_by_id()`** - Retrieve complete application data
- **`get_application_by_number()`** - Find application by number
- **`update_application_status()`** - Change application status
- **`add_document()`** - Add document to application
- **`add_assessment_result()`** - Store AI assessment results
- **`search_applications()`** - Search with various filters

## 📊 Sample Data

The database includes sample data for testing:

- **5 sample applicants** with complete profiles
- **5 sample applications** in various statuses
- **Family members** for each applicant
- **Financial information** and banking details
- **Sample documents** and assessment results
- **Status history** and workflow logs

### Sample Applications

1. **Ahmed Al Mansouri** - Family Support (Submitted)
2. **Fatima Al Zahra** - Regular Support (Under Review)
3. **Mohammed Al Rashid** - Emergency Support (Processing)
4. **Aisha Al Maktoum** - Regular Support (Approved)
5. **Omar Al Nahyan** - Elderly Support (Approved)

## 🔍 Useful Queries

### Get Application Summary
```sql
SELECT * FROM application_summary 
WHERE application_status = 'submitted' 
ORDER BY submitted_at DESC;
```

### Family Information
```sql
SELECT * FROM family_summary 
WHERE dependents_count > 2;
```

### Assessment Results
```sql
SELECT 
    a.application_number,
    ap.first_name || ' ' || ap.last_name as name,
    ar.assessment_score,
    ar.recommendations
FROM applications a
JOIN applicants ap ON a.applicant_id = ap.id
JOIN assessment_results ar ON a.id = ar.application_id
WHERE ar.assessment_type = 'comprehensive'
ORDER BY ar.assessment_score DESC;
```

### Document Processing Status
```sql
SELECT 
    a.application_number,
    d.document_type,
    d.processing_status,
    d.confidence_score
FROM applications a
JOIN documents d ON a.id = d.application_id
WHERE d.processing_status = 'processed'
ORDER BY d.confidence_score DESC;
```

## 🛡️ Security Features

- **UUID Primary Keys** - Prevents ID enumeration
- **Input Validation** - Check constraints on critical fields
- **Audit Logging** - Automatic audit trail for all changes
- **User Permissions** - Separate application user with limited privileges
- **Data Encryption** - Sensitive data can be encrypted at application level

## 🔄 Maintenance

### Backup
```bash
pg_dump -h localhost -U postgres social_security_system > backup.sql
```

### Restore
```bash
psql -h localhost -U postgres -d social_security_system < backup.sql
```

### Monitor Performance
```sql
-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT 
    indexrelname,
    idx_tup_read,
    idx_tup_fetch,
    idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

## 🐛 Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check PostgreSQL is running
   - Verify host/port settings
   - Check firewall settings

2. **Permission Denied**
   - Ensure admin user has sufficient privileges
   - Check database ownership
   - Verify user exists

3. **Schema Creation Failed**
   - Check PostgreSQL version (12+ required)
   - Verify extensions are available
   - Check disk space

4. **Sample Data Issues**
   - Ensure schema is created first
   - Check for constraint violations
   - Verify data types match

### Getting Help

- Check PostgreSQL logs: `/var/log/postgresql/`
- Enable query logging for debugging
- Use `EXPLAIN ANALYZE` for query performance
- Check system resources (CPU, memory, disk)

## 📈 Performance Optimization

- **Indexes** - Created on frequently queried columns
- **Partitioning** - Consider for large tables (applications, documents)
- **Connection Pooling** - Implemented in database_operations.py
- **Query Optimization** - Use EXPLAIN ANALYZE for slow queries
- **Regular Maintenance** - VACUUM and ANALYZE tables regularly

## 🔮 Future Enhancements

- **Read Replicas** - For reporting and analytics
- **Archiving** - Move old applications to archive tables
- **Encryption** - Column-level encryption for sensitive data
- **Monitoring** - Database performance monitoring
- **Backup Automation** - Automated backup and retention policies