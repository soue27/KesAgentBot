from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from loguru import logger
from database.db import session, get_agents
from aiogram.types import Message

from filters.filters import IsAdmin, IsAgent

# Определение роутера для работы агента
router = Router(name='user')


# , not IsAdmin, not IsAgent


@router.message(F.text.isdigit())
async def user_work(message: Message, state: FSMContext):
    """Функция обработки ввода номера ПУ"""
    if message.from_user.id in set(get_agents(session)):
        print('ай ди агентах')
    print(set(get_agents(session)))
    await message.answer('Вы простой потребитель, введите номер прибора учета')
    logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                f' зашел как потребитель')

