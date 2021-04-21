#!/bin/sh
docker exec -it slurmctld bash -c "cd /data/fuzzitall/ && ./status.sh -s /data/fuzzitall/$1/$2/fuzz_out"