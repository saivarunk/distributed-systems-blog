from typing import Dict

from pydantic import BaseModel


class Movie(BaseModel):
    name: str
    id: str
    seat_map: Dict[str, bool]  # Dictionary to track seat availability


class Booking(BaseModel):
    movie: str
    seat_id: str