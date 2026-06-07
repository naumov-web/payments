from uuid import UUID
from pydantic import BaseModel, EmailStr

class CreateActorRequest(BaseModel):
    actor_id: UUID
    email: EmailStr
    full_name: str

class CreateActorResponse(BaseModel):
    actor_id: UUID
    status: str