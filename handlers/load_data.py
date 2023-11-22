"""Модуль для загрузки данных в справочную таблицу"""
from aiogram import Router, F, Bot

from database.db import session, get_admins, connect, load_data
from aiogram.types import Message


# Определение роутера для загрузки данных из файлов
router = Router(name='load_data')


@router.message(F.document & F.from_user.id.in_(set(get_admins(session))))
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
