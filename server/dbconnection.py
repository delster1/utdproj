"""
Basic connection example.
"""
import os
import redis

r = redis.Redis(
    host='redis-10392.c261.us-east-1-4.ec2.redns.redis-cloud.com',
    port=10392,
    decode_responses=True,
    username="default",
    password=os.getenv('REDIS_PASSWORD'),
)

