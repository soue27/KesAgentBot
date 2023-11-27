"""Модуль для создания клавиатуры для админа"""
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton


def admin_kb() -> InlineKeyboardMarkup:
    """Функция создания клавиатуры для выбора процесса работы бота"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Добавить администратора', callback_data="add_admin"))
    builder.row(InlineKeyboardButton(text='Добавить агента', callback_data="add_agent"))
    builder.row(InlineKeyboardButton(text='Выгрузить фото прибора учета', callback_data="get_photo"))
    builder.row(InlineKeyboardButton(text='Статистика по агенту', callback_data="agent_stat"))
    builder.row(InlineKeyboardButton(text='Сделать выгрузку показаний', callback_data="upload"))
    builder.row(InlineKeyboardButton(text='Резерв', callback_data="reserv"))
    return builder.as_markup(one_time_keyboard=True)


def search_kb() -> InlineKeyboardMarkup:
    """Функция создания клавиатуры для выбора способа поиска фотографии из базы данных"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='По номеру счетчика', callback_data="by_number"))
    builder.row(InlineKeyboardButton(text='По номеру договора', callback_data="by_contract"))
    return builder.as_markup(one_time_keyboard=True)