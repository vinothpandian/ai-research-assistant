from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, RootModel, field_serializer


class Author(BaseModel):
    name: str


class Article(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    title: str
    summary: str
    link: str
    authors: List[Author]

    @field_serializer('uuid')
    def serialize_uuid(self, uuid: UUID, _info):
        return str(uuid)


class ArticlesList(RootModel):
    root: List[Article]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]
