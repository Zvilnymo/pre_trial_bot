from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_conference_registration_keyboard(conference_id: int):
    """Inline keyboard for conference registration"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Зареєструватися", callback_data=f"conf_register_{conference_id}"),
            InlineKeyboardButton("❌ Відхилити", callback_data=f"conf_decline_{conference_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_conference_manage_keyboard(conference_id: int):
    """Inline keyboard for managing conference (admin)"""
    keyboard = [
        [
            InlineKeyboardButton("👥 Учасники", callback_data=f"conf_participants_{conference_id}"),
            InlineKeyboardButton("📝 Редагувати", callback_data=f"conf_edit_{conference_id}")
        ],
        [
            InlineKeyboardButton("📢 Надіслати запрошення", callback_data=f"conf_invite_{conference_id}"),
            InlineKeyboardButton("❌ Видалити", callback_data=f"conf_delete_{conference_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_document_keyboard(document_index: int, is_required: bool):
    """Inline keyboard for document upload"""
    keyboard = [
        [InlineKeyboardButton("📤 Завантажити", callback_data=f"upload_doc_{document_index}")],
    ]

    if not is_required:
        keyboard.append([InlineKeyboardButton("⏭️ Пропустити", callback_data=f"skip_doc_{document_index}")])

    return InlineKeyboardMarkup(keyboard)


def get_document_upload_options():
    """Inline keyboard for document upload options"""
    keyboard = [
        [InlineKeyboardButton("✅ Завантажено", callback_data="doc_uploaded")],
        [InlineKeyboardButton("🔄 Завантажити інший", callback_data="doc_another")],
        [InlineKeyboardButton("❌ Скасувати", callback_data="doc_cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_pagination_keyboard(page: int, total_pages: int, prefix: str):
    """Generic pagination keyboard"""
    keyboard = []

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"{prefix}_page_{page-1}"))

    nav_buttons.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="noop"))

    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data=f"{prefix}_page_{page+1}"))

    if nav_buttons:
        keyboard.append(nav_buttons)

    return InlineKeyboardMarkup(keyboard)


def get_client_actions_keyboard(telegram_id: int):
    """Inline keyboard for admin actions on client"""
    keyboard = [
        [
            InlineKeyboardButton("💬 Написати", url=f"tg://user?id={telegram_id}"),
            InlineKeyboardButton("📊 Детальніше", callback_data=f"client_details_{telegram_id}")
        ],
        [
            InlineKeyboardButton("🚫 Вимкнути конференції", callback_data=f"client_disable_conf_{telegram_id}"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
