-- Sample Data for Social Security Application System
-- This file contains sample data for testing and development

-- Insert sample applicants
INSERT INTO applicants (emirates_id, first_name, last_name, date_of_birth, gender, nationality, phone_number, email, education_level) VALUES
('784198912345678', 'Ahmed', 'Al Mansouri', '1985-03-15', 'Male', 'UAE', '+971501234567', 'ahmed.almansouri@email.com', 'Bachelor''s'),
('784198987654321', 'Fatima', 'Al Zahra', '1990-07-22', 'Female', 'UAE', '+971509876543', 'fatima.alzahra@email.com', 'Master''s'),
('784198911111111', 'Mohammed', 'Al Rashid', '1978-12-10', 'Male', 'UAE', '+971502222222', 'mohammed.alrashid@email.com', 'High School'),
('784198922222222', 'Aisha', 'Al Maktoum', '1992-05-18', 'Female', 'UAE', '+971503333333', 'aisha.almaktoum@email.com', 'Diploma'),
('784198933333333', 'Omar', 'Al Nahyan', '1965-09-25', 'Male', 'UAE', '+971504444444', 'omar.alnahyan@email.com', 'Secondary');

-- Insert addresses for applicants
INSERT INTO addresses (applicant_id, emirate, city, area, po_box, address_line) VALUES
((SELECT id FROM applicants WHERE emirates_id = '784198912345678'), 'Dubai', 'Dubai', 'Jumeirah', '12345', 'Villa 123, Jumeirah Beach Road, Dubai'),
((SELECT id FROM applicants WHERE emirates_id = '784198987654321'), 'Abu Dhabi', 'Abu Dhabi', 'Khalifa City', '54321', 'Apartment 45, Building 12, Khalifa City A'),
((SELECT id FROM applicants WHERE emirates_id = '784198911111111'), 'Sharjah', 'Sharjah', 'Al Nahda', '11111', 'House 78, Street 15, Al Nahda'),
((SELECT id FROM applicants WHERE emirates_id = '784198922222222'), 'Dubai', 'Dubai', 'Deira', '22222', 'Flat 203, Al Maktoum Building, Deira'),
((SELECT id FROM applicants WHERE emirates_id = '784198933333333'), 'Abu Dhabi', 'Al Ain', 'Al Jimi', '33333', 'Villa 56, Al Jimi District, Al Ain');

-- Insert employment information
INSERT INTO employment_info (applicant_id, employment_status, employer_name, job_title, monthly_income, years_of_experience, start_date) VALUES
((SELECT id FROM applicants WHERE emirates_id = '784198912345678'), 'Employed', 'Emirates Airlines', 'Senior Engineer', 15000.00, 8, '2016-01-15'),
((SELECT id FROM applicants WHERE emirates_id = '784198987654321'), 'Employed', 'ADNOC', 'Project Manager', 18000.00, 6, '2018-03-01'),
((SELECT id FROM applicants WHERE emirates_id = '784198911111111'), 'Unemployed', NULL, NULL, 0.00, 12, NULL),
((SELECT id FROM applicants WHERE emirates_id = '784198922222222'), 'Self-Employed', 'Freelance Consulting', 'Business Consultant', 8000.00, 4, '2020-06-01'),
((SELECT id FROM applicants WHERE emirates_id = '784198933333333'), 'Retired', 'Dubai Municipality', 'Former Supervisor', 5000.00, 35, NULL);

