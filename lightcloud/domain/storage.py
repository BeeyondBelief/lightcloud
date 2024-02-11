from typing import Generator


class SlackFile:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._parts: dict[str, SlackFilePart] = {}

    def create_part(self, part_hash: str) -> 'SlackFilePart':
        part = SlackFilePart(part_hash)
        self._parts[part_hash] = part
        return part

    def has_part(self, chunk_hash: str) -> bool:
        try:
            return chunk_hash in self._parts
        except KeyError:
            return False

    def iter(self) -> Generator[bytes, None, None]:
        for part in self._parts.values():
            yield from part.iter()


class SlackFilePart:
    def __init__(self, part_hash: str):
        self.hash = part_hash
        self._chunks = []

    def add_chunk(self, chunk: bytes) -> None:
        self._chunks.append(chunk)

    def iter(self) -> Generator[bytes, None, None]:
        for chunk in self._chunks:
            yield chunk
