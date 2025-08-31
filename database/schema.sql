-- Social Security Application System Database Schema
-- PostgreSQL Database Schema for storing application data
-- Create database (run this separately as superuser)
-- CREATE DATABASE social_security_system;
-- \c social_security_system;
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- Create enum types
CREATE TYPE application_status AS ENUM (
    'draft',
    'submitted',
    'under_review',
    'documents_pending',
    'processing',
    'approved',
    'rejected',
    'on_hold',
    'cancelled'
);
CREATE TYPE application_type AS ENUM (
    'Regular Support',
    'Emergency Support',
    'Disability Support',
    'Elderly Support',
    'Family Support'
);
CREATE TYPE priority_level AS ENUM ('Normal', 'High', 'Emergency');
CREATE TYPE support_duration AS ENUM (
    '3 months',
    '6 months',
    '12 months',
    '24 months',
    'Permanent'
);
CREATE TYPE employment_status AS ENUM (
    'Employed',
    'Unemployed',
    'Self-Employed',
    'Retired',
    'Student',
    'Disabled'
);
CREATE TYPE marital_status AS ENUM ('Single', 'Married', 'Divorced', 'Widowed');
CREATE TYPE gender AS ENUM ('Male', 'Female');
CREATE TYPE education_level AS ENUM (
    'No formal education',
    'Primary',
    'Secondary',
    'High School',
    'Diploma',
    'Bachelor''s',
    'Master''s',
    'PhD'
);
CREATE TYPE relationship_type AS ENUM (
    'Spouse',
    'Child',
    'Parent',
    'Sibling',
    'Other'
);
CREATE TYPE emirate AS ENUM (
    'Abu Dhabi',
    'Dubai',
    'Sharjah',
    'Ajman',
    'Umm Al Quwain',
    'Ras Al Khaimah',
    'Fujairah'
);
-- Main applicants table
CREATE TABLE applicants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    emirates_id VARCHAR(15) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender gender NOT NULL,
    nationality VARCHAR(50) NOT NULL DEFAULT 'UAE',
    phone_number VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    education_level education_level,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- Constraints
    CONSTRAINT valid_emirates_id CHECK (
        LENGTH(emirates_id) = 15
        AND emirates_id ~ '^[0-9]+$'
    ),
    CONSTRAINT valid_email CHECK (
        email IS NULL
        OR email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    ),
    CONSTRAINT valid_phone CHECK (phone_number ~ '^[+]?[0-9\s\-()]+$')
);
-- Addresses table
CREATE TABLE addresses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    applicant_id UUID NOT NULL REFERENCES applicants(id) ON DELETE CASCADE,
    emirate emirate NOT NULL,
    city VARCHAR(100) NOT NULL,
    area VARCHAR(100) NOT NULL,
    po_box VARCHAR(20),
    address_line TEXT NOT NULL,
    is_current BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
