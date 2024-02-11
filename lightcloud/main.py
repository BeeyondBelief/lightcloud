from fastapi import FastAPI
from lightcloud.api.middleware.token_auth import TokenAuthMiddleware

app = FastAPI()


app.add_middleware(TokenAuthMiddleware)

from lightcloud.api.controllers import upload_file
from lightcloud.api.controllers import download_file

app.include_router(upload_file.router)
app.include_router(download_file.router)
