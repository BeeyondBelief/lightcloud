import dataclasses
from typing import Annotated

from fastapi import Depends
from starlette.requests import Request

from lightcloud.const import LIGHT_CLOUD_TOKEN_NAME


@dataclasses.dataclass(frozen=True)
class AuthorizedContext:
    token: str


def try_get_token(request: Request) -> AuthorizedContext:
    token = request.headers.get(LIGHT_CLOUD_TOKEN_NAME)
    *_, token = token.split(maxsplit=1)
    if token is None or not token or len(token) != 36:
        raise PermissionError('NotAuthorized')
    return AuthorizedContext(token)


AuthorizedDepends = Depends(try_get_token)
Authorized = Annotated[AuthorizedContext, AuthorizedDepends]
