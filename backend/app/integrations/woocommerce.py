import httpx

from app.core.config import settings
from app.integrations.commerce import CommerceProvider
from app.models.product import Product
from app.services.image import ImageService


class WooCommerceProvider(CommerceProvider):

    def __init__(self):
        self.image_service = ImageService()

    def create_product(
        self,
        product: Product,
        custom_image_data: bytes | None = None,
        custom_image_filename: str | None = None,
        custom_image_content_type: str | None = None,
    ) -> dict:

        image = None

        # Custom uploaded image takes priority.
        if custom_image_data:
            image = self.image_service.upload_image(
                image_data=custom_image_data,
                filename=custom_image_filename or "book-cover.jpg",
                content_type=custom_image_content_type or "image/jpeg",
            )

        # Fall back to Google Books cover.
        elif product.book.cover_image_url:
            image = self.image_service.upload_cover(
                product.book.cover_image_url,
                self._build_image_filename(product),
            )

        description = self._build_description(product)

        payload = {
            "name": self._build_product_title(product),
            "type": "simple",
            "regular_price": (
                str(product.seller.original_price)
                if product.seller.original_price is not None
                else str(product.seller.selling_price)
            ),
            "sale_price": (
                str(product.seller.selling_price)
                if product.seller.original_price is not None
                else ""
            ),
            "manage_stock": True,
            "stock_quantity": product.seller.stock,
            "sku": product.seller.sku,
            "description": description,
            "short_description": description,
        }

        if product.category_ids:
            payload["categories"] = [
                {"id": category_id} for category_id in product.category_ids
            ]

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

    def get_categories(self) -> list[dict]:
        url = f"{settings.woocommerce_url}" "/wp-json/wc/v3/products/categories"

        response = httpx.get(
            url,
            auth=(
                settings.woocommerce_consumer_key,
                settings.woocommerce_consumer_secret,
            ),
            params={
                "per_page": 100,
                "hide_empty": False,
                "orderby": "name",
                "order": "asc",
            },
            timeout=15.0,
        )

        response.raise_for_status()

        categories = response.json()

        return [
            {
                "id": category["id"],
                "name": category["name"],
            }
            for category in categories
        ]

    def _build_image_filename(
        self,
        product: Product,
    ) -> str:
        isbn = product.book.isbn_13 or product.book.isbn_10 or "book"

        return f"{isbn}.jpg"

    def _build_product_title(
        self,
        product: Product,
    ) -> str:
        title = product.book.title or "Untitled Book"
        authors = ", ".join(product.book.authors)

        if authors:
            return f"{title} By {authors}"

        return title

    def _build_description(
        self,
        product: Product,
    ) -> str:
        book = product.book

        authors = ", ".join(book.authors)

        pages = f"{book.page_count} pages" if book.page_count else ""

        return f"""
<strong>About the Book:</strong>

{book.description or ""}

<strong>Author</strong>  :  {authors}
<strong>Publisher</strong>  :  {book.publisher or ""}
<strong>Publication date</strong>  :  {book.publication_date or ""}
<strong>Language</strong>  :  {book.language or ""}
<strong>{book.binding}</strong>  :  {pages}
<strong>ISBN-10</strong>  :  {book.isbn_10 or ""}
<strong>ISBN-13</strong>  :  {book.isbn_13 or ""}
"""
