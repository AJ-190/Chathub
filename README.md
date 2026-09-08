# ChatHub

A real-time chat backend built with FastAPI and WebSockets. Users authenticate with JWT, open a WebSocket connection, and exchange one-on-one messages that are persisted and delivered live to the recipient.

## Features

- JWT authentication (access + refresh tokens, HS256)
- Token rotation and instant JWT revocation via Redis (jti blocklist)
- Real-time one-on-one messaging over WebSockets
- Message persistence with read/unread flag
- Message history per conversation
- Phonebook (contact create / list / update / delete)
- Async SQLAlchemy 2.0 ORM backed by PostgreSQL
- Alembic migrations

## Tech Stack

| Component | Choice |
|---|---|
| Web framework | FastAPI / Starlette |
| Realtime | WebSockets (`websockets`) |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL (`asyncpg`) |
| Migrations | Alembic |
| Auth | PyJWT, Passlib (argon2) |
| ASGI server | Uvicorn |

## Project Structure

```
├── alembic/                  # DB migrations
├── alembic.ini
├── requirements.txt
└── src/
    ├── main.py               # App entrypoint, router registration
    ├── config/core.py        # Pydantic settings (.env)
    ├── db/
    │   ├── database.py       # Async engine + session
    │   ├── redis.py          # Redis client (WIP)
    │   └── cache.py
    ├── auth/                 # Sign up, login, JWT utilities
    ├── users/                # Users model, get/update
    ├── phonebook/            # Contacts CRUD
    ├── chat/                 # Chat model, WebSocket endpoint, history
    └── websocket/            # ConnectionManager, echo endpoint
```

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL

### Setup

```bash
# 1. Clone and enter the project
git clone https://github.com/AJ-190/Chathub.git
cd Chathub

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create the environment file
touch src/.env
```

Add the following to `src/.env`:

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/chathub
SECRET_KEY=your-secret-key
```

### Database

```bash
alembic upgrade head
```

### Run the server

```bash
uvicorn src.main:app --reload
```

API docs: http://localhost:8000/docs

## Configuration

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | Async SQLAlchemy database URL | — |
| `SECRET_KEY` | JWT signing secret | — |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCES_TOKEN_EXPIRE` | Access token lifetime (minutes) | `60` |
| `REFRESH_TOKEN_TIME` | Refresh token lifetime (minutes) | `10080` |
| `REDIS_URL` | Redis URL for token revocation / jti blocklist | — |

## API Overview

| Method | Path | Description | Auth |
|---|---|---|---|
| POST | `/auth/sign_up` | Register a new user | — |
| POST | `/auth/login` | Exchange credentials for tokens | — |
| POST | `/auth/refresh` | Rotate a refresh token for a new access + refresh pair | Bearer (refresh) |
| POST | `/auth/logout` | Revoke the current token (jti blocked in Redis) | Bearer |
| GET | `/users/get/user/{user_id}` | Get a user | Bearer |
| GET | `/users/` | List all users | Bearer (super_admin) |
| POST | `/phonebook/create_contact` | Add a contact | Bearer |
| GET | `/phonebook/contacts` | List your contacts | Bearer |
| GET | `/phonebook/contacts/{id}` | Get one contact | Bearer |
| PUT | `/phonebook/contacts/{id}` | Update a contact | Bearer |
| DELETE | `/phonebook/contacts/{id}` | Delete a contact | Bearer |
| GET | `/chat/conversations/{user_id}/messages` | Conversation history | Bearer |
| WS | `/chat/ws/chat?token=...` | Live messaging | Query token |

## WebSocket Messaging

Obtain an access token via `/auth/login`, then connect with it as a query parameter:

```python
import asyncio
import json
import websockets

async def main():
    token = "<ACCESS_TOKEN>"
    uri = f"ws://localhost:8000/chat/ws/chat?token={token}"

    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"to": 2, "body": "Hello!"}))
        response = await ws.recv()
        print(response)

asyncio.run(main())
```

Sent:

```json
{"to": 2, "body": "Hello!"}
```

Received by the recipient:

```json
{
  "from": 1,
  "message": "Hello!",
  "body": "Hello!",
  "sent_at": "2026-09-07T03:01:54.031628+00:00"
}
```

The sender also receives a copy with `"self": true`.

Messages are written to the `chat` table before delivery, so history can be fetched later via the conversation endpoint.

## Notes

- New accounts are created with `is_verified = False`; the chat WebSocket rejects unverified users. Flip the flag once a user is verified (e.g. `UPDATE users SET is_verified = true WHERE user_id = 1;`).
- Redis/Celery modules are placeholders and not yet wired into the message flow.

## Author

- Addy Samuel - Backend Engineer 
- The Unfathomable Builder 🫥
