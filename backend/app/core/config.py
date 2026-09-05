from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    google_books_api_key: str

    woocommerce_url: str
    woocommerce_consumer_key: str
    woocommerce_consumer_secret: str

    wordpress_username: str
    wordpress_application_password: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
