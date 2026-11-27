"""
OCR utilities for extracting text from scanned/image-based PDF reports.

Uses pdf2image to convert PDF pages to images, then pytesseract for OCR.
Includes image preprocessing (grayscale + threshold) to improve accuracy.
"""

from __future__ import annotations

import io
from typing import List, Tuple

from PIL import Image, ImageFilter, ImageOps
from pdf2image import convert_from_bytes


def pdf_to_images(pdf_bytes: bytes, dpi: int = 300) -> List[Image.Image]:
    """Convert a PDF (as bytes) into a list of PIL Images, one per page."""
    return convert_from_bytes(pdf_bytes, dpi=dpi)


def preprocess_image(img: Image.Image) -> Image.Image:
    """
    Preprocess a page image for better OCR accuracy.

    Steps:
    1. Convert to grayscale
    2. Auto-contrast to normalise brightness
    3. Sharpen for crisper edges
    4. Binarise using a threshold so text is black-on-white
    """
    gray = img.convert("L")
    gray = ImageOps.autocontrast(gray, cutoff=1)
    gray = gray.filter(ImageFilter.SHARPEN)
    binary = gray.point(lambda px: 255 if px > 180 else 0, mode="1")
    return binary.convert("L")


def perform_ocr(
    img: Image.Image,
    lang: str = "eng",
    preprocess: bool = True,
) -> str:
    """
    Run Tesseract OCR on a single PIL Image and return the extracted text.

    Parameters
    ----------
    img : PIL.Image.Image
        The page image.
    lang : str
        Tesseract language code (default ``"eng"``).
    preprocess : bool
        Whether to apply ``preprocess_image`` before OCR.
    """
    import pytesseract

    if preprocess:
        img = preprocess_image(img)

    text = pytesseract.image_to_string(img, lang=lang)
    return text.strip()


def extract_text_from_scanned_pdf(
    pdf_bytes: bytes,
    dpi: int = 300,
    lang: str = "eng",
    preprocess: bool = True,
) -> Tuple[str, List[str]]:
    """
    Full pipeline: PDF bytes → per-page OCR text.

    Returns
    -------
    full_text : str
        All pages concatenated with double newlines.
    page_texts : list[str]
        Individual page texts.
    """
    images = pdf_to_images(pdf_bytes, dpi=dpi)
    page_texts: List[str] = []

    for img in images:
        page_text = perform_ocr(img, lang=lang, preprocess=preprocess)
        page_texts.append(page_text)

    full_text = "\n\n".join(page_texts).strip()
    return full_text, page_texts
