"""Модуль для обработки кнопки старт в боте"""
from aiogram import Router

from database.db import session, get_admins, get_agents
from aiogram.filters import CommandStart
from aiogram.types import Message


# Определение роутера для команды старт
router = Router(name='user_start')


@router.message(CommandStart())
async def command_start(message: Message):
    """Функция обработки команды старт"""
    if message.from_user.id in list(get_admins(session)):
        await message.answer('Вы админ')
    elif message.from_user.id in list(get_agents(session)):
        await message.answer('Вы агент.\nВведите номер прибора учета(можно не полностью)')
    else:
        await message.answer('Вы потребитель электрической энергии \nВведите номер лицевого счета')
