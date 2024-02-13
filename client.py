import abc
import hashlib
import time
import uuid
from pathlib import Path
from typing import IO

import httpx
import numpy as np


class Transformer(abc.ABC):

    @abc.abstractmethod
    def transform(self, data: str) -> str:
        ...


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


class CloudClient:

    CHUNK_SIZE = 1 << 20  # 1 MB

    HASH_HIT = '/upload/file/hash/{hash}/path/{filepath}'
    UPLOAD_CHUNK = '/upload/file/hash/{hash}/path/{filepath}'
    DOWNLOAD_FILE = '/download/file/{filepath}'

    def __init__(self, server_addr: str, token: uuid.UUID):
        self._token = token
        self._client_conf = dict(
            base_url=server_addr,
            timeout=httpx.Timeout(None, read=180.0),
            headers={
                'Authorization': 'token',
            },
            cookies={
                'lightcloud-token': str(token)
            }
        )
        self._send_transformers = []
        self._receive_transformers = []

    def send_transformers(self, *t: Transformer) -> 'CloudClient':
        self._send_transformers.extend(t)
        return self

    def receive_transformers(self, *t: Transformer) -> 'CloudClient':
        self._receive_transformers.extend(t)
        return self

    @staticmethod
    def _get_chunk_hash(chunk: bytes) -> str:
        return hashlib.md5(chunk).hexdigest()

    def upload_file(self, filepath: Path) -> None:
        with httpx.Client(**self._client_conf) as client, filepath.open('rb') as f:
            while chunk := f.read(self.CHUNK_SIZE):
                content_hash = self._get_chunk_hash(chunk)
                if self._is_hash_hits(client, content_hash, filepath):
                    continue
                for transformer in self._send_transformers:
                    chunk = transformer.transform(chunk)
                self._send_chunk(client, content_hash, chunk, filepath)

    def _is_hash_hits(self, client: httpx.Client, content_hash: str, filepath: Path) -> bool:
        hit_request = client.get(
            self.HASH_HIT.format(hash=content_hash, filepath=filepath.as_posix())
        )
        if hit_request.status_code >= 300:
            raise PermissionError()
        return hit_request.status_code == 200

    def _send_chunk(self, client: httpx.Client, content_hash: str, content: bytes, filepath: Path):
        client.post(
            self.UPLOAD_CHUNK.format(hash=content_hash, filepath=filepath.as_posix()),
            content=content
        )

    def download_file(self, filepath: Path, to: Path) -> None:
        with httpx.Client(**self._client_conf) as client:
            stream = client.stream(
                method='GET',
                url=self.DOWNLOAD_FILE.format(filepath=filepath.as_posix()),
            )
            with stream as response, open(to, 'wb') as f:
                response: httpx.Response
                for chunk in response.iter_bytes(self.CHUNK_SIZE):
                    self._write_chunk(f, chunk)

    def _write_chunk(self, f: IO[bytes], chunk: bytes) -> None:
        for transformer in self._receive_transformers:
            chunk = transformer.transform(chunk)
        f.write(chunk)


if __name__ == '__main__':
    token = uuid.UUID('91b26497-9389-4f72-b4ff-53ba4913e801')
    signature = b'BOB'
    client = (
        CloudClient('http://127.0.0.1:8000', token)
        .send_transformers(EncryptTransformer(encryption_signature=signature))
        .receive_transformers(DecryptTransformer(encryption_signature=signature))
    )

    file = Path('/Users/nikita/Downloads/DesignPatterns.pdf')

    client.upload_file(file)
    s = time.perf_counter()
    client.download_file(file, to=Path('/dev/null'))
    print(time.perf_counter()-s)
