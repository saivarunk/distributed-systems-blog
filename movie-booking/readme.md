# movie-booking-app

This folder has sample movie booking application which demonstrates simple distributed locking mechanism using FastAPI and Redis

## Running services

```bash
docker-compose up -d
```

## Getting seat availability for movie

Request: 

```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/movies/availability' \
  -H 'accept: application/json'
```

Expected Response:

```json
{"A1":true,"A2":true,"B1":false,"B2":true}
```

## 1. Placing a lock on a seat

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/movies/book/{seat_id}' \
  -H 'accept: application/json'
```

Request:

```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/api/v1/movies/book/B1' \
  -H 'accept: application/json'
```

Expected Response:

```json
{"message":"Seat locked"}
```

In case a lock/booking exists on given seat, the API throws an error

```json
{"detail":"Seat already booked / locked"}
```

## 2. Releasing the lock on a seat

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/movies/book/{seat_id}/action/{action}' \
  -H 'accept: application/json'
```

The action parameters allows any of the two outcomes -> success, failure

- `success` action creates a booking and removes lock
- `failure` action removes lock

Request:

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/movies/book/B1/action/success' \
  -H 'accept: application/json'
```

Expected Response:

```json
{
  "message": "Booking successful. Lock released"
}
```
