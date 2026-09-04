from pydantic import BaseModel


class BookMetadata(BaseModel):
    isbn_10: str | None = None
    isbn_13: str | None = None

    title: str | None = None
    authors: list[str] = []

    publisher: str | None = None
    publication_date: str | None = None
    language: str | None = None

    binding: str = "Paperback"
    page_count: int | None = None
    reading_age: str | None = None

    description: str | None = None
    categories: list[str] = []

    cover_image_url: str | None = None
