from fastapi import APIRouter
from starlette.responses import JSONResponse, StreamingResponse

from lightcloud.api.controllers.upload_file import storage

router = APIRouter(tags=['Download file'], prefix='/download')


@router.get('/file/{filepath:path}')
async def download_file(filepath: str):
    file = storage.get(filepath)
    if file is None:
        return JSONResponse(content='err', status_code=404)

    return StreamingResponse(
        file.iter()
    )
