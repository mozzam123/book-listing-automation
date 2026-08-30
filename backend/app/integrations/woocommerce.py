import httpx

from app.core.config import settings
from app.models.product import Product
from app.integrations.commerce import CommerceProvider


class WooCommerceProvider(CommerceProvider):

    def create_product(self, product: Product) -> dict:
        url = f"{settings.woocommerce_url.rstrip('/')}/wp-json/wc/v3/products"

        payload = {
            "name": product.book.title,
            "type": "simple",
            "regular_price": str(product.seller.selling_price),
            "manage_stock": True,
            "stock_quantity": product.seller.stock,
            "description": product.book.description or "",
            "sku": product.book.isbn_13 or product.book.isbn_10,
        }

        response = httpx.post(
            url,
            auth=(
                settings.woocommerce_consumer_key,
                settings.woocommerce_consumer_secret,
            ),
            json=payload,
            timeout=15.0,
        )

        if response.is_error:
            print("WooCommerce status:", response.status_code)
            print("WooCommerce response:", response.text)
            raise RuntimeError(
                f"WooCommerce error {response.status_code}: {response.text}"
            )

        return response.json()
