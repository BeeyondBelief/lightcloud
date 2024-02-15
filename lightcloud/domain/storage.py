from typing import Generator


class SlackFile:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._parts: list[SlackFilePart] = []

    def create_part(self, part_hash: str) -> 'SlackFilePart':
        part = SlackFilePart(part_hash)
        self._parts.append(part)
        return part

    def scan(self) -> Generator[str, None, None]:
        for part in reversed(self._parts):
            yield part.fingerprint

    def iter(self) -> Generator[bytes, None, None]:
        for part in self._parts:
            yield from part.iter()


class SlackFilePart:
    def __init__(self, fingerprint: str):
        self.fingerprint = fingerprint
        self._chunks = []

    def add_chunk(self, chunk: bytes) -> None:
        self._chunks.append(chunk)

    def iter(self) -> Generator[bytes, None, None]:
        for chunk in self._chunks:
            yield chunk
