from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    google_books_api_key: str

    woocommerce_url: str
    woocommerce_consumer_key: str
    woocommerce_consumer_secret: str

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()
