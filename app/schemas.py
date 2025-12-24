from pydantic import BaseModel, Field

class ProposalRequest(BaseModel):
    client_name: str = Field(default="")
    user_input: str = Field(..., min_length=10)
    api_key: str = Field(..., min_length=20)


class ProposalResponse(BaseModel):
    project_scope: str
    estimated_timeline: int
    pricing: str
    justification: str
