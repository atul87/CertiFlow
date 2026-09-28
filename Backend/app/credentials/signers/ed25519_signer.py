from __future__ import annotations
import base64
import logging
from typing import Tuple
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet
from app.core.config import settings
from app.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class Ed25519Signer:
    """
    Ed25519 asymmetric cryptographic signing and verification utility
    conforming to W3C Verifiable Credentials Data Integrity proof standards.
    """

    @classmethod
    def generate_keypair(cls) -> Tuple[str, str]:
        """
        Generate a fresh Ed25519 keypair.
        Returns:
            (public_key_pem, encrypted_private_key_str)
        Private key is encrypted at rest using the application master ENCRYPTION_KEY.
        """
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        # Public key in SubjectPublicKeyInfo (SPKI) PEM format
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode("utf-8")

        # Private key in PKCS#8 PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode("utf-8")

        # Encrypt private key with Fernet
        encrypted_private = cls._encrypt_private_key(private_pem)
        return public_pem, encrypted_private

    @classmethod
    def sign_bytes(cls, data: bytes, encrypted_private_key: str) -> str:
        """
        Sign arbitrary payload bytes with an encrypted private key.
        Returns base64-encoded signature string.
        """
        private_pem = cls._decrypt_private_key(encrypted_private_key)
        private_key = serialization.load_pem_private_key(
            private_pem.encode("utf-8"),
            password=None
        )
        if not isinstance(private_key, ed25519.Ed25519PrivateKey):
            raise ValidationError(message="Expected Ed25519 private key", code="INVALID_KEY_TYPE")

        sig_bytes = private_key.sign(data)
        return base64.b64encode(sig_bytes).decode("utf-8")

    @classmethod
    def verify_bytes(cls, data: bytes, signature_b64: str, public_key_pem: str) -> bool:
        """
        Verify a base64-encoded Ed25519 signature against payload bytes and public key PEM.
        Returns True if signature is cryptographically valid, False otherwise.
        """
        try:
            public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
            if not isinstance(public_key, ed25519.Ed25519PublicKey):
                return False

            sig_bytes = base64.b64decode(signature_b64)
            public_key.verify(sig_bytes, data)
            return True
        except Exception as e:
            logger.debug("Ed25519 signature verification failed: %s", e)
            return False

    @classmethod
    def _get_fernet(cls) -> Fernet:
        # Use settings.ENCRYPTION_KEY (or fallback to derived 32-byte key)
        raw_key = getattr(settings, "ENCRYPTION_KEY", None)
        if not raw_key:
            # Fallback for dev/test: derive from JWT_SECRET_KEY
            h = base64.urlsafe_b64encode(settings.JWT_SECRET_KEY.encode("utf-8")[:32].ljust(32, b"0"))
            return Fernet(h)
        if isinstance(raw_key, str):
            raw_key = raw_key.encode("utf-8")
        return Fernet(raw_key)

    @classmethod
    def _encrypt_private_key(cls, private_pem: str) -> str:
        fernet = cls._get_fernet()
        return fernet.encrypt(private_pem.encode("utf-8")).decode("utf-8")

    @classmethod
    def _decrypt_private_key(cls, encrypted_str: str) -> str:
        fernet = cls._get_fernet()
        return fernet.decrypt(encrypted_str.encode("utf-8")).decode("utf-8")
