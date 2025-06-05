from fastapi import FastAPI
import hashlib
import base64
import random
import string
from typing import List

app = FastAPI()

# Invisible Unicode markers
ZWJ = '\u200D'  # Zero Width Joiner (1)
ZWNJ = '\u200C'  # Zero Width Non-Joiner (0)

# Common decoy patterns used by detectors
DECOY_MARKERS = ["WMK+", "EE+", "AIWMK+", "HASH+"]
DECOY_CHARS = ['·', '÷', '×', '¬', '‖', ZWJ, ZWNJ]

def hash_to_binary(data):
    """Hash input data using SHA-256 and return binary string"""
    h = hashlib.sha256(data.encode()).digest()
    return ''.join(f"{byte:08b}" for byte in h)

def binary_to_unicode(bits):
    """
    Convert binary string to invisible Unicode characters
    """
    mapping = {'0': ZWNJ, '1': ZWJ}
    return ''.join(mapping[b] for b in bits)

def generate_decoy_payload(length=32):
    """Generate fake payload with random invisible chars"""
    return ''.join(random.choices(DECOY_CHARS, k=length))

def insert_invisible_watermark(text: str) -> str:
    """Insert invisible watermark based on metadata"""
    metadata = f"prompt_id:{generate_random_id(10)}|model:gpt-4|timestamp:{generate_timestamp()}"
    bits = hash_to_binary(metadata)
    watermark = binary_to_unicode(bits)

    # Insert at random position
    pos = random.randint(len(text)//4, (len(text)//4)*3)
    return text[:pos] + watermark + text[pos:]

def insert_decoy_watermark(text: str) -> str:
    """Add fake watermark patterns to confuse decoders"""
    marker = random.choice(DECOY_MARKERS)
    decoy_data = generate_decoy_payload()
    decoy_pattern = f"{marker}{decoy_data}WMK"

    # Insert randomly
    pos = random.randint(len(text)//3, (len(text)//3)*2)
    return text[:pos] + decoy_pattern + text[pos:]

def generate_random_id(length=10):
    """Generate fake prompt IDs"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_timestamp():
    """Generate fake timestamps"""
    from datetime import datetime
    return datetime.now().isoformat()

@app.post("/bypass")
async def bypass_watermark(data: dict):
    text = data.get("text", "")
    
    # Step 1: Add invisible watermark
    watermarked_text = insert_invisible_watermark(text)

    # Step 2: Add fake watermark pattern
    final_text = insert_decoy_watermark(watermarked_text)

    return {"result": final_text}