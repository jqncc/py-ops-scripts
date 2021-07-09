#!/bin/bash

# mysql 数据导出脚本. sh exportsql.sh db sqlfile

# 数据库连接信息设置
readonly dbserver="localhost"
readonly dbuser=("user" "pwd")
readonly dbport="3306"

db=$1
sqlfile=$2

mysqldump -h$dbserver -P${dbport} -u${dbuser[0]} -p${dbuser[1]} ${db} < $sqlfile > sql.log

