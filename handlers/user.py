from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from database.db import session, get_admins,  get_agents
from aiogram.types import Message


# Определение роутера для работы агента
router = Router(name='user')


@router.message(F.text.isdigit() & ~F.from_user.id.in_(set(get_admins(session)))
                & ~F.from_user.id.in_(set(get_agents(session))))
async def agents_work(message: Message, state: FSMContext):
    """Функция обработки ввода номера ПУ"""
    await message.answer('Вы простой потребитель, введите номер прибора учета')
