#!/bin/sh
docker exec -it slurmctld bash -c "cd /data/th3fuzz3r/ && ./status.sh -s /data/th3fuzz3r/$1/$2/fuzz_out"