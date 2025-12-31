"""
Minimal Flask server for receiving Bitrix24 webhooks
Runs separately from the bot in polling mode
"""
import logging
from flask import Flask, request, jsonify
from config import PORT, DEBUG, setup_logging
from database import get_session, User

setup_logging(DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/')
def index():
    """Health check"""
    return jsonify({
        'status': 'online',
        'service': 'Dosudebka Bot Webhook Server',
        'version': '1.0.0'
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

                        # Send notification to user via bot
                        from bot.utils import messages
                        from config import STAGE_MAPPING, STAGE_DESCRIPTIONS

                        stage_display = STAGE_MAPPING.get(new_stage, new_stage)
                        stage_desc = STAGE_DESCRIPTIONS.get(stage_display, '')

                        message = messages.STAGE_UPDATED.format(stage_display, stage_desc)

                        # Send via Telegram bot API directly
                        import requests as req
                        from config import TELEGRAM_BOT_TOKEN

                        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                        req.post(telegram_url, json={
                            'chat_id': user.telegram_id,
                            'text': message
                        })

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
