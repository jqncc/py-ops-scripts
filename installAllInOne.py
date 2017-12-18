#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# 服务器一键安装配置脚本,请使用root账号执行本脚本

import os,stat
import shutil
import tarfile
import xml.etree.ElementTree as ET

_baseDir = "/usr/local"
_jdkTarFile = "server-jre-8u111-linux-x64.tar.gz"  # jdk安装文件名
_jdkDir = _baseDir + "/jdk1.8"  # jdk安装路径
_tomcatFile = "tomcat-7"  # tomcat文件名


def firewall():
    """
    开启防火墙服务firewalld,开放内网8080, 8081, 8082,外网80, 443端口
    """
    print("------开启防火墙firewalld------")
    os.system("systemctl enable firewalld")
    os.system("systemctl start firewalld")
    print("指定eth0 zone=internal")
    os.system("firewall-cmd --permanent --zone=internal --change-interface=eth0")
    os.system("firewall-cmd --reload")
    print("开放外网端口80, 443, 8888")
    os.system("firewall-cmd --zone=public --add-port=80/tcp --permanent")
    os.system("firewall-cmd --zone=public --add-port=443/tcp --permanent")
    os.system("firewall-cmd --zone=public --add-port=8888/tcp --permanent")
    print("开放内网端口8080, 8081, 8082, 8888")
    os.system("firewall-cmd --zone=internal --add-port=8080/tcp --permanent")
    os.system("firewall-cmd --zone=internal --add-port=8081/tcp --permanent")
    os.system("firewall-cmd --zone=internal --add-port=8082/tcp --permanent")
    os.system("firewall-cmd --zone=internal --add-port=8888/tcp --permanent")
    os.system("firewall-cmd --reload")
    print("当前开放端口结果:")
    os.system("firewall-cmd --list -ports")
    os.system("firewall-cmd --list -ports --zone=internal")


def jdk():
    """
    安装JDK1.8设置环境变量
    """
    print("------安装JDK------")
    print("解压文件到" + _jdkDir)
    tar = tarfile.open(_jdkTarFile)  # 可使用os.system("tar -xvf " + _jdkTarFile),3.2版本shutil也可实现解压缩文件
    tar.extractall()
    shutil.move("jdk1.8.0_111", _jdkDir)  # 解压后的文件夹名为jdk1.8.0_111
    print("设置JDK环境变量")
    java_env = "\n\nJAVA_HOME=/usr/local/jdk1.8" \
               "\nPATH=$JAVA_HOME/bin:$PATH" \
               "\nCLASSPATH=.:$JAVA_HOME/lib/tools.jar:$JAVA_HOME/lib/dt.jar" \
               "\nexport JAVA_HOME" \
               "\nexport PATH" \
               "\nexport CLASSPATH\n"
    fileappend("/etc/profile", java_env)
    os.system("source /etc/profile")  # 更新环境变量
    print("JDK安装完成")
    os.system("java -version")


