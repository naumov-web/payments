import hashlib
import json
from uuid import UUID

def build_transfer_request_hash(
    *,
    sender_actor_id: UUID,
    receiver_actor_id: UUID,
    amount: int,
) -> str:
    payload = {
        "sender_actor_id": str(
            sender_actor_id
        ),
        "receiver_actor_id": str(
            receiver_actor_id
        ),
        "amount": amount,
    }

    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()