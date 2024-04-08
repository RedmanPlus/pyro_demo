from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import CodeRun, RunMissmatchError


async def create_missmatch_error(
    db: AsyncSession, run: CodeRun, interpret_run_result: str, pyro_run_result: str
) -> RunMissmatchError:
    async with db.begin():
        missmatch = RunMissmatchError(
            code=run, interpret_run_result=interpret_run_result, pyro_run_result=pyro_run_result
        )
        db.add(missmatch)
        await db.flush()
        await db.close()

        return missmatch


async def get_missmatch_error(db: AsyncSession, run: CodeRun) -> RunMissmatchError | None:
    async with db.begin():
        query = select(RunMissmatchError).where(RunMissmatchError.code == run)
        missmatch = await db.scalar(query)
        return missmatch
