from pydantic import BaseModel, Field
from typing import Literal


class RouteDecision(BaseModel):
    route: Literal[
        "github",
        "rag",
        "search"
    ] = Field(
        description="Agent that should handle the request"
    )