#!/bin/sh
cd outputs
mkdir $1
cd $1
docker cp slurmctld:/data/fuzzitall/$1/$2/fuzz_out fuzz_out
tar cvzf $1.tar.gz fuzz_out