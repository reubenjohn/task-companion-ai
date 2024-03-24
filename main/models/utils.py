import os
from upstash_redis import Redis

_redis = None


def redis():
    global _redis
    if _redis == None:
        _redis = Redis(
            url=os.environ["KV_REST_API_URL"],
            token=os.environ["KV_REST_API_TOKEN"],
        )
    return _redis


UserId = int
