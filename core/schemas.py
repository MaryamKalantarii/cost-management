from typing import Annotated
from pydantic import BaseModel, Field

class CostBase(BaseModel):
    description: Annotated[str, Field(min_length=3, pattern=r'^[a-zA-Z0-9 ]+$', example="Lunch payment")]
    amount: Annotated[float, Field(ge=0, example=150.75)]

class CostCreate(CostBase):
    pass


class CostUpdate(CostBase):
    pass

class CostResponse(CostBase):
    id: int