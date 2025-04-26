#!/bin/sh

set -e
# Create final config from template
cp redis_data/redis.conf.template redis_data/redis.conf
sed -i "s/\${REDIS_PASSWORD}/$REDIS_PASSWORD/g" redis_data/redis.conf
sed -i "s/\${REDIS_PASSWORD}/$REDIS_PASSWORD/g" redis_data/redis.conf

conf.template > /redis.conf
exec redis-server /redis.conf

exec redis-server redis_data/redis.conf