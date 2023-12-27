from fastapi import FastAPI

from .routers import article, arxiv

app = FastAPI(
    title="AI Research Assistant",
    description="API for AI Research Assistant",
    version="0.0.1",
    contact={
        "name": "Vinoth Pandian",
        "url": "https://vinoth.info",
        "email": "vinothpandian@users.noreply.github.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    docs_url="/",
)

app.include_router(arxiv.router)
app.include_router(article.router)
