"""
Google Cloud Vision OCR service.
This extracts text from uploaded survey images.
"""

from google.cloud import vision


def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Extract text from an image using Google Cloud Vision OCR.
    """
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)
    response = client.text_detection(image=image)

    if response.error.message:
        raise Exception(f"Vision API error: {response.error.message}")

    texts = response.text_annotations
    if texts:
        return texts[0].description

    return ""
