from datetime import timedelta
from enum import Enum
from typing import Optional

import sqlalchemy
from sqlalchemy import ForeignKey, LargeBinary, String
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column, relationship

from src.db.types import code_id, pk


class Base(DeclarativeBase):
    type_annotation_map = {
        Enum: sqlalchemy.Enum(Enum, native_enum=False),
    }

    @classmethod
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Session(Base):
    """
    Contains the session key of the exact user who had been sending the code to run
    Useful to give him all the info on the runs in case the connection with the frontend was broken mid-run
    """

    pk: Mapped[pk]
    session_key: Mapped[str] = mapped_column(String(48))
    code_runs: Mapped[list["CodeRun"]] = relationship(back_populates="session")


class CodeRun(Base):
    """
    Base table for holding code run attempts

    Holds the code that was requested to run, status of all used docker containers in the run and
    the relations to the objects with the result of an execution
    """

    pk: Mapped[pk]
    session_id: Mapped[int] = mapped_column(ForeignKey("session.pk"))
    session: Mapped[Session] = relationship(back_populates="code_runs")
    run_result: Mapped[Optional["RunResult"]] = relationship(back_populates="code_run")
    run_missmatch_error: Mapped[Optional["RunMissmatchError"]] = relationship(
        back_populates="code_run"
    )
    build_error: Mapped[Optional["BuildError"]] = relationship(back_populates="code_run")

    code: Mapped[str]
    pyro_docker_id: Mapped[bytes] = mapped_column(LargeBinary(12))
    pyro_docker_debug_id: Mapped[bytes] = mapped_column(LargeBinary(12))
    pyro_docker_status: Mapped[str]
    interpret_docker_id: Mapped[bytes] = mapped_column(LargeBinary(12))
    interpret_docker_debug_id: Mapped[bytes] = mapped_column(LargeBinary(12))
    interpret_docker_status: Mapped[str]


class RunResult(Base):
    """
    A successful run result

    Contains all the performance metrics that might be useful for the user:

    - Code compilation speed
    - Runtime speed
    - Memory footprint
    """

    pk: Mapped[pk]
    code_id: Mapped[code_id]
    code: Mapped[CodeRun] = relationship(back_populates="run_result")

    pyro_compilation_time: Mapped[timedelta]
    pyro_runtime: Mapped[timedelta]
    pyro_memory_usage: Mapped[Optional[int]]
    interpret_compilation_time: Mapped[timedelta]
    interpret_runtime: Mapped[timedelta]
    interpret_memory_usage: Mapped[Optional[int]]


class RunMissmatchError(Base):
    """
    A result of a separate debug run that was unsuccessful

    Debug run adds debug print statements to the variables in the interpreted version of the code
    and adds `printf("%llu")` directives to the assembly to inspect if the code functions correctly

    Two stdout outputs are compared together, and this record is created only in case if the output
    of the pyro-compiled program is incorrect
    """

    pk: Mapped[pk]
    code_id: Mapped[code_id]
    code: Mapped[CodeRun] = relationship(back_populates="run_missmatch_error")
    interpret_run_result: Mapped[str]
    pyro_run_result: Mapped[str]


class BuildError(Base):
    """
    Holds an information on unhandled errors (e.g. Unreachable) that are the
    result of internal compiler bugs, and not the wrong code semantics

    Holds the abridged stack trace with the information of which file has errored
    and what line raised the exception
    """

    pk: Mapped[pk]
    code_id: Mapped[code_id]
    code_run: Mapped[CodeRun] = relationship(back_populates="build_error")

    filename: Mapped[str]
    line: Mapped[int]
