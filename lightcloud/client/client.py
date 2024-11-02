import io
import uuid
from pathlib import Path

import httpx

from lightcloud.client.downloader import DownloaderMixin
from lightcloud.client.transformers.transformer import Transformer
from lightcloud.client.uploader import UploadContentMixin


class CloudClient:

    CHUNK_SIZE = 5 << 20

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
        self._transformers = []
        self._upload_mixin = UploadContentMixin(
            chunk_size=self.CHUNK_SIZE,
            transformers=self._transformers
        )
        self._download_mixin = DownloaderMixin(
            chunk_size=self.CHUNK_SIZE,
            transformers=self._transformers
        )

    def transformers(self, *t: Transformer) -> 'CloudClient':
        self._transformers.extend(t)
        return self

    @staticmethod
    def _get_file_identity(filepath: Path) -> str:
        return filepath.as_posix().replace('/', '_')

    def upload_file(self, filepath: Path) -> None:
        with httpx.Client(**self._client_conf) as client, filepath.open('rb') as f:
            self._upload_mixin.upload_content(client, f, self._get_file_identity(filepath))

    def upload_content(self, content: bytes, identity: str) -> None:
        with httpx.Client(**self._client_conf) as client:
            self._upload_mixin.upload_content(client, io.BytesIO(content), identity)

    def download_file(self, filepath: Path, to: Path) -> None:
        with httpx.Client(**self._client_conf) as client, open(to, 'wb') as f:
            download_stream = self._download_mixin.download(client, self._get_file_identity(filepath))
            for part in download_stream:
                f.write(part)

    def download_content(self, identity: str) -> bytes:
        content = b''
        with httpx.Client(**self._client_conf) as client:
            for part in self._download_mixin.download(client, identity):
                content += part
        return content
