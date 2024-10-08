"""Модуль для работы с базой данных """
import datetime
import os
from typing import Any

from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import Session, aliased
from database.models import Base, Worker, Catalog, MeterData, LostMeter
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
        return sesion.scalars(stmt).fetchall()


def get_agent_id(sesion: Session, idd: int):
    with sesion as ses:
        stmt = select(Worker.id).where(Worker.tg_id == idd)
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
        return sesion.execute(stmt).unique().all(), count


def get_meter_id(sesion: Session, nomer: str) -> any:
    """Функция возвращает ай ди счетчиков результат поиска по номеру
                :param sesion - текущая сессия для работы с БД
                :param nomer - номер прибора учета полностью или частично
                """
    with sesion as ses:
        stmt = select(Catalog.id, Catalog.zone).select_from(Catalog).where(Catalog.meter_id == nomer)
        return sesion.execute(stmt).fetchall()


def get_meter_id_by_nomer_zone(sesion: Session, nomer: str, zone: str) -> int:
    """Функция отдает ай ди счетчика по номеру и зоне учета
                    :param sesion - текущая сессия для работы с БД
                    :param nomer - номер прибора учета полностью или частично
                    :param zone - номер прибора учета полностью или частично
                    """
    with sesion as ses:
        stmt = select(Catalog.id).select_from(Catalog).where((Catalog.meter_id == nomer) & (Catalog.zone == zone))
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
            counter_date=datetime.date.today(),
            photo_id=photo_nomer)
        session.add(count)
        sesion.commit()


def save_worker(sesion: Session, idd: int, admin: bool) -> None:
    """Функция записи агента или админа в базу данных
                        :param sesion - текущая сессия для работы с БД
                        :param idd - телеграмм ай ди агента
                        :param admin - True если работник является админом"""
    with sesion as ses:
        worker = Worker(
            tg_id=idd,
            is_admin=admin)
        session.add(worker)
        sesion.commit()


def save_lost(sesion: Session, data: list) -> bool:
    """Функция записи не найденного счетчика в базу данных
                            :param sesion - текущая сессия для работы с БД
                            :param data - словарь с данными счетчика"""
    with sesion as ses:
        match len(data):
            case 2:
                lost = LostMeter(meter_id=data[0], counter1=data[1], counter_date=datetime.date.today())
            case 3:
                lost = LostMeter(meter_id=data[0], counter1=data[1], counter2=data[2], counter_date=datetime.date.today())
            case 4:
                lost = LostMeter(meter_id=data[0], counter1=data[1], counter2=data[2], counter3=data[2],
                                 counter_date=datetime.date.today())
            case _:
                sesion.commit()
                return False
        session.add(lost)
        sesion.commit()
        return True


def load_data(filename: str, conn: connect) -> int:
    """Функция производит загрузку данных из файла excel загруженного в бот
    и возвращает количество загруженных строк, что позволяет судить о правильности загрузки
            :param filename - полное имя файла excel для загрузки данных
            :param conn - connection к базе данных"""
    try:
        df = pd.read_excel(filename, dtype=str)
        df.to_sql(name='catalogs', con=engine, if_exists='append', index=False)
        result = df.shape[0]
        print(result)
        del df
        os.remove(filename)
        return result
    except:
        #del df
        os.remove(filename)
        return 0


def get_data(sesion: Session, data: str, for_sales: bool) -> None:
    """Функция производит выгрузку данных из базы данных для
    месяца года для передачи в сбыт и расчетам с агентами
                :param sesion - текущая сессия для работы с БД
                :param data str - строка представления года и месяца
                :param for_sales - если True, то выгрузка для сбыта"""
    with sesion as ses:
        # stmt = session.query(Worker.id, Worker.tg_id, Catalog.name, Catalog.contract_id, Catalog.tu_code,
        #                      Catalog.address, Catalog.meter_id, Catalog.zone, MeterData.counter,
        #                      MeterData.counter_date).join(MeterData, Worker.id == MeterData.agent_id).join(
        #                      Catalog, MeterData.meter_id == Catalog.id).all()
        stmt = session.query(Worker.id, Worker.tg_id, Catalog.name, Catalog.contract_id, Catalog.tu_code,
                             Catalog.address, Catalog.meter_id, Catalog.zone, MeterData.counter,
                             MeterData.counter_date).join(MeterData, Worker.id == MeterData.agent_id).join(
            Catalog, MeterData.meter_id == Catalog.id).where(MeterData.counter_date.like(data))
        datafr = pd.DataFrame(stmt)
        if not for_sales:
            datafr.to_excel('files\\upload.xlsx', index=False)
            del datafr
        else:
            df1 = datafr.loc[datafr['zone'].str.lower() == "день"]
            df2 = datafr.loc[datafr['zone'].str.lower() == "ночь"]
            df3 = df1.merge(df2, on=['meter_id'])
            df4 = datafr.loc[datafr['zone'].str.lower() == "кр/сут"]
            df5 = pd.concat([df3, df4], ignore_index=True)
            df5.to_excel('files\\upload.xlsx', index=False)


