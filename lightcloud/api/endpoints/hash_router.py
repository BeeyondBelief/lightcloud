from fastapi import APIRouter, Response

from lightcloud.api.endpoints.upload_router import storage
from lightcloud.api.utils import AuthorizedDepends

hash_router = APIRouter(prefix='/resources')


@hash_router.get('/resource/{resource_id}/hit/{chunk_hash}', dependencies=[AuthorizedDepends])
async def check_cache_hit(resource_id: str, chunk_hash: str):
    resource = storage.get(resource_id)
    response = Response(status_code=204)
    if resource is None:
        return response

    if resource.has_part(chunk_hash):
        response.status_code = 200
        return response
    return response
