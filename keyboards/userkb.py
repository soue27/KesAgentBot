"""Модуль для создания клавиатуры для потребителей"""
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton


def user_kb() -> InlineKeyboardMarkup:
    """Функция создания главной клавиатуры для выбора процесса работы бота"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Передать показания', callback_data="user_counter"))
    builder.row(InlineKeyboardButton(text='Передать показания с фото', callback_data="user_counterphoto"))
    return builder.as_markup(one_time_keyboard=True)

