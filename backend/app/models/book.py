from pydantic import BaseModel


class BookMetadata(BaseModel):
    isbn_10: str | None = None
    isbn_13: str | None = None
    title: str | None = None
    subtitle: str | None = None
    authors: list[str] = []
    publisher: str | None = None
    publication_date: str | None = None
    description: str | None = None
    page_count: int | None = None
    categories: list[str] = []
    language: str | None = None
    cover_image_url: str | None = None
