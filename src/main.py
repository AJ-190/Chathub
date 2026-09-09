from src.auth.router import router as auth_router
from src.users.router import router as users_router
from src.phonebook.router import router as phonebook_router
from src.websocket.manager import router as socket_router
from src.chat.router import router as chat_router
from src.db.database import Base, engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.db.redis import get_redis_client
import asyncio



async def lifespan(app: FastAPI):
    
    async with engine.begin() as conn:
        app.state.redis = await get_redis_client()
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    


app = FastAPI(
    title="ChatHub",
    description="A real time chat backend powered by FastAPI and WebSockets",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(phonebook_router)
app.include_router(socket_router)
app.include_router(chat_router)


@app.get("/")
async def root():
    return "API is running...."