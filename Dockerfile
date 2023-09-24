# Используйте официальный образ Python
FROM python:3.11

# Установка переменных окружения для Poetry
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Добавление Poetry и $PATH
ENV PATH="$POETRY_HOME/bin:$HOME/.local/bin:$PATH"

# Установка Poetry

RUN pip install poetry
RUN mkdir /app
# Установка рабочего каталога
WORKDIR /app

# Копирование исходного кода
COPY . /app

# Копирование pyproject.toml и poetry.lock файлов для установки зависимостей
COPY pyproject.toml poetry.lock /app/

# Установка зависимостей
RUN poetry install --no-dev --no-root --no-interaction --no-ansi -vvv

# Запуск приложения
ENTRYPOINT ["poetry", "run", "python3", "botenv.py"]
