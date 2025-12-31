from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class ClientCategory(enum.Enum):
    CRYPTO = 'CRYPTO'
    MFO = 'MFO'
    BANK = 'BANK'


class User(Base):
    __tablename__ = 'users'

    telegram_id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False, unique=True)
    bitrix_contact_id = Column(Integer, nullable=True)
    bitrix_deal_id = Column(Integer, nullable=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    current_stage = Column(String(50), nullable=True)
    client_category = Column(Enum(ClientCategory), nullable=True)
    conference_attended = Column(Boolean, default=False)
    conference_disabled = Column(Boolean, default=False)
    financial_push_enabled = Column(Boolean, default=False)
    google_drive_folder_id = Column(String(255), nullable=True)

    # Relationships
    questionnaire_answers = relationship('QuestionnaireAnswer', back_populates='user', cascade='all, delete-orphan')
    documents = relationship('Document', back_populates='user', cascade='all, delete-orphan')
    conference_registrations = relationship('ConferenceRegistration', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, full_name='{self.full_name}', phone='{self.phone_number}')>"


class QuestionnaireAnswer(Base):
    __tablename__ = 'questionnaire_answers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)
    question_number = Column(Integer, nullable=False)
    answer_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship('User', back_populates='questionnaire_answers')

    def __repr__(self):
        return f"<QuestionnaireAnswer(user={self.telegram_id}, q={self.question_number})>"


class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)
    document_type = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    google_drive_file_id = Column(String(255), nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    is_validated = Column(Boolean, default=False)

    # Relationship
    user = relationship('User', back_populates='documents')

    def __repr__(self):
        return f"<Document(user={self.telegram_id}, type='{self.document_type}')>"


class Conference(Base):
    __tablename__ = 'conferences'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    date_time = Column(DateTime, nullable=False)
    zoom_link = Column(String(500), nullable=False)
    max_participants = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationship
    registrations = relationship('ConferenceRegistration', back_populates='conference', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Conference(id={self.id}, title='{self.title}')>"


class ConferenceRegistration(Base):
    __tablename__ = 'conference_registrations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    conference_id = Column(Integer, ForeignKey('conferences.id'), nullable=False)
    telegram_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)
    attended = Column(Boolean, default=False)

    # Relationships
    conference = relationship('Conference', back_populates='registrations')
    user = relationship('User', back_populates='conference_registrations')

    def __repr__(self):
        return f"<ConferenceRegistration(conf={self.conference_id}, user={self.telegram_id})>"


class ScheduledMessage(Base):
    __tablename__ = 'scheduled_messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, nullable=False)
    message_type = Column(String(50), nullable=False)
    scheduled_for = Column(DateTime, nullable=False)
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<ScheduledMessage(type='{self.message_type}', user={self.telegram_id})>"
