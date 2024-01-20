"""Модуль для создания клавиатуры для админа"""
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton


def main_kb() -> InlineKeyboardMarkup:
    """Функция создания главной клавиатуры для выбора процесса работы бота"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Персонал', callback_data="staff"))
    builder.row(InlineKeyboardButton(text='Выгрузки показаний', callback_data="uploads"))
    builder.row(InlineKeyboardButton(text='Найти фото прибора учета', callback_data="get_photo"))
    builder.row(InlineKeyboardButton(text='Операции с приборами учета', callback_data="meter_ops"))
    builder.row(InlineKeyboardButton(text='Резерв', callback_data="reserve1"))
    builder.row(InlineKeyboardButton(text='Резерв', callback_data="reserve2"))
    return builder.as_markup(one_time_keyboard=True)


def staff_kb() -> InlineKeyboardMarkup:
    """Функция создания клавиатуры для выбора операций с персоналом"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Добавить агента', callback_data="add_agent"))
    builder.row(InlineKeyboardButton(text='Добавить администратора', callback_data="add_admin"))
    builder.row(InlineKeyboardButton(text='Посмотреть всех', callback_data="wiew_staff"))
    builder.row(InlineKeyboardButton(text='Отправить сообщение пользователям', callback_data="send"))
    builder.row(InlineKeyboardButton(text='Удалить работника', callback_data="del_staff"))
    return builder.as_markup(one_time_keyboard=True)


def uploads_kb() -> InlineKeyboardMarkup:
    """Функция создания  клавиатуры для проведения выгрузок"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Сделать текущую выгрузку', callback_data="current_upload"))
    builder.row(InlineKeyboardButton(text='Сделать текущую выгрузка для сбыта', callback_data="sale_upload"))
    builder.row(InlineKeyboardButton(text='Сделать выгрузку за любой месяц', callback_data="upload"))
    return builder.as_markup(one_time_keyboard=True)


def meterops_kb() -> InlineKeyboardMarkup:
    """Функция создания  клавиатуры для проведения операций с приборами учета"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Изменить данные для прибора учета', callback_data="update"))
    builder.row(InlineKeyboardButton(text='Удалить прибор учета', callback_data="delete"))
    builder.row(InlineKeyboardButton(text='Просмотр данных прибора учета', callback_data="meter_info"))
    return builder.as_markup(one_time_keyboard=True)


def admin_kb() -> InlineKeyboardMarkup:
    """Функция создания клавиатуры для выбора процесса работы бота"""
    builder = InlineKeyboardBuilder()
    return builder.as_markup(one_time_keyboard=True)


def search_kb() -> InlineKeyboardMarkup:
    """Функция создания клавиатуры для выбора способа поиска фотографии из базы данных"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='По номеру счетчика', callback_data="by_number"))
    builder.row(InlineKeyboardButton(text='По номеру договора', callback_data="by_contract"))
    return builder.as_markup(one_time_keyboard=True)


def update_kb() -> InlineKeyboardMarkup:
    """Функция создания клавиатуры для выбора типа данных для изменения базы данных"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='ФИО, Наименование', callback_data="upd_name"))
    builder.row(InlineKeyboardButton(text='Номер л/с, Номер договора', callback_data="upd_contract"))
    builder.row(InlineKeyboardButton(text='Адрес точки учета', callback_data="upd_address"))
    builder.row(InlineKeyboardButton(text='Тип прибора учета', callback_data="upd_type"))
    return builder.as_markup(one_time_keyboard=True)