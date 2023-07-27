#!/bin/bash
# openssh升级脚本
set -e
# 依赖库安装,已经有的忽略
# 安装包官网太慢,国内镜像地址:https://mirrors.aliyun.com/pub/OpenBSD/OpenSSH/portable/
yum install -y wget gcc pam-devel libselinux-devel zlib-devel openssl-devel
cp /etc/ssh/sshd_config sshd_config.bak
cp /etc/pam.d/sshd sshd.bak
cd openssh-9.3p1
# openssl目录如果没有,解压openssl源码包
./configure --prefix=/usr --sysconfdir=/etc/ssh --with-zlib --with-pam --with-ssl-dir=/usr/local/openssl
make
make install
chmod 600 /etc/ssh/ssh_host_ecdsa_key
chmod 600 /etc/ssh/ssh_host_ed25519_key
chmod 600 /etc/ssh/ssh_host_rsa_key
if test -e /lib/systemd/system/sshd.service
then
  mv /lib/systemd/system/sshd.service /lib/systemd/system/sshd.service.bak
fi
cp -a contrib/redhat/sshd.init /etc/init.d/sshd
chmod u+x /etc/init.d/sshd
chkconfig --add sshd
chkconfig sshd on
systemctl daemon-reload
systemctl restart sshd

echo 'openssh upgrade finish'