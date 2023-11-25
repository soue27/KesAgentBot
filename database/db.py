"""Модуль для работы с базой данных """
import os
from typing import Any

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from database.models import Base, Worker, Catalog, MeterData
from data.config import DB_URL, ECHO
import pandas as pd

# Получение движка и сессии для работы с базой данных
engine = create_engine(DB_URL, echo=ECHO)
Base.metadata.create_all(engine)
session = Session(engine)
connect = engine.connect()


def check_admin(sesion: Session, idd: int) -> bool | None:
    """Функция проверяет пользователя как админитстротора
        :param sesion - текущая сессия для работы с БД
        :param idd - Телеграм ай ди пользователя"""
    with sesion as ses:
        stmt = select(Worker.is_admin).where(Worker.tg_id == idd)
        return sesion.scalar(stmt)


def check_agent(sesion: Session, idd: int) -> bool | None:
    """Функция проверяет пользователя как админитстротора
        :param sesion - текущая сессия для работы с БД
        :param idd - Телеграм ай ди пользователя"""
    with sesion as ses:
        stmt = select(Worker.is_admin).where(Worker.tg_id == idd)
        print(sesion.scalar(stmt))
        return not sesion.scalar(stmt)


def get_admins(sesion: Session) -> Any:
    """Функция возвращает всех администраторов из базы данных
        :param sesion - текущая сессия для работы с БД"""
    with sesion as ses:
        stmt = select(Worker.tg_id).where(Worker.is_admin == True)
        return sesion.scalars(stmt).fetchall()


def get_agents(sesion: Session) -> Any:
    """Функция возвращает всех агентов из базы данных
        :param sesion - текущая сессия для работы с БД
        """
    with sesion as ses:
        stmt = select(Worker.tg_id).where(Worker.is_admin == False)
    # print(sesion.scalars(stmt).fetchall())
        return sesion.scalars(stmt).fetchall()


def get_agent_id(sesion: Session, idd: int):
    with sesion as ses:
        stmt = select(Worker.id).where(Worker.tg_id == idd)
    # print(sesion.scalar(stmt))
        return sesion.scalar(stmt)


def find_meter_by_nomer(sesion: Session, nomer: str) -> Any:
    """Функция для получения всех тарифов прибора учета по номеру
            :param sesion - текущая сессия для работы с БД
            :param nomer - номер прибора учета полностью или частично
            """
    with sesion as ses:
        stmt = select(Catalog.address, Catalog.meter_id).select_from(Catalog).where(Catalog.meter_id.contains(nomer))
        count = 0
        for item in sesion.execute(stmt).unique():
            count += 1
        return sesion.execute(stmt).unique(), count


def get_meter_id(sesion: Session, nomer: str) -> any:
    """Функция возвращает ай ди счетчиков результат поиска по номеру
                :param sesion - текущая сессия для работы с БД
                :param nomer - номер прибора учета полностью или частично
                """
    with sesion as ses:
        stmt = select(Catalog.id, Catalog.zone).select_from(Catalog).where(Catalog.meter_id == nomer)
        # print(sesion.scalars(stmt).fetchall())
        return sesion.execute(stmt).fetchall()


def get_meter_id_by_nomer_zone(sesion: Session, nomer: str, zone: str) -> int:
    """Функция отдает ай ди счетчика по номеру и зоне учета
                    :param sesion - текущая сессия для работы с БД
                    :param nomer - номер прибора учета полностью или частично
                    :param zone - номер прибора учета полностью или частично
                    """
    with sesion as ses:
        stmt = select(Catalog.id).select_from(Catalog).where((Catalog.meter_id == nomer) & (Catalog.zone == zone))
    # print(sesion.scalars(stmt).fetchall())
        return sesion.scalar(stmt)


def save_counter(sesion: Session, idd: int, number: int, pokazanie: str, photo_nomer: str):
    """Функция сохранения показания, фото и данных об агенте, номере счетчика в базу данных
                    :param sesion - текущая сессия для работы с БД
                    :param idd - телеграмм ай ди агента
                    :param number - ай ди номер прибора учета из базы данных
                    :param pokazanie - строка с показаниями тарифа прибора учета
                    :param photo_nomer - ай ди фотографии показаний прибора учета"""
    with sesion as ses:
        count = MeterData(
            agent_id=get_agent_id(session, idd),
            meter_id=number,
            counter=pokazanie,
            photo_id=photo_nomer)
        session.add(count)
        sesion.commit()


def save_worker(sesion: Session, idd: int, admin: bool) -> None:
    with sesion as ses:
        worker = Worker(
            tg_id=idd,
            is_admin=admin)
        session.add(worker)
        sesion.commit()


def load_data(filename: str, conn) -> int:
    """Функция производит загрузку данных из файла excel загруженного в бот
    и возвращает количество загруженных строк, что позволяет судить о правильности загрузки
            :param filename - полное имя файла excel для загрузки данных
            :param conn - connection к базе данных"""
    try:
        df = pd.read_excel(filename)
        df.to_sql(name='catalogs', con=connect, if_exists='append', index=False)
        connect.close()
        result = df.shape[0]
        df = None
        os.remove(filename)
        return result
    except:
        df = None
        os.remove(filename)
        return 0


def get_data(sesion: Session):
    with sesion as ses:
        stmt = sesion.query(Catalog.contract_id, Catalog.tu_code, Catalog.meter_id, Catalog.zone, MeterData.counter).join(Catalog).all()
        # for meterData, catalog in stmt:
        #     print(meterData)
        #     print(catalog)
        data = pd.DataFrame(stmt)
        data.to_excel('files\\upload.xlsx', index=False)