def tomcat(index, enable_redis_session=False):
    """安装tomcat,配置端口,安装为系统服务.

    :param index: tomcat索引,即第几个.如:index=1,则安装的目录为tomcat-7-1,服务名为tomcat1.
    :param enable_redis_session: 是否配置用redis存储tomcat session.默认不安装
    :return: 无
    """

    print("------安装tomcat " + index + "------")
    target = _baseDir + "/tomcat-7"
    if index > 0:
        target = target + "-" + index
    print("复制文件到" + target)
    shutil.copytree(_tomcatFile, target)
    bin_path = target + "/bin/"
    print("设置PID文件")
    pid_path_config = "CATALINA_PID=\"" + target + "/tomcat.pid\""
    fileappend(bin_path + "setenv.sh", pid_path_config)

    # 修改端口
    if index > 0:
        print("配置端口")
        server_file = target + "/conf/server.xml"
        server_xml = ET.parse(server_file)

        node_server = server_xml.getroot()
        old_port = node_server.attrib["port"]
        node_server.set("port", str(int(old_port) + index))

        node_connector = node_server.find("./Service/Connector")
        old_port = node_connector.attrib["port"]
        node_connector.set("port", str(int(old_port) + index))

        old_port = node_connector.attrib["redirectPort"]
        node_connector.set("redirectPort", str(int(old_port) + index))
        server_xml.write(server_file)

    '''
     集群环境,配置redssion存储tomcat session
     配置redis redisson.conf文件
     修改conf/context.xml,加内容<Manager className="org.redisson.tomcat.RedissonSessionManager" configPath="/etc/redisson.conf" />  
    '''
    if enable_redis_session:
        print("配置redis session")
        shutil.copy("redisson.conf", "/etc/redisson.conf")
        context_file = target + "/conf/context.xml"
        context_xml = ET.parse(context_file)
        ele = ET.Element("Manager")
        ele.attrib = {"className": "org.redisson.tomcat.RedissonSessionManager", "configPath": "/etc/redisson.conf"}
        root = context_xml.getroot()
        root.append(ele)
        context_xml.write(context_file)

    service_name = "tomcat" + index
    print("设置为系统服务" + service_name)
    service_config_text = "[Unit]" \
                          "\nDescription=" + service_name \
                          + "\nAfter=syslog.target network.target remote-fs.target nss-lookup.target" \
                            "\n[Service]" \
                            "\nType=forking" \
                            "\nPIDFile=" + pid_path_config \
                          + "\nExecStart=" + bin_path \
                          + "startup.sh" \
                            "\nExecReload=/bin/kill -s HUP $MAINPID" \
                            "\nExecStop=" + bin_path \
                          + "shutdown.sh\nPrivateTmp=true\n\n[Install]\nWantedBy=multi-user.target"
    with open("/usr/lib/systemd/system/" + service_name + ".service", "a") as service_file:
        service_file.write(service_config_text)
    os.system("systemctl enable " + service_name)
    os.system("chown -R tomcat:tomcat " + target)
    print(service_name + "安装完成")
    return


def adduser():
    print("------创建账号------")
    print("创建tomcat运行账号")
    tcat_exist = filesearch("/etc/passwd", "tomcat:")
    if tcat_exist:
        print("用户tomcat已存在")
    else:
        os.system("useradd -r tomcat")
    print("创建管理账号oper")
    oper_exist = filesearch("/etc/passwd", "oper:")
    if oper_exist:
        print("用户oper已存在")
    else:
        os.system("useradd -G tomcat oper")
        print("设置oper密码")
        os.system("echo 'Ghgcom*2017'|passwd --stdin oper")


def mkappdir():
    print("创建应用目录:/webserver/bin")
    if not os.path.exists("/webserver/bin/bak"):
        os.makedirs("/webserver/bin/bak")
    print("创建web应用目录:/webserver/webapps")
    if not os.path.exists("/webserver/webapps/bak"):
        os.makedirs("/webserver/webapps/bak")
    print("创建数据目录:/webserver/data")
    if not os.path.exists("/webserver/data"):
        os.makedirs("/webserver/data")
    print("创建日志目录:/webserver/logs")
    if not os.path.exists("/webserver/logs"):
        os.makedirs("/webserver/logs")
    print("创建发布包上传目录:/webserver/updatefile")
    if not os.path.exists("/webserver/updatefile"):
        os.makedirs("/webserver/updatefile")
    print("创建数据库备份目录:/webserver/dback")
    if not os.path.exists("/webserver/dback"):
        os.makedirs("/webserver/dback")
    print("分配目录权限给用户tomcat")
    os.system("chown -R tomcat:tomcat /webserver")
    print("分配目录权限给用户oper")

    os.chmod("/webserver",stat.S_IWGRP)
    os.system("chown -R oper:oper /webserver/updatefile")
    return


def fileappend(file_path, text):
    with open(file_path, "a") as file:
        file.write(text)
    return


def filesearch(file_path, search_text):
    is_exist = False
    with open(file_path) as file:
        for line in file.readlines():
            if line.find(search_text) >= 0:
                is_exist = True
                break
    return is_exist


firewall()
jdk()
mkappdir()
tomcat(0)
tomcat(1)
tomcat(2)
