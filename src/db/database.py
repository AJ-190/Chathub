from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from src.config.core import settings

Base = declarative_base()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args= {"statement_cache_size": 0},
    pool_size=5,
    pool_recycle=300,
    )

AsynSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, class_=AsyncSession)

async def get_db():
    async with AsynSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
    