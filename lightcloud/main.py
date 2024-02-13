from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from lightcloud.api.controllers import download_file, upload_file


app = FastAPI()

app.include_router(upload_file.router)
app.include_router(download_file.router)


@app.exception_handler(PermissionError)
def permission_error_handler(exc: PermissionError, _: Request) -> JSONResponse:
    return JSONResponse(status_code=403, content='')
