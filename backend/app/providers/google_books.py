import httpx

from app.core.config import settings
from app.models.book import BookMetadata


class GoogleBooksProvider:
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

    def get_by_isbn(self, isbn: str) -> BookMetadata | None:
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

        return self._normalize(items[0])

    def _normalize(self, book: dict) -> BookMetadata:
        volume_info = book.get("volumeInfo", {})

        identifiers = {
            item["type"]: item["identifier"]
            for item in volume_info.get("industryIdentifiers", [])
        }

        image_links = volume_info.get("imageLinks", {})

        return BookMetadata(
            isbn_10=identifiers.get("ISBN_10"),
            isbn_13=identifiers.get("ISBN_13"),
            title=volume_info.get("title"),
            authors=volume_info.get("authors", []),
            publisher=volume_info.get("publisher"),
            publication_date=volume_info.get("publishedDate"),
            language=self._get_language(volume_info.get("language")),
            binding="Paperback",
            page_count=volume_info.get("pageCount"),
            reading_age=None,
            description=volume_info.get("description"),
            categories=volume_info.get("categories", []),
            cover_image_url=image_links.get("thumbnail"),
        )

    @staticmethod
    def _get_format(volume_info: dict) -> str | None:
        print_type = volume_info.get("printType")

        if print_type == "BOOK":
            return None

        return print_type

    @staticmethod
    def _get_language(language: str | None) -> str | None:
        language_map = {
            "en": "English",
            "hi": "Hindi",
            "mr": "Marathi",
            "fr": "French",
            "de": "German",
            "es": "Spanish",
            "it": "Italian",
            "pt": "Portuguese",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese",
            "ru": "Russian",
        }

        if not language:
            return None

        return language_map.get(
            language.lower(),
            language,
        )
