from uuid import UUID
from pydantic import BaseModel

class ActorDetailsResponse(BaseModel):
    actor_id: UUID
    name: str
    email: str
    role: str
    balance: int