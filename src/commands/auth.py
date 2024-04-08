import secrets
from typing import Annotated

from fastapi import Cookie
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import Session, UserSession


async def create_user_session(db: AsyncSession) -> UserSession:
    session = UserSession(session_key=secrets.token_urlsafe(32))
    db.add(session)
    await db.flush()
    await db.close()
    return session


async def get_session_by_key(session_key: str, db: AsyncSession) -> UserSession | None:
    async with db.begin():
        session_query = select(UserSession).where(UserSession.session_key == session_key)
        session = await db.scalar(session_query)
        return session


async def get_user_session(session_id: Annotated[str | None, Cookie()], db: Session) -> UserSession:
    if session_id is None:
        return await create_user_session(db=db)
    else:
        session = await get_session_by_key(session_key=session_id, db=db)
        if session is None:
            return await create_user_session(db=db)
        return session


User = Annotated[UserSession, Depends(get_user_session)]
