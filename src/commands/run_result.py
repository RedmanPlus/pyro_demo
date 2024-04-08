from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import CodeRun, RunResult


async def create_run_result(
    db: AsyncSession,
    run: CodeRun,
    pyro_compile_time: timedelta,
    pyro_runtile: timedelta,
    pyro_memory_usage: int,
    interpret_compile_time: timedelta,
    interpret_runtime: timedelta,
    interpret_memory_usage: int,
) -> RunResult:
    async with db.begin():
        result = RunResult(
            code=run,
            pyro_compilation_time=pyro_compile_time,
            pyro_runtime=pyro_runtile,
            pyro_memory_usage=pyro_memory_usage,
            interpret_compilation_time=interpret_compile_time,
            interpret_runtime=interpret_runtime,
            interpret_memory_usage=interpret_memory_usage,
        )
        db.add(result)
        await db.flush()
        await db.close()

        return result


async def get_run_result(db: AsyncSession, run: CodeRun) -> RunResult | None:
    async with db.begin():
        query = select(RunResult).where(RunResult.code == run)
        run = await db.scalar(query)
        return run
