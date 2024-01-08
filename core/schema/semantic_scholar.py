from typing import Annotated, Iterable, List

from pydantic import AfterValidator, BaseModel, RootModel

from core.utils.validation import clean_text


class Author(BaseModel):
    name: str


class OpenAccessPdf(BaseModel):
    url: str


class SemanticScholarArticle(BaseModel):
    paperId: str
    title: Annotated[str | None, AfterValidator(clean_text)]
    abstract: Annotated[str | None, AfterValidator(clean_text)] = ""
    url: str
    authors: List[Author]
    publicationDate: str | None = None
    isOpenAccess: bool = False
    openAccessPdf: OpenAccessPdf | None = None


class SemanticScholarArticlesList(RootModel):
    root: List[SemanticScholarArticle]

    def __iter__(self) -> Iterable[SemanticScholarArticle]:
        return iter(self.root)

    def __getitem__(self, item) -> SemanticScholarArticle:
        return self.root[item]

    def __len__(self) -> int:
        return len(self.root)

    def __bool__(self) -> bool:
        return bool(self.root)