-- Employment information table
CREATE TABLE employment_info (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    applicant_id UUID NOT NULL REFERENCES applicants(id) ON DELETE CASCADE,
    employment_status employment_status NOT NULL,
    employer_name VARCHAR(200),
    job_title VARCHAR(150),
    monthly_income DECIMAL(12, 2) DEFAULT 0.00,
    years_of_experience INTEGER DEFAULT 0,
    is_current BOOLEAN DEFAULT TRUE,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- Constraints
    CONSTRAINT valid_income CHECK (monthly_income >= 0),
    CONSTRAINT valid_experience CHECK (years_of_experience >= 0),
    CONSTRAINT employment_dates CHECK (
        end_date IS NULL
        OR end_date >= start_date
    )
);
-- Applications table
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_number VARCHAR(20) UNIQUE NOT NULL,
    applicant_id UUID NOT NULL REFERENCES applicants(id) ON DELETE CASCADE,
    application_type application_type NOT NULL,
    application_status application_status DEFAULT 'draft',
    priority_level priority_level DEFAULT 'Normal',
    requested_amount DECIMAL(12, 2) NOT NULL,
    support_duration support_duration NOT NULL,
    reason_for_application TEXT NOT NULL,
    additional_notes TEXT,
    -- Timestamps
    submitted_at TIMESTAMP WITH TIME ZONE,
    processed_at TIMESTAMP WITH TIME ZONE,
    approved_at TIMESTAMP WITH TIME ZONE,
    rejected_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- Assessment results
    ai_assessment_score DECIMAL(5, 2),
    ai_assessment_status VARCHAR(50),
    ai_assessment_date TIMESTAMP WITH TIME ZONE,
    human_review_required BOOLEAN DEFAULT FALSE,
    -- Decision information
    approved_amount DECIMAL(12, 2),
    approved_duration support_duration,
    rejection_reason TEXT,
    conditions TEXT,
    -- Constraints
    CONSTRAINT valid_requested_amount CHECK (requested_amount > 0),
    CONSTRAINT valid_approved_amount CHECK (
        approved_amount IS NULL
        OR approved_amount >= 0
    ),
    CONSTRAINT valid_assessment_score CHECK (
        ai_assessment_score IS NULL
        OR (
            ai_assessment_score >= 0
            AND ai_assessment_score <= 100
        )
    )
);
-- Family members table
CREATE TABLE family_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    applicant_id UUID NOT NULL REFERENCES applicants(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    relationship relationship_type NOT NULL,
    age INTEGER NOT NULL,
    emirates_id VARCHAR(15),
    has_income BOOLEAN DEFAULT FALSE,
    monthly_income DECIMAL(12, 2) DEFAULT 0.00,
    is_dependent BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- Constraints
    CONSTRAINT valid_age CHECK (
        age >= 0
        AND age <= 150
    ),
    CONSTRAINT valid_family_emirates_id CHECK (
        emirates_id IS NULL
        OR (
            LENGTH(emirates_id) = 15
            AND emirates_id ~ '^[0-9]+$'
        )
    ),
    CONSTRAINT valid_family_income CHECK (monthly_income >= 0)
);
-- Financial information table
CREATE TABLE financial_info (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    total_household_income DECIMAL(12, 2) DEFAULT 0.00,
    monthly_expenses DECIMAL(12, 2) DEFAULT 0.00,
    existing_debts DECIMAL(12, 2) DEFAULT 0.00,
    savings_amount DECIMAL(12, 2) DEFAULT 0.00,
    property_value DECIMAL(12, 2) DEFAULT 0.00,
    other_assets DECIMAL(12, 2) DEFAULT 0.00,
    net_worth DECIMAL(12, 2) GENERATED ALWAYS AS (
        savings_amount + property_value + other_assets - existing_debts
    ) STORED,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- Constraints
    CONSTRAINT valid_financial_amounts CHECK (
        total_household_income >= 0
        AND monthly_expenses >= 0
        AND existing_debts >= 0
        AND savings_amount >= 0
        AND property_value >= 0
        AND other_assets >= 0
    )
);
-- Banking information table
CREATE TABLE banking_info (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    bank_name VARCHAR(100),
    account_number VARCHAR(50),
    iban VARCHAR(34),
    has_bank_loan BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- Constraints
    CONSTRAINT valid_iban CHECK (
        iban IS NULL
        OR iban ~ '^[A-Z]{2}[0-9]{2}[A-Z0-9]+$'
    )
);
-- Emergency contacts table
CREATE TABLE emergency_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    relationship VARCHAR(100),
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    is_primary BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- Constraints
    CONSTRAINT valid_emergency_email CHECK (
        email IS NULL
        OR email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    ),
    CONSTRAINT valid_emergency_phone CHECK (phone ~ '^[+]?[0-9\s\-()]+$')
);
-- Documents table for uploaded files
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,
    document_purpose VARCHAR(100),
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processing_status VARCHAR(50) DEFAULT 'pending',
    processing_date TIMESTAMP WITH TIME ZONE,
    extracted_data JSONB,
    confidence_score DECIMAL(5, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- Constraints
    CONSTRAINT valid_file_size CHECK (
        file_size IS NULL
        OR file_size > 0
    ),
    CONSTRAINT valid_confidence_score CHECK (
        confidence_score IS NULL
        OR (
            confidence_score >= 0
            AND confidence_score <= 1
        )
    )
);
-- Assessment results table
CREATE TABLE assessment_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    assessment_type VARCHAR(50) NOT NULL,
    -- 'income', 'employment', 'family', 'wealth', 'demographic', 'comprehensive'
    assessment_score DECIMAL(5, 2) NOT NULL,
    assessment_details JSONB,
    recommendations TEXT [],
    risk_factors TEXT [],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- Constraints
    CONSTRAINT valid_assessment_score CHECK (
        assessment_score >= 0
        AND assessment_score <= 1
    )
);
-- Application status history table
CREATE TABLE application_status_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    old_status application_status,
    new_status application_status NOT NULL,
    changed_by VARCHAR(100),
    -- User ID or 'system' for automated changes
    change_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
-- Workflow execution logs
CREATE TABLE workflow_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    workflow_id VARCHAR(100) NOT NULL,
    workflow_status VARCHAR(50) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    documents_processed INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    warnings_count INTEGER DEFAULT 0,
    workflow_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
-- System audit log
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    operation VARCHAR(10) NOT NULL,
    -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
