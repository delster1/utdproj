import os
import redis
import json

r = redis.Redis(
    host='redis-10392.c261.us-east-1-4.ec2.redns.redis-cloud.com',
    port=10392,
    decode_responses=True,
    username="default",
    password=os.getenv('REDIS_PASSWORD'),
)

def write2redis(jsonline):
    jsonline = json.loads(jsonline)
    for key, value in jsonline.items():
        r.rpush(key, value)
