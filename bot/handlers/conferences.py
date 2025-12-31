import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards import reply, inline
from bot.utils import messages
from services import conference_service, user_service
from datetime import datetime

logger = logging.getLogger(__name__)


async def show_conferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of active conferences"""
    telegram_id = update.effective_user.id

    # Get active conferences
    conferences = conference_service.get_active_conferences()

    if not conferences:
        await update.message.reply_text(
            "Наразі немає запланованих конференцій.\nМи повідомимо вас, коли з'явиться нова!",
            reply_markup=reply.get_main_menu_keyboard()
        )
        return

    await update.message.reply_text(
        "📅 ЗАПЛ АНОВАНІ КОНФЕРЕНЦІЇ:",
        reply_markup=reply.get_main_menu_keyboard()
    )

    for conf in conferences:
        is_registered = conference_service.is_user_registered(conf.id, telegram_id)
        participants_count = conference_service.get_participants_count(conf.id)

        message = messages.CONFERENCE_INVITATION.format(
            conf.title,
            conf.date_time.strftime("%d.%m.%Y о %H:%M"),
            conf.zoom_link,
            conf.description or ""
        )

        message += f"\n\n👥 Зареєстровано: {participants_count}/{conf.max_participants}"

        if is_registered:
            message += "\n✅ Ви вже зареєстровані"
            await update.message.reply_text(message)
        else:
            keyboard = inline.get_conference_registration_keyboard(conf.id)
            await update.message.reply_text(message, reply_markup=keyboard)


async def handle_conference_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle conference-related callbacks"""
    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id
    data = query.data

    if data.startswith('conf_register_'):
        conference_id = int(data.replace('conf_register_', ''))

        # Register user
        success = conference_service.register_user(conference_id, telegram_id)

        if success:
            # Update conference attendance flag
            user_service.update_user(telegram_id, conference_attended=True)

            await query.edit_message_text(
                messages.CONFERENCE_REGISTERED
            )
        else:
            await query.edit_message_text("Помилка при реєстрації. Спробуйте пізніше.")

    elif data.startswith('conf_decline_'):
        await query.edit_message_text("Дякуємо за відповідь!")
