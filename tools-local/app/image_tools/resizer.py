from PIL import Image


class ImageResizer:
    @staticmethod
    def resize(img: Image.Image, width: int, height: int) -> Image.Image:
        return img.resize((width, height), Image.LANCZOS)
