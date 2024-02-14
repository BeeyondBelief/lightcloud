from fastapi import APIRouter
from starlette.responses import JSONResponse, StreamingResponse

from lightcloud.api.controllers.upload_router import storage

download_router = APIRouter(prefix='/resources')


@download_router.get('/resource/{resource_id}')
async def download_full_resource(resource_id: str):
    resource = storage.get(resource_id)
    if resource is None:
        return JSONResponse(content='err', status_code=404)
    return StreamingResponse(
        resource.iter()
    )
