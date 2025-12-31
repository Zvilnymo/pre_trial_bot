import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards import reply
from bot.utils import messages
from services import user_service
from config import STAGE_MAPPING, STAGE_DESCRIPTIONS

logger = logging.getLogger(__name__)


async def show_roadmap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show client's roadmap (current stage)"""
    telegram_id = update.effective_user.id

    # Get user
    user = user_service.get_user(telegram_id)

    if not user:
        await update.message.reply_text(
            "Будь ласка, спочатку пройдіть реєстрацію (/start)",
            reply_markup=reply.get_start_keyboard()
        )
        return

    # Get current stage
    current_stage_bitrix = user.current_stage
    current_stage_display = STAGE_MAPPING.get(current_stage_bitrix, "Невідома стадія")
    stage_description = STAGE_DESCRIPTIONS.get(current_stage_display, "")

    # Build roadmap message
    stages = [
        "🎯 Стратегію розроблено",
        "🛡️ Ведемо переговори",
        "✅ Є перші результати",
        "⚡ Фінальний етап",
        "🏆 Справу завершено"
    ]

    roadmap_text = messages.ROADMAP_HEADER
    roadmap_text += f"**{current_stage_display}**\n"
    roadmap_text += f"_{stage_description}_\n\n"
    roadmap_text += "📍 ДОРОЖНЯ КАРТА:\n"

    for stage in stages:
        if stage == current_stage_display:
            roadmap_text += f"▶️ **{stage}** (ви тут)\n"
        else:
            roadmap_text += f"   {stage}\n"

    roadmap_text += "\n" + messages.ROADMAP_FOOTER

    await update.message.reply_text(
        roadmap_text,
        parse_mode='Markdown',
        reply_markup=reply.get_main_menu_keyboard()
    )
