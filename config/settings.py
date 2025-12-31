import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# Bitrix24
BITRIX_WEBHOOK_URL = os.getenv('BITRIX_WEBHOOK_URL')
BITRIX_CATEGORY_ID = int(os.getenv('BITRIX_CATEGORY_ID', '7'))

# Google Drive
GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
GOOGLE_OAUTH_TOKEN = os.getenv('GOOGLE_OAUTH_TOKEN')

# Database
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Admin
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN', 'f7T9vQ1111wLp2Gx8Z')

# Server (managed by Render.com)
PORT = int(os.getenv('PORT', '8080'))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Stage mapping: Bitrix -> Client Display
STAGE_MAPPING = {
    'C7:NEW': '🎯 Стратегію розроблено',
    'C7:UC_60XKB5': '🎯 Стратегію розроблено',
    'C7:UC_DSTO0P': '🛡️ Ведемо переговори',
    'C7:PREPARATION': '✅ Є перші результати',
    'C7:EXECUTING': '⚡ Фінальний етап',
    'C7:1': '⚡ Фінальний етап',
    'C7:2': '💬 Потрібна ваша участь',
    'C7:WON': '🏆 Справу завершено',
    'C7:LOSE': '📋 Справу закрито',
}

# Stage descriptions
STAGE_DESCRIPTIONS = {
    '🎯 Стратегію розроблено': 'Клієнт прийшов → ми вивчили ситуацію → є план',
    '🛡️ Ведемо переговори': 'Взяли в роботу = почали комунікацію з кредиторами',
    '✅ Є перші результати': 'Закрили першого кредитора — є чим похвалитись',
    '⚡ Фінальний етап': 'Активна робота або очікування відповідей',
    '🏆 Справу завершено': 'Перемога!',
    '💬 Потрібна ваша участь': 'Спеціальний статус: потрібна ваша участь',
    '📋 Справу закрито': 'Справу закрито',
}

# Client categories
CLIENT_CATEGORIES = {
    'CRYPTO': 'Криптовалюта',
    'MFO': 'МФО',
    'BANK': 'Банки',
}
