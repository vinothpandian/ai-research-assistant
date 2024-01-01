from typing import Annotated, Iterable, List

from pydantic import AfterValidator, BaseModel, RootModel

from core.utils.text import clean_text


class CreateArticle(BaseModel):
    arxiv_id: str
    title: Annotated[str, AfterValidator(clean_text)]
    abstract: Annotated[str, AfterValidator(clean_text)]
    link: str
    published: str
    authors: List[str]


class Article(CreateArticle):
    id: str | None = None
    ai_summary: str = ""
    vector_id: str = ""


class ArticleWithScore(Article):
    score: float


class ArticlesList(RootModel):
    root: List[Article]

    def __iter__(self) -> Iterable[Article]:
        return iter(self.root)

    def __getitem__(self, item) -> Article:
        return self.root[item]

    def __len__(self) -> int:
        return len(self.root)

    def __bool__(self) -> bool:
        return bool(self.root)


class ArticlesWithScoreList(RootModel):
    root: List[ArticleWithScore]

    def __iter__(self) -> Iterable[Article]:
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)

    def __bool__(self) -> bool:
        return bool(self.root)
