-- Dosudebka Bot Database Schema
-- PostgreSQL

-- Users table
CREATE TABLE IF NOT EXISTS users (
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
CREATE TABLE IF NOT EXISTS questionnaire_answers (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    question_number INTEGER NOT NULL,
    answer_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    document_type VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    google_drive_file_id VARCHAR(255),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_validated BOOLEAN DEFAULT FALSE
);

-- Conferences table
CREATE TABLE IF NOT EXISTS conferences (
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
CREATE TABLE IF NOT EXISTS conference_registrations (
    id SERIAL PRIMARY KEY,
    conference_id INTEGER NOT NULL REFERENCES conferences(id) ON DELETE CASCADE,
    telegram_id BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    attended BOOLEAN DEFAULT FALSE,
    UNIQUE(conference_id, telegram_id)
);

-- Scheduled messages table
CREATE TABLE IF NOT EXISTS scheduled_messages (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    message_type VARCHAR(50) NOT NULL,
    scheduled_for TIMESTAMP NOT NULL,
    sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number);
CREATE INDEX IF NOT EXISTS idx_users_category ON users(client_category);
CREATE INDEX IF NOT EXISTS idx_questionnaire_user ON questionnaire_answers(telegram_id);
CREATE INDEX IF NOT EXISTS idx_documents_user ON documents(telegram_id);
CREATE INDEX IF NOT EXISTS idx_conferences_datetime ON conferences(date_time);
CREATE INDEX IF NOT EXISTS idx_conference_regs_conf ON conference_registrations(conference_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_msgs_sent ON scheduled_messages(sent, scheduled_for);
