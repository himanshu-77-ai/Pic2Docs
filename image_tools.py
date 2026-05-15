"""
image_tools.py — Pre-OCR Image Editing (PIL only, no OpenCV)
"""
from __future__ import annotations
import io
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


def rotate_image(img: Image.Image, degrees: float) -> Image.Image:
    return img.rotate(-degrees, expand=True, resample=Image.BICUBIC,
                      fillcolor=(255, 255, 255))


def crop_image(img: Image.Image,
               left_pct: float, top_pct: float,
               right_pct: float, bottom_pct: float) -> Image.Image:
    w, h = img.size
    left   = int(w * left_pct   / 100)
    top    = int(h * top_pct    / 100)
    right  = int(w * right_pct  / 100)
    bottom = int(h * bottom_pct / 100)
    if right <= left or bottom <= top:
        return img
    return img.crop((left, top, right, bottom))


def adjust_brightness(img: Image.Image, factor: float) -> Image.Image:
    return ImageEnhance.Brightness(img).enhance(factor)


def adjust_contrast(img: Image.Image, factor: float) -> Image.Image:
    return ImageEnhance.Contrast(img).enhance(factor)


def adjust_sharpness(img: Image.Image, factor: float) -> Image.Image:
    return ImageEnhance.Sharpness(img).enhance(factor)


def denoise_image(img: Image.Image) -> Image.Image:
    """PIL-based denoise using median filter."""
    return img.filter(ImageFilter.MedianFilter(size=3))


def to_grayscale(img: Image.Image) -> Image.Image:
    return img.convert("L").convert("RGB")


def pil_to_bytes(img: Image.Image, fmt: str = "PNG") -> bytes:
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def apply_all(img: Image.Image,
              rotate_deg: float = 0,
              brightness: float = 1.0,
              contrast:   float = 1.0,
              sharpness:  float = 1.0,
              denoise:    bool  = False,
              grayscale:  bool  = False,
              crop_left:  float = 0,
              crop_top:   float = 0,
              crop_right: float = 100,
              crop_bottom:float = 100) -> Image.Image:
    img = img.convert("RGB")
    if rotate_deg != 0:
        img = rotate_image(img, rotate_deg)
    if any(v != d for v, d in [(crop_left,0),(crop_top,0),(crop_right,100),(crop_bottom,100)]):
        img = crop_image(img, crop_left, crop_top, crop_right, crop_bottom)
    if brightness != 1.0:
        img = adjust_brightness(img, brightness)
    if contrast != 1.0:
        img = adjust_contrast(img, contrast)
    if sharpness != 1.0:
        img = adjust_sharpness(img, sharpness)
    if denoise:
        img = denoise_image(img)
    if grayscale:
        img = to_grayscale(img)
    return img
