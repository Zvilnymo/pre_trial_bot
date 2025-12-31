import logging
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application
from config import TELEGRAM_BOT_TOKEN, WEBHOOK_URL, PORT, DEBUG, setup_logging
from database import init_db, get_session, User

# Setup logging
setup_logging(DEBUG)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Telegram bot application
telegram_app = None


def create_telegram_app():
    """Create and configure telegram application"""
    global telegram_app

    from bot.main import setup_handlers

    telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Setup handlers
    setup_handlers(telegram_app)

    logger.info("Telegram application created")
    return telegram_app


@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'service': 'Dosudebka Bot',
        'version': '1.0.0'
    })


@app.route(f'/telegram-webhook', methods=['POST'])
async def telegram_webhook():
    """Handle Telegram webhook"""
    try:
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        await telegram_app.process_update(update)
        return jsonify({'ok': True})
    except Exception as e:
        logger.error(f"Error processing telegram update: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/bitrix-webhook', methods=['POST'])
def bitrix_webhook():
    """Handle Bitrix24 webhook for stage updates"""
    try:
        data = request.get_json()
        logger.info(f"Received Bitrix webhook: {data}")

        # Extract deal info
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
                        # Update stage
                        user_service.update_stage(user.telegram_id, new_stage)

                        # Send notification to user
                        asyncio.create_task(send_stage_update_notification(user.telegram_id, new_stage))

                        logger.info(f"Updated stage for user {user.telegram_id} to {new_stage}")

        return jsonify({'ok': True})

    except Exception as e:
        logger.error(f"Error processing Bitrix webhook: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


async def send_stage_update_notification(telegram_id: int, new_stage: str):
    """Send stage update notification to user"""
    try:
        from config import STAGE_MAPPING, STAGE_DESCRIPTIONS
        from bot.utils import messages

        stage_display = STAGE_MAPPING.get(new_stage, new_stage)
        stage_desc = STAGE_DESCRIPTIONS.get(stage_display, '')

        message = messages.STAGE_UPDATED.format(stage_display, stage_desc)

        await telegram_app.bot.send_message(chat_id=telegram_id, text=message)
    except Exception as e:
        logger.error(f"Error sending stage update notification: {e}")


async def setup_webhook():
    """Setup Telegram webhook"""
    try:
        webhook_url = f"{WEBHOOK_URL}/telegram-webhook"
        await telegram_app.bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")


def run_async_setup():
    """Run async setup in event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup_webhook())
    loop.close()


# Initialize on startup
with app.app_context():
    # Initialize database
    init_db()
    logger.info("Database initialized")

    # Create telegram app
    create_telegram_app()

    # Setup webhook (only in production)
    if WEBHOOK_URL and not DEBUG:
        run_async_setup()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
