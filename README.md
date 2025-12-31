# Dosudebka Bot

Telegram бот для отдела досудебки с интеграцией Bitrix24 и Google Drive.

## Установка

```bash
pip install -r requirements.txt
```

## Запуск

**Локально**:
```bash
python bot/main.py
```

**Production**:
```bash
gunicorn web.app:app
```

## Конфигурация

Все настройки через переменные среды (см. `.env.example`)

## Render.com

1. Добавь переменные из `.env.example` в Environment Variables
2. Добавь `credentials.json` как Secret File
3. Deploy
