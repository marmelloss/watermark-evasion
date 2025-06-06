from fastapi import FastAPI, Response, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import hashlib
import base64
import random
import string
from datetime import datetime
from fastapi.staticfiles import StaticFiles
import os
import logging
from typing import Optional

# Setup logging
logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Invisible Unicode markers
ZWJ = '\u200D'  # Zero Width Joiner (1)
ZWNJ = '\u200C'  # Zero Width Non-Joiner (0)
ZWSP = '\u200B'  # Zero Width Space
ZWNBSP = '\uFEFF'  # Zero Width No-Break Space

# Common decoy patterns used by detectors
DECOY_MARKERS = ["WMK+", "EE+", "AIWMK+", "HASH+", "META+", "ID+"]
DECOY_CHARS = [ZWJ, ZWNJ, ZWSP, ZWNBSP, '·', '÷', '×', '¬', '‖']

# Advanced decoy phrases for different languages
LANGUAGE_DECOYS = {
    "en": ["generated", "output", "response"],
    "fr": ["généré", "réponse", "sortie"],
    "es": ["generado", "respuesta", "salida"],
    "zh": ["生成", "输出", "响应"],
    "ar": ["تم_الإنشاء", "الإجابة", "الناتج"]
}


def hash_to_binary(data: str) -> str:
    """Hash input data using SHA-256 and return binary string."""
    h = hashlib.sha256(data.encode()).digest()
    return ''.join(f"{byte:08b}" for byte in h)


def binary_to_unicode(bits: str) -> str:
    """Convert binary string to invisible Unicode characters."""
    mapping = {'0': ZWNJ, '1': ZWJ}
    return ''.join(mapping[b] for b in bits)


def generate_decoy_payload(length: int = 32) -> str:
    """Generate fake payload with random invisible characters."""
    return ''.join(random.choices(DECOY_CHARS, k=length))


def insert_invisible_watermark(text: str) -> str:
    """Insert invisible watermark based on metadata."""
    metadata = f"prompt_id:{generate_random_id(10)}|model:gpt-4|timestamp:{generate_timestamp()}"
    bits = hash_to_binary(metadata)
    watermark = binary_to_unicode(bits)

    # Add randomized spacing between watermark bits
    spaced_watermark = ''.join([c + random.choice(['', ZWSP, ZWNBSP]) for c in watermark])

    # Insert at a random position
    pos = random.randint(len(text) // 4, (len(text) // 4) * 3)
    return text[:pos] + spaced_watermark + text[pos:]


def insert_decoy_watermark(text: str) -> str:
    """Add fake watermark patterns to confuse decoders."""
    marker = random.choice(DECOY_MARKERS)
    decoy_data = generate_decoy_payload()

    # Add language-specific decoy phrases
    lang_decoys = random.choice(list(LANGUAGE_DECOYS.values()))
    decoy_phrase = random.choice(lang_decoys)

    decoy_pattern = f"{marker}{decoy_data}{decoy_phrase}WMK"

    # Insert randomly
    pos = random.randint(len(text) // 3, (len(text) // 3) * 2)
    return text[:pos] + decoy_pattern + text[pos:]


def inject_statistical_noise(text: str) -> str:
    """Inject random noise into the text to disrupt statistical analysis."""
    noise_chars = [ZWJ, ZWNJ, ZWSP, ZWNBSP]
    noisy_text = list(text)
    num_noise = max(1, len(text) // 20)  # ~5% noise

    for _ in range(num_noise):
        pos = random.randint(0, len(noisy_text) - 1)
        noisy_text.insert(pos, random.choice(noise_chars))

    return ''.join(noisy_text)


def generate_random_id(length: int = 10) -> str:
    """Generate fake prompt IDs."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_timestamp() -> str:
    """Generate fake timestamps."""
    return datetime.now().isoformat()


def obfuscate_with_base64(text: str) -> str:
    """Encode text into Base64 format."""
    return base64.b64encode(text.encode()).decode()


def apply_rot13(text: str) -> str:
    """Apply ROT13 encoding to the text."""
    return text.translate(str.maketrans(
        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
        'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'
    ))


def multi_layer_obfuscation(text: str) -> str:
    """Apply multiple layers of obfuscation to the text."""
    # Layer 1: Base64 encoding
    encoded = obfuscate_with_base64(text)

    # Layer 2: ROT13 encoding
    encoded = apply_rot13(encoded)

    # Layer 3: Reverse the string
    encoded = encoded[::-1]

    return encoded


class TextInput(BaseModel):
    text: str
    download: Optional[bool] = False


@app.post("/process")
async def process_text(data: TextInput, request: Request):
    """Endpoint to process text with watermarks and obfuscation."""
    try:
        text = data.text
        should_download = data.download or False
        logging.debug(f"Processing text (download={should_download}): {text[:50]}...")

        # Step 1: Add invisible watermark
        watermarked_text = insert_invisible_watermark(text)

        # Step 2: Add fake watermark pattern
        final_text = insert_decoy_watermark(watermarked_text)

        # Step 3: Inject statistical noise
        noisy_text = inject_statistical_noise(final_text)

        # Step 4: Apply multi-layer obfuscation
        obfuscated_text = multi_layer_obfuscation(noisy_text)

        # For debugging purposes, return also the invisible watermark
        metadata = f"prompt_id:{generate_random_id(10)}|model:gpt-4|timestamp:{generate_timestamp()}"
        bits = hash_to_binary(metadata)
        unicode_hash = binary_to_unicode(bits)

        if should_download:
            # Prepare the file content
            file_content = obfuscated_text.encode()
            headers = {
                "Content-Disposition": "attachment; filename=watermarked_output.txt",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
            return Response(
                content=file_content,
                media_type="text/plain",
                headers=headers
            )
        else:
            return {
                "status": "success",
                "processed_text": obfuscated_text,
                "unicode_hash": base64.b64encode(unicode_hash.encode()).decode(),
                "metadata": metadata
            }
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.post("/bypass")
async def bypass_watermark(data: TextInput):
    """Endpoint to bypass watermark detection by adding noise and obfuscation."""
    try:
        text = data.text
        logging.debug(f"Bypassing watermark for text: {text[:50]}...")

        # Step 1: Add invisible watermark
        watermarked_text = insert_invisible_watermark(text)

        # Step 2: Add fake watermark pattern
        final_text = insert_decoy_watermark(watermarked_text)

        # Step 3: Encode in Base64 for obfuscation
        obfuscated_text = obfuscate_with_base64(final_text)

        # For debugging purposes, return also the invisible watermark
        metadata = f"prompt_id:{generate_random_id(10)}|model:gpt-4|timestamp:{generate_timestamp()}"
        bits = hash_to_binary(metadata)
        unicode_hash = binary_to_unicode(bits)

        return {
            "status": "success",
            "processed_text": obfuscated_text,
            "unicode_hash": base64.b64encode(unicode_hash.encode()).decode(),
            "metadata": metadata
        }
    except Exception as e:
        logging.error(f"Error in bypass endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Serve static files for frontend
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