-- Insert sample applications
INSERT INTO applications (applicant_id, application_type, priority_level, requested_amount, support_duration, reason_for_application, additional_notes, application_status, submitted_at) VALUES
((SELECT id FROM applicants WHERE emirates_id = '784198912345678'), 'Family Support', 'Normal', 3000.00, '6 months', 'Need support for children education expenses due to recent medical bills', 'Have two children in private school', 'submitted', '2024-01-15 10:30:00'),
((SELECT id FROM applicants WHERE emirates_id = '784198987654321'), 'Regular Support', 'High', 5000.00, '12 months', 'Temporary financial difficulty due to job transition', 'Starting new position next month', 'under_review', '2024-01-20 14:15:00'),
((SELECT id FROM applicants WHERE emirates_id = '784198911111111'), 'Emergency Support', 'Emergency', 8000.00, '3 months', 'Lost job due to company closure, need immediate support for family', 'Have 4 dependents, actively looking for work', 'processing', '2024-01-25 09:45:00'),
((SELECT id FROM applicants WHERE emirates_id = '784198922222222'), 'Regular Support', 'Normal', 2500.00, '6 months', 'Business income reduced due to market conditions', 'Expecting business to recover in 6 months', 'approved', '2024-01-10 16:20:00'),
((SELECT id FROM applicants WHERE emirates_id = '784198933333333'), 'Elderly Support', 'High', 4000.00, 'Permanent', 'Retirement pension insufficient for medical expenses', 'Have chronic health conditions requiring regular treatment', 'approved', '2024-01-05 11:00:00');

-- Insert family members
INSERT INTO family_members (applicant_id, name, relationship, age, emirates_id, has_income, monthly_income, is_dependent) VALUES
-- Ahmed Al Mansouri's family
((SELECT id FROM applicants WHERE emirates_id = '784198912345678'), 'Mariam Al Mansouri', 'Spouse', 32, '784199012345678', false, 0.00, false),
((SELECT id FROM applicants WHERE emirates_id = '784198912345678'), 'Khalid Al Mansouri', 'Child', 8, NULL, false, 0.00, true),
((SELECT id FROM applicants WHERE emirates_id = '784198912345678'), 'Sara Al Mansouri', 'Child', 5, NULL, false, 0.00, true),

-- Fatima Al Zahra's family
((SELECT id FROM applicants WHERE emirates_id = '784198987654321'), 'Hassan Al Zahra', 'Spouse', 35, '784199087654321', true, 12000.00, false),
((SELECT id FROM applicants WHERE emirates_id = '784198987654321'), 'Layla Al Zahra', 'Child', 3, NULL, false, 0.00, true),

-- Mohammed Al Rashid's family
((SELECT id FROM applicants WHERE emirates_id = '784198911111111'), 'Khadija Al Rashid', 'Spouse', 42, '784199011111111', false, 0.00, false),
((SELECT id FROM applicants WHERE emirates_id = '784198911111111'), 'Ali Al Rashid', 'Child', 16, NULL, false, 0.00, true),
((SELECT id FROM applicants WHERE emirates_id = '784198911111111'), 'Noor Al Rashid', 'Child', 14, NULL, false, 0.00, true),
((SELECT id FROM applicants WHERE emirates_id = '784198911111111'), 'Yusuf Al Rashid', 'Child', 10, NULL, false, 0.00, true),
((SELECT id FROM applicants WHERE emirates_id = '784198911111111'), 'Amina Al Rashid', 'Child', 7, NULL, false, 0.00, true),

-- Aisha Al Maktoum's family
((SELECT id FROM applicants WHERE emirates_id = '784198922222222'), 'Rashid Al Maktoum', 'Child', 12, NULL, false, 0.00, true),

-- Omar Al Nahyan's family
((SELECT id FROM applicants WHERE emirates_id = '784198933333333'), 'Sheikha Al Nahyan', 'Spouse', 62, '784199033333333', false, 0.00, false);

-- Insert financial information for applications
INSERT INTO financial_info (application_id, total_household_income, monthly_expenses, existing_debts, savings_amount, property_value, other_assets) VALUES
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198912345678')), 15000.00, 12000.00, 50000.00, 25000.00, 800000.00, 15000.00),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198987654321')), 30000.00, 18000.00, 80000.00, 45000.00, 1200000.00, 25000.00),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198911111111')), 0.00, 8000.00, 120000.00, 5000.00, 600000.00, 8000.00),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198922222222')), 8000.00, 6000.00, 30000.00, 15000.00, 450000.00, 10000.00),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198933333333')), 5000.00, 7000.00, 20000.00, 35000.00, 900000.00, 20000.00);

