from pydantic import BaseModel
from typing import Literal


class SuccessResponse(BaseModel):
    status: Literal["success"]


class CreateAdvertisementRequest(BaseModel):  # Создание объявления - Запрос
    title: str
    description: str
    price: int | None = None
    author: str


class CreateAdvertisement(BaseModel):  # Создание объявления - Ответ
    id: int
    title: str
    description: str
    price: int | None = None
    author: str


class UpdateAdvertisement(BaseModel):  # Обновление
    title: str
    description: str | None = None
    price: int | None = None


class DeleteAdvertisement(SuccessResponse):  # Удаление
    pass


class FindIdAdvertisement(BaseModel):  # Поиск по id - Ответ
    title: str
    description: str | None = None
    price: int | None = None
    author: str
    created_at: str


class FindFieldAdvertisementRequest(BaseModel):  # Поиск по значению - Запрос
    title: str | None = None
    description: str | None = None
    price: int | None = None


class FindFieldAdvertisement(BaseModel):  # Поиск по значению - Ответ
    id: int | None = None
    title: str | None = None
    description: str | None = None
    price: int | None = None
    author: str
    created_at: str