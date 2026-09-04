from pydantic import BaseModel

from app.models.book import BookMetadata


class SellerInformation(BaseModel):
    selling_price: float | None = None
    original_price: float | None = None
    stock: int = 1


class Product(BaseModel):
    book: BookMetadata
    seller: SellerInformation
    category_ids: list[int] = []
