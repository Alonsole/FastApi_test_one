from fastapi import FastAPI, Depends
from schema import CreateAdvertisement, UpdateAdvertisement, DeleteAdvertisement, FindIdAdvertisement, \
    FindFieldAdvertisement, FindFieldAdvertisementRequest, CreateAdvertisementRequest
import crud
import models
from dependancy import SessionDependency
from typing import List
from lifespan import lifespan

app = FastAPI(
    title="Advertisement Api",
    terms_of_service="",
    description="Advertisement Api - purchase sale",
    lifespan=lifespan
)

SUCCESS_RESPONSE = {"status": "success"}


@app.post(path="/advertisement", tags=["Create Advertisement"], response_model=CreateAdvertisement)
async def create_advertisement(advertisement: CreateAdvertisementRequest,
                               session: SessionDependency):
    """
    Функция запуска создания объявления. Вернёт:
    'id', 'title', 'description', 'price', 'author'
    """
    advertisement_dict = advertisement.model_dump(exclude_unset=True)
    advertisement_orm_obj = models.ORM_OBJ(**advertisement_dict)
    new_advertisement = await crud.create_advertisement(session, advertisement_orm_obj)
    return new_advertisement.dict


@app.get(path="/advertisement/{advertisement_id}", tags=["Find Id Advertisement"], response_model=FindIdAdvertisement)
async def get_id_advertisement(advertisement_id: int, session: SessionDependency):
    """
    Функция запуска запроса Объявления по ID. Вернёт:
    'id', 'title', 'description', 'price', 'author', 'created_at'
    """
    advertisement_orm_obj = await crud.get_id_advertisement(session, models.ORM_OBJ, advertisement_id)
    return advertisement_orm_obj.dict


@app.get(path="/advertisement", tags=["Find Field Advertisement"], response_model=List[FindFieldAdvertisement])
async def get_field_advertisement(session: SessionDependency,
                                  request: FindFieldAdvertisementRequest = Depends()
                                  ):
    """
    Функция запуска запроса Объявления по Query string. Вернёт:
    'id', 'title', 'description', 'price', 'author', 'created_at'
    """
    advertisement_dict = request.model_dump(exclude_none=True)
    advertisement_orm_obj = await crud.get_field_advertisement(session, models.ORM_OBJ, advertisement_dict)
    return [advertisement.dict for advertisement in advertisement_orm_obj]


@app.patch("/advertisement/{advertisement_id}", tags=["Update Advertisement"], response_model=UpdateAdvertisement)
async def update_advertisement(advertisement_id: int, advertisement: UpdateAdvertisement, session: SessionDependency):
    """
    Функция запуска обновления Объявления по ID. Вернёт:
    'title', 'description', 'price'
    """
    advertisement_dict = advertisement.model_dump(exclude_unset=True)
    advertisement_orm_obj = await crud.get_id_advertisement(session, models.ORM_OBJ, advertisement_id)
    await crud.update_advertisement(session, advertisement_orm_obj, advertisement_dict, advertisement_id)
    return advertisement_orm_obj.dict


@app.delete("/advertisement/{advertisement_id}", tags=["Delete Advertisement"], response_model=DeleteAdvertisement)
async def delete_advertisement(advertisement_id: int, session: SessionDependency):
    """
    Функция запуска удаления Объявления по ID.
    """
    advertisement_orm_obj = await crud.get_id_advertisement(session, models.ORM_OBJ, advertisement_id)
    await crud.delete_advertisement(session, advertisement_orm_obj)
    return SUCCESS_RESPONSE