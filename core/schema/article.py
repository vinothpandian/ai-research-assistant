from typing import Annotated, Iterator, List

from pydantic import AfterValidator, BaseModel, RootModel

from core.utils.validation import clean_text


class CreateArticle(BaseModel):
    arxiv_id: str
    title: Annotated[str, AfterValidator(clean_text)]
    abstract: Annotated[str, AfterValidator(clean_text)]
    link: str
    published: str
    authors: List[str]
    pdf_url: str | None = None


class Article(CreateArticle):
    id: str | None = None
    ai_summary: str = ""
    embeddings_generated: bool = False


class ArticleWithScore(Article):
    score: float
    chunks: List[str] = []


class ArticlesList(RootModel):
    root: List[Article]

    def __iter__(self) -> Iterator[Article]:
        return iter(self.root)

    def __getitem__(self, item) -> Article:
        return self.root[item]

    def __len__(self) -> int:
        return len(self.root)

    def __bool__(self) -> bool:
        return bool(self.root)


class ArticlesWithScoreList(RootModel):
    root: List[ArticleWithScore]

    def __iter__(self) -> Iterator[ArticleWithScore]:
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)

    def __bool__(self) -> bool:
        return bool(self.root)
