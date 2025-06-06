from fastapi import FastAPI, Response
from pydantic import BaseModel
import hashlib
import base64
import random
import string
from datetime import datetime
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Invisible Unicode markers
ZWJ = '\u200D'  # Zero Width Joiner (1)
ZWNJ = '\u200C'  # Zero Width Non-Joiner (0)

# Common decoy patterns used by detectors
DECOY_MARKERS = ["WMK+", "EE+", "AIWMK+", "HASH+"]
DECOY_CHARS = ['·', '÷', '×', '¬', '‖', ZWJ, ZWNJ]


def hash_to_binary(data: str) -> str:
    """
    Hash input data using SHA-256 and return binary string.
    """
    h = hashlib.sha256(data.encode()).digest()
    return ''.join(f"{byte:08b}" for byte in h)


def binary_to_unicode(bits: str) -> str:
    """
    Convert binary string to invisible Unicode characters.
    """
    mapping = {'0': ZWNJ, '1': ZWJ}
    return ''.join(mapping[b] for b in bits)


def generate_decoy_payload(length: int = 32) -> str:
    """
    Generate fake payload with random invisible characters.
    """
    return ''.join(random.choices(DECOY_CHARS, k=length))


def insert_invisible_watermark(text: str) -> str:
    """
    Insert invisible watermark based on metadata.
    """
    metadata = f"prompt_id:{generate_random_id(10)}|model:gpt-4|timestamp:{generate_timestamp()}"
    bits = hash_to_binary(metadata)
    watermark = binary_to_unicode(bits)

    # Insert at a random position
    pos = random.randint(len(text) // 4, (len(text) // 4) * 3)
    return text[:pos] + watermark + text[pos:]


def insert_decoy_watermark(text: str) -> str:
    """
    Add fake watermark patterns to confuse decoders.
    """
    marker = random.choice(DECOY_MARKERS)
    decoy_data = generate_decoy_payload()
    decoy_pattern = f"{marker}{decoy_data}WMK"

    # Insert randomly
    pos = random.randint(len(text) // 3, (len(text) // 3) * 2)
    return text[:pos] + decoy_pattern + text[pos:]


def generate_random_id(length: int = 10) -> str:
    """
    Generate fake prompt IDs.
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_timestamp() -> str:
    """
    Generate fake timestamps.
    """
    return datetime.now().isoformat()


def obfuscate_with_base64(text: str) -> str:
    """
    Encode text into Base64 format.
    """
    return base64.b64encode(text.encode()).decode()


class TextInput(BaseModel):
    text: str


@app.post("/bypass")
async def bypass_watermark(data: TextInput):
    """
    Endpoint to process text by adding invisible watermarks and decoy patterns,
    then encoding the result in Base64.
    """
    text = data.text

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
        "processed_text": obfuscated_text,
        "unicode_hash": base64.b64encode(unicode_hash.encode()).decode()
    }

@app.post("/download")
async def download_watermarked_file(data: TextInput):
    """
    Endpoint to process text and return it as a downloadable `.txt` file.
    """
    text = data.text

    # Process the text
    watermarked_text = insert_invisible_watermark(text)
    final_text = insert_decoy_watermark(watermarked_text)
    obfuscated_text = obfuscate_with_base64(final_text)

    headers = {
        "Content-Disposition": "attachment; filename=watermarked_output.txt"
    }

    return Response(content=obfuscated_text, media_type="text/plain", headers=headers)

# Serve static files
app.mount("/", StaticFiles(directory="dist", html=True), name="static")

# Get the port from the environment variable or default to 8000
port = int(os.getenv("PORT", 8000))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
