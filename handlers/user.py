from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from loguru import logger
from database.db import session, get_agents, get_meterid_bycontract
from aiogram.types import Message
from filters.filters import IsAdmin, IsAgent
from keyboards.userkb import user_kb

# Определение роутера для работы агента
router = Router(name='user')


class ContractId(StatesGroup):  # Стейт для текста сообщения для рассылки
    contract = State()


# @router.message(F.text.isdigit(), ~IsAgent(), ~IsAdmin())
# async def user_work(message: Message):
#     """Функция обработки ввода номера ПУ для простых потребителей"""
#     await message.answer('Вы простой потребитель, введите номер прибора учета', reply_markup=user_kb())
#     logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
#                 f' зашел как потребитель')


# @router.callback_query(F.data == 'user_counter')
# async def staff(callback: types.CallbackQuery, state: FSMContext):
#     """Функция обработки нажатия кнопки Передачи показаний"""
#     await callback.message.delete()
#     await callback.message.answer('Введите номер лицевого счета/договора')
#     await state.set_state(ContractId.contract)
#
#
# @router.message(ContractId.contract)
# async def get_meterdata(message: Message, state: FSMContext):
#     """Функция добавления номера ай ди админа из стейта"""
#     if message.text.isdigit():
#         # result, count = get_meterid_bycontract(sesion=session, contract=message.text)
#         result, count = get_meterid_bycontract(sesion=session, contract=message.text)
#         print(result, len(result))
#         print(count)
#         # for res in result:
#         #     print(res)
#         logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
#                     f' нашел номер договора {message.text}')
#         await message.answer('Даные найдены')
#         await state.clear()
#     else:
#         logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
#                     f' ввел номер договора с ошибкой {message.text}')
#         await message.answer('Вы ввели неверный номер договора')


