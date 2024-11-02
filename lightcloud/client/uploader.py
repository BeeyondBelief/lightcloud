import abc
import hashlib
from typing import IO, Sequence

import httpx

from lightcloud.client.transformers.transformer import ForwardTransformer


class UploadContentMixin(abc.ABC):

    def __init__(
            self,
            chunk_size: int = 1 << 20,
            digest_url: str = '/resources/resource/{resource_id}/digest',
            upload_chunk_url: str = '/resources/resource/{resource_id}/chunk/{hash}',
            transformers: Sequence[ForwardTransformer] | None = None
    ) -> None:
        self._chunk_size = chunk_size
        self._digest_url = digest_url
        self._upload_chunk_url = upload_chunk_url
        self._send_transformers = transformers or []

    def upload_content(self, client: httpx.Client, data: IO[bytes], identity: str) -> None:
        """
        Uploads a file to the server

        :param client: Client to use for the upload
        :param data: Content to upload
        :param identity: Identity of the content
        """
        size = self._get_data_size(data)
        digest = self._get_file_digest(client, identity, size)
        while chunk := data.read(self._chunk_size):
            content_hash = self._get_chunk_hash(chunk)
            if content_hash == digest.pop():
                continue
            for transformer in self._send_transformers:
                chunk = transformer.transform(chunk)
            self._send_chunk(client, content_hash, chunk, identity)

    @staticmethod
    def _get_data_size(data: IO[bytes]) -> int:
        data.seek(0, 2)
        size = data.tell()
        data.seek(0)
        return size

    def _get_file_digest(self, client: httpx.Client, identity: str, size: int) -> list[str]:
        digest_request = client.get(
            self._digest_url.format(
                resource_id=identity,
            )
        )
        if digest_request.status_code != 200:
            values = (size + self._chunk_size - 1) // self._chunk_size
            return [''] * values
        return digest_request.json()['blocks']

    @staticmethod
    def _get_chunk_hash(chunk: bytes) -> str:
        return hashlib.md5(chunk).hexdigest()

    def _send_chunk(self, client: httpx.Client, content_hash: str, content: bytes, identity: str):
        client.post(
            self._upload_chunk_url.format(
                hash=content_hash,
                resource_id=identity,
            ),
            content=content
        )
