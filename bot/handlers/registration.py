import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from bot.keyboards import reply
from bot.utils import validators, messages
from bot.utils.validators import sanitize_folder_name
from services import user_service
from integrations import bitrix_client, google_drive_client
from config import STAGE_MAPPING

logger = logging.getLogger(__name__)

# Conversation states
AWAITING_NAME, AWAITING_PHONE = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    telegram_id = update.effective_user.id

    # Check if user is already registered
    if user_service.user_exists(telegram_id):
        await update.message.reply_text(
            "Ви вже зареєстровані! Використовуйте меню для навігації.",
            reply_markup=reply.get_main_menu_keyboard()
        )
        return ConversationHandler.END

    # Show welcome message
    await update.message.reply_text(
        messages.WELCOME_MESSAGE,
        reply_markup=reply.get_start_keyboard()
    )

    return AWAITING_NAME


async def request_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Request full name from user"""
    await update.message.reply_text(
        messages.REQUEST_FULL_NAME,
        reply_markup=reply.get_back_keyboard()
    )
    return AWAITING_PHONE


async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle full name input"""
    full_name = update.message.text.strip()

    # Validate name
    is_valid, error_msg = validators.validate_full_name(full_name)

    if not is_valid:
        await update.message.reply_text(error_msg)
        return AWAITING_PHONE

    # Save name in context
    context.user_data['full_name'] = full_name

    # Request phone number
    await update.message.reply_text(messages.REQUEST_PHONE)

    return AWAITING_PHONE


async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle phone number input and complete registration"""
    phone = update.message.text.strip()
    telegram_id = update.effective_user.id

    # Validate phone
    is_valid, cleaned_phone, error_msg = validators.validate_phone_number(phone)

    if not is_valid:
        await update.message.reply_text(error_msg)
        return AWAITING_PHONE

    full_name = context.user_data.get('full_name', '')

    # Show syncing message
    await update.message.reply_text(messages.SYNCING_DATA)

    # Search in Bitrix24
    try:
        bitrix_data = bitrix_client.find_client_in_funnel(cleaned_phone)

        if not bitrix_data:
            await update.message.reply_text(
                messages.CLIENT_NOT_FOUND,
                reply_markup=reply.get_back_keyboard()
            )
            return ConversationHandler.END

        # Create user in database
        user = user_service.create_user(
            telegram_id=telegram_id,
            full_name=full_name,
            phone_number=cleaned_phone,
            bitrix_contact_id=bitrix_data['contact_id'],
            bitrix_deal_id=bitrix_data['deal_id'],
            current_stage=bitrix_data['current_stage']
        )

        if not user:
            await update.message.reply_text(
                "❌ Помилка при збереженні даних. Спробуйте пізніше."
            )
            return ConversationHandler.END

        # Create Google Drive folder structure
        folder_structure = google_drive_client.create_client_folder_structure(
            sanitize_folder_name(full_name),
            cleaned_phone.replace('+', '')
        )

        if folder_structure:
            user_service.set_google_folder(telegram_id, folder_structure['main_folder_id'])
            logger.info(f"Created Google Drive folder for user {telegram_id}")

        # Registration success
        await update.message.reply_text(messages.REGISTRATION_SUCCESS)

        # Import here to avoid circular import
        from .questionnaire import start_questionnaire
        await start_questionnaire(update, context)

        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Error during registration: {e}")
        await update.message.reply_text(
            "❌ Виникла помилка. Будь ласка, спробуйте пізніше."
        )
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel registration"""
    await update.message.reply_text(
        "Реєстрацію скасовано. Натисніть /start для початку.",
        reply_markup=reply.get_start_keyboard()
    )
    return ConversationHandler.END


# Create conversation handler
registration_handler = ConversationHandler(
    entry_points=[
        CommandHandler('start', start),
        MessageHandler(filters.Regex('^Розпочати реєстрацію$'), request_name)
    ],
    states={
        AWAITING_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)
        ],
        AWAITING_PHONE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone)
        ]
    },
    fallbacks=[
        CommandHandler('cancel', cancel),
        MessageHandler(filters.Regex('^🏠 Головне меню$'), cancel)
    ]
)
