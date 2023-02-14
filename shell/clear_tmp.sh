#!bin/sh

logdir=("/webserver/logs" "/opt/tomcat")

for ld in ${logdir[@]}
do
  if [ -e $ld ];then
     find $ld -mtime +7 -name "*.log" -exec rm -rf {} \;
  fi
done

if [ -e /webserver/logs/cishop42/job/handler ];then
  find /webserver/logs/cishop42/job/handler -mtime +3 -name "*.log" -exec rm -rf {} \;
fi

if [ -e /webserver/lastpackages ];then
  find /webserver/lastpackages -mtime +7 -name "*.jar" -exec rm -rf {} \;
fi

if [ -e /webserver/backup ];then
  find /webserver/backup -mtime +7 -name "*.jar_*" -exec rm -rf {} \;
fi

if [ -e /data/applogs/xxl-job ];then
  find /data/applogs/xxl-job -mtime +7 -name "*.zip" -exec rm -rf {} \;
fi

cat /dev/null > /webserver/logs/log.out
cat /dev/null > /opt/tomcat/pricetag/logs/catalina.out

