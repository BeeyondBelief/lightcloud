from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from lightcloud.api.endpoints import download_router, hash_router, upload_router

app = FastAPI()

app.include_router(upload_router.upload_router)
app.include_router(download_router.download_router)
app.include_router(hash_router.hash_router)


@app.exception_handler(PermissionError)
def permission_error_handler(exc: PermissionError, _: Request) -> JSONResponse:
    return JSONResponse(status_code=403, content='')
