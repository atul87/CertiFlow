"""
HashService — P3.41 / P3.42

Computes SHA-256 of arbitrary bytes for tamper detection.
"""
import hashlib


class HashService:
    @staticmethod
    def sha256(data: bytes) -> str:
        """Return lowercase hex SHA-256 string of data."""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def verify(data: bytes, expected_hash: str) -> bool:
        """Return True if SHA-256 of data matches expected_hash (case-insensitive)."""
        return hashlib.sha256(data).hexdigest() == expected_hash.lower()
