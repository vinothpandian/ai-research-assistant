import dramatiq
from dramatiq.brokers.redis import RedisBroker

from core.settings import settings

redis_broker = RedisBroker(
    host=settings.redis.host,
    port=settings.redis.port,
)

dramatiq.set_broker(redis_broker)
