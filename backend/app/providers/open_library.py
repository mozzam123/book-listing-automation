import httpx

from app.models.book import BookMetadata


class OpenLibraryProvider:
    BASE_URL = "https://openlibrary.org/isbn"
    USER_AGENT = "book-listing-automation/1.0"

    def get_by_isbn(self, isbn: str) -> BookMetadata | None:
        response = httpx.get(
            f"{self.BASE_URL}/{isbn}.json",
            headers={"User-Agent": self.USER_AGENT},
            timeout=10.0,
            follow_redirects=True,
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return self._normalize(response.json())

    def _normalize(self, data: dict) -> BookMetadata:
        authors = self._get_authors(data.get("authors", []))
        covers = data.get("covers", [])
        valid_covers = [cover_id for cover_id in covers if cover_id and cover_id > 0]

        return BookMetadata(
            isbn_10=self._first(data.get("isbn_10")),
            isbn_13=self._first(data.get("isbn_13")),
            title=data.get("title"),
            authors=authors,
            publisher=self._first(data.get("publishers")),
            publication_date=data.get("publish_date"),
            language=self._get_language(data.get("languages", [])),
            binding="Paperback",
            page_count=data.get("number_of_pages"),
            reading_age=None,
            description=self._get_text(data.get("description")),
            categories=data.get("subjects", []),
            cover_image_url=(
                f"https://covers.openlibrary.org/b/id/{valid_covers[0]}-L.jpg"
                if valid_covers
                else None
            ),
        )

    def _get_authors(self, author_refs: list[dict]) -> list[str]:
        authors = []

        for author in author_refs:
            key = author.get("key")
            if not key:
                continue

            try:
                response = httpx.get(
                    f"https://openlibrary.org{key}.json",
                    headers={"User-Agent": self.USER_AGENT},
                    timeout=5.0,
                )
                response.raise_for_status()
                name = response.json().get("name")
                if name:
                    authors.append(name)
            except httpx.HTTPError:
                continue

        return authors

    @staticmethod
    def _first(values: list | None):
        return values[0] if values else None

    @staticmethod
    def _get_text(value) -> str | None:
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            return value.get("value")
        return None

    @staticmethod
    def _get_language(languages: list[dict]) -> str | None:
        language_map = {
            "eng": "English",
            "hin": "Hindi",
            "mar": "Marathi",
            "fre": "French",
            "fra": "French",
            "ger": "German",
            "deu": "German",
            "spa": "Spanish",
            "ita": "Italian",
            "por": "Portuguese",
            "jpn": "Japanese",
            "kor": "Korean",
            "chi": "Chinese",
            "zho": "Chinese",
            "rus": "Russian",
        }

        if not languages:
            return None

        key = languages[0].get("key", "")
        code = key.rsplit("/", 1)[-1]
        return language_map.get(code, code or None)
