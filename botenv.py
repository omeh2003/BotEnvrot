# Импорт необходимых библиотек и модулей
import asyncio
import datetime
import shutil
import traceback
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import os
import subprocess
import dotenv
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Загрузка переменных окружения из .env файла
dotenv.load_dotenv()

# Генерация имени файла для логов с текущей датой и временем
str_now = datetime.datetime.now().strftime("%d-%m-%Y_%H%M")
file_log = os.path.abspath("data" + os.sep + f"appbot_{str_now}.log")

# Получение значения переменной DEBUG из окружения
DEBUG = os.environ.get("DEBUG")

# Настройка логгирования в зависимости от DEBUG
if DEBUG:
    logging.basicConfig(
        level=logging.INFO,
        encoding="utf-8",
        format="%(levelname)s - %(name)s - %(funcName)s  -  "
        "Message: %(message)s - "
        " - Line: %(lineno)d",
    )
else:
    logging.basicConfig(
        level=logging.ERROR,
        filemode="a",
        filename=file_log,
        encoding="utf-8",
        format="%(levelname)s | %(asctime)s | %(name)s | %(lineno)d |  "
        "Method: %(funcName)s | "
        "Message: %(message)s | "
        "%(pathname)s",
    )

# Инициализация логгера
logger = logging.getLogger(__name__)

# Примеры сообщений для логгера
logger.info(f"Стартуем!!!!!")
logger.debug("Debug")
logger.info("Info")
logger.warning("Warning")
logger.error("Error")
logger.critical("Critical")

# Пример обработки исключения с логированием
try:
    logging.info(f"check loging exeption")
    raise Exception("Test exeption")
except Exception as e:
    logging.exception(f"Exception!!!")
    logging.exception(f"{e.args}")
    logging.exception(f"{traceback.format_tb(e.__traceback__)}")

