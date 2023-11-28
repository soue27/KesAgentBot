"""Модуль для создания клавиатуры с потверждением выбора прибора учета"""
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import find_meter_by_nomer, session


def metersid_kb(nomer) -> InlineKeyboardMarkup:
    """Функция создания клавиатуры для выбора процесса работы бота"""
    builder = InlineKeyboardBuilder()
    metersid, count = find_meter_by_nomer(session, nomer)
    print(count)
    if count == 0:
        builder.row(InlineKeyboardButton(text='Передайте информацию о счетчике администратору!', callback_data="0"))
        return builder.as_markup()
    elif count < 7:
        for item in metersid:
            try:
                street = item[0].split('ул.')[1]
            except IndexError:
                street = 'Без адреса'
            builder.row(InlineKeyboardButton(text=street + '  №' + item[1], callback_data=item[1]))
        return builder.as_markup(one_time_keyboard=True)
