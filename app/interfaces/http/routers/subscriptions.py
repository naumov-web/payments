from uuid import UUID

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status

from app.application.subscriptions.create_subscription import (
    ActorNotFoundError,
)
from app.application.subscriptions.create_subscription import (
    CreateSubscriptionUseCase,
)
from app.application.subscriptions.create_subscription import (
    InsufficientFundsError,
)
from app.application.subscriptions.create_subscription import (
    InvalidSubscriptionError,
)
from app.application.subscriptions.create_subscription import (
    SubscriptionAlreadyExistsError,
)
from app.infrastructure.unit_of_work import (
    UnitOfWork,
)
from app.interfaces.http.schemas.subscription import (
    CreateSubscriptionRequest,
)
from app.interfaces.http.schemas.subscription import (
    CreateSubscriptionResponse,
)

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"],
)


@router.post(
    "",
    response_model=CreateSubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create subscription",
)
async def create_subscription(
    request: CreateSubscriptionRequest,
):
    use_case = CreateSubscriptionUseCase(
        uow=UnitOfWork(),
    )

    try:
        result = await use_case.execute(
            subscriber_actor_id=(
                request.subscriber_actor_id
            ),
            service_actor_id=(
                request.service_actor_id
            ),
            amount=request.amount,
            billing_period=(
                request.billing_period
            ),
        )

    except SubscriptionAlreadyExistsError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    except ActorNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except InsufficientFundsError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except InvalidSubscriptionError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return CreateSubscriptionResponse(
        subscription_id=UUID(
            result["subscription_id"]
        ),
        transaction_id=UUID(
            result["transaction_id"]
        ),
    )