"""
Скрипт для генерации OAuth токена Google Drive
ВАЖНО: Запускайте ЛОКАЛЬНО на своём компьютере, НЕ на сервере!

Инструкция:
1. Создайте проект в Google Cloud Console (console.cloud.google.com)
2. Включите Google Drive API
3. Создайте OAuth 2.0 Client ID (тип: Desktop app)
4. Скачайте JSON файл и сохраните как 'client_secret.json' в этой папке
5. Запустите: python generate_oauth_token.py
6. Откроется браузер - войдите и разрешите доступ
7. Скопируйте содержимое token.json в переменную окружения GOOGLE_OAUTH_TOKEN на Render.com
"""

from google_auth_oauthlib.flow import InstalledAppFlow
import json
import os

# Права доступа к Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']


def main():
    """Генерирует OAuth токен для Google Drive API"""

    client_secret_file = 'client_secret.json'

    # Проверка наличия файла client_secret.json
    if not os.path.exists(client_secret_file):
        print("\n❌ ОШИБКА: Файл 'client_secret.json' не найден!")
        print("\nИнструкция по созданию:")
        print("1. Перейдите на https://console.cloud.google.com/")
        print("2. Создайте новый проект или выберите существующий")
        print("3. Включите Google Drive API:")
        print("   - APIs & Services → Library → Google Drive API → Enable")
        print("4. Создайте OAuth 2.0 Client ID:")
        print("   - APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID")
        print("   - Application type: Desktop app")
        print("   - Скачайте JSON файл и переименуйте в 'client_secret.json'")
        print("5. Поместите 'client_secret.json' в папку с этим скриптом")
        print("\nПосле этого запустите скрипт снова.")
        return

    print("\n🔐 Генерация OAuth токена для Google Drive...\n")

    try:
        # Создание OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secret_file,
            SCOPES
        )

        # Запуск локального сервера для авторизации
        print("📱 Сейчас откроется браузер для авторизации...")
        print("   Войдите в Google аккаунт и разрешите доступ к Google Drive\n")

        creds = flow.run_local_server(port=0)

        # Подготовка данных токена
        token_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }

        # Сохранение в файл
        token_file = 'token.json'
        with open(token_file, 'w') as f:
            json.dump(token_data, f, indent=2)

        print("\n✅ Токен успешно создан и сохранён в 'token.json'!\n")
        print("=" * 70)
        print("\n📋 Следующие шаги:\n")
        print("1. Скопируйте всё содержимое файла 'token.json'")
        print("2. На Render.com добавьте переменную окружения:")
        print("   Имя: GOOGLE_OAUTH_TOKEN")
        print("   Значение: <содержимое token.json>")
        print("\n3. Также создайте переменную GOOGLE_DRIVE_FOLDER_ID")
        print("   со значением ID корневой папки в Google Drive")
        print("\n" + "=" * 70)
        print("\n💡 Содержимое token.json:\n")
        print(json.dumps(token_data, indent=2))
        print("\n" + "=" * 70)

    except Exception as e:
        print(f"\n❌ ОШИБКА при генерации токена: {e}")
        print("\nПроверьте:")
        print("- Правильность файла 'client_secret.json'")
        print("- Включен ли Google Drive API в проекте")
        print("- Настроены ли OAuth consent screen в Google Cloud Console")


if __name__ == '__main__':
    main()
