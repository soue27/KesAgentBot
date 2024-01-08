import os
import datetime

from aiogram import Router, F, types, Bot
from aiogram.client import bot
from aiogram.fsm.context import FSMContext
from database.db import session, get_admins, save_worker, get_data, get_meter_id, get_photo, delete_meter, \
    change_meter, get_agents
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from loguru import logger
from aiogram.methods import SendDocument, SendPhoto
from aiogram.types.input_file import FSInputFile


from filters.filters import IsAdmin
from keyboards.adminkb import admin_kb, search_kb, update_kb

# Определение роутера для работы админа
router = Router(name='admins')


class Admin(StatesGroup):  # Стейт для ввода ай ди телеграмма для админа
    admin_id = State()


class Agent(StatesGroup):  # Стейт для ввода ай ди телеграмма для агента
    agent_id = State()


class ByNumber(StatesGroup):  # Стейт для ввода номера прибора учета для поиска фото
    number = State()


class ByContract(StatesGroup):  # Стейт для ввода номера договора для поиска фото
    contract = State()


class UploadDate(StatesGroup):  # Стейт для ввода года и месяца для выгрузки показаний
    upload_date = State()


class MeterDelete(StatesGroup):  # Стейт для ввода номера прибора учета для удаления
    del_number = State()


class MeterUpdate(StatesGroup):  # Стейт для ввода номера прибора учета для изменения
    upd_number = State()
    upd_cat = State()
    upd_data = State()


class SengMessage(StatesGroup):  # Стейт для текста сообщения для рассылки
    send_text = State()


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
async def add_admin(callback: types.CallbackQuery, state: FSMContext):
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
async def add_agent(callback: types.CallbackQuery, state: FSMContext):
    """Функция добавления номера ай ди агента"""
    await callback.message.delete()
    await callback.message.answer('Введите id агента')
    await state.set_state(Agent.agent_id)


@router.message(Agent.agent_id)
async def set_agent(message: Message, state: FSMContext):
    """Функция добавления номера ай ди агента из стейта"""
    if message.text.isdigit():
        save_worker(sesion=session, idd=int(message.text), admin=False)
        logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                    f' добавил агента {message.text}')
    await message.answer('агент добавлен')
    await state.clear()


@router.callback_query(F.data == 'current_upload')
async def current_upload(callback: types.CallbackQuery, bot: Bot):
    """Функция для выгрузки файлов с показаниями"""
    await callback.answer('Файл готов')
    data = str(datetime.date.today().year) + "-" + str(datetime.date.today().month).zfill(2) + "-%"
    get_data(session, data)
    document = FSInputFile('files\\upload.xlsx')
    await bot.send_document(chat_id=callback.from_user.id, document=document)
    logger.info(f'{callback.from_user.first_name} {callback.from_user.last_name} {callback.from_user.id}'
                f' Сделал выгрузку текущих показаний')
    os.remove('files\\upload.xlsx')


@router.callback_query(F.data == 'upload')
async def upload(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    """Функция для выгрузки файлов с показаниями"""
    await callback.message.delete()
    await callback.message.answer('Введите год и месяц в формате: \n'
                                  '2023-11,\n для выгрузки за ноябрь 2023г.')
    await state.set_state(UploadDate.upload_date)


@router.message(UploadDate.upload_date)
async def upload_dates(message: Message, state: FSMContext, bot: Bot):
    upload_date = message.text + "-%"
    get_data(session, upload_date)
    document = FSInputFile('files\\upload.xlsx')
    await bot.send_document(chat_id=message.from_user.id, document=document)
    logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                f' Сделал выгрузку показаний за {message.text}')
    os.remove('files\\upload.xlsx')


@router.callback_query(F.data == 'get_photo')
async def get_photo(callback: types.CallbackQuery, state: FSMContext):
    """Функция обработки нажатия на кнопку выгрузки фотографии"""
    await callback.message.delete()
    await callback.message.answer('Выберете как будем искать', reply_markup=search_kb())
    # await state.set_state(Admin.admin_id)


