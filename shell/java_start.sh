#!/bin/sh

# java程序启动脚本,适用于主jar包中指定了classpath和main-class的程序
# 项目目录结构:
#    project->main.jar
#           ->bin/start.sh


# 主jar包名称
appStarter="main.jar"
appName="myapp"

cygwin=false
darwin=false
os400=false
case "`uname`" in
CYGWIN*) cygwin=true;;
Darwin*) darwin=true;;
OS400*) os400=true;;
esac
error_exit ()
{
    echo "ERROR: $1 !!"
    exit 1
}
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
BASE_DIR=`cd $(dirname $0)/..; pwd`
JAVACMD="$JAVA_HOME/bin/java"
# jvm参数
JAVA_OPT="-server -Xms256M -Xmx384M -Xss256k -XX:MetaspaceSize=128M -XX:MaxMetaspaceSize=256M"
 
nohup $JAVACMD ${JAVA_OPT} -jar ${BASE_DIR}/${appStarter} >> console.out 2>&1 &

echo "JVM arguments : ${JAVA_OPT}"
echo "${appName} starting..."
# 检查进程PID
sleep 3
pid=`ps -ef|grep $appStarter|grep -v grep|awk '{print $2}' `
if [ -z "${pid}" ]; then
    echo "${appName} start failed!"
else
    echo "${appName} started. pid: ${pid}"
fi