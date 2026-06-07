from uuid import UUID

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status

from app.application.subscriptions.create_subscription import (
    ActorNotFoundError,
    CreateSubscriptionUseCase,
    InsufficientFundsError,
    InvalidSubscriptionError,
    SubscriptionAlreadyExistsError,
)
from app.application.subscriptions.cancel_subscription import (
    CancelSubscriptionUseCase,
    SubscriptionAlreadyCancelledError,
    SubscriptionNotFoundError
)
from app.infrastructure.unit_of_work import UnitOfWork
from app.interfaces.http.schemas.subscription import (
    CreateSubscriptionRequest,
    CreateSubscriptionResponse,
)
from app.application.subscriptions.get_subscription_by_id import GetSubscriptionByIdUseCase
from app.application.subscriptions.get_subscription_by_id import SubscriptionNotFoundError as DetailSubscriptionNotFoundError
from app.interfaces.http.schemas.subscription_details import SubscriptionDetailsResponse

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
async def create_subscription(request: CreateSubscriptionRequest):
    use_case = CreateSubscriptionUseCase(uow=UnitOfWork())

    try:
        result = await use_case.execute(
            subscriber_actor_id=request.subscriber_actor_id,
            service_actor_id=request.service_actor_id,
            amount=request.amount,
            billing_period=request.billing_period,
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
        subscription_id=UUID(result["subscription_id"]),
        transaction_id=UUID(result["transaction_id"]),
    )

@router.delete(
    "/{subscription_id}/cancel",
    status_code=200,
    summary="Cancel subscription",
)
async def cancel_subscription(subscription_id: UUID):
    use_case = CancelSubscriptionUseCase(uow=UnitOfWork())

    try:
        await use_case.execute(subscription_id=subscription_id)

    except SubscriptionNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except SubscriptionAlreadyCancelledError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    return {"success": True}

@router.get(
    "/{subscription_id}",
    response_model=SubscriptionDetailsResponse,
    summary="Get subscription by id",
)
async def get_subscription_by_id(subscription_id: UUID):
    use_case = GetSubscriptionByIdUseCase(uow=UnitOfWork())

    try:
        result = await use_case.execute(subscription_id=subscription_id)
    except DetailSubscriptionNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return SubscriptionDetailsResponse(
        subscription_id=result["subscription_id"],
        subscriber_actor_id=result["subscriber_actor_id"],
        subscriber_name=result["subscriber_name"],
        service_actor_id=result["service_actor_id"],
        service_name=result["service_name"],
        amount=result["amount"],
        billing_period=str(result["billing_period"]),
        status=str(result["status"]),
        next_billing_at=result["next_billing_at"],
        created_at=result["created_at"],
    )