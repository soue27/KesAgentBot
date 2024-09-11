from aiogram.filters import BaseFilter
from aiogram.types import Message
from database.db import get_agents, get_admins, session


class IsAgent(BaseFilter):
    async def __call__(self, message: Message):
        if message.from_user.id in set(get_agents(session)):
            return True
        else:
            return False


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message):
        if message.from_user.id in set(get_admins(session)):
            return True
        else:
            return False


class IsMyDigit(BaseFilter):
    async def __call__(self, message: Message):
        if message.text is None:
            return False
        if any(map(str.isdigit, message.text)):
            return True
        else:
            return False
