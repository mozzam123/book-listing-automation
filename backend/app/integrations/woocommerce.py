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
        # Expanded product description to meet SEO minimum word count (~600+ words).
        book = product.book

        authors = ", ".join(book.authors) if book.authors else "Unknown Author"

        binding = book.binding or "Paperback"
        language = book.language or "English"
        publisher = book.publisher or "Publisher not specified"
        publication_date = book.publication_date or "Date not specified"
        pages = f"{book.page_count} pages" if book.page_count else "page count not specified"
        reading_age = book.reading_age or "Not specified"
        isbn_10 = book.isbn_10 or "Not available"
        isbn_13 = book.isbn_13 or "Not available"
        description = (book.description or "").strip()

        product_title = self._build_product_title(product)

        # External links for SEO: link out to external resources
        isbn_10_link = (
            f'<a href="https://www.isbn-search.org/search?isbn={isbn_10}" target="_blank" rel="noopener noreferrer">{isbn_10}</a>'
            if isbn_10 != "Not available"
            else isbn_10
        )
        isbn_13_link = (
            f'<a href="https://www.isbn-search.org/search?isbn={isbn_13}" target="_blank" rel="noopener noreferrer">{isbn_13}</a>'
            if isbn_13 != "Not available"
            else isbn_13
        )

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
            sections.append(description)
            sections.append(
                f"{product_title} by {authors} is published by {publisher} and "
                f"was released on {publication_date}. This {language} edition is "
                f"presented in {binding} format with {pages}."
            )
        else:
            sections.append(
                f"Discover {product_title}, a {binding} edition authored by {authors}. "
                f"Published by {publisher}, this title is presented in {language} "
                f"and offers readers a complete and engaging reading experience. "
                f"{product_title} brings together quality content and thoughtful "
                f"presentation in a format designed for lasting enjoyment."
            )
        sections.append("")

        # Book overview
        sections.append("<h2>Book Overview</h2>")
        sections.append(
            f"{product_title} by {authors} is published by {publisher} "
            f"and was released on {publication_date}. Written in {language}, "
            f"this {binding} edition contains {pages}. This book brings together "
            f"thoughtful content and quality presentation, making it suitable for "
            f"readers interested in the subject. Whether you are adding to your "
            f"personal library or looking for a reliable reference, this edition "
            f"delivers the full text in a durable format that stands up to "
            f"repeated reading."
        )
        sections.append("")

        # Author information
        sections.append("<h2>Author Information</h2>")
        sections.append(
            f"The author of {product_title} is {authors}. This title represents "
            f"the author's work in this edition, published under the {publisher} "
            f"imprint. The author's name appears prominently on this publication, "
            f"signaling their creative contribution to the work. Readers who enjoy "
            f"this book may also appreciate other works by the same author. "
            f"Understanding the author behind {product_title} adds context and "
            f"depth to the reading experience."
        )
        sections.append("")

        # Publisher and publication details
        sections.append("<h2>Publisher and Publication Details</h2>")
        sections.append(
            f"This book is published by {publisher}. It was released on "
            f"{publication_date}. The publisher's involvement ensures that the "
            f"content meets editorial standards and is presented professionally "
            f"for readers. {publisher} brings this edition to market with care "
            f"for quality and readability. The publication date marks when this "
            f"edition became available, helping readers identify the specific "
            f"version of {product_title} they are purchasing."
        )
        sections.append("")

        # Format and physical details
        sections.append("<h2>Format and Physical Details</h2>")
        sections.append(
            f"<strong>Binding:</strong> {binding}<br>"
            f"<strong>Pages:</strong> {book.page_count or 'Not specified'}<br>"
            f"<strong>Language:</strong> {language}<br>"
            f"<strong>Reading Age:</strong> {reading_age}<br>"
            f"The {binding} binding is designed for durability, allowing the book "
            f"to be handled and read repeatedly. With {pages}, this edition offers "
            f"substantial content. The {language} language presentation makes it "
            f"accessible to readers comfortable with that language, and the "
            f"reading age guidance of {reading_age} helps determine suitability."
        )
        sections.append("")

        # ISBN and book identification
        sections.append("<h2>ISBN and Book Identification</h2>")
        sections.append(
            f"<strong>ISBN-10:</strong> {isbn_10_link}<br>"
            f"<strong>ISBN-13:</strong> {isbn_13_link}<br>"
            f"These identifiers uniquely identify this edition of {product_title}, "
            f"making it easy to order the correct version from booksellers, "
            f"libraries, and online retailers. ISBN-10 {isbn_10} and ISBN-13 "
            f"{isbn_13} are the standard numbers used across the book industry "
            f"to distinguish one edition from another. When searching for "
            f"{product_title}, use these ISBNs to ensure you receive exactly "
            f"this edition published by {publisher}."
        )
        sections.append("")

        # What to expect
        sections.append("<h2>What to Expect</h2>")
        sections.append(
            f"Readers of {product_title} can expect a complete presentation of "
            f"the content in {language}. The {binding} format provides durability "
            f"for repeated reading, and {pages} offers substantial content to "
            f"explore. With clear identification through its ISBN numbers, this "
            f"edition is straightforward to locate and purchase. The book is "
            f"suited to readers with a reading age of {reading_age}. From the "
            f"first page to the last, {product_title} delivers a consistent and "
            f"well-produced reading experience backed by {publisher}."
        )
        sections.append("")

        # About this edition
        sections.append("<h2>About This Edition</h2>")
        sections.append(
            f"This edition of {product_title} is brought to you by {publisher}. "
            f"It features the full content in {language}, presented in a "
            f"{binding} format with {pages}. The book carries ISBN-10 {isbn_10} "
            f"and ISBN-13 {isbn_13} for accurate identification. Whether you are "
            f"buying for yourself, as a gift, or for a collection, this edition "
            f"provides a complete and professionally presented reading experience. "
            f"The author {authors} and publisher {publisher} have collaborated to "
            f"bring this title to readers in a form that is ready for bookshelves "
            f"and personal libraries alike."
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

        return "\n".join(sections)
