#!/bin/sh

# java程序停止脚本

# 程序名或启动包名
app="main.jar"

is_exist(){
    pid=`ps -ef|grep $app|grep -v grep|awk '{print $2}' `
    #如果不存在返回0，存在返回1    
    if [ -z "${pid}" ]; then
		  return 0
    else
		  return 1
    fi
}

is_exist
if [ $? -eq "1" ]; then
    echo "${app} is stopping,pid ${pid}..."
	  #温柔一刀
    kill $pid
	  sleep 3
	 
	  is_exist
	  if [ $? -eq "1" ]; then
      #还在则强杀
      kill -9 $pid
      sleep 2
      echo "kill -9 ${pid}"
      echo "${app} process stopped"
	  fi
else
     echo "${app} is not running"  
fi
   
   
