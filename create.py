import httpx

# cleanup existing data
response = httpx.get("http://localhost:8000/articles/").json()

for item in response["items"]:
    httpx.delete(f"http://localhost:8000/articles/?article_id={item['id']}")

data = httpx.get("http://localhost:8000/arxiv/search/?q=test&start=0&limit=10").json()

for item in data["items"]:
    article = dict(
        arxiv_id=item["id"],
        title=item["title"],
        abstract=item["summary"],
        link=item["link"],
        published=item["published"],
        authors=[author["name"] for author in item["authors"]],
    )

    httpx.post("http://localhost:8000/articles/", json=article)
