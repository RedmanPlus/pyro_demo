from pydantic import BaseConfig


class Settings(BaseConfig):

    db_url: str = "postgresql+asyncpg://postgres:postgres@0.0.0.0:5432/test"
