from fastapi import APIRouter

from app.schemas.book import ISBNRequest
from app.services.book_metadata import BookMetadataService
from app.providers.google_books import GoogleBooksProvider
from app.utils.isbn import validate_isbn


router = APIRouter(prefix="/books", tags=["Books"])

provider = GoogleBooksProvider()
metadata_service = BookMetadataService(provider)


@router.post("/validate-isbn")
def validate_book_isbn(request: ISBNRequest):
    is_valid, normalized_isbn = validate_isbn(request.isbn)

    if not is_valid:
        return {
            "valid": False,
            "isbn": None,
        }

    return {
        "valid": True,
        "isbn": normalized_isbn,
    }


@router.post("/lookup")
def lookup_book(request: ISBNRequest):
    is_valid, normalized_isbn = validate_isbn(request.isbn)

    if not is_valid:
        return {
            "found": False,
            "error": "Invalid ISBN",
        }

    book = metadata_service.get_by_isbn(normalized_isbn)

    if book is None:
        return {
            "found": False,
            "error": "Book not found",
        }

    return {
        "found": True,
        "data": book,
    }