-- Insert banking information
INSERT INTO banking_info (application_id, bank_name, account_number, iban, has_bank_loan) VALUES
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198912345678')), 'Emirates NBD', '1234567890', 'AE070331234567890123456', true),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198987654321')), 'ADCB', '2345678901', 'AE070332345678901234567', true),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198911111111')), 'FAB', '3456789012', 'AE070333456789012345678', false),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198922222222')), 'Mashreq Bank', '4567890123', 'AE070334567890123456789', false),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198933333333')), 'RAK Bank', '5678901234', 'AE070335678901234567890', false);

-- Insert emergency contacts
INSERT INTO emergency_contacts (application_id, name, relationship, phone, email) VALUES
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198912345678')), 'Salem Al Mansouri', 'Brother', '+971506666666', 'salem.almansouri@email.com'),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198987654321')), 'Maryam Al Zahra', 'Sister', '+971507777777', 'maryam.alzahra@email.com'),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198911111111')), 'Abdullah Al Rashid', 'Father', '+971508888888', 'abdullah.alrashid@email.com'),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198922222222')), 'Noura Al Maktoum', 'Mother', '+971509999999', 'noura.almaktoum@email.com'),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198933333333')), 'Khalifa Al Nahyan', 'Son', '+971501111111', 'khalifa.alnahyan@email.com');

-- Insert sample documents
INSERT INTO documents (application_id, document_type, document_purpose, file_name, file_path, file_size, mime_type, processing_status, confidence_score) VALUES
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198912345678')), 'pdf', 'emirates_id', 'ahmed_emirates_id.pdf', '/uploads/documents/ahmed_emirates_id.pdf', 2048576, 'application/pdf', 'processed', 0.95),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198912345678')), 'pdf', 'salary_certificate', 'ahmed_salary_cert.pdf', '/uploads/documents/ahmed_salary_cert.pdf', 1024768, 'application/pdf', 'processed', 0.88),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198987654321')), 'pdf', 'emirates_id', 'fatima_emirates_id.pdf', '/uploads/documents/fatima_emirates_id.pdf', 2156789, 'application/pdf', 'processed', 0.92),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198987654321')), 'xlsx', 'bank_statement', 'fatima_bank_statement.xlsx', '/uploads/documents/fatima_bank_statement.xlsx', 512345, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'processed', 0.90),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198911111111')), 'pdf', 'emirates_id', 'mohammed_emirates_id.pdf', '/uploads/documents/mohammed_emirates_id.pdf', 1987654, 'application/pdf', 'processed', 0.87);

-- Insert sample assessment results
INSERT INTO assessment_results (application_id, assessment_type, assessment_score, assessment_details, recommendations, risk_factors) VALUES
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198912345678')), 'comprehensive', 0.75, '{"income_score": 0.6, "employment_score": 0.8, "family_score": 0.9, "wealth_score": 0.7}', ARRAY['Approve for 6 months', 'Monitor employment stability'], ARRAY['High medical expenses', 'Dependent children']),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198987654321')), 'comprehensive', 0.82, '{"income_score": 0.9, "employment_score": 0.7, "family_score": 0.8, "wealth_score": 0.9}', ARRAY['Approve for 12 months', 'Provide job transition support'], ARRAY['Job transition period']),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198911111111')), 'comprehensive', 0.95, '{"income_score": 1.0, "employment_score": 1.0, "family_score": 1.0, "wealth_score": 0.8}', ARRAY['Approve emergency support', 'Provide job placement assistance'], ARRAY['Unemployment', 'Large family', 'Limited savings']),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198922222222')), 'comprehensive', 0.68, '{"income_score": 0.7, "employment_score": 0.6, "family_score": 0.7, "wealth_score": 0.7}', ARRAY['Approve for 6 months', 'Business recovery monitoring'], ARRAY['Self-employment income variability']),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198933333333')), 'comprehensive', 0.85, '{"income_score": 0.8, "employment_score": 0.9, "family_score": 0.8, "wealth_score": 0.9}', ARRAY['Approve permanent support', 'Healthcare assistance'], ARRAY['Age-related health issues', 'Fixed income']);

