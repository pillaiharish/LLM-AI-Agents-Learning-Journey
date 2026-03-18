import colorsys

import numpy as np
from PIL import Image, ImageEnhance


class ImageEditor:
    @staticmethod
    def adjust(img: Image.Image, brightness: float = 100, saturation: float = 100, hue: float = 0) -> Image.Image:
        # Brightness (100 = original)
        if brightness != 100:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(brightness / 100)

        # Saturation (100 = original)
        if saturation != 100:
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(saturation / 100)

        # Hue rotation (0-360 degrees)
        if hue != 0:
            img = ImageEditor._rotate_hue(img, hue)

        return img

    @staticmethod
    def _rotate_hue(img: Image.Image, degrees: float) -> Image.Image:
        if img.mode != 'RGB':
            img = img.convert('RGB')

        arr = np.array(img, dtype=np.float64) / 255.0
        # Convert RGB to HSV
        r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]

        maxc = np.maximum(np.maximum(r, g), b)
        minc = np.minimum(np.minimum(r, g), b)
        v = maxc
        s = np.where(maxc != 0, (maxc - minc) / maxc, 0)

        delta = maxc - minc
        with np.errstate(divide='ignore', invalid='ignore'):
            h = np.where(delta == 0, 0,
                np.where(maxc == r, ((g - b) / delta) % 6,
                np.where(maxc == g, (b - r) / delta + 2,
                (r - g) / delta + 4)))
        h = h / 6.0  # Normalize to 0-1

        # Rotate hue
        h = (h + degrees / 360.0) % 1.0

        # Convert back to RGB
        hi = (h * 6).astype(int) % 6
        f = h * 6 - hi
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)

        result = np.zeros_like(arr)
        for i in range(6):
            mask = hi == i
            if i == 0: result[mask] = np.stack([v, t, p], axis=-1)[mask]
            elif i == 1: result[mask] = np.stack([q, v, p], axis=-1)[mask]
            elif i == 2: result[mask] = np.stack([p, v, t], axis=-1)[mask]
            elif i == 3: result[mask] = np.stack([p, q, v], axis=-1)[mask]
            elif i == 4: result[mask] = np.stack([t, p, v], axis=-1)[mask]
            elif i == 5: result[mask] = np.stack([v, p, q], axis=-1)[mask]

        result = (result * 255).clip(0, 255).astype(np.uint8)
        return Image.fromarray(result)
