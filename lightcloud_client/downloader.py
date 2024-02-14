import abc
from typing import IO, Sequence

import httpx

from lightcloud_client.transformers.transformer import BackwardTransformer


class DownloaderMixin(abc.ABC):

    def __init__(
            self,
            chunk_size: int = 1 << 20,
            download_chunk_url: str = '/resources/resource/{resource_id}',
            transformers: Sequence[BackwardTransformer] | None = None
    ) -> None:
        self._chunk_size = chunk_size
        self._download_chunk_url = download_chunk_url
        self._receive_transformers = transformers or []

    def download_content(self, client: httpx.Client, to: IO[bytes], identity: str, ) -> None:
        """
        Downloads a content from the server

        :param client: Client to use for the download
        :param to: Where to write the content
        :param identity: Identity of the content
        """
        stream = client.stream(
            method='GET',
            url=self._download_chunk_url.format(resource_id=identity),
        )
        with stream as response:
            response: httpx.Response
            for chunk in response.iter_bytes(self._chunk_size):
                for transformer in self._receive_transformers:
                    chunk = transformer.reverse(chunk)
                to.write(chunk)
