import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import TELEGRAM_BOT_TOKEN, setup_logging, DEBUG

logger = logging.getLogger(__name__)


def setup_handlers(application: Application):
    """Setup all bot handlers"""

    # Import handlers
    from .handlers import registration

    # Registration handler (ConversationHandler)
    application.add_handler(registration.registration_handler)

    # Main menu commands
    from .handlers import main_menu
    application.add_handler(CommandHandler('help', main_menu.help_command))
    application.add_handler(MessageHandler(filters.Regex('^ℹ️ Довідка$'), main_menu.help_command))
    application.add_handler(MessageHandler(filters.Regex('^🏠 Головне меню$'), main_menu.main_menu_command))

    # Roadmap
    from .handlers import roadmap
    application.add_handler(CommandHandler('roadmap', roadmap.show_roadmap))
    application.add_handler(MessageHandler(filters.Regex('^📊 Моя дорожня карта$'), roadmap.show_roadmap))

    # Documents
    from .handlers import documents
    application.add_handler(MessageHandler(filters.Regex('^📤 Завантажити документи$'), documents.start_upload))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, documents.handle_document))

    # Conferences
    from .handlers import conferences
    application.add_handler(MessageHandler(filters.Regex('^📅 Конференції$'), conferences.show_conferences))
    application.add_handler(CallbackQueryHandler(conferences.handle_conference_callback, pattern='^conf_'))

    # Admin commands (через deep link)
    from .handlers import admin
    application.add_handler(CommandHandler('admin', admin.admin_start))
    application.add_handler(CallbackQueryHandler(admin.handle_admin_callback, pattern='^admin_'))

    # Questionnaire
    from .handlers import questionnaire
    application.add_handler(questionnaire.questionnaire_handler)

    logger.info("All handlers registered")


def main():
    """Main function to run bot in polling mode (for local development)"""
    setup_logging(DEBUG)

    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Setup handlers
    setup_handlers(application)

    # Initialize database
    from database import init_db
    init_db()

    # Run bot
    logger.info("Starting bot in polling mode...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    from telegram import Update
    main()
