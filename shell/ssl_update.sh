#!/bin/bash

# openssl升级脚本
set -e
yum install -y gcc gcc-c++ autoconf automake zlib-devel pcre-devel
tar -xzf openssl-1.1.1q.tar.gz
cd openssl-1.1.1q
./config --prefix=/usr/local/openssl --openssldir=/etc/ssl --shared zlib
make
make install
#更新系统库
sudo echo "/usr/local/openssl/lib" > /etc/ld.so.conf.d/openssl.conf
sudo ldconfig
mv /usr/bin/openssl /usr/bin/openssl.old
ln -s /usr/local/openssl/bin/openssl /usr/bin/openssl
openssl version