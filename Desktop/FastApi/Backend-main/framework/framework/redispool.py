import aioredis
import framework.settings
import framework.utilities

@framework.utilities.run_once
async def get_redis_connection() -> aioredis.Redis:
    return await aioredis.create_redis_pool(framework.settings.redis_url, minsize=1, maxsize=300, encoding='utf8')


