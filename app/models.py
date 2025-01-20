import config
import asyncio
import traceback
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, text
from sqlalchemy.orm import DeclarativeBase

# engine = create_async_engine(config.PG_DSN)
# Session = async_sessionmaker(bind=engine, expire_on_commit=False)

engine = create_async_engine(config.PG_DSN)
#  Асинхронный движок базы для создания Таблиц
engine_table = create_async_engine(f"{config.PG_DSN}/{config.DB_NAME}")
# Управление соединениями с базой данных и выполнение запросов
Session = async_sessionmaker(bind=engine_table, expire_on_commit=False)

class Base(DeclarativeBase, AsyncAttrs):
    @property
    def id_dict(self):
        """Получение id в виде Json"""
        return {"id": self.id}


class Advertisement(Base):
    """Модель таблицы объявлений"""
    __tablename__ = 'advertisement'
    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)  # Заголовок
    description = Column(String(500), nullable=True)  # Описание
    price = Column(Integer(), nullable=True)  # Цена
    author = Column(String(50), nullable=False)  # Автор
    created_at = Column(DateTime, default=datetime.now)  # дата создания

    @property
    def dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'author': self.author,
            'created_at': self.created_at.isoformat()
        }


ORM_OBJ = Advertisement
ORM_CLS = type[Advertisement]


async def init_orm():
    """
    Асинхронная функция для удаления и создания базы данных.
    """
    try:
        # Открываем соединение
        async with engine.connect() as conn:
            # Устанавливаем уровень изоляции
            await conn.execution_options(isolation_level="AUTOCOMMIT")
            # 1 Проверка и удаление + закрыть все активные соединения 2 Создание
            await conn.execute(text(f'DROP DATABASE IF EXISTS {config.DB_NAME} WITH (FORCE);'))  # 1
            await conn.execute(text(f'CREATE DATABASE {config.DB_NAME};'))  # 2
        # Создаем таблицы
        async with engine_table.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print(f'База данных {config.DB_NAME} успешно создана.')
    except Exception as e:
        print(f'Произошла ошибка при создании базы данных: {e} \n {traceback.format_exc()}')


async def close_orm():
    await engine.dispose()


async def main():
    await init_orm()  # залить таблицу
    await close_orm()


if __name__ == "__main__":
    asyncio.run(main())