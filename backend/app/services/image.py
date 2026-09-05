import httpx

from app.core.config import settings


class ImageService:

    def upload_cover(
        self,
        image_url: str,
        filename: str,
    ) -> dict | None:
        if not image_url:
            return None

        response = httpx.get(
            image_url,
            timeout=15.0,
            follow_redirects=True,
        )

        response.raise_for_status()

        return self._upload_to_wordpress(
            image_data=response.content,
            filename=filename,
            content_type=response.headers.get(
                "content-type",
                "image/jpeg",
            ),
        )

    def upload_image(
        self,
        image_data: bytes,
        filename: str,
        content_type: str,
    ) -> dict:
        return self._upload_to_wordpress(
            image_data=image_data,
            filename=filename,
            content_type=content_type,
        )

    def _upload_to_wordpress(
        self,
        image_data: bytes,
        filename: str,
        content_type: str,
    ) -> dict:
        media_url = f"{settings.woocommerce_url}" "/wp-json/wp/v2/media"

        response = httpx.post(
            media_url,
            content=image_data,
            headers={
                "Content-Disposition": (f'attachment; filename="{filename}"'),
                "Content-Type": content_type,
            },
            auth=(
                settings.wordpress_username,
                settings.wordpress_application_password,
            ),
            timeout=15.0,
        )

        response.raise_for_status()

        return response.json()
