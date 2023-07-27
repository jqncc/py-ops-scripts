 #!/bin/bash

# java程序 运行/停止/重启 脚本,适用于以jar方式启动


#使用说明，用来提示输入参数
usage() {
    echo "Usage: [start|stop|restart|status]"
    exit 1
}

error_exit ()
{
    echo "ERROR: $1 !!"
    exit 1
}

BIN_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# java启动jar包名
appStarter=sentinel-dashboard-1.8.0.jar

 #检查程序是否在运行
 is_exist(){
   pid=`ps -ef|grep $appStarter|grep -v grep|awk '{print $2}' `
   #如果不存在返回1，存在返回0     
   if [ -z "${pid}" ]; then
     return 1
   else
     return 0
   fi
 }
  
 #启动方法
 start(){
    is_exist
    if [ $? -eq "0" ]; then
      error_exit "${appStarter} is already running. pid=${pid} ."
    fi
   # 查找jar文件所在目录(相对脚本目录: . , lib, ../, ../lib 4个位置),如果不在以下目录,请显式指定
    JAR_DIR=$BIN_DIR
    [ ! -e "$JAR_DIR/$appStarter" ] && JAR_DIR=$BIN_DIR/lib
    [ ! -e "$JAR_DIR/$appStarter" ] && JAR_DIR=$BIN_DIR/..
    [ ! -e "$JAR_DIR/$appStarter" ] && JAR_DIR=$BIN_DIR/../lib
    [ ! -e "$JAR_DIR/$appStarter" ] && unset JAR_DIR

    if [ -z "$JAR_DIR" ]; then
      error_exit "$appStarter file is not found"
    fi

    [ ! -e "$JAVA_HOME/bin/java" ] && JAVA_HOME=$HOME/jdk/java
    [ ! -e "$JAVA_HOME/bin/java" ] && JAVA_HOME=/usr/java
    [ ! -e "$JAVA_HOME/bin/java" ] && unset JAVA_HOME

    if [ -z "$JAVA_HOME" ]; then
      if $darwin; then
        if [ -x '/usr/libexec/java_home' ] ; then
          export JAVA_HOME=`/usr/libexec/java_home`
        elif [ -d "/System/Library/Frameworks/JavaVM.framework/Versions/CurrentJDK/Home" ]; then
          export JAVA_HOME="/System/Library/Frameworks/JavaVM.framework/Versions/CurrentJDK/Home"
        fi
      else
        JAVA_PATH=`dirname $(readlink -f $(which javac))`
        if [ "x$JAVA_PATH" != "x" ]; then
          export JAVA_HOME=`dirname $JAVA_PATH 2>/dev/null`
        fi
      fi
      if [ -z "$JAVA_HOME" ]; then
            error_exit "Please set the JAVA_HOME variable in your environment, We need java(x64)! jdk8 or later is better!"
      fi
    fi

    export JAVA_HOME
    JAVACMD="$JAVA_HOME/bin/java"
    JAVA_OPS="-server -Xms256m -Xmx512m -Xss256k -XX:MetaspaceSize=128M -XX:MaxMetaspaceSize=128M -Djava.security.egd=file:/dev/./urandom"
     cd $JAR_DIR
     nohup java -jar $JAVA_OPS $appStarter> console.out 2>&1 &
     echo "${appStarter} start successfully"
 }
  
 #停止方法
 stop(){
     is_exist
     if [ $? -eq "0" ]; then
       kill $pid
       sleep 3
       is_exist
       if [ $? -eq "0" ]; then
         kill -9 $pid
       fi
     else
       echo "${APP_NAME} is not running"
     fi
 }
  
 #输出运行状态
 status(){
   is_exist
   if [ $? -eq "0" ]; then
     echo "${APP_NAME} is running. Pid is ${pid}"
   else
     echo "${APP_NAME} is NOT running."
   fi
 }
  
 #重启
 restart(){
   stop
   start
 }
  
 #根据输入参数，选择执行对应方法，不输入则执行使用说明
 case "$1" in
   "start")
     start
     ;;
   "stop")
     stop
     ;;
   "status")
     status
     ;;
   "restart")
     restart
     ;;
   *)
     usage
     ;;
 esac
