from pydantic import BaseModel


class UserInfo(BaseModel):
    email: str
    first_name: str
    last_name: str
    country: str


class NextQueryResponse(BaseModel):
    next_sentence: str | None
