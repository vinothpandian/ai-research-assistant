from typing import Generic, List, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class Pagination(BaseModel, Generic[DataT]):
    total_items: int
    start: int
    limit: int
    items: List[DataT]
