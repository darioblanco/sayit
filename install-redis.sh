#!/bin/bash
echo "Download latest stable Redis version"
curl -O http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
echo "Compile Redis"
make
echo "Test if the Redis build works correctly"
make test
echo "Moving redis-server to /usr/local/bin (sudo privileges needed)"
sudo cp src/redis-server /usr/local/bin
echo "Moving redis-cli to /usr/local/bin (sudo privileges needed)"
sudo p src/redis-cli /usr/local/bin
echo "Cleaning up downloaded directories"
cd ..
rm -f redis-stable.tar.gz
rm -rf redis-stable
