from fastapi import FastAPI

from app.api.routes.books import router as books_router
from app.api.routes.categories import router as categories_router


app = FastAPI(
    title="Book Listing Automation",
    version="0.1.0",
)

app.include_router(books_router)
app.include_router(categories_router)
