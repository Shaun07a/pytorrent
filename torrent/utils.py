import hashlib


def sha1(data: bytes) -> bytes:
    return hashlib.sha1(data).digest()