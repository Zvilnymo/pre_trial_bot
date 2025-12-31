import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from bot.keyboards import reply
from bot.utils import messages
from bot.utils.messages import QUESTIONNAIRE_QUESTIONS
from bot.utils.document_packages import get_required_documents
from services import questionnaire_service, user_service
from integrations import google_drive_client, bitrix_client
from database import User, get_session

logger = logging.getLogger(__name__)

# Conversation states
ASKING_QUESTION = range(1)


async def start_questionnaire(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start questionnaire"""
    telegram_id = update.effective_user.id

    await update.message.reply_text(
        messages.QUESTIONNAIRE_START,
        reply_markup=reply.get_back_keyboard()
    )

    # Start with question 1
    context.user_data['current_question'] = 1
    await ask_question(update, context)

    return ASKING_QUESTION


async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask current question"""
    q_num = context.user_data.get('current_question', 1)

    if q_num > 15:
        return await finish_questionnaire(update, context)

    question_text = QUESTIONNAIRE_QUESTIONS[q_num - 1]

    # Questions 1-14 are yes/no
    if q_num <= 14:
        keyboard = reply.get_yes_no_keyboard()
        await update.message.reply_text(
            f"❓ Питання {q_num}/15:\n\n{question_text}",
            reply_markup=keyboard
        )
    else:
        # Question 15 is open text
        await update.message.reply_text(
            f"❓ Питання {q_num}/15:\n\n{question_text}",
            reply_markup=reply.get_back_keyboard()
        )

    return ASKING_QUESTION


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle answer to question"""
    telegram_id = update.effective_user.id
    q_num = context.user_data.get('current_question', 1)
    answer = update.message.text

    # Save answer
    questionnaire_service.save_answer(telegram_id, q_num, answer)

    # Update question 15 in Bitrix if it's the last question
    if q_num == 15:
        user = user_service.get_user(telegram_id)
        if user and user.bitrix_deal_id:
            bitrix_client.update_deal_custom_field(
                user.bitrix_deal_id,
                'UF_CRM_QUESTION_15',
                answer
            )

    # Move to next question
    context.user_data['current_question'] = q_num + 1

    return await ask_question(update, context)


async def finish_questionnaire(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Finish questionnaire and determine category"""
    telegram_id = update.effective_user.id

    # Get all answers
    answers = questionnaire_service.get_answers(telegram_id)

    # Determine client category
    category = questionnaire_service.determine_client_category(answers)

    # Update user category
    user_service.set_client_category(telegram_id, category)

    # Save questionnaire to Google Drive
    user = user_service.get_user(telegram_id)
    if user and user.google_drive_folder_id:
        answers_with_questions = questionnaire_service.get_answers_with_questions(telegram_id)
        google_drive_client.create_questionnaire_file(
            answers_with_questions,
            user.phone_number,
            user.google_drive_folder_id
        )

    await update.message.reply_text(
        messages.QUESTIONNAIRE_COMPLETE,
        reply_markup=reply.get_main_menu_keyboard()
    )

    # Start document upload process
    from .documents import start_upload
    await start_upload(update, context)

    return ConversationHandler.END


async def cancel_questionnaire(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel questionnaire"""
    await update.message.reply_text(
        "Анкетування скасовано.",
        reply_markup=reply.get_main_menu_keyboard()
    )
    return ConversationHandler.END


# Conversation handler
questionnaire_handler = ConversationHandler(
    entry_points=[
        CommandHandler('questionnaire', start_questionnaire)
    ],
    states={
        ASKING_QUESTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)
        ]
    },
    fallbacks=[
        CommandHandler('cancel', cancel_questionnaire),
        MessageHandler(filters.Regex('^🏠 Головне меню$'), cancel_questionnaire)
    ]
)
