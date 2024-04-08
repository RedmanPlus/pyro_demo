from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import BuildError, CodeRun


async def create_build_error(
    db: AsyncSession, run: CodeRun, filename: str, line: int
) -> BuildError:
    async with db.begin():
        error = BuildError(code=run, filename=filename, line=line)
        db.add(error)
        await db.flush()
        await db.close()

        return error


async def get_build_error(db: AsyncSession, run: CodeRun) -> BuildError | None:
    async with db.begin():
        query = select(BuildError).where(BuildError.code_run == run)
        error = await db.scalar(query)
        return error
