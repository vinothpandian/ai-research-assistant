from typing import Annotated, Iterable, List

from pydantic import AfterValidator, AwareDatetime, BaseModel, RootModel

from ..lib.text import clean_text


class Author(BaseModel):
    name: str


class ArxivArticle(BaseModel):
    id: str
    title: Annotated[str, AfterValidator(clean_text)]
    summary: Annotated[str, AfterValidator(clean_text)]
    link: str
    authors: List[Author]
    published: AwareDatetime


class ArxivArticlesList(RootModel):
    root: List[ArxivArticle]

    def __iter__(self) -> Iterable[ArxivArticle]:
        return iter(self.root)

    def __getitem__(self, item) -> ArxivArticle:
        return self.root[item]