def get_photo(sesion: Session, nomer: str, isnomer: bool) -> list:
    """Функция возвращает фото по ай ди прибора учета
                :param sesion - текущая сессия для работы с БД
                :param nomer - номер прибора учета полностью или частично
                :param isnomer - номер прибора учета полностью
                """
    with sesion as ses:
        my_photo = []
        if isnomer:
            stmt = select(Catalog.id).where(Catalog.meter_id == nomer)
        else:
            stmt = select(Catalog.id).where(Catalog.contract_id == nomer)
        for nomer in sesion.scalars(stmt).fetchall():
            stmt = select(MeterData.photo_id, MeterData.counter_date).select_from(MeterData).where(
                MeterData.meter_id == nomer).order_by(desc(MeterData.counter_date))
            my_photo.append(sesion.execute(stmt).all())
        return my_photo


def delete_meter(sesion: Session, nomer: str):
    """Функция удаляет прибор учета из базы данных
                :param sesion - текущая сессия для работы с БД
                :param nomer - номер прибора учета полностью
                """
    with sesion as ses:
        sesion.query(Catalog).filter(Catalog.meter_id == nomer).delete()
        sesion.commit()


def change_meter(sesion: Session, nomer: str, cat: str, value: str) -> int:
    """Функция изменяет данные прибора учета в базы данных, возвращает количество изменных записей
                :param sesion - текущая сессия для работы с БД
                :param nomer - номер прибора учета полностью
                :param cat - метка данных для изменения (ФИО, адрес, номер л/с)
                :param value - новое значение для прибора учета полностью
                """
    with sesion as ses:
        changes = sesion.query(Catalog).filter(Catalog.meter_id == nomer).all()
        for change in changes:
            match cat:
                case 'upd_name':
                    change.name = value
                    sesion.commit()
                case 'upd_contract':
                    change.contract_id = value
                    sesion.commit()
                case 'upd_type':
                    change.meter_type = value
                    sesion.commit()
                case 'upd_address':
                    change.address = value
                    sesion.commit()
    return len(changes)


def get_staff(sesion: Session) -> None:
    """Функция для получения всех агентов и администраторов бота
            :param sesion - текущая сессия для работы с БД
            """
    with sesion as ses:
        stmt = sesion.query("*").select_from(Worker)
        datafr = pd.DataFrame(stmt)
        datafr.to_excel('files\\staff.xlsx', index=False)
        del datafr
        sesion.commit()


def del_staff(sesion: Session, idd: int) -> None:
    """Функция для удаления работника из базы данных по id
            :param sesion - текущая сессия для работы с БД
            :param idd - ай ди номер работника
            """
    with sesion as ses:
        sesion.query(Worker).filter(Worker.tg_id == idd).delete()
        sesion.commit()


def get_info_meters(sesion: Session, nomer: str) -> Any:
    """Функция возвращает информацию о приборе учета по введенному номеру
                :param sesion - текущая сессия для работы с БД
                :param nomer - номер прибора учета полностью или частично
                """
    with sesion as ses:
        stmt = select("*").select_from(Catalog).where(Catalog.meter_id.contains(nomer))
        return sesion.execute(stmt).all()

# Раздел для работы с таблицей показаний, полученных от потребителей


def get_meterid_bycontract(sesion: Session, contract: str) -> any:
    """Функция возвращает ай ди счетчиков результат поиска по номеру договора
                :param sesion - текущая сессия для работы с БД
                :param contract - номер прибора учета полностью или частично
                """
    with sesion as ses:
        count = 0
        stmt = select(Catalog.contract_id, Catalog.meter_id).select_from(Catalog).where(Catalog.contract_id == contract)
        stmt1 = select(Catalog.id, Catalog.zone).select_from(Catalog).where(Catalog.contract_id == contract)
        for item in sesion.execute(stmt).unique():
            count += 1
        return sesion.execute(stmt).all(), count

        # with sesion as ses:
        #     stmt = select(Catalog.address, Catalog.meter_id).select_from(Catalog).where(
        #         Catalog.meter_id.contains(nomer))
        #     count = 0
        #     for item in sesion.execute(stmt).unique():
        #         count += 1
        #     return sesion.execute(stmt).unique(), count