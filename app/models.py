import config
import asyncio
import traceback
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, text, ForeignKey, UUID, func, UniqueConstraint, \
    CheckConstraint, Table, Boolean
from sqlalchemy.orm import DeclarativeBase, relationship

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


# Промежуточная таблица многие к многим Role(роль) - Right(права)
role_rights = Table(
    "role_rights_relation",
    Base.metadata,
    Column("role_id", ForeignKey("role.id"), index=True),
    Column("right_id", ForeignKey("right.id"), index=True)
)


# Промежуточная таблица многие к многим Role(роль) - User(юзер)
user_roles = Table(
    "user_roles_relation",
    Base.metadata,
    Column("role_id", ForeignKey("role.id"), index=True),
    Column("user_id", ForeignKey("user.id"), index=True)
)


# таблица Права у роли (админ = все права, обычный юзер = ограниченные права)
class Right(Base):
    __tablename__ = "right"
    _model = "right"
    id = Column(Integer, primary_key=True)
    write = Column(Boolean, default=False)
    read = Column(Boolean, default=False)
    only_own = Column(Boolean, default=True)
    model = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint("model", "only_own", "read", "write"),
        CheckConstraint("model in ('user', 'advertisement', 'token', 'right', 'role')")
    )


# таблица Ролей (Админ, обычный юзер)
class Role(Base):
    __tablename__ = "role"
    _model = "role"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    rights = relationship(Right,
                          secondary=role_rights,
                          lazy="joined",
                          uselist=True
                          )

    @property
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "rights": [right.id for right in self.rights],
        }


class Token(Base):
    """Модель таблицы Хранения токенов]"""
    __tablename__ = "token"
    _model = "token"
    id = Column(Integer, primary_key=True)
    token = Column(UUID, unique=True, server_default=func.gen_random_uuid())
    creation_token = Column(DateTime, server_default=func.now())
    user_id = Column(ForeignKey("user.id"))
    user = relationship(
        "User",
        lazy="joined",
        back_populates="tokens"
    )

    @property
    def dict(self):
        return {"token": self.token}


class User(Base):
    """Модель таблицы Пользователи"""
    __tablename__ = "user"
    _model = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    password = Column(String)
    tokens = relationship('Token', back_populates='user')
    advertisements = relationship("Advertisement", back_populates="user", lazy="joined")
    roles = relationship(Role, secondary=user_roles, lazy="joined")

    @property
    def dict(self):
        return {"id": self.id,
                "name": self.name,
                "roles": [role.id for role in self.roles],
                "advertisements": [advertisement.id for advertisement in self.advertisements]
                }

    @property
    def model(self):
        return self._model


class Advertisement(Base):
    """Модель таблицы объявлений"""
    __tablename__ = 'advertisement'
    _model = "advertisement"
    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)  # Заголовок
    description = Column(String(500), nullable=True)  # Описание
    price = Column(Integer(), nullable=True)  # Цена
    author = Column(String(50), nullable=False)  # Автор
    created_at = Column(DateTime, default=datetime.now)  # дата создания
    # Доработка модели под аутентификацию и верификацию - принадлежность объявления
    user_id = Column(ForeignKey("user.id"))
    user = relationship("User", lazy="joined", back_populates="advertisements")

    @property
    def dict(self):
        return {
                'id': self.id,
                'title': self.title,
                'description': self.description,
                'price': self.price,
                'author': self.author,
                'created_at': self.created_at.isoformat(),
                'user_id': self.user_id
                }

    @property
    def model(self):
        return self._model


ORM_OBJ = Advertisement | User | Token | Role | Right
ORM_CLS = type[Advertisement] | type[User] | type[Token] | type[Role] | type[Right]


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
    await init_orm()  # залить ДБ и таблицы
    await close_orm()


if __name__ == "__main__":
    asyncio.run(main())