# Получение токена бота и ID администратора из переменных окружения
BOT_API_TOKEN = os.environ.get("BOT_API_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_API_TOKEN)
dp = Dispatcher()

# Получение директорий проекта и окружения из переменных окружения
project_dir = os.environ.get("PROJECT_DIR")
env_dir = os.environ.get("ENV_DIR")


def list_projects():
    """
    Получает список всех проектов в директории, указанной в переменной окружения project_dir.

    Returns:
        list: Список имен проектов или строку "No projects dir found.", если директория не найдена.
    """
    logger.info(f"list_projects: {project_dir}")
    try:
        return os.listdir(project_dir)
    except FileNotFoundError as e:
        logger.exception(f"Exception: {e}")
        return "No projects dir found."


def list_env_files(project):
    """
    Получает список всех файлов окружения для заданного проекта.

    Args:
        project (str): Имя проекта.

    Returns:
        list: Список файлов окружения или строку "No env files found.", если файлы не найдены.
    """
    logger.info(f"list_env_files: {env_dir}")
    try:
        return os.listdir(env_dir + project)
    except FileNotFoundError as e:
        logger.exception(f"Exception: {e}")
        return "No env files found."


def docker_command(*args):
    """
    Выполняет команду docker-compose с заданными аргументами.

    Args:
        *args: Аргументы для команды docker-compose.

    Returns:
        bool: True, если команда выполнена успешно, иначе False.
    """
    logger.info(f"docker_command: {args}")
    try:
        subprocess.run(["docker-compose", *args], check=True)
        logger.info(f"docker_command:  {args} success")
        return True
    except subprocess.CalledProcessError as e:
        logger.exception(f"Exception: {e}")
        return False


@dp.message(CommandStart)
async def handle_start(msg: types.Message):
    """
    Обрабатывает команду /start. Предлагает пользователю выбрать проект из списка.

    Args:
        msg (types.Message): Входящее сообщение от пользователя.
    """
    # Проверка прав доступа пользователя
    if msg.from_user.id != int(ADMIN_ID):
        await msg.answer("You are not allowed to use this bot.")
        return

    # Создание кнопок для выбора проекта
    buttons = []
    for project in list_projects():
        buttons.append(
            InlineKeyboardButton(text=project, callback_data=f"project:{project}")
        )

    # Создание клавиатуры
    keybord = InlineKeyboardMarkup(
        inline_keyboard=[buttons],
        row_width=1,
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    # Отправка сообщения с клавиатурой
    await msg.answer(text="Choose a project:", reply_markup=keybord)


@dp.callback_query(F.data.startswith("project:"))
async def handle_project(callback_query: types.CallbackQuery):
    """
    Обрабатывает выбор проекта. Предлагает пользователю выбрать файл окружения.

    Args:
        callback_query (types.CallbackQuery): Входящий callback запрос от пользователя.
    """
    # Получение имени проекта из callback_data
    project = callback_query.data.split(":")[1]

    # Создание кнопок для выбора файла окружения
    buttons = []
    for env_file in list_env_files(project):
        button = [
            [
                InlineKeyboardButton(
                    text=env_file, callback_data=f"env:{project}:{env_file}"
                )
            ],
        ]
        buttons.extend(button)

    # Добавление дополнительных кнопок управления
    buttons.extend(
        [
            [InlineKeyboardButton(text="Stop", callback_data=f"stop:{project}")],
            [InlineKeyboardButton(text="Restart", callback_data=f"restart:{project}")],
            [InlineKeyboardButton(text="Start", callback_data=f"start:{project}")],
        ]
    )

    # Создание клавиатуры
    keybord = InlineKeyboardMarkup(
        inline_keyboard=buttons,
        row_width=1,
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    # Редактирование предыдущего сообщения с новой клавиатурой
    await bot.edit_message_text(
        "Choose an env file:",
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=keybord,
    )


@dp.callback_query(F.data.startswith("env:"))
async def handle_env(callback_query: types.CallbackQuery):
    """
    Обрабатывает callback-запрос, связанный с выбором файла окружения для Docker-контейнера.
    Останавливает текущий контейнер, обновляет файл окружения и запускает контейнер заново.
    """
    # Разбор данных из callback-запроса
    _, project, env_file = callback_query.data.split(":")

    # Остановка текущего Docker-контейнера
    if docker_command(
            "--file",
            f"{project_dir}{project}/docker-compose.yml",
            "--project-directory",
            f"{os.path.abspath(project_dir + project)}",
            "down",
    ):
        # Удаление текущего файла окружения, если он существует
        if os.path.exists(project_dir + project + "/.env"):
            os.remove(f"{project_dir}{project}/.env")

        # Копирование нового файла окружения
        shutil.copy(f"{env_dir}{project}/{env_file}", f"{project_dir}{project}/.env")

        # Запуск Docker-контейнера с новым файлом окружения
        if docker_command(
                "--file",
                f"{project_dir}{project}/docker-compose.yml",
                "--project-directory",
                f"{os.path.abspath(project_dir + project)}",
                "up",
                "-d",
        ):
            # Логирование вывода команды 'docker-compose logs'
            logs = subprocess.run(
                [
                    "docker",
                    "compose",
                    "--file",
                    f"{project_dir}{project}/docker-compose.yml",
                    "logs",
                ],
                capture_output=True,
                text=True,
            )
            logging.info(logs.stdout)

            # Отправка сообщения о успешном запуске контейнера
            await bot.send_message(
                callback_query.from_user.id,
                "Operation successful. Docker container is up.",
            )
        else:
            # Отправка сообщения о неудачном запуске контейнера
            await bot.send_message(
                callback_query.from_user.id, "Failed to start Docker container."
            )
    else:
        # Отправка сообщения о неудачной остановке контейнера
        await bot.send_message(
            callback_query.from_user.id, "Failed to stop Docker container."
        )


@dp.callback_query(F.data.startswith("start:"))
async def handle_start(callback_query: types.CallbackQuery):
    """
    Обрабатывает callback-запрос для запуска Docker-контейнера.
    Запускает Docker-контейнер с текущей конфигурацией.
    """
    # Извлечение имени проекта из данных callback-запроса
    _, project = callback_query.data.split(":")

    # Попытка запуска Docker-контейнера
    if docker_command(
            "--file",
            f"{project_dir}{project}/docker-compose.yml",
            "--project-directory",
            f"{os.path.abspath(project_dir + project)}",
            "up",
            "-d",
    ):
        # Логирование вывода команды 'docker-compose logs'
        logs = subprocess.run(
            [
                "docker",
                "compose",
                "--file",
                f"{project_dir}{project}/docker-compose.yml",
                "logs",
            ],
            capture_output=True,
            text=True,
        )
        logging.info(logs.stdout)

        # Отправка сообщения о успешном запуске контейнера
        await bot.send_message(
            callback_query.from_user.id, "Operation successful. Docker container is up."
        )
    else:
        # Отправка сообщения о неудачном запуске контейнера
        await bot.send_message(
            callback_query.from_user.id, "Failed to start Docker container."
        )


@dp.callback_query(F.data.startswith("stop:"))
async def handle_stop(callback_query: types.CallbackQuery):
    _, project = callback_query.data.split(":")

    if docker_command(
        "--file",
        f"{project_dir}{project}/docker-compose.yml",
        "--project-directory",
        f"{os.path.abspath(project_dir + project)}",
        "down",
    ):
        await bot.send_message(
            callback_query.from_user.id,
            "Operation successful. Docker container is down.",
        )
    else:
        await bot.send_message(
            callback_query.from_user.id, "Failed to stop Docker container."
        )


@dp.callback_query(F.data.startswith("restart:"))
async def handle_restart(callback_query: types.CallbackQuery):
    _, project = callback_query.data.split(":")

    if docker_command(
        "--file",
        f"{project_dir}{project}/docker-compose.yml",
        "--project-directory",
        f"{os.path.abspath(project_dir + project)}",
        "restart",
    ):
        logs = subprocess.run(
            [
                "docker",
                "compose",
                "--file",
                f"{project_dir}{project}/docker-compose.yml",
                "logs",
            ],
            capture_output=True,
            text=True,
        )
        logging.info(logs.stdout)
        await bot.send_message(
            callback_query.from_user.id,
            "Operation successful. Docker container is restarted.",
        )
    else:
        await bot.send_message(
            callback_query.from_user.id, "Failed to restart Docker container."
        )


async def main():
    """
    Основная асинхронная функция для запуска опроса бота.
    """
    # Запуск опроса бота для получения обновлений
    await dp.start_polling(bot)

# Точка входа в программу
if __name__ == "__main__":
    # Запуск асинхронного цикла событий
    asyncio.run(main())
