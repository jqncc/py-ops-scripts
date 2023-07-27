#!/bin/sh
webapp=/webserver/webapps
appdir=/webserver/webapps/$1
backupdir=/webserver/static_bak
jardir=/webserver/lastpackages

JAR_NAME=$1\.jar

P_ID=`ps -ef | grep $JAR_NAME | grep -v "grep" | awk '{print $2}'`

if [ ! -e ${appdir} ];then
    mkdir ${appdir}
fi

function backup(){
    echo "开始备份目录: ${appdir}-------"
    cd ${appdir}
    if [ -e $JAR_NAME ];then
        bakname=${JAR_NAME}_`date +%Y%m%d%S`
    	mv ${JAR_NAME} ${backupdir}/$bakname
        #mv *  ${backupdir}
        sleep 3
	if [ $? -eq 0 ];then
        	echo "---------备份完成"
    	fi
    else
	echo "原文件不存在忽略备份"
    fi
}


backup

if [ "$P_ID" == "" ]; then
        cd ${jardir}       
        mv $JAR_NAME ${appdir}
        cd ${appdir}
        echo "Service is starting........"
        nohup /usr/local/jdk1.8/bin/java -Xms256m -Xmx512m -jar $JAR_NAME >$appdir/$1.out 2>&1 &
        sleep 5
else
        kill -9 "$P_ID"

        cd ${jardir}
        mv $JAR_NAME ${appdir}
        cd ${appdir}

        sleep 5
        echo "Service is starting........"
        nohup /usr/local/jdk1.8/bin/java -Xms256m -Xmx512m -jar $JAR_NAME >$appdir/$1.out 2>&1 &
        sleep 5
        echo "Service is runing........"
fi

