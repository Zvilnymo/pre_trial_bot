"""
Main application file - runs both Flask webhook server and Telegram bot
"""
import logging
import asyncio
from threading import Thread
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application

from config import TELEGRAM_BOT_TOKEN, PORT, DEBUG, setup_logging
from config import STAGE_MAPPING, STAGE_DESCRIPTIONS
from database import init_db, get_session, User
from bot.main import setup_handlers

# Setup logging
setup_logging(DEBUG)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Global telegram application
telegram_app = None


def create_telegram_app():
    """Create and configure telegram application"""
    global telegram_app

    telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Setup all handlers
    setup_handlers(telegram_app)

    logger.info("Telegram application created")
    return telegram_app


def run_telegram_bot():
    """Run telegram bot in polling mode in separate thread"""
    logger.info("Starting Telegram bot in polling mode...")

    # Initialize database
    init_db()
    logger.info("Database initialized")

    # Create telegram app
    create_telegram_app()

    # Run polling
    telegram_app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


# Start telegram bot in background thread
bot_thread = Thread(target=run_telegram_bot, daemon=True)
bot_thread.start()


@app.route('/')
def index():
    """Health check"""
    return jsonify({
        'status': 'online',
        'service': 'Dosudebka Bot',
        'version': '1.0.0',
        'bot_running': telegram_app is not None
    })


@app.route('/bitrix-webhook', methods=['POST'])
def bitrix_webhook():
    """Handle Bitrix24 webhook for stage updates"""
    try:
        data = request.get_json()
        logger.info(f"Received Bitrix webhook: {data}")

        event = data.get('event')

        if event == 'ONCRMDEALUPDATE':
            deal_id = data['data']['FIELDS']['ID']
            new_stage = data['data']['FIELDS'].get('STAGE_ID')

            if new_stage:
                from services import user_service

                # Find user by deal_id
                with get_session() as db_session:
                    user = db_session.query(User).filter(User.bitrix_deal_id == int(deal_id)).first()

                    if user:
                        # Update stage in database
                        user_service.update_stage(user.telegram_id, new_stage)

                        # Send notification to user
                        from bot.utils import messages

                        stage_display = STAGE_MAPPING.get(new_stage, new_stage)
                        stage_desc = STAGE_DESCRIPTIONS.get(stage_display, '')

                        message = messages.STAGE_UPDATED.format(stage_display, stage_desc)

                        # Send message via telegram bot
                        if telegram_app:
                            asyncio.run(telegram_app.bot.send_message(
                                chat_id=user.telegram_id,
                                text=message
                            ))

                        logger.info(f"Stage updated for user {user.telegram_id}: {new_stage}")
                        return jsonify({'status': 'ok', 'message': 'Stage updated'}), 200

                logger.warning(f"User not found for deal_id: {deal_id}")
                return jsonify({'status': 'error', 'message': 'User not found'}), 404

        return jsonify({'status': 'ok'}), 200

    except Exception as e:
        logger.error(f"Error processing Bitrix webhook: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
