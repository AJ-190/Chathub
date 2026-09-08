import redis.asyncio as airedis
from src.config.core import settings

async def get_redis_client() -> airedis.Redis: 
    url = settings.REDIS_URL
    if not  url:
        print("Redis ULR not set")
        return None
    
    try:
        client = await airedis.from_url(url, decode_responses=True)
        await client.ping()
        print("Connceted to redis successfully")
    except Exception as e:
        print(f"Error ocurred whole connecting redis: {e}")
        
    return client


async def block_jti(redis: airedis.Redis, jti: str, user_id: int, exp: int) -> bool:
    try:
        await redis.setex(f"blocked_jti:{user_id}", exp, jti)
    except Exception as e:
        print("f Error ocurred while blocking token: {e}")
        
        
async def check_jti_blocked(redis: airedis.Redis, jti: str, user_id: int):
    try:
        jti_St =  await redis.get(f"blocked_jti:{user_id}")
        if jti_St == jti:
            return True
        return False
    except Exception as e:
        print(f"Error ocurred while checking jti")
        
        
async def rate_limitter(redis: airedis, user_id: int):
    pass