from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from database.db import session, get_admins, save_worker
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from loguru import logger
from keyboards.adminkb import admin_kb

# Определение роутера для работы админа
router = Router(name='admins')


class Admin(StatesGroup):
    admin_id = State()


class Agent(StatesGroup):
    agent_id = State()


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Функция обработки команды отмена"""
    if message.from_user.id in set(get_admins(session)):
        await message.answer("Выберите действие", reply_markup=admin_kb())
        logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                    f' зашел как админ')
    else:
        await message.answer("Вы не являетесь администратором")
        logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                    f' попытался зайти как админ')


@router.callback_query(F.data == 'add_admin')
async def func_name(callback: types.CallbackQuery, state: FSMContext):
    """Функция добавления номера ай ди админа"""
    await callback.message.delete()
    await callback.message.answer('Введите id администратора')
    await state.set_state(Admin.admin_id)


@router.message(Admin.admin_id)
async def set_admin(message: Message, state: FSMContext):
    """Функция добавления номера ай ди админа из стейта"""
    if message.text.isdigit():
        save_worker(sesion=session, idd=int(message.text), admin=True)
        logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                    f' добавил админа {message.text}')
    await message.answer('администратор добавлен')
    await state.clear()


@router.callback_query(F.data == 'add_agent')
async def func_name(callback: types.CallbackQuery, state: FSMContext):
    """Функция добавления номера ай ди агента"""
    await callback.message.delete()
    await callback.message.answer('Введите id агента')
    await state.set_state(Agent.agent_id)


@router.message(Agent.agent_id)
async def set_admin(message: Message, state: FSMContext):
    """Функция добавления номера ай ди агента из стейта"""
    if message.text.isdigit():
        save_worker(sesion=session, idd=int(message.text), admin=False)
        logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                    f' добавил агента {message.text}')
    await message.answer('агент добавлен')
    await state.clear()
