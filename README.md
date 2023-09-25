# Управление Docker-контейнерами через Telegram-бота

## Описание

Этот проект представляет собой Telegram-бота для управления Docker-контейнерами. Бот позволяет запускать, останавливать и перезапускать контейнеры, а также менять их конфигурацию на лету.

## Особенности

- Асинхронное программирование для эффективного взаимодействия с Telegram API и Docker.
- Поддержка множества проектов и конфигураций.
- Логгирование всех ключевых действий и исключений.
- Безопасность: доступ ограничен только для администратора.

## Требования

- Python 3.8+
- Docker
- Telegram Bot API Token
- Переменные окружения (см. раздел "Конфигурация")

## Конфигурация

Переменные окружения задаются в файле `.env`:

- `BOT_API_TOKEN`: Токен Telegram-бота
- `ADMIN_ID`: ID администратора в Telegram
- `PROJECT_DIR`: Директория с Docker-проектами
- `ENV_DIR`: Директория с файлами окружения для Docker-контейнеров
- `DEBUG`: Флаг для активации режима отладки (опционально)

## Установка

1. Клонировать репозиторий:

    ```bash
    git clone https://github.com/omeh2003/BotEnvrot.git
    ```

2. Установить зависимости:

    ```bash
    pip install -r requirements.txt
    ```

3. Заполнить `.env` файл согласно шаблону.

4. Запустить бота:

    ```bash
    python botenv.py
    ```

## Использование

1. Отправьте команду `/start` боту в Telegram.
2. Выберите проект из предложенного списка.
3. Выберите файл окружения или выполните другую команду (остановить, перезапустить).

## Возможные улучшения

- Многопользовательская поддержка
- Юнит-тестирование
- Дополнительная документация
- Улучшенная обработка ошибок
- Интерфейс пользователя с дополнительными функциями
- Мониторинг и алертинг
- Кэширование

## Лицензия

MIT

---
