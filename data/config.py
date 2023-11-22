"""Модуль для загрузки переменных окружения"""
from dotenv import load_dotenv
import os
from settings import ADMIN, DB_URL, ECHO

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
DB_URL = DB_URL
ECHO = ECHO
admins = ADMIN
