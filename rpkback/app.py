from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .exceptions import HttpException
from .files.routes import files
from .packages.routes import packages
from .tokens.routes import tokens
from .users.routes import users
from .core.routes import core


async def exception_handler(request: Request, exception: HttpException):
    return JSONResponse(
        {"detail": exception.detail if len(exception.args) == 0 else exception.args[0]},
        status_code=exception.code,
    )


def create_app() -> FastAPI:
    app = FastAPI(
        title="Raccoon Package Tool",
        description="simple backend for raccoon package tool",
        version="0.0.1",
        contact={
            'name': "Eugene Ivanov",
            'url': 'https://t.me/saladware',
        }
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_exception_handler(HttpException, exception_handler)
    app.include_router(core)
    app.include_router(users)
    app.include_router(packages)
    app.include_router(tokens)
    app.include_router(files)
    return app
