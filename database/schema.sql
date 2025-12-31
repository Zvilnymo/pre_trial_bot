-- Dosudebka Bot Database Schema
-- PostgreSQL

-- Create schema
CREATE SCHEMA IF NOT EXISTS pretrial;

-- Set search path
SET search_path TO pretrial;

-- Users table
CREATE TABLE IF NOT EXISTS pretrial.pt_users (
    telegram_id BIGINT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    bitrix_contact_id INTEGER,
    bitrix_deal_id INTEGER,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    current_stage VARCHAR(50),
    client_category VARCHAR(20),
    conference_attended BOOLEAN DEFAULT FALSE,
    conference_disabled BOOLEAN DEFAULT FALSE,
    financial_push_enabled BOOLEAN DEFAULT FALSE,
    google_drive_folder_id VARCHAR(255)
);

-- Questionnaire answers table
CREATE TABLE IF NOT EXISTS pretrial.pt_questionnaire_answers (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL REFERENCES pretrial.pt_users(telegram_id) ON DELETE CASCADE,
    question_number INTEGER NOT NULL,
    answer_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents table
CREATE TABLE IF NOT EXISTS pretrial.pt_documents (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL REFERENCES pretrial.pt_users(telegram_id) ON DELETE CASCADE,
    document_type VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    google_drive_file_id VARCHAR(255),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_validated BOOLEAN DEFAULT FALSE
);

-- Conferences table
CREATE TABLE IF NOT EXISTS pretrial.pt_conferences (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    date_time TIMESTAMP NOT NULL,
    zoom_link VARCHAR(500) NOT NULL,
    max_participants INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Conference registrations table
CREATE TABLE IF NOT EXISTS pretrial.pt_conference_registrations (
    id SERIAL PRIMARY KEY,
    conference_id INTEGER NOT NULL REFERENCES pretrial.pt_conferences(id) ON DELETE CASCADE,
    telegram_id BIGINT NOT NULL REFERENCES pretrial.pt_users(telegram_id) ON DELETE CASCADE,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    attended BOOLEAN DEFAULT FALSE,
    UNIQUE(conference_id, telegram_id)
);

-- Scheduled messages table
CREATE TABLE IF NOT EXISTS pretrial.pt_scheduled_messages (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    message_type VARCHAR(50) NOT NULL,
    scheduled_for TIMESTAMP NOT NULL,
    sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_pt_users_phone ON pretrial.pt_users(phone_number);
CREATE INDEX IF NOT EXISTS idx_pt_users_category ON pretrial.pt_users(client_category);
CREATE INDEX IF NOT EXISTS idx_pt_questionnaire_user ON pretrial.pt_questionnaire_answers(telegram_id);
CREATE INDEX IF NOT EXISTS idx_pt_documents_user ON pretrial.pt_documents(telegram_id);
CREATE INDEX IF NOT EXISTS idx_pt_conferences_datetime ON pretrial.pt_conferences(date_time);
CREATE INDEX IF NOT EXISTS idx_pt_conference_regs_conf ON pretrial.pt_conference_registrations(conference_id);
CREATE INDEX IF NOT EXISTS idx_pt_scheduled_msgs_sent ON pretrial.pt_scheduled_messages(sent, scheduled_for);

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON SCHEMA pretrial TO your_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA pretrial TO your_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA pretrial TO your_user;
