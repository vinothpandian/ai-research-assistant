from typing import Annotated, Iterable, List

from pydantic import AfterValidator, AwareDatetime, BaseModel, RootModel

from core.lib.text import clean_text


class CreateArticle(BaseModel):
    arxiv_id: str
    title: Annotated[str, AfterValidator(clean_text)]
    abstract: Annotated[str, AfterValidator(clean_text)]
    link: str
    published: AwareDatetime
    authors: List[str]


class Article(CreateArticle):
    id: str | None = None
    ai_summary: str = ""
    vector_id: str = ""


class ArticlesList(RootModel):
    root: List[Article]

    def __iter__(self) -> Iterable[Article]:
        return iter(self.root)

    def __getitem__(self, item) -> Article:
        return self.root[item]
