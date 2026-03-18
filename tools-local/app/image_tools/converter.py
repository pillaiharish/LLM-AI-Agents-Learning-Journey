import io
from PIL import Image

FORMAT_MAP = {
    "JPEG": ("JPEG", ".jpg"),
    "PNG": ("PNG", ".png"),
    "WEBP": ("WEBP", ".webp"),
    "BMP": ("BMP", ".bmp"),
    "TIFF": ("TIFF", ".tiff"),
    "GIF": ("GIF", ".gif"),
    "ICO": ("ICO", ".ico"),
}


class ImageConverter:
    @staticmethod
    def convert(img: Image.Image, target_format: str) -> tuple[bytes, str, str]:
        """Returns (bytes, mime_type, extension)."""
        fmt_info = FORMAT_MAP.get(target_format.upper())
        if not fmt_info:
            raise ValueError(f"Unsupported format: {target_format}")

        pil_format, ext = fmt_info

        # Handle RGBA for formats that don't support it
        if img.mode == 'RGBA' and pil_format in ('JPEG', 'BMP', 'ICO'):
            img = img.convert('RGB')
        elif img.mode == 'P' and pil_format == 'JPEG':
            img = img.convert('RGB')

        buf = io.BytesIO()
        if pil_format == 'ICO':
            sizes = [(min(img.width, 256), min(img.height, 256))]
            img_resized = img.resize(sizes[0], Image.LANCZOS)
            img_resized.save(buf, format=pil_format)
        else:
            img.save(buf, format=pil_format)
        buf.seek(0)

        mime_map = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp",
                    "BMP": "image/bmp", "TIFF": "image/tiff", "GIF": "image/gif", "ICO": "image/x-icon"}
        return buf.getvalue(), mime_map.get(pil_format, "application/octet-stream"), ext
