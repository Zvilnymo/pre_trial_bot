import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards import reply
from bot.utils import messages

logger = logging.getLogger(__name__)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    await update.message.reply_text(
        messages.HELP_MESSAGE,
        reply_markup=reply.get_main_menu_keyboard()
    )


async def main_menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu"""
    await update.message.reply_text(
        messages.MAIN_MENU_TEXT,
        reply_markup=reply.get_main_menu_keyboard()
    )
