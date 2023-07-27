#!/bin/bash

# mysql rpm安装方式小版本升级脚本
# 先到https://dev.mysql.com/downloads/mysql/ 下载对应版本的rpm包,解压放在与脚本相同目录
set -e
# 备份配置文件
cp /etc/my.cnf my.cnf.bak
# 备份整个mysql文件夹,包括了数据库文件
cp -r /var/lib/mysql /var/lib/bakmysql
# 数据库导出sql, 上一步已经备份了整个数据库文件,这步可以跳过
mysqldump -uroot -p密码 --set-gtid-purged=off --all-databases --single-transaction > /opt/data.sql

mysql -u root -p密码 --execute="SET GLOBAL innodb_fast_shutdown=0"
systemctl stop mysqld
rpm -Uvh mysql-community-common-5.7.43-1.el7.x86_64.rpm --nodeps
rpm -Uvh mysql-community-libs-compat-5.7.43-1.el7.x86_64.rpm --nodeps 
rpm -Uvh mysql-community-libs-5.7.43-1.el7.x86_64.rpm --nodeps
rpm -Uvh mysql-community-client-5.7.43-1.el7.x86_64.rpm --nodeps
rpm -Uvh mysql-community-server-5.7.43-1.el7.x86_64.rpm --nodeps
systemctl start mysqld

mysql -V
mysql_upgrade -uroot -p密码