-- Insert application status history
INSERT INTO application_status_history (application_id, old_status, new_status, changed_by, change_reason) VALUES
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198912345678')), 'draft', 'submitted', 'applicant', 'Application submitted by applicant'),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198912345678')), 'submitted', 'under_review', 'system', 'Automatic status change after document upload'),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198987654321')), 'draft', 'submitted', 'applicant', 'Application submitted by applicant'),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198987654321')), 'submitted', 'under_review', 'system', 'AI assessment completed'),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198911111111')), 'draft', 'submitted', 'applicant', 'Emergency application submitted'),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198911111111')), 'submitted', 'processing', 'system', 'Fast-tracked due to emergency status'),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198922222222')), 'under_review', 'approved', 'admin_user', 'Manual approval after review'),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198933333333')), 'processing', 'approved', 'system', 'AI recommendation approved automatically');

-- Insert workflow logs
INSERT INTO workflow_logs (application_id, workflow_id, workflow_status, start_time, end_time, duration_seconds, documents_processed, errors_count, warnings_count, workflow_data) VALUES
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198912345678')), 'WF-20240115-001', 'completed', '2024-01-15 10:35:00', '2024-01-15 10:42:30', 450, 2, 0, 1, '{"documents": ["emirates_id", "salary_certificate"], "ai_confidence": 0.91}'),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198987654321')), 'WF-20240120-002', 'completed', '2024-01-20 14:20:00', '2024-01-20 14:28:15', 495, 2, 0, 0, '{"documents": ["emirates_id", "bank_statement"], "ai_confidence": 0.89}'),
((SELECT id FROM applications WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198911111111')), 'WF-20240125-003', 'completed', '2024-01-25 09:50:00', '2024-01-25 09:56:45', 405, 1, 0, 0, '{"documents": ["emirates_id"], "ai_confidence": 0.87, "priority": "emergency"}');

-- Update applications with AI assessment results
UPDATE applications SET 
    ai_assessment_score = 75.0,
    ai_assessment_status = 'approved',
    ai_assessment_date = '2024-01-15 10:42:30',
    human_review_required = false,
    approved_amount = 3000.00,
    approved_duration = '6 months'
WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198912345678');

UPDATE applications SET 
    ai_assessment_score = 82.0,
    ai_assessment_status = 'approved',
    ai_assessment_date = '2024-01-20 14:28:15',
    human_review_required = false,
    approved_amount = 5000.00,
    approved_duration = '12 months'
WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198987654321');

UPDATE applications SET 
    ai_assessment_score = 95.0,
    ai_assessment_status = 'approved',
    ai_assessment_date = '2024-01-25 09:56:45',
    human_review_required = false,
    approved_amount = 8000.00,
    approved_duration = '3 months'
WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198911111111');

UPDATE applications SET 
    ai_assessment_score = 68.0,
    ai_assessment_status = 'conditionally_approved',
    ai_assessment_date = '2024-01-10 16:25:00',
    human_review_required = true,
    approved_amount = 2500.00,
    approved_duration = '6 months'
WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198922222222');

UPDATE applications SET 
    ai_assessment_score = 85.0,
    ai_assessment_status = 'approved',
    ai_assessment_date = '2024-01-05 11:05:00',
    human_review_required = false,
    approved_amount = 4000.00,
    approved_duration = 'Permanent'
WHERE applicant_id = (SELECT id FROM applicants WHERE emirates_id = '784198933333333');