from pydantic import BaseModel, Field


class VlanCreate(BaseModel):
    site_id: int = Field(..., gt=0)
    vid: int = Field(..., ge=1, le=4094)
    name: str
    description: str | None = None


class VlanUpdate(BaseModel):
    site_id: int = Field(..., gt=0)
    vid: int | None = Field(default=None, ge=1, le=4094)
    name: str | None = None
    description: str | None = None


class VlanResponse(BaseModel):
    vid: int
    site_id: int
    name: str
    description: str | None = None