@router.callback_query(F.data == 'by_number')
async def get_photo_bynumber(callback: types.CallbackQuery, state: FSMContext):
    """Функция обработки нажатия на кнопку поиска по номеру прибора учета"""
    await callback.message.delete()
    await callback.message.answer('Введите номер прибора учета')
    await state.set_state(ByNumber.number)


@router.callback_query(F.data == 'by_contract')
async def get_photo_bycontract(callback: types.CallbackQuery, state: FSMContext):
    """Функция обработки нажатия на кнопку поиска по номеру договора"""
    await callback.message.delete()
    await callback.message.answer('Введите номер договора')
    await state.set_state(ByContract.contract)


@router.message(ByNumber.number)
async def upload_photo_bynumber(message: Message, state: FSMContext, bot: Bot):
    """Функция добавления номера прибора учета из стейта и поиск из базы данных"""
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
async def upload_photo_bycontract(message: Message, state: FSMContext, bot: Bot):
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


@router.callback_query(F.data == 'delete')
async def delete(callback: types.CallbackQuery, state: FSMContext):
    """Функция обработки нажатия на кнопки удаления ПУ из базы"""
    await callback.message.delete()
    await callback.message.answer('Введите номер ПУ для удаления')
    await state.set_state(MeterDelete.del_number)


@router.message(MeterDelete.del_number)
async def delete_bynumber(message: Message, state: FSMContext):
    """Функция удаления ПУ из БД по номеру прибора учета из стейта"""
    delete_meter(sesion=session, nomer=message.text)
    await message.answer('Прибор учета удален')
    logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                f' удалил прибор учета № {message.text}')
    await state.clear()


@router.callback_query(F.data == 'update')
async def update(callback: types.CallbackQuery, state: FSMContext):
    """Функция обработки нажатия на кнопку изменения ПУ в базы"""
    await callback.message.delete()
    await callback.message.answer('Введите номер прибора учета для изменения')
    await state.set_state(MeterUpdate.upd_number)


@router.message(MeterUpdate.upd_number)
async def update_number(message: Message, state: FSMContext):
    """Функция удаления ПУ из БД по номеру прибора учета из стейта"""
    await state.update_data(upd_number=message.text)
    await message.answer('Выберете, что будем менять', reply_markup=update_kb())
    await state.set_state(MeterUpdate.upd_cat)


@router.callback_query(MeterUpdate.upd_cat)
async def update_cat(callback: types.CallbackQuery, state: FSMContext):
    """Функция обработки нажатия на кнопку изменения ПУ в базы"""
    await callback.message.delete()
    await state.update_data(upd_cat=callback.data)
    await callback.message.answer('Введите данные для изменения')
    await state.set_state(MeterUpdate.upd_data)


@router.message(MeterUpdate.upd_data)
async def update_data(message: Message, state: FSMContext):
    """Функция обработки нажатия на кнопку изменения ПУ в базы"""
    await state.update_data(upd_data=message.text)
    my_data = await state.get_data()
    res = change_meter(sesion=session, nomer=my_data['upd_number'], cat=my_data['upd_cat'], value=my_data['upd_data'])
    await message.answer(f'Изменено {res} записи')
    logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                f" изменил данные прибора учета № {my_data['upd_number']} по категории {my_data['upd_cat']},"
                f" на  {my_data['upd_data']}")
    await state.clear()


@router.callback_query(F.data == 'send')
async def send(callback: types.CallbackQuery, state: FSMContext):
    """Функция обработки нажатия на кнопку отправки сообщения пользователям"""
    await callback.message.delete()
    await callback.message.answer('Введите текст сообщения для отправки')
    await state.set_state(SengMessage.send_text)


@router.message(SengMessage.send_text)
async def send_message(message: Message, state: FSMContext, bot: Bot):
    """Функция считывания текста и отправки сообщения пользователям"""
    for worker in get_admins(sesion=session) + get_agents(sesion=session):
        await bot.send_message(chat_id=int(worker), text=message.text)
    await message.answer('Сообщение отправлено всем пользователям')
    logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                f' отправил сообщение пользователям {message.text}')
    await state.clear()

