import hashlib
import io
import uuid
from pathlib import Path
from typing import IO

import httpx

from lightcloud_client.transformers.transformer import Transformer
from lightcloud_client.uploader import UploadContentMixin


class CloudClient:

    CHUNK_SIZE = 1 << 20  # 1 MB

    DOWNLOAD_FILE = '/resources/resource/{resource_id}'

    def __init__(self, server_addr: str, token: uuid.UUID):
        self._token = token
        self._client_conf = dict(
            base_url=server_addr,
            timeout=httpx.Timeout(None, read=180.0),
            headers={
                'Authorization': 'token',
            },
            cookies={
                'light-cloud-token': str(token)
            }
        )
        self._send_transformers = []
        self._receive_transformers = []
        self._upload_mixin = UploadContentMixin(
            transformers=self._send_transformers
        )

    def send_transformers(self, *t: Transformer) -> 'CloudClient':
        self._send_transformers.extend(t)
        return self

    def receive_transformers(self, *t: Transformer) -> 'CloudClient':
        self._receive_transformers.extend(t)
        return self

    @staticmethod
    def _get_file_identity(filepath: Path) -> str:
        return filepath.as_posix().replace('/', '_')

    def upload_file(self, filepath: Path) -> None:
        with httpx.Client(**self._client_conf) as client, filepath.open('rb') as f:
            self._upload_mixin.upload_content(client, f, self._get_file_identity(filepath))

    def download_file(self, filepath: Path, to: Path) -> None:
        with httpx.Client(**self._client_conf) as client:
            stream = client.stream(
                method='GET',
                url=self.DOWNLOAD_FILE.format(resource_id=self._get_file_identity(filepath)),
            )
            with stream as response, open(to, 'wb') as f:
                response: httpx.Response
                for chunk in response.iter_bytes(self.CHUNK_SIZE):
                    self._write_chunk(f, chunk)

    def _write_chunk(self, f: IO[bytes], chunk: bytes) -> None:
        for transformer in self._receive_transformers:
            chunk = transformer.transform(chunk)
        f.write(chunk)
