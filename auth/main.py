import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.apis.main_api_router import api_router
from common.configs.app_config import config

logger = logging.getLogger(__name__)


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def setup_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.allowed_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )


def setup_routes(app: FastAPI):
    app.include_router(api_router)


def main():
    app = FastAPI(title="Auth Service", version="1.0.0")
    setup_logging()
    setup_middleware(app)
    setup_routes(app)

    logger.info(f"Starting auth service on port {config.AUTH_PORT}")

    uvicorn.run(app, host="0.0.0.0", port=config.AUTH_PORT)


if __name__ == '__main__':
    main()
