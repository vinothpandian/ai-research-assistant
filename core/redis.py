import hashlib
import json
from typing import Any, List

import numpy as np
import redis

from core.settings import Settings

CacheKeys = List[str | int]


class RedisCache:
    client = None

    def __init__(self, settings: Settings) -> None:
        self.client = redis.Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.db,
        )

    @property
    def connected(self):
        if self.client is None:
            return False

        return self.ping()

    @staticmethod
    def _generate_key(keys: CacheKeys) -> str:
        return hashlib.md5("".join(map(str, keys)).encode()).hexdigest()

    def get(self, keys: CacheKeys) -> np.ndarray | None:
        key = self._generate_key(keys)

        if data := self.client.get(key):
            data = json.loads(data)
            return data

        return None

    def set(self, keys: CacheKeys, value: Any, ex: int = 60 * 5) -> None:
        key = self._generate_key(keys)
        data = json.dumps(value)
        self.client.set(key, data, ex=ex)

    def delete(self, keys: CacheKeys) -> None:
        key = self._generate_key(keys)
        self.client.delete(key)

    def ping(self) -> bool:
        return self.client.ping()

    def disconnect(self) -> None:
        self.client.close()
