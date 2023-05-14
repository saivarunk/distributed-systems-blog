from fastapi import HTTPException

from redis_client import redis_client, LOCK_EXPIRATION_TIME


def lock_seat(seat: str) -> None:
    # Generate the key for the seat lock
    key = f"seat:{seat}"

    # Try to acquire the lock
    acquired = redis_client.set(key, "locked", ex=LOCK_EXPIRATION_TIME, nx=True)
    if not acquired:
        raise HTTPException(status_code=409, detail="Seat already locked")


def unlock_seat(seat: str) -> None:
    # Generate the key for the seat lock
    key = f"seat:{seat}"

    # Release the lock
    redis_client.delete(key)
