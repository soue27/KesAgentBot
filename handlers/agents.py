from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from database.db import session, get_agents, get_meter_id, save_counter, find_meter_by_nomer
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from keyboards.metersid import metersid_kb

# Определение роутера для работы агента
router = Router(name='agents')


class Zone(StatesGroup):
    meter_nomer = State()
    fhoto1 = State()
    fhoto2 = State()
    fhoto3 = State()


@router.message(Command("cancel"))
async def cmd_canxel(message: Message, state: FSMContext):
    """Функция обработки команды отмена"""
    await message.answer("Данные по последнему введенному прибору учета сброшены\nНачните с ввода номера")
    await state.clear()


@router.message(Zone.fhoto1, ~F.photo)
async def incorrect_photo(message: Message):
    """Функция проверяет корректность фото соответствующего тарифа"""
    await message.answer("Вы отправили не фото прибора учета, отправьте корректное фото")


@router.message(Zone.fhoto2, ~F.photo)
async def incorrect_photo(message: Message):
    """Функция проверяет корректность фото соответствующего тарифа"""
    await message.answer("Вы отправили не фото прибора учета, отправьте корректное фото")


@router.message(Zone.fhoto3, ~F.photo)
async def incorrect_photo(message: Message):
    """Функция проверяет корректность фото соответствующего тарифа"""
    await message.answer("Вы отправили не фото прибора учета, отправьте корректное фото")


@router.message(F.text.isdigit() & F.from_user.id.in_(set(get_agents(session))))
async def agents_work(message: Message, state: FSMContext):
    """Функция обработки ввода номера ПУ"""
    metersid, count = find_meter_by_nomer(session, message.text)
    if count > 7:
        await message.answer('найдено более 7 приборов учета \n Введите больше цифр номера')
    else:
        await message.answer('Выберите действие', reply_markup=metersid_kb(message.text))
        await state.set_state(Zone.meter_nomer)


@router.callback_query(F.data == '0')
async def func_zero(callback: types.CallbackQuery):
    """Функция обработки добавления счетчика, если не обнаружен в базе"""
    await callback.message.delete()
    await callback.message.answer('Работает функция добавления счетичка')


@router.callback_query(Zone.meter_nomer)
async def func_name(callback: types.CallbackQuery, state: FSMContext):
    """Функция добавления номера прибора учета"""
    await callback.message.delete()
    zone = len(get_meter_id(session, callback.data))
    zones = get_meter_id(session, callback.data)
    await state.update_data(meter_nomer=callback.data)
    await state.set_state(Zone.fhoto1)
    if zone == 1:
        await callback.message.answer('Введите фото общего тарифа')
    elif zone == 2:
        await callback.message.answer(f'Введите фото тарифа *{zones[0][1]}*')
    else:
        await callback.message.answer(f'Введите фото тарифа *{zones[0][1]}*')


@router.message(Zone.fhoto1, F.photo)
async def get_fhoto1(message: Message, state: FSMContext):
    """Функция добавления фотографии 1 тарифа прибора учета"""
    my_data = await state.get_data()
    await state.update_data(photo1=[message.photo[-1].file_id, message.caption])
    zone = len(get_meter_id(session, my_data['meter_nomer']))
    zones = get_meter_id(session, my_data['meter_nomer'])
    if zone == 1:
        await message.answer('Переходите к следующему счетчику')
        my_data = await state.get_data()
        save_counter(session, message.from_user.id, get_meter_id(session, my_data['meter_nomer'])[0][0],
                     my_data['photo1'][1], my_data['photo1'][0])
        await state.clear()
    elif zone == 2:
        await message.answer(f"Введите фото тарифа *{zones[1][1]}*")
        my_data = await state.get_data()
        save_counter(session, message.from_user.id, get_meter_id(session, my_data['meter_nomer'])[0][0],
                     my_data['photo1'][1], my_data['photo1'][0])
        await state.set_state(Zone.fhoto2)
    else:
        await message.answer(f"Введите фото тарифа *{zones[1][1]}*")
        my_data = await state.get_data()
        save_counter(session, message.from_user.id, get_meter_id(session, my_data['meter_nomer'])[0][0],
                     my_data['photo1'][1], my_data['photo1'][0])
        await state.set_state(Zone.fhoto2)


@router.message(Zone.fhoto2, F.photo)
async def get_fhoto2(message: Message, state: FSMContext):
    """Функция добавления фотографии 2 тарифа прибора учета"""
    my_data = await state.get_data()
    zone = len(get_meter_id(session, my_data['meter_nomer']))
    zones = get_meter_id(session, my_data['meter_nomer'])
    await state.update_data(photo2=[message.photo[-1].file_id, message.caption])
    if zone == 2:
        await message.answer('Переходите к следующему счетчику')
        my_data = await state.get_data()
        save_counter(session, message.from_user.id, get_meter_id(session, my_data['meter_nomer'])[1][0],
                     my_data['photo2'][1], my_data['photo2'][0])
        await state.clear()
    elif zone == 3:
        await message.answer(f"Введите фото тарифа *{zones[2][1]}*")
        my_data = await state.get_data()
        save_counter(session, message.from_user.id, get_meter_id(session, my_data['meter_nomer'])[1][0],
                     my_data['photo2'][1], my_data['photo2'][0])
        await state.set_state(Zone.fhoto3)


@router.message(Zone.fhoto3, F.photo)
async def get_fhoto3(message: Message, state: FSMContext):
    """Функция добавления фотографии 3 тарифа прибора учета"""
    await state.update_data(photo3=[message.photo[-1].file_id, message.caption])
    my_data = await state.get_data()
    save_counter(session, message.from_user.id, get_meter_id(session, my_data['meter_nomer'])[2][0],
                 my_data['photo3'][1], my_data['photo3'][0])
    await message.answer('Переходите к следующему счетчику')
    await state.clear()
