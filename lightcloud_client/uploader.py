import abc
import hashlib
from typing import IO, Sequence

import httpx

from lightcloud_client.transformers.transformer import ForwardTransformer


class UploadContentMixin(abc.ABC):

    def __init__(
            self,
            chunk_size: int = 1 << 20,
            hash_hit_url: str = '/resources/resource/{resource_id}/hit/{hash}',
            upload_chunk_url: str = '/resources/resource/{resource_id}/chunk/{hash}',
            transformers: Sequence[ForwardTransformer] | None = None
    ) -> None:
        self._chunk_size = chunk_size
        self._hash_hit_url = hash_hit_url
        self._upload_chunk_url = upload_chunk_url
        self._send_transformers = transformers or []

    def upload_content(self, client: httpx.Client, data: IO[bytes], identity: str) -> None:
        """
        Uploads a file to the server

        :param client: Client to use for the upload
        :param data: Content to upload
        :param identity: Identity of the content
        """
        while chunk := data.read(self._chunk_size):
            content_hash = self._get_chunk_hash(chunk)
            if self._is_hash_hits(client, content_hash, identity):
                continue
            for transformer in self._send_transformers:
                chunk = transformer.transform(chunk)
            self._send_chunk(client, content_hash, chunk, identity)

    @staticmethod
    def _get_chunk_hash(chunk: bytes) -> str:
        return hashlib.md5(chunk).hexdigest()

    def _is_hash_hits(self, client: httpx.Client, content_hash: str, identity: str) -> bool:
        hit_request = client.get(
            self._hash_hit_url.format(
                hash=content_hash,
                resource_id=identity,
            )
        )
        if hit_request.status_code >= 300:
            raise PermissionError()
        return hit_request.status_code == 200

    def _send_chunk(self, client: httpx.Client, content_hash: str, content: bytes, identity: str):
        client.post(
            self._upload_chunk_url.format(
                hash=content_hash,
                resource_id=identity,
            ),
            content=content
        )
