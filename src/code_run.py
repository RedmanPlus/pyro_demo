from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import CodeRun, UserSession


docker_statuses: list[str] = [
    "BUILD",
    "BUILD_SEEN",
    "RUNNING",
    "RUNNING_SEEN",
    "FINISHED",
    "FINISHED_SEEN",
    "ERROR",
    "ERROR_SEEN",
]

docker_reload_statuses: list[str] = [
    "BUILD",
    "BUILD_SEEN",
    "RUNNING",
    "RUNNING_SEEN",
    "FINISHED",
    "ERROR",
]


async def create_code_run(
    db: AsyncSession,
    user: UserSession,
    code: str,
    pyro_docker_id: bytes,
    pyro_docker_debug_id: bytes,
    interpret_docker_id: bytes,
    interpret_docker_debug_id: bytes,
) -> CodeRun:
    async with db.begin():
        run = CodeRun(
            session=user,
            code=code,
            pyro_docker_id=pyro_docker_id,
            pyro_docker_debug_id=pyro_docker_debug_id,
            pyro_docker_status="BUILD",
            interpret_docker_id=interpret_docker_id,
            interpret_docker_debug_id=interpret_docker_debug_id,
            interpret_docker_status="BUILD",
        )
        db.add(run)
        await db.flush()
        await db.close()
        return run


async def update_code_run_status(
    db: AsyncSession, run: CodeRun, pyro_docker_status: str, interpret_docker_status: str
) -> CodeRun:
    async with db.begin():
        run.pyro_docker_status = pyro_docker_status
        run.interpret_docker_status = interpret_docker_status
        await db.flush()
        await db.close()
        return run


async def get_active_code_run(
    db: AsyncSession,
    user: UserSession,
) -> CodeRun | None:
    async with db.begin():
        code_run_qs = select(CodeRun).where(
            CodeRun.session == user, CodeRun.pyro_docker_status.in_(docker_reload_statuses)
        )
        code_run = await db.scalar(code_run_qs)
        return code_run
