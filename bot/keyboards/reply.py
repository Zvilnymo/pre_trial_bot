from telegram import ReplyKeyboardMarkup, KeyboardButton


def get_start_keyboard():
    """Keyboard for starting registration"""
    keyboard = [
        [KeyboardButton("Розпочати реєстрацію")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_yes_no_keyboard():
    """Keyboard for yes/no questions"""
    keyboard = [
        [KeyboardButton("Так"), KeyboardButton("Ні")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


def get_main_menu_keyboard():
    """Main menu keyboard for clients"""
    keyboard = [
        [KeyboardButton("📊 Моя дорожня карта")],
        [KeyboardButton("📤 Завантажити документи")],
        [KeyboardButton("📅 Конференції")],
        [KeyboardButton("ℹ️ Довідка")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_admin_menu_keyboard():
    """Main menu keyboard for admins"""
    keyboard = [
        [KeyboardButton("👥 Статистика"), KeyboardButton("📊 Список користувачів")],
        [KeyboardButton("📢 Створити конференцію"), KeyboardButton("📋 Конференції")],
        [KeyboardButton("💬 Розсилка")],
        [KeyboardButton("🔙 Вийти з адмін-панелі")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_skip_keyboard():
    """Keyboard with skip button for optional questions"""
    keyboard = [
        [KeyboardButton("⏭️ Пропустити")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


def get_back_keyboard():
    """Keyboard with back to main menu button"""
    keyboard = [
        [KeyboardButton("🏠 Головне меню")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
