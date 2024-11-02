import dataclasses
from typing import Annotated

from fastapi import Depends
from starlette.requests import Request

from lightcloud.server.const import LIGHT_CLOUD_TOKEN_NAME


@dataclasses.dataclass(frozen=True)
class AuthorizedContext:
    token: str


def try_get_token(request: Request) -> AuthorizedContext:
    token = request.cookies.get(LIGHT_CLOUD_TOKEN_NAME)
    if token is None or not token or len(token) != 36:
        raise PermissionError('NotAuthorized')
    return AuthorizedContext(token)


AuthorizedDepends = Depends(try_get_token)
Authorized = Annotated[AuthorizedContext, AuthorizedDepends]
