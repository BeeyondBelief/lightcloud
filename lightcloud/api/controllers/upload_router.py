from fastapi import APIRouter
from fastapi.requests import Request

from lightcloud.api.utils import AuthorizedDepends
from lightcloud.domain.storage import SlackFile

upload_router = APIRouter(prefix='/resources')
storage: dict[str, 'SlackFile'] = {}


@upload_router.post('/resource/{resource_id}/chunk/{chunk_hash}', dependencies=[AuthorizedDepends])
async def upload_content(resource_id: str, chunk_hash: str, request: Request):
    resource = storage.get(resource_id)
    if resource is None:
        resource = SlackFile(resource_id)
        storage[resource_id] = resource

    file_part = resource.create_part(chunk_hash)
    async for chunk in request.stream():
        file_part.add_chunk(chunk)
