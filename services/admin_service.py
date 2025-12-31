"""Admin service for managing admin users"""
import logging
from typing import Optional
from sqlalchemy.orm import Session
from database.models import Admin
from database.connection import get_db

logger = logging.getLogger(__name__)


def is_admin(telegram_id: int) -> bool:
    """
    Check if user is an active admin

    Args:
        telegram_id: Telegram user ID

    Returns:
        True if user is an active admin, False otherwise
    """
    db = next(get_db())
    try:
        admin = db.query(Admin).filter(
            Admin.telegram_id == telegram_id,
            Admin.is_active == True
        ).first()
        return admin is not None
    finally:
        db.close()


def register_admin(telegram_id: int, full_name: Optional[str] = None, username: Optional[str] = None) -> Admin:
    """
    Register a new admin or update existing admin info

    Args:
        telegram_id: Telegram user ID
        full_name: User's full name
        username: User's Telegram username

    Returns:
        Admin object
    """
    db = next(get_db())
    try:
        # Check if admin already exists
        admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()

        if admin:
            # Update existing admin
            admin.full_name = full_name or admin.full_name
            admin.username = username or admin.username
            admin.is_active = True
            logger.info(f"Updated existing admin: {telegram_id}")
        else:
            # Create new admin
            admin = Admin(
                telegram_id=telegram_id,
                full_name=full_name,
                username=username,
                is_active=True
            )
            db.add(admin)
            logger.info(f"Registered new admin: {telegram_id}")

        db.commit()
        db.refresh(admin)
        return admin
    except Exception as e:
        db.rollback()
        logger.error(f"Error registering admin {telegram_id}: {e}")
        raise
    finally:
        db.close()


def deactivate_admin(telegram_id: int) -> bool:
    """
    Deactivate an admin

    Args:
        telegram_id: Telegram user ID

    Returns:
        True if admin was deactivated, False if not found
    """
    db = next(get_db())
    try:
        admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()

        if admin:
            admin.is_active = False
            db.commit()
            logger.info(f"Deactivated admin: {telegram_id}")
            return True

        return False
    except Exception as e:
        db.rollback()
        logger.error(f"Error deactivating admin {telegram_id}: {e}")
        raise
    finally:
        db.close()


def get_all_admins() -> list[Admin]:
    """
    Get all active admins

    Returns:
        List of Admin objects
    """
    db = next(get_db())
    try:
        admins = db.query(Admin).filter(Admin.is_active == True).all()
        return admins
    finally:
        db.close()
