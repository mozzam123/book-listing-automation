import httpx

from app.core.config import settings


class GoogleBooksProvider:
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

    def get_by_isbn(self, isbn: str) -> dict | None:
        params = {
            "q": f"isbn:{isbn}",
            "key": settings.google_books_api_key,
        }

        response = httpx.get(
            self.BASE_URL,
            params=params,
            timeout=10.0,
        )

        response.raise_for_status()

        data = response.json()

        items = data.get("items", [])

        if not items:
            return None

        return items[0]
