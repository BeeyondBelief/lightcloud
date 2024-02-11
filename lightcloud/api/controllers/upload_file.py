from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from lightcloud.domain.storage import SlackFile

router = APIRouter(tags=['Upload file'], prefix='/upload')
storage: dict[str, 'SlackFile'] = {}


@router.post('/file/hash/{chunk_hash}/path/{filepath:path}')
async def upload_file(filepath: str, chunk_hash: str, request: Request):
    if not filepath:
        return JSONResponse(status_code=418, content='')
    file = storage.get(filepath)
    if file is None:
        file = SlackFile(filepath)
        storage[filepath] = file

    file_part = file.create_part(chunk_hash)
    async for chunk in request.stream():
        file_part.add_chunk(chunk)


@router.get('/file/hash/{chunk_hash}/path/{filepath:path}')
async def check_cache_hit(chunk_hash: str, filepath: str):
    file = storage.get(filepath)
    response = JSONResponse(status_code=404, content='')
    if file is None:
        return response

    if file.has_part(chunk_hash):
        response.status_code = 200
        return response
    return response
