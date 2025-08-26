import os
from typing import cast

class AuthConfig:
    def __init__(self):
        self.ENV = cast(str, os.getenv("ENV", "DEV"))
        self.PORT = int(os.getenv("AUTH_PORT", "8887"))
        
    def allowed_origins(self):
        env_origins = os.getenv("ALLOWED_ORIGINS")
        if env_origins:
            return [origin.strip() for origin in env_origins.split(",")]

        return [
            "http://localhost:3000",
            "https://opportunity-intake-chatbot.coolify.dd-dpe.com",
        ]


config = AuthConfig() 