from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from loguru import logger
from database.db import session, get_agents, get_meter_id, save_counter, find_meter_by_nomer, save_lost, get_admins
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State

from filters.filters import IsAgent, IsMyDigit
from keyboards.metersid import metersid_kb

# Определение роутера для работы агента
router = Router(name='agents')


class Zone(StatesGroup):
    meter_nomer = State()
    fhoto1 = State()
    fhoto2 = State()
    fhoto3 = State()


class LostMeter(StatesGroup):
    lost_data = State()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Функция обработки команды отмена"""
    logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                f' нажал "/cancel"')
    await message.answer("Данные по последнему введенному прибору учета сброшены\nНачните с ввода номера")
    await state.clear()


@router.message(Zone.fhoto1, ~F.photo)
async def incorrect_photo1(message: Message):
    """Функция проверяет корректность фото соответствующего тарифа"""
    await message.answer("Вы отправили не фото прибора учета, отправьте корректное фото")
    logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                f' ошибся в вводе фотографии, подпись {message.caption}')


@router.message(Zone.fhoto2, ~F.photo)
async def incorrect_photo2(message: Message):
    """Функция проверяет корректность фото соответствующего тарифа"""
    await message.answer("Вы отправили не фото прибора учета, отправьте корректное фото")
    logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                f' ошибся в вводе фотографии, подпись {message.caption}')


@router.message(Zone.fhoto3, ~F.photo)
async def incorrect_photo3(message: Message):
    """Функция проверяет корректность фото соответствующего тарифа"""
    await message.answer("Вы отправили не фото прибора учета, отправьте корректное фото")
    logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                f' ошибся в вводе фотографии, подпись {message.caption}')

# F.text.isdigit()


@router.message(IsMyDigit(), IsAgent())
async def agents_work(message: Message, state: FSMContext):
    """Функция обработки ввода номера ПУ"""
    metersid, count = find_meter_by_nomer(session, message.text)
    if count > 7:
        for i in metersid:
            if len(i[1]) == len(message.text):
                y = list(i)
                await message.answer('Выберите прибор учета:', reply_markup=metersid_kb(y, 1))
                await state.set_state(Zone.meter_nomer)
                logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                            f' нашел номер прибора учета {message.text}')
                break
        else:
            await message.answer('найдено более 7 приборов учета \n Введите больше цифр номера')
        logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                    f' нашел слишком много приборов учета c номером {message.text}')
    else:
        print(type(metersid), '****')
        await message.answer('Выберите прибор учета:', reply_markup=metersid_kb(metersid, count))
        await state.set_state(Zone.meter_nomer)
        logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                    f' нашел номер прибора учета {message.text}')


@router.callback_query(F.data == '0')
async def func_zero(callback: types.CallbackQuery, state: FSMContext):
    """Функция обработки добавления счетчика, если не обнаружен в базе"""
    await callback.message.delete()
    await callback.message.answer('Введите информацию о не найденном счетчике:\n'
                                  'Номер ПУ, показания, адрес, собственник\n'
                                  'В свободном виде')
    await state.set_state(LostMeter.lost_data)
    logger.info(f'{callback.from_user.first_name} {callback.from_user.last_name} {callback.from_user.id}'
                f' номер прибора учета  не найден{callback.data}')


@router.callback_query(Zone.meter_nomer)
async def func_name(callback: types.CallbackQuery, state: FSMContext):
    """Функция добавления номера прибора учета"""
    await callback.message.delete()
    zone = len(get_meter_id(session, callback.data))
    zones = get_meter_id(session, callback.data)
    await state.update_data(meter_nomer=callback.data)
    await state.set_state(Zone.fhoto1)
    logger.info(f'{callback.from_user.first_name} {callback.from_user.last_name} {callback.from_user.id}'
                f' зашел в первый стэйт')
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
    logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                f' зашел во второй стэйт, показания {message.caption}')
    if message.caption is not None:
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
    else:
        await message.answer('Вы не ввели показания, как попдись к фотографии \n'
                             'Попробуйте отправить фотографию еще раз\nОбязательно с подписью')


@router.message(Zone.fhoto2, F.photo)
async def get_fhoto2(message: Message, state: FSMContext):
    """Функция добавления фотографии 2 тарифа прибора учета"""
    my_data = await state.get_data()
    zone = len(get_meter_id(session, my_data['meter_nomer']))
    zones = get_meter_id(session, my_data['meter_nomer'])
    await state.update_data(photo2=[message.photo[-1].file_id, message.caption])
    logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                f' зашел в третий стэйт, показания {message.caption}')
    if message.caption is not None:
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
    else:
        await message.answer('Вы не ввели показания, как попдись к фотографии \n'
                             'Попробуйте отправить фотографию еще раз\nОбязательно с подписью')


@router.message(Zone.fhoto3, F.photo)
async def get_fhoto3(message: Message, state: FSMContext):
    """Функция добавления фотографии 3 тарифа прибора учета"""
    await state.update_data(photo3=[message.photo[-1].file_id, message.caption])
    if message.caption is not None:
        my_data = await state.get_data()
        logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                    f' зашел в четвертый стэйт, показания {message.caption}')
        save_counter(session, message.from_user.id, get_meter_id(session, my_data['meter_nomer'])[2][0],
                     my_data['photo3'][1], my_data['photo3'][0])
        await message.answer('Переходите к следующему счетчику')
        await state.clear()
    else:
        await message.answer('Вы не ввели показания, как попдись к фотографии \n'
                             'Попробуйте отправить фотографию еще раз\nОбязательно с подписью')


@router.message(LostMeter.lost_data)
async def save_lost_data(message: Message, state: FSMContext, bot: Bot):
    """Функция добавления потерянного прибора учета из стейта"""
    data = message.text.split(' ')
    await bot.send_message(chat_id=get_admins(session)[0], text=message.text)
    await message.answer('Данные переданы администратору \n'
                         'для принятия дальнейшего решения \n'
                         'Спасибо!')
    await state.clear()
    logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                f' передал потерянный счетчик админу {data}')
