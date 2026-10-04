import httpx

from app.models.book import BookMetadata
from app.providers.google_books import GoogleBooksProvider
from app.providers.open_library import OpenLibraryProvider


class BookMetadataService:

    def __init__(
        self,
        provider: GoogleBooksProvider,
        fallback_provider: OpenLibraryProvider | None = None,
    ):
        self.provider = provider
        self.fallback_provider = fallback_provider or OpenLibraryProvider()

    def get_by_isbn(self, isbn: str) -> BookMetadata | None:
        try:
            book = self.provider.get_by_isbn(isbn)
            if book is not None:
                return book
        except httpx.HTTPError:
            pass

        try:
            return self.fallback_provider.get_by_isbn(isbn)
        except httpx.HTTPError:
            return None
