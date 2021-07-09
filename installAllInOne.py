#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os, stat
import shutil
import tarfile
import xml.etree.ElementTree as ET

_baseDir = "/usr/local"
_jdkTarFile = "jdk-8u151-linux-x64.tar.gz"  # jdk安装文件名
_jdkDir = _baseDir + "/jdk1.8"  # jdk安装路径
_tomcatFile = "tomcat-7"  # tomcat包文件名

'''
centos服务器java web 环境一键安装配置脚本.
开启防火墙,开放指定端口,新增用户,安装JDK配置JAVA环境变量,安装并配置TOMCAT.
请使用root账号执行本脚本
'''

def firewall():
    """
    开启防火墙服务firewalld
    """
    print("------开启防火墙firewalld------")
    r = os.system("systemctl enable firewalld")
    if r != 0:
        raise RuntimeError('开启firewalld服务失败')
    os.system("systemctl start firewalld")
    print("指定eth0 zone=internal")
    os.system("firewall-cmd --permanent --zone=internal --change-interface=eth0")
    os.system("firewall-cmd --reload")


def openport(port, protocol='tcp', zone='public', isreload=True):
    """
    开启端口
    :param port: 开启的端口
    :param protocol: 协议,默认tcp
    :param zone: 作用域,默认public
    :param isreload: 是否重载防火墙配置
    :return:
    """
    cmd = "firewall-cmd --zone={0} --add-port={1}/{2} --permanent".format(zone, port, protocol)
    r = os.system(cmd)
    if r != 0:
        print("端口%s开启失败" % port)
    if isreload:
        os.system("firewall-cmd --reload")


def openports(protocol='tcp', zone='public', *ports):
    """
    一次开启多个端口号
    :param protocol: 协议,默认tcp
    :param zone: 作用域,默认public
    :param ports: 端口号
    :return:
    """
    for p in ports:
        openport(p, protocol, zone, False)
    os.system("firewall-cmd --reload")


def install_jdk():
    """
    安装JDK1.8设置环境变量
    """
    print("------安装JDK------")
    print("解压文件到" + _jdkDir)
    tar = tarfile.open(_jdkTarFile)  # 可使用os.system("tar -xvf " + _jdkTarFile),3.2版本shutil也可实现解压缩文件
    tar.extractall()
    shutil.move("jdk1.8.0_151", _jdkDir)  # 解压后的文件夹名为jdk1.8.0_151
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


