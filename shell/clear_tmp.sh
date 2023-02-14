#!bin/sh

logdir=("/webserver/logs" "/opt/tomcat")
# 清理上面目录下的.log 和 log.gz文件
for ld in ${logdir[@]}
do
  if [ -e $ld ];then
     find $ld -mtime +7 -name "*.log" -o -name "*.log.gz" -exec rm -rf {} \;
  fi
done

# 清空tomcat catalina.out
cat /dev/null > /opt/tomcat/logs/catalina.out

