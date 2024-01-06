"""Модуль для загрузки данных в справочную таблицу"""
from aiogram import Router, F, Bot

from database.db import session, get_admins, connect, load_data
from aiogram.types import Message
from loguru import logger
from filters.filters import IsAdmin

# Определение роутера для загрузки данных из файлов
router = Router(name='load_data')


@router.message(F.document, IsAdmin())
async def load_dates(message: Message, bot: Bot):
    """Функция для загрузки данных из excel файла, загруженного в бота
    сработает только если файл является документом и ай ди пользователя входит в таблицу админов.
    Пользователю возвращается количество внесенных строк в базу данных"""
    file_id = message.document.file_id
    file = await bot.get_file(file_id=file_id)
    file_path = file.file_path
    await bot.download_file(file_path, "files\\forload.xlsx")
    result = load_data("files\\forload.xlsx", connect)
    await message.answer(f'Загружено {result} строк')
    logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                f' загрузил данные по {result} строкам')
