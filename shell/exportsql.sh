#!/bin/bash

# mysql 数据导出脚本. sh exportsql.sh db sqlfile

# 数据库连接信息设置
readonly dbserver="localhost"
readonly dbuser=("user" "pwd")
readonly dbport="3306"

db=$1
sqlfile=$2

while getopts :ab:c opt
do
  case "$opt" in
  a) echo "Found the -a option" ;;
  b) echo "Found the -b option, with parameter value $OPTAVG" ;;
  c) echo "Found the -c option" ;;
  *) echo "Unknown option: $opt" ;;
  esac
done


