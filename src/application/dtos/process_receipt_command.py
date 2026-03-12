from dataclasses import dataclass


@dataclass
class ProcessReceiptCommand:
    image_bytes: bytes
    content_type: str
