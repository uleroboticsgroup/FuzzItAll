#!/bin/sh

docker exec -it slurmctld bash -c "cd /data/fuzzitall/ && ./fuzzitall.sh $1 $2"