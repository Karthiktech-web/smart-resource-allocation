"""
Translation service.
Detects source language and translates survey text to English.
"""

from google.cloud import translate_v2 as translate


def detect_and_translate(text: str) -> dict:
    """
    Detect language and translate text to English.
    Returns:
    {
      "original_text": "...",
      "translated_text": "...",
      "language_detected": "te"
    }
    """
    client = translate.Client()

    detection = client.detect_language(text)
    language_detected = detection["language"]

    if language_detected == "en":
        return {
            "original_text": text,
            "translated_text": text,
            "language_detected": "en",
        }

    result = client.translate(text, target_language="en")

    return {
        "original_text": text,
        "translated_text": result["translatedText"],
        "language_detected": language_detected,
    }
