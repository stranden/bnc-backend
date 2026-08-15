from pydantic import BaseModel


class NetworkTemplateResponse(BaseModel):
    slug: str
    name: str
    description: str
