from uuid import UUID
from pydantic import BaseModel
from pydantic import Field
from app.domain.subscriptions.billing_period import (BillingPeriod)

class CreateSubscriptionRequest(BaseModel):
    subscriber_actor_id: UUID
    service_actor_id: UUID
    amount: int = Field(
        gt=0,
        description="Amount in cents",
    )
    billing_period: BillingPeriod


class CreateSubscriptionResponse(BaseModel):
    subscription_id: UUID
    transaction_id: UUID