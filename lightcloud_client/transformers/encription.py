import numpy as np

from lightcloud_client.transformers.transformer import Transformer


def _cycle_xor(data: bytes, key: bytes) -> bytes:
    key_array = np.frombuffer(key * (len(data) // len(key) + 1), dtype=np.uint8)[:len(data)]
    return np.bitwise_xor(
        np.frombuffer(data, dtype=np.uint8),
        key_array
    ).tobytes()


class EncryptTransformer(Transformer):

    def __init__(self, encryption_signature: bytes):
        self._encryption_signature = encryption_signature

    def transform(self, data: bytes) -> bytes:
        return _cycle_xor(data, self._encryption_signature)


class DecryptTransformer(Transformer):

    def __init__(self, encryption_signature: bytes):
        self._encryption_signature = encryption_signature

    def transform(self, data: bytes) -> bytes:
        return _cycle_xor(data, self._encryption_signature)
