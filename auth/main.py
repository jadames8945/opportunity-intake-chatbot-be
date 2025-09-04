# import logging
#
# import uvicorn
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.gzip import GZipMiddleware
#
# from auth.apis.main_api_router import api_router
# from common.configs.app_config import config
#
# logger = logging.getLogger(__name__)
#
#
# def setup_logging():
#     logging.basicConfig(
#         level=logging.INFO,
#         format="%(asctime)s %(levelname)s %(name)s %(message)s",
#     )
#
#
# def setup_middleware(app: FastAPI):
#     app.add_middleware(GZipMiddleware, minimum_size=1000)
#
#     origins = config.allowed_origins()
#
#     logger.info(f"Configured CORS origins: {origins}")
#
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=origins,
#         allow_credentials=True,
#         allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
#         allow_headers=["*"],
#         expose_headers=["*"],
#     )
#
#
# def setup_routes(app: FastAPI):
#     app.include_router(api_router)
#
#
# def create_app() -> FastAPI:
#     app = FastAPI(
#         title="Opportunity Intake Chatbot Authentication",
#         description="Handles user authentication for Opportunity Intake Chatbot",
#         version="1.0.0",
#         docs_url="/docs",
#         redoc_url="/redoc",
#     )
#
#     setup_logging()
#     setup_middleware(app)
#     setup_routes(app)
#
#     return app
#
#
# def main():
#     auth_app = create_app()
#
#     logger.info(f"Starting auth service on port {config.AUTH_PORT}")
#
#     uvicorn.run(auth_app, host="0.0.0.0", port=config.AUTH_PORT)
#
#
# if __name__ == '__main__':
#     main()