-- Create indexes for better performance
CREATE INDEX idx_applicants_emirates_id ON applicants(emirates_id);
CREATE INDEX idx_applicants_phone ON applicants(phone_number);
CREATE INDEX idx_applications_number ON applications(application_number);
CREATE INDEX idx_applications_status ON applications(application_status);
CREATE INDEX idx_applications_applicant ON applications(applicant_id);
CREATE INDEX idx_applications_submitted ON applications(submitted_at);
CREATE INDEX idx_family_members_applicant ON family_members(applicant_id);
CREATE INDEX idx_documents_application ON documents(application_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_assessment_results_application ON assessment_results(application_id);
CREATE INDEX idx_status_history_application ON application_status_history(application_id);
CREATE INDEX idx_workflow_logs_application ON workflow_logs(application_id);
CREATE INDEX idx_audit_log_table_record ON audit_log(table_name, record_id);
-- Create function to generate application number
CREATE OR REPLACE FUNCTION generate_application_number() RETURNS TEXT AS $$
DECLARE year_part TEXT;
sequence_part TEXT;
app_number TEXT;
BEGIN year_part := EXTRACT(
    YEAR
    FROM CURRENT_DATE
)::TEXT;
-- Get next sequence number for this year
SELECT LPAD((COUNT(*) + 1)::TEXT, 6, '0') INTO sequence_part
FROM applications
WHERE EXTRACT(
        YEAR
        FROM created_at
    ) = EXTRACT(
        YEAR
        FROM CURRENT_DATE
    );
app_number := 'APP-' || year_part || '-' || sequence_part;
RETURN app_number;
END;
$$ LANGUAGE plpgsql;
-- Create function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column() RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = CURRENT_TIMESTAMP;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
-- Create triggers for updated_at columns
CREATE TRIGGER update_applicants_updated_at BEFORE
UPDATE ON applicants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_addresses_updated_at BEFORE
UPDATE ON addresses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_employment_info_updated_at BEFORE
UPDATE ON employment_info FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_applications_updated_at BEFORE
UPDATE ON applications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_family_members_updated_at BEFORE
UPDATE ON family_members FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_financial_info_updated_at BEFORE
UPDATE ON financial_info FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_banking_info_updated_at BEFORE
UPDATE ON banking_info FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_emergency_contacts_updated_at BEFORE
UPDATE ON emergency_contacts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_documents_updated_at BEFORE
UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
-- Create trigger to auto-generate application number
CREATE OR REPLACE FUNCTION set_application_number() RETURNS TRIGGER AS $$ BEGIN IF NEW.application_number IS NULL THEN NEW.application_number := generate_application_number();
END IF;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER set_application_number_trigger BEFORE
INSERT ON applications FOR EACH ROW EXECUTE FUNCTION set_application_number();
-- Create audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger_function() RETURNS TRIGGER AS $$ BEGIN IF TG_OP = 'DELETE' THEN
INSERT INTO audit_log (
        table_name,
        record_id,
        operation,
        old_values,
        changed_by
    )
VALUES (
        TG_TABLE_NAME,
        OLD.id,
        TG_OP,
        row_to_json(OLD),
        current_user
    );
RETURN OLD;
ELSIF TG_OP = 'UPDATE' THEN
INSERT INTO audit_log (
        table_name,
        record_id,
        operation,
        old_values,
        new_values,
        changed_by
    )
VALUES (
        TG_TABLE_NAME,
        NEW.id,
        TG_OP,
        row_to_json(OLD),
        row_to_json(NEW),
        current_user
    );
RETURN NEW;
ELSIF TG_OP = 'INSERT' THEN
INSERT INTO audit_log (
        table_name,
        record_id,
        operation,
        new_values,
        changed_by
    )
VALUES (
        TG_TABLE_NAME,
        NEW.id,
        TG_OP,
        row_to_json(NEW),
        current_user
    );
RETURN NEW;
END IF;
RETURN NULL;
END;
$$ LANGUAGE plpgsql;
-- Create audit triggers for main tables
CREATE TRIGGER audit_applicants
AFTER
INSERT
    OR
UPDATE
    OR DELETE ON applicants FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
CREATE TRIGGER audit_applications
AFTER
INSERT
    OR
UPDATE
    OR DELETE ON applications FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
-- Create views for common queries
CREATE VIEW application_summary AS
SELECT a.id,
    a.application_number,
    ap.first_name || ' ' || ap.last_name AS applicant_name,
    ap.emirates_id,
    ap.phone_number,
    a.application_type,
    a.application_status,
    a.priority_level,
    a.requested_amount,
    a.approved_amount,
    a.support_duration,
    a.submitted_at,
    a.ai_assessment_score,
    a.human_review_required,
    addr.emirate,
    addr.city
FROM applications a
    JOIN applicants ap ON a.applicant_id = ap.id
    LEFT JOIN addresses addr ON ap.id = addr.applicant_id
    AND addr.is_current = TRUE;
CREATE VIEW family_summary AS
SELECT ap.id AS applicant_id,
    ap.first_name || ' ' || ap.last_name AS applicant_name,
    COUNT(fm.id) AS total_family_members,
    COUNT(
        CASE
            WHEN fm.is_dependent = TRUE THEN 1
        END
    ) AS dependents_count,
    SUM(
        CASE
            WHEN fm.has_income = TRUE THEN fm.monthly_income
            ELSE 0
        END
    ) AS family_income
FROM applicants ap
    LEFT JOIN family_members fm ON ap.id = fm.applicant_id
GROUP BY ap.id,
    ap.first_name,
    ap.last_name;
-- Grant permissions (adjust as needed for your user roles)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO social_security_app;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO social_security_app;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO social_security_app;