"""Модуль для декларативного описания таблиц в базе данных"""
import datetime

from sqlalchemy import String, ForeignKey, Integer, Date, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовый класс для объявления таблиц"""
    id: Mapped[int] = mapped_column(primary_key=True)


class Worker(Base):
    """Класс для описания существующих агентов и админов"""
    __tablename__ = 'workers'
    tg_id: Mapped[int] = mapped_column(Integer, unique=True)
    is_admin: Mapped[Boolean | None] = mapped_column(Boolean, default=False)
    # Связи с другими таблицами
    metersdates: Mapped[list['MeterData']] = relationship(back_populates='worker')

    def __str__(self):
        return f'Worker(id={self.id!r}, tg_id={self.tg_id!r}, is_admin={self.is_admin!r})'

    def __repr__(self) -> str:
        return str(self)


class Catalog(Base):
    """Класс для описания справочной информации по контрагентам"""
    __tablename__ = 'catalogs'
    name: Mapped[str] = mapped_column(String(200))
    contract_id: Mapped[str] = mapped_column(String(20))
    tu_code: Mapped[int] = mapped_column(Integer)
    address: Mapped[str] = mapped_column(String(100))
    meter_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    meter_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    zone: Mapped[str | None] = mapped_column(String(10), nullable=True)
    # Связи с другими таблицами
    metersdates: Mapped[list['MeterData']] = relationship(back_populates='catalog')

    def __str__(self):
        return (f'Catalog(id={self.id!r}, name={self.name}, contract_id={self.contract_id},'
                f' tu_code={self.tu_code!r}, address:={self.address}, meter_type={self.meter_type},'
                f'meter_id={self.meter_id}, zone={self.zone}')

    def __repr__(self) -> str:
        return str(self)


class MeterData(Base):
    """Класс для описания сбора показаний"""
    __tablename__ = 'metersdates'
    agent_id: Mapped[int] = mapped_column(ForeignKey('workers.id'))
    meter_id: Mapped[int] = mapped_column(ForeignKey('catalogs.id'))
    counter: Mapped[str] = mapped_column(String(20))
    counter_date: Mapped[Date] = mapped_column(Date, default=datetime.date.today())
    photo_id: Mapped[str] = mapped_column(String(100))
    # Связи с другими таблицами
    worker: Mapped['Worker'] = relationship(back_populates='metersdates')
    catalog: Mapped['Catalog'] = relationship(back_populates='metersdates')

    def __str__(self):
        return (f'MeterData(id={self.id!r}, agent_id={self.agent_id!r}, meter_id={self.meter_id!r},'
                f' counter={self.counter!r}, counter_date:={self.counter_date:!r}, photo_id={self.photo_id!r},')

    def __repr__(self) -> str:
        return str(self)
