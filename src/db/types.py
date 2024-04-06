from typing import Annotated

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column


pk = Annotated[int, mapped_column(primary_key=True)]
code_id = Annotated[int, mapped_column(ForeignKey("coderun.pk"))]
