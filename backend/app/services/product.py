from app.integrations.commerce import CommerceProvider
from app.models.product import Product


class ProductService:

    def __init__(self, commerce_provider: CommerceProvider):
        self.commerce_provider = commerce_provider

    def create_product(self, product: Product) -> dict:
        return self.commerce_provider.create_product(product)
