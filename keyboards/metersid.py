"""Модуль для создания клавиатуры с потверждением выбора прибора учета"""
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import find_meter_by_nomer, session


def metersid_kb(meter_list, counter) -> InlineKeyboardMarkup:
    """Функция создания клавиатуры для выбора процесса работы бота"""
    builder = InlineKeyboardBuilder()
    metersid = meter_list
    print(metersid)
    count = counter
    if count == 0:
        builder.row(InlineKeyboardButton(text='Передайте информацию о счетчике администратору!', callback_data="0"))
        return builder.as_markup()
    # elif count < 7:
    if count == 1:
        print(metersid[0], metersid[1])
        try:
            lst = metersid[0].split(',')
            if 'кв.' in metersid[0]:
                street = lst[-3] + lst[-2] + lst[-1]
            else:
                street = lst[-2] + lst[-1]
        except IndexError:
            street = 'Без адреса'
        builder.row(InlineKeyboardButton(text=street + '  №' + metersid[1], callback_data=metersid[1]))
        return builder.as_markup(one_time_keyboard=True)
    else:
        for item in metersid:
            print(item[0], item[1])
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
