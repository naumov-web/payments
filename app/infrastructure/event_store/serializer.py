from datetime import datetime
from decimal import Decimal
from uuid import UUID


def serialize_value(value):
    if isinstance(value, UUID):
        return str(value)

    if isinstance(value, Decimal):
        return str(value)

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            key: serialize_value(val)
            for key, val in value.items()
        }

    if isinstance(value, list):
        return [serialize_value(item) for item in value]

    return value


def deserialize_value(value):
    return value