#!/bin/bash

yum install -y glibc-static
yum install -y zlib*
yum install -y centos-release-scl
yum install -y llvm-toolset-7
scl enable llvm-toolset-7 bash
yum install -y automake
yum install -y autoconf
yum install -y llvm-devel
git clone https://github.com/AFLplusplus/AFLplusplus.git
cd AFLplusplus
git checkout 86a8ef168dda766d2f25f15c15c4d3ecf21d0667 # They stopped support for llvm < 11
make distrib STATIC=1
make install
cp afl-cc /usr/local/bin/
ldconfig