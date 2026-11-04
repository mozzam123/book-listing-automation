import re

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

        # Focus keyword is the product title (used as Rank Math focus keyword
        # and as image alt text for SEO).
        product_title = self._build_product_title(product)

        # Custom uploaded image takes priority.
        if custom_image_data:
            image = self.image_service.upload_image(
                image_data=custom_image_data,
                filename=custom_image_filename or "book-cover.jpg",
                content_type=custom_image_content_type or "image/jpeg",
                book_title=product_title,
            )

        # Fall back to Google Books cover.
        elif product.book.cover_image_url:
            image = self.image_service.upload_cover(
                product.book.cover_image_url,
                self._build_image_filename(product),
                book_title=product_title,
            )

        description = self._build_description(product)

        payload = {
            "name": product_title,
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
            "meta_data": [
                {
                    "key": "rank_math_focus_keyword",
                    "value": product_title,
                }
            ],
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
        # Product description targeting 600-650 words for SEO.
        # All paragraphs are short (2-4 sentences). Book description is capped
        # to the first 3 sentences to prevent very long descriptions from
        # inflating the word count. Required product detail format is preserved.
        book = product.book

        authors = ", ".join(book.authors) if book.authors else "Unknown Author"

        binding = book.binding or "Paperback"
        language = book.language or "English"
        publisher = book.publisher or "Publisher not specified"
        publication_date = book.publication_date or "Date not specified"
        pages = (
            f"{book.page_count} pages"
            if book.page_count
            else "page count not specified"
        )
        reading_age = book.reading_age or "Not specified"
        isbn_10 = book.isbn_10 or "Not available"
        isbn_13 = book.isbn_13 or "Not available"
        description = (book.description or "").strip()

        product_title = self._build_product_title(product)

        sections: list[str] = []

        if book.cover_image_url:
            sections.append(
                f'<strong><a href="{book.cover_image_url}" target="_blank" rel="noopener noreferrer">{product_title}</a></strong>'
            )
        else:
            sections.append(f"<strong>{product_title}</strong>")
        sections.append("")

        # About this book
        sections.append(f"<h2>About {product_title}</h2>")
        if description:
            # Cap book description to first 3 sentences for SEO word count
            sentences = re.split(r"(?<=[.!?])\s+", description.strip())
            desc_chunk = " ".join(sentences[:3]).strip()
            if desc_chunk:
                sections.append(desc_chunk)
                sections.append("")
            sections.append(
                f"{product_title} by {authors} is published by {publisher} and was released on {publication_date}."
            )
            sections.append("")
            sections.append(
                f"This {language} edition is presented in {binding} format with {pages}."
            )
            sections.append("")
            sections.append(
                f"Readers will find a complete presentation of the content, "
                f"carefully prepared for an engaging reading experience."
            )
        else:
            sections.append(
                f"Discover {product_title}, a {binding} edition authored by {authors}. Published by {publisher}."
            )
            sections.append("")
            sections.append(
                f"This {language} edition is presented in {binding} format with {pages}."
            )
            sections.append("")
            sections.append(
                f"The book offers a complete presentation suitable for readers interested in the subject matter."
            )
        sections.append("")

        # Book overview
        sections.append("<h2>Book Overview</h2>")
        sections.append(
            f"{product_title} by {authors} is published by {publisher} and was released on {publication_date}."
        )
        sections.append("")
        sections.append(
            f"Written in {language}, this {binding} edition contains {pages}."
        )
        sections.append("")
        sections.append(
            f"This book brings together thoughtful content and quality presentation, making it suitable for readers interested in the subject."
        )
        sections.append("")
        sections.append(
            f"The content is organized to provide a clear and engaging reading experience from beginning to end."
        )
        sections.append("")

        # Author information
        sections.append("<h2>Author Information</h2>")
        sections.append(
            f"The author of {product_title} is {authors}. This title represents the author's work published under the {publisher} imprint."
        )
        sections.append("")
        sections.append(
            f"Readers who enjoy this book may also appreciate other works by the same author."
        )
        sections.append("")
        sections.append(
            f"Understanding the author behind {product_title} adds context and depth to the reading experience."
        )
        sections.append("")
        sections.append(
            f"The author's contribution brings a distinctive voice and perspective to this edition."
        )
        sections.append("")

        # Key features
        sections.append("<h2>Key Features</h2>")
        sections.append(
            f"<ul>"
            f"<li>Title: {product_title}</li>"
            f"<li>Author: {authors}</li>"
            f"<li>Publisher: {publisher}</li>"
            f"<li>Publication date: {publication_date}</li>"
            f"<li>Language: {language}</li>"
            f"<li>Binding: {binding}</li>"
            f"<li>Pages: {book.page_count or 'Not specified'}</li>"
            f"<li>Reading age: {reading_age}</li>"
            f"<li>ISBN-10: {isbn_10}</li>"
            f"<li>ISBN-13: {isbn_13}</li>"
            f"</ul>"
        )
        sections.append("")

        # Internal links for SEO: link to other pages on the same store
        shop_url = f"{settings.woocommerce_url}/shop"
        sections.append("<h2>Browse Our Bookshop</h2>")
        sections.append(
            f"Discover more titles in our "
            f'<a href="{shop_url}" target="_blank" rel="noopener noreferrer">online bookshop</a>.'
        )
        sections.append("")
        sections.append(
            f"Visit our bookshop to explore additional books by {authors} and other authors published by {publisher}."
        )
        sections.append("")
        sections.append(
            f"Each visit helps you discover new editions and formats available in our collection."
        )
        sections.append("")

        return "\n".join(sections)
