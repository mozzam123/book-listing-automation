from abc import ABC, abstractmethod

from app.models.product import Product


class CommerceProvider(ABC):

    @abstractmethod
    def create_product(self, product: Product) -> dict:
        pass

    @abstractmethod
    def get_categories(self) -> list[dict]:
        pass
