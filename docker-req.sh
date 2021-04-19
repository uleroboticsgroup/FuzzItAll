#!/bin/bash

yum install glibc-static
yum install zlib*
yum install centos-release-scl
yum install llvm-toolset-7
scl enable llvm-toolset-7 bash
yum install automake
yum install autoconf
yum install llvm-devel
git clone https://github.com/AFLplusplus/AFLplusplus.git
make distrib STATIC=1
make install
cp afl-cc /usr/local/bin/
ldconfig