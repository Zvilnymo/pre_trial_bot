import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards import reply, inline
from bot.utils import messages
from bot.utils.document_packages import get_required_documents
from services import questionnaire_service, document_service, user_service
from integrations import google_drive_client

logger = logging.getLogger(__name__)


async def start_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start document upload process"""
    telegram_id = update.effective_user.id

    # Get user
    user = user_service.get_user(telegram_id)
    if not user:
        await update.message.reply_text("Будь ласка, спочатку пройдіть реєстрацію (/start)")
        return

    # Get questionnaire answers
    answers = questionnaire_service.get_answers(telegram_id)

    if not answers:
        await update.message.reply_text("Будь ласка, спочатку заповніть анкету")
        return

    # Get required documents based on answers
    required_docs = get_required_documents(answers)

    if not required_docs:
        await update.message.reply_text(
            "Не вдалося визначити необхідні документи. Зверніться до менеджера.",
            reply_markup=reply.get_main_menu_keyboard()
        )
        return

    # Save to context
    context.user_data['required_docs'] = required_docs
    context.user_data['current_doc_index'] = 0

    # Show document list
    doc_list = messages.DOCUMENTS_UPLOAD_START + "\n\n"

    for i, (doc_name, is_required) in enumerate(required_docs, 1):
        marker = "⭐" if is_required else "📋"
        doc_list += f"{i}. {marker} {doc_name}\n"

    await update.message.reply_text(
        doc_list,
        reply_markup=reply.get_main_menu_keyboard()
    )

    await update.message.reply_text(
        "Будь ласка, надсилайте документи по черзі.\nПідтримуються формати: PDF, JPG, PNG",
        reply_markup=reply.get_back_keyboard()
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document upload"""
    telegram_id = update.effective_user.id

    # Get user
    user = user_service.get_user(telegram_id)
    if not user or not user.google_drive_folder_id:
        await update.message.reply_text("Помилка: не знайдено папку на Google Drive")
        return

    # Get file
    if update.message.document:
        file = update.message.document
        file_name = file.file_name
    elif update.message.photo:
        file = update.message.photo[-1]
        file_name = f"photo_{file.file_id}.jpg"
    else:
        await update.message.reply_text("Непідтримуваний формат файлу")
        return

    try:
        # Download file
        telegram_file = await file.get_file()
        file_content = await telegram_file.download_as_bytearray()

        # Get documents folder ID
        with get_session() as session:
            from database import User
            user_obj = session.query(User).filter(User.telegram_id == telegram_id).first()

            if not user_obj:
                await update.message.reply_text("Помилка: користувача не знайдено")
                return

            # In real implementation, we need to get the documents subfolder ID
            # For now, use main folder
            folder_id = user_obj.google_drive_folder_id

        # Upload to Google Drive
        mime_type = file.mime_type if hasattr(file, 'mime_type') else 'application/octet-stream'
        google_file_id = google_drive_client.upload_file(
            bytes(file_content),
            file_name,
            folder_id,
            mime_type
        )

        if google_file_id:
            # Save to database
            document_service.save_document(
                telegram_id=telegram_id,
                document_type=file_name,
                file_name=file_name,
                google_drive_file_id=google_file_id
            )

            await update.message.reply_text(
                messages.DOCUMENT_UPLOADED.format(file_name),
                reply_markup=reply.get_main_menu_keyboard()
            )
        else:
            await update.message.reply_text("Помилка при завантаженні файлу")

    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        await update.message.reply_text(f"Помилка: {str(e)}")


from database import get_session
