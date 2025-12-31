import logging
from typing import Optional, List
from database import Document, get_session

logger = logging.getLogger(__name__)


class DocumentService:
    @staticmethod
    def save_document(telegram_id: int, document_type: str, file_name: str,
                      google_drive_file_id: str = None) -> Optional[Document]:
        """Save document record"""
        try:
            with get_session() as session:
                document = Document(
                    telegram_id=telegram_id,
                    document_type=document_type,
                    file_name=file_name,
                    google_drive_file_id=google_drive_file_id
                )
                session.add(document)
                session.commit()
                session.refresh(document)
                logger.info(f"Saved document for user {telegram_id}: {document_type}")
                return document
        except Exception as e:
            logger.error(f"Error saving document: {e}")
            return None

    @staticmethod
    def get_user_documents(telegram_id: int) -> List[Document]:
        """Get all documents for user"""
        try:
            with get_session() as session:
                documents = session.query(Document).filter(
                    Document.telegram_id == telegram_id
                ).order_by(Document.upload_date).all()
                return documents
        except Exception as e:
            logger.error(f"Error getting documents: {e}")
            return []

    @staticmethod
    def get_document_count(telegram_id: int) -> int:
        """Get count of uploaded documents for user"""
        try:
            with get_session() as session:
                count = session.query(Document).filter(
                    Document.telegram_id == telegram_id
                ).count()
                return count
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0

    @staticmethod
    def document_exists(telegram_id: int, document_type: str) -> bool:
        """Check if specific document type already uploaded"""
        try:
            with get_session() as session:
                exists = session.query(Document).filter(
                    Document.telegram_id == telegram_id,
                    Document.document_type == document_type
                ).first() is not None
                return exists
        except Exception as e:
            logger.error(f"Error checking document existence: {e}")
            return False


document_service = DocumentService()
