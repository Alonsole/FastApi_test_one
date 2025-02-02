from fastapi import FastAPI, Depends, HTTPException
from schema import CreateAdvertisement, UpdateAdvertisement, DeleteAdvertisement, FindIdAdvertisement, \
    FindFieldAdvertisement, FindFieldAdvertisementRequest, CreateAdvertisementRequest, LoginRequest, LoginResponse, \
    CreateUserResponse, CreateUserRequest, GetUserResponse, UpdateUserResponse, UpdateUserRequest, DeleteUserResponse
import crud
import models
from dependancy import SessionDependency, TokenDependency
from typing import List
from lifespan import lifespan
import auth
from sqlalchemy import select, delete

app = FastAPI(
    title="Advertisement Api",
    terms_of_service="",
    description="Advertisement Api - purchase sale",
    lifespan=lifespan
)

SUCCESS_RESPONSE = {"status": "success"}


@app.post(path="/advertisement", tags=["Create Advertisement"], response_model=CreateAdvertisement)
async def create_advertisement(advertisement: CreateAdvertisementRequest,
                               session: SessionDependency,
                               token: TokenDependency):
    """
    Функция запуска создания объявления. Вернёт:
    'id', 'title', 'description', 'price', 'author'
    """
    advertisement_dict = advertisement.model_dump(exclude_none=True)
    advertisement_orm_obj = models.Advertisement(user_id=token.user_id, **advertisement_dict)
    await auth.check_access_rights(session, token, advertisement_orm_obj, write=True, read=False)
    new_advertisement = await crud.create_advertisement(session, advertisement_orm_obj)
    return new_advertisement.dict


@app.get(path="/advertisement/{advertisement_id}", tags=["Find Id Advertisement"], response_model=FindIdAdvertisement)
async def get_id_advertisement(advertisement_id: int,
                               session: SessionDependency):
    """
    Функция запуска запроса Объявления по ID. Вернёт:
    'id', 'title', 'description', 'price', 'author', 'created_at'
    """
    advertisement_orm_obj = await crud.get_id_advertisement(session, models.Advertisement, advertisement_id)
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
    advertisement_orm_obj = await crud.get_field_advertisement(session, models.Advertisement, advertisement_dict)
    return [advertisement.dict for advertisement in advertisement_orm_obj]


@app.patch("/advertisement/{advertisement_id}", tags=["Update Advertisement"], response_model=UpdateAdvertisement)
async def update_advertisement(advertisement_id: int,
                               advertisement: UpdateAdvertisement,
                               session: SessionDependency,
                               token: TokenDependency):
    """
    Функция запуска обновления Объявления по ID. Вернёт:
    'title', 'description', 'price'
    """
    advertisement_dict = advertisement.model_dump(exclude_unset=True)
    advertisement_orm_obj = await crud.get_id_advertisement(session, models.Advertisement, advertisement_id)
    await auth.check_access_rights(session, token, advertisement_orm_obj, write=True, read=False)
    await crud.update_advertisement(session, advertisement_orm_obj, advertisement_dict, advertisement_id)
    return advertisement_orm_obj.dict


@app.delete("/advertisement/{advertisement_id}", tags=["Delete Advertisement"], response_model=DeleteAdvertisement)
async def delete_advertisement(advertisement_id: int,
                               session: SessionDependency,
                               token: TokenDependency):
    """
    Функция запуска удаления Объявления по ID.
    """
    advertisement_orm_obj = await crud.get_id_advertisement(session, models.Advertisement, advertisement_id)
    await auth.check_access_rights(session, token, advertisement_orm_obj, write=True, read=False)
    await crud.delete_advertisement(session, models.Advertisement, advertisement_id)
    return SUCCESS_RESPONSE


@app.post("/user/login", tags=["Login User"], response_model=LoginResponse)
async def login(login_data: LoginRequest, session: SessionDependency):
    """
    Вход и получение токена.
    Если вход первый создаётся токен.
    При повторном входе предыдущий токен будет удалён и создан новый.
    """
    user_query = select(models.User).where(models.User.name == login_data.name).execution_options()
    user = (await session.scalars(user_query)).first()
    if user is None:
        raise HTTPException(401, "Incorrect user or password")
    if not auth.check_password(login_data.password, user.password):
        raise HTTPException(401, "Incorrect user or password")
    # Удаляю существующий токен для данного пользователя
    delete_tokens_stmt = delete(models.Token).where(models.Token.user_id == int(user.id))
    await session.execute(delete_tokens_stmt)
    await session.commit()
    # Создаю новый токен юзеру
    new_token = models.Token(user_id=user.id)
    await crud.add_item(session, new_token)
    return new_token.dict


@app.post("/user/create", tags=["Create User"], response_model=CreateUserResponse)
async def create_user(user_data: CreateUserRequest,
                      session: SessionDependency):
    """Создание пользователя"""
    user_data_dict = user_data.dict()
    user_data_dict['password'] = auth.hash_password(user_data_dict["password"])
    user = models.User(**user_data_dict)
    role = await auth.get_default_role(session)
    user.roles = [role]
    await crud.add_item(session, user)
    return user.id_dict


@app.get("/user/{user_id}", tags=["Get User"], response_model=GetUserResponse)
async def get_user_by_id(
        session: SessionDependency,
        user_id: int):
    """Получить информацию о пользователе, его правах и его объявления"""
    user = await crud.get_item(session, models.User, user_id)
    return user.dict


@app.patch("/user/{user_id}", tags=["Update User"], response_model=UpdateUserResponse)
async def update_user(
        session: SessionDependency,
        update_user_request: UpdateUserRequest,
        user_id: int,
        token: TokenDependency):
    """
    Обновить Имя пользователя или пароль, или имя пользователя и пароль
    """
    user = await crud.get_id_advertisement(session, models.User, user_id)
    await auth.check_access_rights(session, token, user, write=True, read=False, owner_field="id")
    user_dict = update_user_request.model_dump(exclude_none=True)
    if 'password' in user_dict:  # Если передан пароль - зашифровать новый пароль
        user_dict['password'] = auth.hash_password(user_dict["password"])
    for key, value in user_dict.items():
        setattr(user, key, value)
    await crud.add_item(session, user)
    return user.id_dict



@app.delete("/user/{user_id}", tags=["Delete User"], response_model=DeleteUserResponse)
async def delete_user(
        session: SessionDependency,
        user_id: int,
        token: TokenDependency):
    """Удалить аккаунт"""
    user = await crud.get_id_advertisement(session, models.User, user_id)
    await auth.check_access_rights(session, token, user, write=True, read=False, owner_field="id")
    await crud.delete_advertisement(session, models.User, user_id)
    return SUCCESS_RESPONSE