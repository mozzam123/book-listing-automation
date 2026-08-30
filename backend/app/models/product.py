from pydantic import BaseModel

from app.models.book import BookMetadata


class SellerInformation(BaseModel):
    selling_price: float
    original_price: float | None = None
    stock: int = 1
    condition: str
    condition_notes: str | None = None


class Product(BaseModel):
    book: BookMetadata
    seller: SellerInformation
