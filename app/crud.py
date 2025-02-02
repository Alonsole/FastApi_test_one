from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Advertisement, ORM_CLS, ORM_OBJ
from sqlalchemy.exc import IntegrityError


async def create_advertisement(session: AsyncSession, advertisement: ORM_OBJ):
    """Создание нового объявления"""
    db_advertisement = Advertisement(
        title=advertisement.title,
        description=advertisement.description,
        price=advertisement.price,
        author=advertisement.author,
        user_id=advertisement.user_id
    )
    session.add(db_advertisement)
    try:
        await session.commit()  # Сохраняем изменения в базе данных
        await session.refresh(db_advertisement)  # Обновляем объект в сессии
        return db_advertisement
    except IntegrityError:
        raise HTTPException(409, "Error. Advertising not created")


async def delete_advertisement(session: AsyncSession, advertisement: ORM_OBJ, advertisement_id: int):
    """Удаление объявления"""
    advertisement_orm_obj = await get_item(session, advertisement, advertisement_id)
    await session.delete(advertisement_orm_obj)
    await session.commit()


async def get_id_advertisement(session: AsyncSession, orm_cls: ORM_CLS, advertisement_id: int):
    """Получить объявление по ID"""
    advertisement_orm_obj = await session.get(orm_cls, advertisement_id)
    if advertisement_orm_obj is None:
        raise HTTPException(404, f"Advertisement not found")
    return advertisement_orm_obj


async def get_field_advertisement(session: AsyncSession, orm_cls: ORM_CLS, item_params: dict):
    """Получить объявления по Значению поля"""
    query = select(orm_cls).filter_by(**item_params)
    result = await session.execute(query)
    advertisement_orm_obj = result.unique().scalars().all()
    if not advertisement_orm_obj:
        raise HTTPException(status_code=404, detail="items not found")
    return advertisement_orm_obj


async def update_advertisement(session: AsyncSession, advertisement_orm_obj, advertisement_dict, advertisement_id):
    """Обновить объявление по ID"""
    if advertisement_orm_obj is None:
        raise HTTPException(status_code=404, detail=f"Advertisement with id {advertisement_id} not found.")
    for field, value in advertisement_dict.items():
        setattr(advertisement_orm_obj, field, value)
    await session.commit()
    await session.refresh(advertisement_orm_obj)
    return advertisement_orm_obj


async def add_item(session: AsyncSession, item: ORM_OBJ):
    """Универсальная функция добавления"""
    session.add(item)
    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(409, "Item already exists")


async def get_item(session: AsyncSession, orm_cls: ORM_CLS, item_id: int) -> ORM_OBJ:
    """Универсальная функция получения"""
    orm_obj = await session.get(orm_cls, item_id)
    if orm_obj is None:
        raise HTTPException(status_code=404, detail="item not found")
    return orm_obj