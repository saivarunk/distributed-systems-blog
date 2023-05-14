from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict

from models import Movie, Booking
from redis_client import redis_client
from utils import lock_seat, unlock_seat

app = FastAPI(name="Movie Booking Service", version="1.0.0")

movie = Movie(id="avengers_endgame", name="Avengers Endgame",
              seat_map={"A1": True, "A2": True, "B1": True, "B2": True})


@app.on_event("startup")
async def startup_event():
    # Set initial seat availability
    for seat in movie.seat_map.keys():
        booking_key = f"booking:{seat}"
        if not redis_client.exists(booking_key):
            redis_client.hset(f"movie:{movie.id}", seat, "True")


@app.get("/api/v1/movies/availability")
def get_seat_availability() -> Dict[str, bool]:
    # Retrieve all movie seat availability from Redis
    movies = redis_client.keys("movie:*")
    seat_availability = {}

    # Iterate through each movie and extract seat availability
    for movie in movies:
        movie_data = redis_client.hgetall(movie)
        seat_map = {}

        # Check booking and lock details for each seat
        for seat, availability in movie_data.items():
            seat = seat.decode("utf-8")
            booking_key = f"booking:{seat}"
            lock_key = f"seat:{seat}"

            if redis_client.exists(booking_key) or redis_client.exists(lock_key):
                seat_map[seat] = False  # Seat is booked or locked
            else:
                seat_map[seat] = True  # Seat is available

        seat_availability = seat_map

    return seat_availability


@app.post("/api/v1/movies/book/{seat_id}")
async def book_seat(seat_id: str):
    booking_key = f"booking:{seat_id}"
    lock_key = f"seat:{seat_id}"

    if redis_client.exists(booking_key) or redis_client.exists(lock_key):
        raise HTTPException(status_code=409, detail="Seat already booked / locked")

    lock_seat(seat_id)
    return JSONResponse(status_code=200, content={"message": "Seat locked"})


@app.post("/api/v1/movies/book/{seat_id}/action/{action}")
async def process_booking(seat_id: str, action: str):
    if action == "success":
        movie_data = redis_client.hgetall(f"movie:{movie.id}")

        # Update seat availability in movie data
        movie_data[seat_id] = "False"

        # Save updated movie data to Redis
        redis_client.hmset(f"movie:{movie.id}", movie_data)

        # Save booking details and unlock the seat
        booking = Booking(movie=movie.id, seat_id=seat_id)
        booking_key = f"booking:{seat_id}"
        redis_client.hmset(booking_key, booking.dict())
        unlock_seat(seat_id)
        return JSONResponse(status_code=200, content={"message": "Booking successful. Lock released"})
    elif action == "failure":
        # Unlock the seat
        unlock_seat(seat_id)
        return JSONResponse(status_code=200, content={"message": "Booking failed. Lock released"})
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
