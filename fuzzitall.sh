#!/bin/sh
source ./HS.conf

project_name=$1
repository=$2

# Dowload code
mkdir $project_name
cd $project_name
git clone $repository
project_path=`echo $repository | rev | cut -d/ -f1 | cut -d. -f2 | rev`
cd $project_path

echo $PWD
source $PWD/conf.conf

# Build code
CC=$CC $compilation_file

cd ../..
# Fuzz
jid1=$(sbatch -J $project_name-$project_path-M run-master_fuzzer.slurm $project_name/$project_path)
echo "Waiting for the master to start..."
sleep 5
for i in $(seq 1 $slaves);
do
   sbatch -J $project_name-$project_path-$i run-slave_fuzzer.slurm --dependency=after:$jid1 $project_name/$project_path $i
done
