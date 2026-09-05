from fastapi import APIRouter
import json
from app.schemas.book import ISBNRequest
from app.services.book_metadata import BookMetadataService
from app.providers.google_books import GoogleBooksProvider
from app.utils.isbn import validate_isbn
from fastapi import APIRouter, File, UploadFile, Form
from app.models.product import Product
from app.services.product import ProductService
from app.integrations.woocommerce import WooCommerceProvider

commerce_provider = WooCommerceProvider()
product_service = ProductService(commerce_provider)


router = APIRouter(prefix="/books", tags=["Books"])

provider = GoogleBooksProvider()
metadata_service = BookMetadataService(provider)


@router.post("/validate-isbn")
def validate_book_isbn(request: ISBNRequest):
    is_valid, normalized_isbn = validate_isbn(request.isbn)

    if not is_valid:
        return {
            "valid": False,
            "isbn": None,
        }

    return {
        "valid": True,
        "isbn": normalized_isbn,
    }


@router.post("/lookup")
def lookup_book(request: ISBNRequest):
    is_valid, normalized_isbn = validate_isbn(request.isbn)

    if not is_valid:
        return {
            "found": False,
            "error": "Invalid ISBN",
        }

    book = metadata_service.get_by_isbn(normalized_isbn)

    if book is None:
        return {
            "found": False,
            "error": "Book not found",
        }

    return {
        "found": True,
        "data": book,
    }


@router.post("/products")
async def create_product(
    product: str = Form(...),
    image: UploadFile | None = File(None),
):

    product_data = Product.model_validate(json.loads(product))

    provider = WooCommerceProvider()

    product_service = ProductService(commerce_provider=provider)

    custom_image_data = None

    custom_image_filename = None

    custom_image_content_type = None

    if image:

        custom_image_data = await image.read()

        custom_image_filename = image.filename

        custom_image_content_type = image.content_type

    return provider.create_product(
        product=product_data,
        custom_image_data=custom_image_data,
        custom_image_filename=custom_image_filename,
        custom_image_content_type=custom_image_content_type,
    )
