#!/bin/sh

set -e
cp redis_data/redis.conf.template redis_data/redis.conf
sed -i "s/\${REDIS_PASSWORD}/$REDIS_PASSWORD/g" redis_data/redis.conf
sed -i "s/\${REDIS_PASSWORD}/$REDIS_PASSWORD/g" redis_data/redis.conf
redis-server /usr/local/etc/redis/redis.conf --appendonly yes --save "" --io-threads
command: 
  - redis-server 
  - /etc/redis/redis.conf 
  - --appendfsync no  # Disable fsync for maximum speed (risk data loss on crash)
  - --activerehashing no  # Disable active rehashing to reduce CPU usage
  - --save ""  # Disable RDB snapshots
  - --io-threads 4  # Use 4 I/O threads (adjust based on CPU cores)
  - --io-threads-do-reads yes  # Enable threads for reads too
exec redis-server /etc/redis/redis.conf tagglabs@tagglabs:~Desktop/tg-inventory-management-system/redis_data
redis-server redis_data/redis.conf

