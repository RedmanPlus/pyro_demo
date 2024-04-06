from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.settings import Settings


engine = create_async_engine(Settings.db_url)
SessionLocal = async_sessionmaker(autoflush=False, autocommit=False, bind=engine)


def get_session() -> AsyncSession:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


Session = Annotated[AsyncSession, Depends(get_session)]
