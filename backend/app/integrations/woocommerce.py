import httpx

from app.core.config import settings
from app.integrations.commerce import CommerceProvider
from app.models.product import Product
from app.services.image import ImageService


class WooCommerceProvider(CommerceProvider):

    def __init__(self):
        self.image_service = ImageService()

    def create_product(self, product: Product) -> dict:
        image = None

        if product.book.cover_image_url:
            image = self.image_service.upload_cover(
                product.book.cover_image_url,
                self._build_image_filename(product),
            )

        payload = {
            "name": product.book.title or "Untitled Book",
            "type": "simple",
            "regular_price": str(product.seller.selling_price),
            "manage_stock": True,
            "stock_quantity": product.seller.stock,
            "description": self._build_description(product),
            "sku": product.book.isbn_13 or product.book.isbn_10,
        }

        if image:
            payload["images"] = [
                {
                    "id": image["id"],
                    "position": 0,
                }
            ]

        url = f"{settings.woocommerce_url}" "/wp-json/wc/v3/products"

        response = httpx.post(
            url,
            auth=(
                settings.woocommerce_consumer_key,
                settings.woocommerce_consumer_secret,
            ),
            json=payload,
            timeout=15.0,
        )

        response.raise_for_status()

        return response.json()

    def _build_image_filename(self, product: Product) -> str:
        isbn = product.book.isbn_13 or product.book.isbn_10 or "book"

        return f"{isbn}.jpg"

    def _build_description(self, product: Product) -> str:
        book = product.book

        authors = ", ".join(book.authors)

        description = book.description or ""

        return f"""About the Book:

{description}

Author  {authors}
Publisher  :  {book.publisher or ""}
Publication date  :  {book.publication_date or ""}
Language :  {book.language or ""}
{book.format or ""}  :  {f"{book.page_count} pages" if book.page_count else ""}
ISBN-10 : {book.isbn_10 or ""}
ISBN-13 :  {book.isbn_13 or ""}
"""
