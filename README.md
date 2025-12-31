# Dosudebka Bot

Telegram бот для отдела досудебки с интеграцией Bitrix24 и Google Drive.

## Установка

```bash
pip install -r requirements.txt
```

## Настройка Google Drive OAuth

### 1. Создание OAuth credentials в Google Cloud Console

1. Перейдите на [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите Google Drive API:
   - **APIs & Services** → **Library** → найдите **Google Drive API** → **Enable**
4. Создайте OAuth 2.0 Client ID:
   - **APIs & Services** → **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
   - Application type: **Desktop app**
   - Название: `Dosudebka Bot` (или любое другое)
5. Скачайте JSON файл и сохраните как `client_secret.json` в корне проекта

### 2. Генерация OAuth токена (ЛОКАЛЬНО)

**ВАЖНО**: Этот шаг выполняется ТОЛЬКО на вашем локальном компьютере!

```bash
python generate_oauth_token.py
```

- Откроется браузер для авторизации
- Войдите в Google аккаунт и разрешите доступ к Google Drive
- Токен сохранится в файл `token.json`
- Скопируйте **всё содержимое** файла `token.json`

### 3. Настройка переменных окружения на Render.com

В Environment Variables добавьте:

```env
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_from_drive
GOOGLE_OAUTH_TOKEN=<содержимое token.json одной строкой>
```

**Примечание**: `GOOGLE_OAUTH_TOKEN` должен быть JSON объектом в одну строку, например:
```json
{"token": "ya29...", "refresh_token": "1//...", "token_uri": "https://oauth2.googleapis.com/token", "client_id": "123.apps.googleusercontent.com", "client_secret": "GOCSPX-...", "scopes": ["https://www.googleapis.com/auth/drive.file"]}
```

## Запуск

**Локально**:
```bash
python bot/main.py
```

**Production (Render.com)**:
```bash
gunicorn web.app:app
```

## Конфигурация

Все настройки через переменные среды (см. `.env.example`)

### Необходимые переменные окружения:

- `TELEGRAM_BOT_TOKEN` - токен Telegram бота от @BotFather
- `WEBHOOK_URL` - URL вашего приложения на Render (https://your-app.onrender.com)
- `BITRIX_WEBHOOK_URL` - webhook URL из Bitrix24
- `BITRIX_CATEGORY_ID` - ID воронки в Bitrix24 (по умолчанию: 7)
- `GOOGLE_DRIVE_FOLDER_ID` - ID корневой папки в Google Drive
- `GOOGLE_OAUTH_TOKEN` - OAuth токен для Google Drive (JSON)
- `DATABASE_URL` - PostgreSQL connection string (автоматически на Render)
- `ADMIN_TOKEN` - токен для доступа к админ-панели

## Развёртывание на Render.com

1. Создайте новый **Web Service**
2. Подключите GitHub репозиторий
3. Настройки:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn web.app:app`
   - **Environment**: Python 3.11
4. Добавьте PostgreSQL базу данных (Add Database)
5. Добавьте все переменные окружения из `.env.example`
6. Deploy

## Структура проекта

```
dosudebka_bot/
├── bot/                    # Telegram bot handlers
├── config/                 # Configuration
├── database/              # Database models & schema
├── integrations/          # Bitrix24 & Google Drive
├── services/              # Business logic
├── web/                   # Flask app для webhooks
├── generate_oauth_token.py  # Скрипт генерации OAuth токена
└── requirements.txt
```

## Админ-панель

Доступ к админ-панели через deep link:
```
https://t.me/your_bot?start=admin_YOUR_ADMIN_TOKEN
```

Любой пользователь с валидным токеном автоматически становится администратором.
