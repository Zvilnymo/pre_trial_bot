import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards import reply, inline
from services import user_service, conference_service
from services.admin_service import is_admin, register_admin
from config import ADMIN_TOKEN
from database import ClientCategory

logger = logging.getLogger(__name__)


async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin deep link"""
    telegram_id = update.effective_user.id
    user = update.effective_user

    # Check if started with admin token
    args = context.args

    if args and len(args) > 0:
        token = args[0].replace('admin_', '')

        if token == ADMIN_TOKEN:
            # Auto-register admin if they have valid token
            register_admin(
                telegram_id=telegram_id,
                full_name=user.full_name,
                username=user.username
            )

            await update.message.reply_text(
                "🔐 Ласкаво просимо до адмін-панелі!\n\nВи додані як адміністратор.\n\nОберіть дію:",
                reply_markup=reply.get_admin_menu_keyboard()
            )
            return

    # Regular admin command (for existing admins)
    if not is_admin(telegram_id):
        await update.message.reply_text("❌ У вас немає доступу до адмін-панелі.")
        return

    await update.message.reply_text(
        "🔐 Адмін-панель\n\nОберіть дію:",
        reply_markup=reply.get_admin_menu_keyboard()
    )


async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin callbacks"""
    query = update.callback_query
    telegram_id = update.effective_user.id

    if not is_admin(telegram_id):
        await query.answer("Немає доступу", show_alert=True)
        return

    await query.answer()

    # Handle different admin actions
    data = query.data

    if data.startswith('client_disable_conf_'):
        client_id = int(data.replace('client_disable_conf_', ''))
        user_service.toggle_conference_disabled(client_id, True)
        await query.edit_message_text(f"✅ Конференції вимкнено для користувача {client_id}")

    # Add more admin callbacks as needed
