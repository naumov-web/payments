from dataclasses import asdict, is_dataclass
from datetime import datetime
from uuid import UUID


def serialize_value(value):
    if isinstance(value, UUID):
        return str(value)

    if isinstance(value, datetime):
        return value.isoformat()

    if is_dataclass(value):
        return {
            key: serialize_value(val)
            for key, val in asdict(value).items()
        }

    if isinstance(value, list):
        return [
            serialize_value(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            key: serialize_value(val)
            for key, val in value.items()
        }

    return value