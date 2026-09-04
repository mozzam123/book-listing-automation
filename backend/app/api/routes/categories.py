from fastapi import APIRouter

from app.integrations.woocommerce import WooCommerceProvider


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.get("")
def get_categories():
    provider = WooCommerceProvider()

    return provider.get_categories()
