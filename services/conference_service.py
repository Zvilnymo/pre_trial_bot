import logging
from typing import Optional, List
from datetime import datetime
from database import Conference, ConferenceRegistration, get_session, ClientCategory
from services.user_service import user_service

logger = logging.getLogger(__name__)


class ConferenceService:
    @staticmethod
    def create_conference(title: str, description: str, date_time: datetime,
                          zoom_link: str, max_participants: int = 100) -> Optional[Conference]:
        """Create new conference"""
        try:
            with get_session() as session:
                conference = Conference(
                    title=title,
                    description=description,
                    date_time=date_time,
                    zoom_link=zoom_link,
                    max_participants=max_participants
                )
                session.add(conference)
                session.commit()
                session.refresh(conference)
                logger.info(f"Created conference: {title}")
                return conference
        except Exception as e:
            logger.error(f"Error creating conference: {e}")
            return None

    @staticmethod
    def get_conference(conference_id: int) -> Optional[Conference]:
        """Get conference by ID"""
        try:
            with get_session() as session:
                conference = session.query(Conference).filter(
                    Conference.id == conference_id
                ).first()
                return conference
        except Exception as e:
            logger.error(f"Error getting conference: {e}")
            return None

    @staticmethod
    def get_active_conferences() -> List[Conference]:
        """Get all active conferences"""
        try:
            with get_session() as session:
                conferences = session.query(Conference).filter(
                    Conference.is_active == True,
                    Conference.date_time > datetime.utcnow()
                ).order_by(Conference.date_time).all()
                return conferences
        except Exception as e:
            logger.error(f"Error getting active conferences: {e}")
            return []

    @staticmethod
    def register_user(conference_id: int, telegram_id: int) -> bool:
        """Register user for conference"""
        try:
            with get_session() as session:
                # Check if already registered
                existing = session.query(ConferenceRegistration).filter(
                    ConferenceRegistration.conference_id == conference_id,
                    ConferenceRegistration.telegram_id == telegram_id
                ).first()

                if existing:
                    logger.info(f"User {telegram_id} already registered for conference {conference_id}")
                    return True

                # Create registration
                registration = ConferenceRegistration(
                    conference_id=conference_id,
                    telegram_id=telegram_id
                )
                session.add(registration)
                session.commit()
                logger.info(f"Registered user {telegram_id} for conference {conference_id}")
                return True
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return False

    @staticmethod
    def is_user_registered(conference_id: int, telegram_id: int) -> bool:
        """Check if user is registered for conference"""
        try:
            with get_session() as session:
                exists = session.query(ConferenceRegistration).filter(
                    ConferenceRegistration.conference_id == conference_id,
                    ConferenceRegistration.telegram_id == telegram_id
                ).first() is not None
                return exists
        except Exception as e:
            logger.error(f"Error checking registration: {e}")
            return False

    @staticmethod
    def get_conference_participants(conference_id: int) -> List[ConferenceRegistration]:
        """Get all participants for conference"""
        try:
            with get_session() as session:
                participants = session.query(ConferenceRegistration).filter(
                    ConferenceRegistration.conference_id == conference_id
                ).all()
                return participants
        except Exception as e:
            logger.error(f"Error getting participants: {e}")
            return []

    @staticmethod
    def get_participants_count(conference_id: int) -> int:
        """Get count of participants for conference"""
        try:
            with get_session() as session:
                count = session.query(ConferenceRegistration).filter(
                    ConferenceRegistration.conference_id == conference_id
                ).count()
                return count
        except Exception as e:
            logger.error(f"Error getting participants count: {e}")
            return 0

    @staticmethod
    def mark_attendance(conference_id: int, telegram_id: int) -> bool:
        """Mark user as attended"""
        try:
            with get_session() as session:
                registration = session.query(ConferenceRegistration).filter(
                    ConferenceRegistration.conference_id == conference_id,
                    ConferenceRegistration.telegram_id == telegram_id
                ).first()

                if not registration:
                    return False

                registration.attended = True
                session.commit()
                logger.info(f"Marked attendance for user {telegram_id} at conference {conference_id}")
                return True
        except Exception as e:
            logger.error(f"Error marking attendance: {e}")
            return False

    @staticmethod
    def delete_conference(conference_id: int) -> bool:
        """Delete conference"""
        try:
            with get_session() as session:
                conference = session.query(Conference).filter(
                    Conference.id == conference_id
                ).first()

                if not conference:
                    return False

                session.delete(conference)
                session.commit()
                logger.info(f"Deleted conference {conference_id}")
                return True
        except Exception as e:
            logger.error(f"Error deleting conference: {e}")
            return False


conference_service = ConferenceService()
