from fastapi import APIRouter, Response
from pydantic import BaseModel

from lightcloud.api.endpoints.upload_router import storage
from lightcloud.api.utils import AuthorizedDepends

hash_router = APIRouter(prefix='/resources')


class DigestResponse(BaseModel):
    blocks: list[str]


@hash_router.get('/resource/{resource_id}/digest', dependencies=[AuthorizedDepends])
async def get_digest(resource_id: str):
    resource = storage.get(resource_id)
    if resource is None:
        return Response(status_code=404)
    return DigestResponse(blocks=[part for part in resource.scan()])
