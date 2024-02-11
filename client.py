import os
import tempfile
from pathlib import Path
import hashlib
import httpx


class CloudClient:

    CHUNK_SIZE = 1 << 20  # 1 MB

    def __init__(self, server_addr: str):
        self._client_conf = dict(
            base_url=server_addr,
            timeout=httpx.Timeout(None, read=180.0)
        )

    @staticmethod
    def _get_chunk_hash(chunk: bytes) -> str:
        return hashlib.md5(chunk).hexdigest()

    def upload_file(self, filepath: Path) -> None:
        with httpx.Client(**self._client_conf) as client, filepath.open('rb') as f:
            while chunk := f.read(self.CHUNK_SIZE):
                context_hash = self._get_chunk_hash(chunk)
                hit_request = client.get(
                    f'/upload/file/hash/{context_hash}/path/{filepath.as_posix()}',
                )
                if hit_request.status_code == 200:
                    continue
                client.post(
                    f'/upload/file/hash/{context_hash}/path/{filepath.as_posix()}',
                    files={
                        'part': chunk
                    }
                )

    def download_file(self, filepath: Path, to: Path) -> None:
        with httpx.Client(**self._client_conf) as client:
            stream = client.stream(
                method='GET',
                url=f'/download/file/{filepath.as_posix()}'
            )
            tmp_file = tempfile.NamedTemporaryFile(delete=False)
            with stream as r, tmp_file as f:
                for chunk in r.iter_bytes():
                    f.write(chunk)
            os.rename(tmp_file.name, to)


if __name__ == '__main__':
    client = CloudClient(server_addr='http://127.0.0.1:8000')
    file = Path('/Users/nikita/Downloads/DesignPatterns.pdf')

    client.upload_file(file)
    client.download_file(file, to=Path('bob.pdf'))
