import re


def normalize_isbn(isbn: str) -> str:
    """Remove spaces and hyphens from an ISBN."""
    return re.sub(r"[\s-]", "", isbn).upper()


def validate_isbn(isbn: str) -> tuple[bool, str | None]:
    isbn = normalize_isbn(isbn)

    if len(isbn) == 13 and isbn.isdigit():
        if _validate_isbn13(isbn):
            return True, isbn

    if len(isbn) == 10 and re.fullmatch(r"\d{9}[\dX]", isbn):
        if _validate_isbn10(isbn):
            return True, isbn

    return False, None


def _validate_isbn13(isbn: str) -> bool:
    total = sum(
        int(digit) * (1 if index % 2 == 0 else 3) for index, digit in enumerate(isbn)
    )

    return total % 10 == 0


def _validate_isbn10(isbn: str) -> bool:
    total = sum(
        (10 - index) * (10 if digit == "X" else int(digit))
        for index, digit in enumerate(isbn)
    )

    return total % 11 == 0
