from app.providers.google_books import GoogleBooksProvider


class BookMetadataService:

    def __init__(self, provider: GoogleBooksProvider):
        self.provider = provider

    def get_by_isbn(self, isbn: str) -> dict | None:
        return self.provider.get_by_isbn(isbn)
