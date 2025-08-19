import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from .routers import frontend, health, blog

LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | "
    "%(funcName)s() | %(threadName)s | %(message)s"
)

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI):
    # Print all registered routes
    for route in app.routes:
        if hasattr(route, 'path'):
            logger.info(f'Route: {route.name} | Path: {route.path} | Methods: {getattr(route, 'methods', 'N/A')}')  # pyright: ignore[reportAttributeAccessIssue]
    # Startup
    logger.info('Application starting...')
    yield
    # Shutdown
    logger.info('Application shutting down...')

def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.include_router(frontend.router)
    app.include_router(health.router)
    app.include_router(blog.router)

    static_dir = os.path.join(os.path.dirname(__file__), '../../static')
    app.mount('/static', StaticFiles(directory=static_dir), name='static')

    return app

def start_server() -> None:
    logger.info('Starting uvicorn server on port 8027')
    logger.info('Application URL: http://localhost:8027')

    uvicorn.run(
        'app.main:app',
        host='0.0.0.0',
        port=8027,
        reload=False,
        access_log=True
    )

app = create_app()
