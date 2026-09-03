import httpx

from app.core.config import settings


class ImageService:

    def upload_cover(self, image_url: str, filename: str) -> dict | None:
        if not image_url:
            return None

        response = httpx.get(
            image_url,
            timeout=15.0,
            follow_redirects=True,
        )

        response.raise_for_status()

        media_url = f"{settings.woocommerce_url}/wp-json/wp/v2/media"

        upload_response = httpx.post(
            media_url,
            content=response.content,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": response.headers.get(
                    "content-type",
                    "image/jpeg",
                ),
            },
            auth=(
                settings.wordpress_username,
                settings.wordpress_application_password,
            ),
            timeout=15.0,
        )

        upload_response.raise_for_status()

        return upload_response.json()
