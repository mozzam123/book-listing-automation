from pydantic import BaseModel


class ISBNRequest(BaseModel):
    isbn: str
