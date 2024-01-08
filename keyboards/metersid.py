"""Модуль для создания клавиатуры с потверждением выбора прибора учета"""
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import find_meter_by_nomer, session


def metersid_kb(nomer) -> InlineKeyboardMarkup:
    """Функция создания клавиатуры для выбора процесса работы бота"""
    builder = InlineKeyboardBuilder()
    metersid, count = find_meter_by_nomer(session, nomer)
    if count == 0:
        builder.row(InlineKeyboardButton(text='Передайте информацию о счетчике администратору!', callback_data="0"))
        return builder.as_markup()
    elif count < 7:
        for item in metersid:
            try:
                lst = item[0].split(',')
                if 'кв.' in item[0]:
                    street = lst[-3] + lst[-2] + lst[-1]
                else:
                    street = lst[-2] + lst[-1]
            except IndexError:
                street = 'Без адреса'
            builder.row(InlineKeyboardButton(text=street + '  №' + item[1], callback_data=item[1]))
        return builder.as_markup(one_time_keyboard=True)