def install_tomcat(alias, incr_port=0, install_service=False):
    """ 安装tomcat,配置端口,安装为系统服务.

    :param alias: tomcat别名,如:alias=app,则安装的目录为tomcat-app,服务名为tomcat-app.
    :param incr_port: 端口修改值,即各端口在原基础上增加的值
    :param install_service: 是否安装为系统服务centos 7
    :return: 无
    """

    print "------ 安装tomcat 别名:%s ------" % alias
    tomcat_base = _baseDir + "/tomcat-" + alias
    print("复制文件到" + tomcat_base)
    shutil.copytree(_tomcatFile, tomcat_base)
    tomcat_bin = tomcat_base + "/bin/"
    tomcat_pid = tomcat_base + "/tomcat.pid"
    print("设置JAVA_OPTS")
    env_config = "CATALINA_PID=" + tomcat_pid + \
                 "\nJAVA_OPTS = \"-server -Djava.security.egd=file:/dev/./urandom -Djava.awt.headless=true " \
                 "-XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=256m -Xms512M -Xmx768M -Xss256k\""
    filewrite(tomcat_bin + "setenv.sh", env_config)

    # incr_port>0修改端口，在默认端口上加incr_port

    if incr_port > 0:
        port_conn = 8080 + incr_port
        port_server = 8005 + incr_port
        port_redirect = 8443 + incr_port
        port_ajp = 8009 + incr_port

        print("配置端口")
        server_file = tomcat_base + "/conf/server.xml"
        server_xml = ET.parse(server_file)
        # 修改端口<Server port="8005"
        node_server = server_xml.getroot()
        node_server.set("port", str(port_server))

        # 修改端口<Connector port="8080" redirectPort="8443"
        node_connectors = node_server.findall("./Service/Connector")
        for node_conn in node_connectors:
            if node_conn.get('protocol').startswith('AJP'):
                node_conn.set("port", port_ajp)
                node_conn.set("redirectPort", port_redirect)
            elif node_conn.get('protocol').startswith('HTTP'):
                node_conn.set("port", port_ajp)
                node_conn.set("redirectPort", port_conn)

        server_xml.write(server_file)

        print("开放内网端口" + port_conn)
        openport(port_conn, isreload=True)
        os.system("firewall-cmd --zone=internal --add-port=" + port_conn + "/tcp --permanent")
        os.system("firewall-cmd --reload")

    tcat_exist = filesearch("/etc/passwd", "tomcat:")
    if tcat_exist:
        print("用户tomcat已存在")
    else:
        print("创建tomcat运行账号")
        os.system("useradd -r tomcat")  # -r建系统账号
    os.system("chown -R tomcat:tomcat " + tomcat_base)
    print("tomcat %s 安装完成" % alias)

    if install_service:
        service_name = "tomcat-" + alias
        print("设置为系统服务" + service_name)
        service_config_text = "[Unit]" \
                              "\nDescription=" + service_name \
                              + "\nAfter=syslog.target network.target remote-fs.target nss-lookup.target" \
                                "\n[Service]" \
                                "\nType=forking" \
                                "\nPIDFile=" + tomcat_pid \
                              + "\nExecStart=" + tomcat_bin \
                              + "startup.sh" \
                                "\nExecReload=/bin/kill -s HUP $MAINPID" \
                                "\nExecStop=" + tomcat_bin \
                              + "shutdown.sh\nPrivateTmp=true\n\n[Install]\nWantedBy=multi-user.target"
        with open("/usr/lib/systemd/system/" + service_name + ".service", "w") as service_file:
            service_file.write(service_config_text)
        os.system("systemctl enable " + service_name)
        print(service_name + "服务安装完成")
    return


def adduser(newuser, passwd=None):
    print("创建用户" + newuser)
    projuser_exist = filesearch("/etc/passwd", newuser + ":")
    if projuser_exist:
        print("用户已存在")
    else:
        os.system("useradd -G tomcat " + newuser)
        if (passwd is not None) and len(passwd) > 1:
            os.system("echo '" + newuser + "'|passwd --stdin projuser")


def mkappdir():
    """
    所有发布的项目和相关文件放在/project下，只分配projuser ,tomcat 两个用户权限
    :return: 
    """
    base_dir = "/project"
    bin_dir = base_dir + "/bin"
    webapp_dir = base_dir + "/webapps"
    bak_dir = base_dir + "bak"
    data_dir = base_dir + "data"
    log_dir = base_dir + "logs"
    if not os.path.exists(bin_dir):
        print("创建应用目录:" + bin_dir)
        os.makedirs(bin_dir)
    if not os.path.exists(webapp_dir):
        print("创建web应用目录:" + webapp_dir)
        os.makedirs(webapp_dir)
    if not os.path.exists(data_dir):
        print("创建数据目录:" + data_dir)
        os.makedirs(data_dir)
    if not os.path.exists(log_dir):
        print("创建日志目录:" + log_dir)
        os.makedirs(log_dir)
    print("分配目录权限给用户tomcat")
    os.system("chown -R tomcat:tomcat " + base_dir)
    return


def fileappend(file_path, text):
    with open(file_path, "a") as file:
        file.write(text)
    return


def filewrite(file_path, text):
    with open(file_path, "w") as file:
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


# 开启firewalld服务,开放端口
firewall()
print("开放外网端口80, 443")
# openport(80, isreload=False)
# openport(443, isreload=True)
openports(80, 443)
print("结果:")
os.system("firewall-cmd --list-ports --zone=public")
print("开放内网端口2181,8080,8888")
openports('tcp', 'internal', 2181, 8080, 8888)
print("结果:")
os.system("firewall-cmd --list-ports --zone=internal")
# 安装jdk
install_jdk()
# 增加用户
adduser()
# 创建工程目录
mkappdir()
# 安装tomcat
install_tomcat()
