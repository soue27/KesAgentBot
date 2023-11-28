import os

from aiogram import Router, F, types, Bot
from aiogram.client import bot
from aiogram.fsm.context import FSMContext
from database.db import session, get_admins, save_worker, get_data, get_meter_id, get_photo
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from loguru import logger
from aiogram.methods import SendDocument, SendPhoto
from aiogram.types.input_file import FSInputFile


from filters.filters import IsAdmin
from keyboards.adminkb import admin_kb, search_kb

# Определение роутера для работы админа
router = Router(name='admins')


class Admin(StatesGroup):
    admin_id = State()


class Agent(StatesGroup):
    agent_id = State()


class ByNumber(StatesGroup):
    number = State()


class ByContract(StatesGroup):
    contract = State()


@router.message(Command("admin"), IsAdmin())
async def cmd_admin(message: Message):
    """функция обработки команды admin"""
    # if message.from_user.id in set(get_admins(session)):
    await message.answer("Выберите действие", reply_markup=admin_kb())
    logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                f' зашел как админ')
    # else:
    #     await message.answer("Вы не являетесь администратором")
    #     logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
    #                 f' попытался зайти как админ')


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


@router.callback_query(F.data.in_({'upload', 'agent_stat'}))
async def upload(callback: types.CallbackQuery, bot: Bot):
    """Функция для выгрузки файлов с показаниями"""
    await callback.answer('Файл готов')
    get_data(session)
    document = FSInputFile('files\\upload.xlsx')
    await bot.send_document(chat_id=callback.from_user.id, document=document)
    logger.info(f'{callback.from_user.first_name} {callback.from_user.last_name} {callback.from_user.id}'
                f' Сделал выгрузка показаний')
    os.remove('files\\upload.xlsx')


@router.callback_query(F.data == 'get_photo')
async def func_name(callback: types.CallbackQuery, state: FSMContext):
    """Функция обработки нажатия на кнопку выгрузки фотографии"""
    await callback.message.delete()
    await callback.message.answer('Выберете как будем искать', reply_markup=search_kb())
    # await state.set_state(Admin.admin_id)


@router.callback_query(F.data == 'by_number')
async def func_name(callback: types.CallbackQuery, state: FSMContext):
    """Функция обработки нажатия на кнопку поиска по номеру прибора учета"""
    await callback.message.delete()
    await callback.message.answer('Введите номер прибора учета')
    await state.set_state(ByNumber.number)


@router.callback_query(F.data == 'by_contract')
async def func_name(callback: types.CallbackQuery, state: FSMContext):
    """Функция обработки нажатия на кнопку поиска по номеру договора"""
    await callback.message.delete()
    await callback.message.answer('Введите номер договора')
    await state.set_state(ByContract.contract)


@router.message(ByNumber.number)
async def set_admin(message: Message, state: FSMContext, bot: Bot):
    """Функция добавления номера прибора учета из стейта и поиск из базы данных"""
    if message.text.isdigit():
        spisok = get_photo(session, message.text, True)
        for item in spisok:
            if len(item) == 1:
                await bot.send_photo(chat_id=message.chat.id, photo=item[0][0], caption=str(item[0][1]))
            else:
                for i in range(len(item)):
                    await bot.send_photo(chat_id=message.chat.id, photo=item[i][0], caption=str(item[0][1]))
            # await SendPhoto(chat_id=message.chat.id, photo='file_id', caption='Описание фотки')
        logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                    f' выгрузил фотографии по номеру')
        await message.answer('Это все что нашлось!')
        await state.clear()


@router.message(ByContract.contract)
async def set_admin(message: Message, state: FSMContext, bot: Bot):
    if message.text.isdigit():
        spisok = get_photo(session, message.text, False)
        for item in spisok:
            if len(item) == 1:
                await bot.send_photo(chat_id=message.chat.id, photo=item[0][0], caption=str(item[0][1]))
            else:
                for i in range(len(item)):
                    await bot.send_photo(chat_id=message.chat.id, photo=item[i][0], caption=str(item[0][1]))
        logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                    f' выгрузил фотографии по номеру')
        await message.answer('Это все что нашлось!')
        await state.clear()
