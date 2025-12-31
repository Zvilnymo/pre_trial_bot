import os
import io
import json
import logging
from typing import Optional, Dict, List
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaFileUpload
from config import GOOGLE_DRIVE_FOLDER_ID

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.file']


class GoogleDriveClient:
    def __init__(self):
        self.creds = None
        self.service = None
        self.main_folder_id = GOOGLE_DRIVE_FOLDER_ID
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Drive API using OAuth token from environment"""
        try:
            # ПРИОРИТЕТ 1: OAuth токен из переменной окружения (для production на Render.com)
            oauth_token = os.getenv('GOOGLE_OAUTH_TOKEN')

            if oauth_token:
                logger.info("Using OAuth token from environment variable")
                token_data = json.loads(oauth_token)

                self.creds = Credentials(
                    token=token_data.get('token'),
                    refresh_token=token_data.get('refresh_token'),
                    token_uri=token_data.get('token_uri'),
                    client_id=token_data.get('client_id'),
                    client_secret=token_data.get('client_secret'),
                    scopes=token_data.get('scopes', SCOPES)
                )

            # ПРИОРИТЕТ 2: Файл token.json (для локальной разработки)
            elif os.path.exists('token.json'):
                logger.info("Using token.json file for local development")
                self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)

            else:
                logger.error(
                    "Google Drive credentials not found!\n"
                    "For production: Set GOOGLE_OAUTH_TOKEN environment variable\n"
                    "For local development: Run 'python generate_oauth_token.py' to create token.json"
                )
                raise ValueError("Google Drive credentials not configured")

            # Обновление токена если истёк
            if self.creds.expired and self.creds.refresh_token:
                logger.info("Refreshing expired OAuth token")
                self.creds.refresh(Request())

                # Если токен из файла, сохраняем обновлённый
                if os.path.exists('token.json') and not oauth_token:
                    with open('token.json', 'w') as token:
                        token.write(self.creds.to_json())

            # Создание API сервиса
            self.service = build('drive', 'v3', credentials=self.creds)
            logger.info("Google Drive authenticated successfully")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in GOOGLE_OAUTH_TOKEN: {e}")
            raise
        except Exception as e:
            logger.error(f"Error authenticating with Google Drive: {e}")
            raise

    def create_folder(self, folder_name: str, parent_folder_id: str = None) -> Optional[str]:
        """Create folder in Google Drive"""
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id or self.main_folder_id]
            }

            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()

            folder_id = folder.get('id')
            logger.info(f"Created folder '{folder_name}' with ID: {folder_id}")
            return folder_id

        except Exception as e:
            logger.error(f"Error creating folder: {e}")
            return None

    def create_client_folder_structure(self, full_name: str, phone_number: str) -> Optional[Dict]:
        """
        Create folder structure for client:
        {ФИО}_{телефон}/
        └── documents/
        """
        try:
            # Create main client folder
            folder_name = f"{full_name}_{phone_number}"
            main_folder_id = self.create_folder(folder_name)

            if not main_folder_id:
                return None

            # Create documents subfolder
            docs_folder_id = self.create_folder('documents', main_folder_id)

            logger.info(f"Created folder structure for client: {folder_name}")

            return {
                'main_folder_id': main_folder_id,
                'documents_folder_id': docs_folder_id,
                'folder_name': folder_name
            }

        except Exception as e:
            logger.error(f"Error creating client folder structure: {e}")
            return None

    def upload_file(self, file_content: bytes, file_name: str, folder_id: str, mime_type: str = None) -> Optional[str]:
        """Upload file to Google Drive"""
        try:
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }

            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype=mime_type or 'application/octet-stream',
                resumable=True
            )

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            file_id = file.get('id')
            logger.info(f"Uploaded file '{file_name}' with ID: {file_id}")
            return file_id

        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return None

    def upload_text_file(self, content: str, file_name: str, folder_id: str) -> Optional[str]:
        """Upload text file to Google Drive"""
        try:
            file_content = content.encode('utf-8')
            return self.upload_file(file_content, file_name, folder_id, 'text/plain')
        except Exception as e:
            logger.error(f"Error uploading text file: {e}")
            return None

    def create_questionnaire_file(self, answers: List[tuple], phone: str, folder_id: str) -> Optional[str]:
        """
        Create anketa_{phone}.txt with questionnaire answers
        answers: list of (question_number, question_text, answer_text)
        """
        try:
            content = "АНКЕТА КЛІЄНТА\n"
            content += "=" * 50 + "\n\n"

            for q_num, q_text, answer in answers:
                content += f"{q_num}. {q_text}\n"
                content += f"Відповідь: {answer}\n\n"

            content += "=" * 50 + "\n"
            content += f"Телефон: {phone}\n"

            file_name = f"anketa_{phone}.txt"
            return self.upload_text_file(content, file_name, folder_id)

        except Exception as e:
            logger.error(f"Error creating questionnaire file: {e}")
            return None

    def get_folder_link(self, folder_id: str) -> str:
        """Get shareable link to folder"""
        return f"https://drive.google.com/drive/folders/{folder_id}"


# Singleton instance
google_drive_client = GoogleDriveClient()
