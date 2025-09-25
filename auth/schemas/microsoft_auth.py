from pydantic import BaseModel


class MicrosoftLoginRequest(BaseModel):
    accessToken: str
    userInfo: dict
