#!/bin/sh

docker exec -it slurmctld bash -c "cd /data/th3fuzz3r/ && ./fuzzitall.sh $1 $2"