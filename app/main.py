import logging
from pathlib import Path

import uvicorn
from common.configs.app_config import config
from common.redis_infrastructure import infra
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.apis.api_router import api_router

load_dotenv(Path(__file__).parent.parent / ".env")

logger = logging.getLogger(__name__)


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    logging.getLogger("langchain").setLevel(logging.ERROR)
    logging.getLogger("langchain_core").setLevel(logging.ERROR)
    logging.getLogger("langchain_openai").setLevel(logging.ERROR)


def setup_infrastructure():
    try:
        infra.setup()
        logger.info("Infrastructure setup completed successfully")
    except Exception as e:
        logger.error(f"Infrastructure setup failed: {e}")
        raise


def setup_middleware(app: FastAPI):
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    origins = config.allowed_origins()
    logger.info(f"Configured CORS origins: {origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
        allow_headers=["*"],
        expose_headers=["*"],
    )


def setup_routes(app: FastAPI):
    app.include_router(api_router)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Opportunity Intake Chatbot Backend",
        description="Backend API for Opportunity Intake Chatbot with intelligent conversation and form generation capabilities",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    setup_logging()
    setup_infrastructure()
    setup_middleware(app)
    setup_routes(app)

    return app


def main():
    app = create_app()
    logger.info(f"Starting server on port {config.PORT}")
    uvicorn.run(app, host="0.0.0.0", port=config.PORT, log_level="info")


def get_app():
    return create_app()


if __name__ == "__main__":
    main()
# Test comment
