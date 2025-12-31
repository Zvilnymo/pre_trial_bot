import logging
from typing import Optional
from database import User, get_session, ClientCategory
from datetime import datetime

logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    def create_user(telegram_id: int, full_name: str, phone_number: str,
                    bitrix_contact_id: int = None, bitrix_deal_id: int = None,
                    current_stage: str = None) -> Optional[User]:
        """Create new user"""
        try:
            with get_session() as session:
                user = User(
                    telegram_id=telegram_id,
                    full_name=full_name,
                    phone_number=phone_number,
                    bitrix_contact_id=bitrix_contact_id,
                    bitrix_deal_id=bitrix_deal_id,
                    current_stage=current_stage,
                    registration_date=datetime.utcnow()
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                logger.info(f"Created user: {telegram_id}")
                return user
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

    @staticmethod
    def get_user(telegram_id: int) -> Optional[User]:
        """Get user by telegram_id"""
        try:
            with get_session() as session:
                user = session.query(User).filter(User.telegram_id == telegram_id).first()
                return user
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    @staticmethod
    def get_user_by_phone(phone_number: str) -> Optional[User]:
        """Get user by phone number"""
        try:
            with get_session() as session:
                user = session.query(User).filter(User.phone_number == phone_number).first()
                return user
        except Exception as e:
            logger.error(f"Error getting user by phone: {e}")
            return None

    @staticmethod
    def update_user(telegram_id: int, **kwargs) -> bool:
        """Update user fields"""
        try:
            with get_session() as session:
                user = session.query(User).filter(User.telegram_id == telegram_id).first()
                if not user:
                    return False

                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)

                session.commit()
                logger.info(f"Updated user {telegram_id}: {kwargs}")
                return True
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False

    @staticmethod
    def update_stage(telegram_id: int, new_stage: str) -> bool:
        """Update user's current stage"""
        return UserService.update_user(telegram_id, current_stage=new_stage)

    @staticmethod
    def set_client_category(telegram_id: int, category: ClientCategory) -> bool:
        """Set client category (CRYPTO, MFO, BANK)"""
        return UserService.update_user(telegram_id, client_category=category)

    @staticmethod
    def set_google_folder(telegram_id: int, folder_id: str) -> bool:
        """Set Google Drive folder ID for user"""
        return UserService.update_user(telegram_id, google_drive_folder_id=folder_id)

    @staticmethod
    def toggle_conference_disabled(telegram_id: int, disabled: bool) -> bool:
        """Enable/disable conference invitations for user"""
        return UserService.update_user(telegram_id, conference_disabled=disabled)

    @staticmethod
    def toggle_financial_push(telegram_id: int, enabled: bool) -> bool:
        """Enable/disable financial push notifications for user"""
        return UserService.update_user(telegram_id, financial_push_enabled=enabled)

    @staticmethod
    def get_all_users(category: ClientCategory = None) -> list:
        """Get all users, optionally filtered by category"""
        try:
            with get_session() as session:
                query = session.query(User)

                if category:
                    query = query.filter(User.client_category == category)

                users = query.all()
                return users
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

    @staticmethod
    def get_users_for_conferences(category: ClientCategory = None) -> list:
        """Get users eligible for conference invitations"""
        try:
            with get_session() as session:
                query = session.query(User).filter(User.conference_disabled == False)

                if category:
                    query = query.filter(User.client_category == category)

                users = query.all()
                return users
        except Exception as e:
            logger.error(f"Error getting users for conferences: {e}")
            return []

    @staticmethod
    def get_user_count() -> int:
        """Get total user count"""
        try:
            with get_session() as session:
                count = session.query(User).count()
                return count
        except Exception as e:
            logger.error(f"Error getting user count: {e}")
            return 0

    @staticmethod
    def user_exists(telegram_id: int) -> bool:
        """Check if user exists"""
        return UserService.get_user(telegram_id) is not None


user_service = UserService()
