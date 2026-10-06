import httpx

from app.core.config import settings


class ImageService:

    def upload_cover(
        self,
        image_url: str,
        filename: str,
        book_title: str,
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
            content_type=response.headers.get("content-type", "image/jpeg"),
            book_title=book_title,
        )

    def upload_image(
        self,
        image_data: bytes,
        filename: str,
        content_type: str,
        book_title: str,
    ) -> dict:
        return self._upload_to_wordpress(
            image_data=image_data,
            filename=filename,
            content_type=content_type,
            book_title=book_title,
        )

    def _upload_to_wordpress(
        self,
        image_data: bytes,
        filename: str,
        content_type: str,
        book_title: str,
    ) -> dict:
        media_url = f"{settings.woocommerce_url}/wp-json/wp/v2/media"
        auth = (
            settings.wordpress_username,
            settings.wordpress_application_password,
        )

        response = httpx.post(
            media_url,
            content=image_data,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": content_type,
            },
            auth=auth,
            timeout=15.0,
        )
        response.raise_for_status()

        media = response.json()

        metadata_response = httpx.post(
            f"{media_url}/{media['id']}",
            json={
                "title": book_title,
                "alt_text": book_title,
            },
            auth=auth,
            timeout=15.0,
        )
        metadata_response.raise_for_status()

        return metadata_response.json()
