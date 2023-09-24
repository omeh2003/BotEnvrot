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

dotenv.load_dotenv()

# Создаем имя файла с текущим временем
str_now = datetime.datetime.now().strftime("%d-%m-%Y_%H%M")
file_log = os.path.abspath("data" + os.sep + f"appbot_{str_now}.log")
# endregion
DEBUG = os.environ.get("DEBUG")
if DEBUG:
    logging.basicConfig(level=logging.INFO, encoding="utf-8",
                        format='%(levelname)s - %(name)s - %(funcName)s  -  '

                               'Message: %(message)s - '
                               ' - Line: %(lineno)d'
                        ,

                        )


else:
    logging.basicConfig(level=logging.ERROR, filemode="a", filename=file_log, encoding="utf-8",
                        format='%(levelname)s | %(asctime)s | %(name)s | %(lineno)d |  '
                               'Method: %(funcName)s | '
                               'Message: %(message)s | '
                               '%(pathname)s',

                        )

logger = logging.getLogger(__name__)

logger.info(f"Стартуем!!!!!")
logger.debug("Debug")
logger.info("Info")
logger.warning("Warning")
logger.error("Error")
logger.critical("Critical")

try:
    logging.info(f"check loging exeption")
    raise Exception("Test exeption")
except Exception as e:
    logging.exception(f"Exception!!!")
    logging.exception(f"{e.args}")
    logging.exception(f"{traceback.format_tb(e.__traceback__)}")

BOT_API_TOKEN = os.environ.get("BOT_API_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID")

bot = Bot(token=BOT_API_TOKEN)
dp = Dispatcher()

project_dir = os.environ.get("PROJECT_DIR")
env_dir = os.environ.get("ENV_DIR")


def list_projects():
    logger.info(f"list_projects: {project_dir}")
    try:
        return os.listdir(project_dir)
    except FileNotFoundError as e:
        return "No projects dir found."


def list_env_files(project):
    logger.info(f"list_env_files: {env_dir}")
    try:
        return os.listdir(env_dir + project)
    except FileNotFoundError as e:
        return "No env files found."


def docker_command(*args):
    logger.info(f"docker_command: {args}")
    try:
        subprocess.run(["docker-compose", *args], check=True)
        logger.info(f"docker_command:  {args} success")

        return True
    except subprocess.CalledProcessError:
        return False


@dp.message(CommandStart)
async def handle_start(msg: types.Message):
    if msg.from_user.id != int(ADMIN_ID):
        await msg.answer("You are not allowed to use this bot.")
        return
    buttons = []
    for project in list_projects():
        buttons.append(InlineKeyboardButton(text=project, callback_data=f"project:{project}"))
    keybord = InlineKeyboardMarkup(inline_keyboard=[buttons], row_width=1, resize_keyboard=True, one_time_keyboard=True
        )

    await msg.answer(text="Choose a project:", reply_markup=keybord)


@dp.callback_query(F.data.startswith("project:"))
async def handle_project(callback_query: types.CallbackQuery):
    project = callback_query.data.split(":")[1]
    buttons = []
    for env_file in list_env_files(project):
        button = [
            [InlineKeyboardButton(text=env_file, callback_data=f"env:{project}:{env_file}")],
            ]

        buttons.extend(button)
    buttons.extend( [[InlineKeyboardButton(text="Stop", callback_data=f"stop:{project}")],
            [InlineKeyboardButton(text="Restart", callback_data=f"restart:{project}")],
            [InlineKeyboardButton(text="Start", callback_data=f"start:{project}")],
           ])

    keybord = InlineKeyboardMarkup(inline_keyboard=buttons, row_width=1, resize_keyboard=True, one_time_keyboard=True)
    await bot.edit_message_text("Choose an env file:", callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=keybord)


@dp.callback_query(F.data.startswith("env:"))
async def handle_env(callback_query: types.CallbackQuery):
    _, project, env_file = callback_query.data.split(":")

    if docker_command("--file", f'{project_dir}{project}/docker-compose.yml', "--project-directory",
                      f'{os.path.abspath(project_dir + project)}', 'down'):
        if os.path.exists(project_dir + project + "/.env"):
            os.remove(f"{project_dir}{project}/.env")
        shutil.copy(f"{env_dir}{project}/{env_file}", f"{project_dir}{project}/.env")

        if docker_command("--file", f'{project_dir}{project}/docker-compose.yml', "--project-directory",
                          f'{os.path.abspath(project_dir + project)}', "up", "-d"):
            logs = subprocess.run(["docker", "compose", "--file", f"{project_dir}{project}/docker-compose.yml", "logs"],
                                  capture_output=True, text=True)
            logging.info(logs.stdout)

            await bot.send_message(callback_query.from_user.id, "Operation successful. Docker container is up.")
        else:
            await bot.send_message(callback_query.from_user.id, "Failed to start Docker container.")
    else:
        await bot.send_message(callback_query.from_user.id, "Failed to stop Docker container.")


@dp.callback_query(F.data.startswith("start:"))
async def handle_start(callback_query: types.CallbackQuery):
    _, project = callback_query.data.split(":")

    if docker_command("--file", f'{project_dir}{project}/docker-compose.yml', "--project-directory",
                      f'{os.path.abspath(project_dir + project)}', "up", '-d'):
        logs = subprocess.run(["docker", "compose", "--file", f"{project_dir}{project}/docker-compose.yml", "logs"],
                              capture_output=True, text=True)
        logging.info(logs.stdout)
        await bot.send_message(callback_query.from_user.id, "Operation successful. Docker container is up.")
    else:
        await bot.send_message(callback_query.from_user.id, "Failed to start Docker container.")


@dp.callback_query(F.data.startswith("stop:"))
async def handle_stop(callback_query: types.CallbackQuery):
    _, project = callback_query.data.split(":")

    if docker_command("--file", f'{project_dir}{project}/docker-compose.yml', "--project-directory",
                      f'{os.path.abspath(project_dir + project)}', 'down'):
        await bot.send_message(callback_query.from_user.id, "Operation successful. Docker container is down.")
    else:
        await bot.send_message(callback_query.from_user.id, "Failed to stop Docker container.")


@dp.callback_query(F.data.startswith("restart:"))
async def handle_restart(callback_query: types.CallbackQuery):
    _, project = callback_query.data.split(":")

    if docker_command("--file", f'{project_dir}{project}/docker-compose.yml', "--project-directory",
                      f'{os.path.abspath(project_dir + project)}', 'restart'):
        logs = subprocess.run(["docker", "compose", "--file", f"{project_dir}{project}/docker-compose.yml", "logs"],
                              capture_output=True, text=True)
        logging.info(logs.stdout)
        await bot.send_message(callback_query.from_user.id, "Operation successful. Docker container is restarted.")
    else:
        await bot.send_message(callback_query.from_user.id, "Failed to restart Docker container.")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
