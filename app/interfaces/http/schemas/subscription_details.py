from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class SubscriptionDetailsResponse(BaseModel):
    subscription_id: UUID
    subscriber_actor_id: UUID
    subscriber_name: str
    service_actor_id: UUID
    service_name: str
    amount: int
    billing_period: str
    status: str
    next_billing_at: datetime
    created_at: datetime