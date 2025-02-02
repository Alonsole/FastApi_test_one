from bcrypt import checkpw, gensalt, hashpw
from sqlalchemy.ext.asyncio import AsyncSession
from models import ORM_OBJ, ORM_CLS, User, Token, Role, Right
from fastapi import HTTPException
from sqlalchemy import select, func
from config import DEFAULT_ROLE


def hash_password(password: str) -> str:
    return hashpw(password.encode(), gensalt()).decode()


def check_password(password: str, hashed_password: str) -> bool:
    return checkpw(password.encode(), hashed_password.encode())


async def get_default_role(session: AsyncSession) -> Role:
    return (await session.scalars(select(Role).where(Role.name == DEFAULT_ROLE))).first()


async def check_access_rights(
        session: AsyncSession,
        token: Token,
        model: ORM_OBJ | ORM_CLS,
        write: bool,
        read: bool,
        owner_field: str = "user_id",
        raise_exception: bool = True,
) -> bool:
    where_args = []

    where_args.append(
        User.id == Token.user_id
    )
    where_args.append(
        Right.model == model._model
    )
    if write:
        where_args.append(
            Right.write == True
        )
    if read:
        where_args.append(
            Right.read == True
        )

    if hasattr(model, owner_field) and getattr(model, owner_field) != token.user.id:
        where_args.append(
            Right.only_own == False
        )
    right_query = (
        select(func.count(User.id)).join(Role, User.roles).join(Right, Role.rights).
        where(*where_args)
    )

    rights_count = await session.scalar(right_query)
    if rights_count == 0 and raise_exception:
        raise HTTPException(403, "Access denied")
    return rights_count > 0
