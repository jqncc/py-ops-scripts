#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys,stat,shutil

pass_file = "/etc/rsync.pass"
rsync_config_file = "/etc/rsyncd.conf"
rc_local_file = "/etc/rc.local"

def installServer():
    """
    安装配置目标服务(即文件同步到的机器)
    开放端口(默认873),配置rsync,配置密码,加入开机启动
    """
    print("开放端口873")
    os.system("firewall-cmd --zone=internal --add-port=873/tcp --permanent")
    os.system("firewall-cmd --reload")
    print("安装rsync")
    if os.access("/usr/bin/rsync",os.F_OK):
        print("已存在rsync")
    else:
        os.system("yum install rsync")
    config_text = "\nlog file =/var/log/rsyncd.log\n" \
                  "pid file =/var/run/rsyncd.pid\n" \
                  "lock file =/var/run/rsync.lock\n" \
                  "ignore errors\n" \
                  "uid=root\n" \
                  "gid=root\n" \
                  "read only=no\n" \
                  "list=no\n" \
                  "timeout=600\n" \
                  "[自定义名称]\n" \
                  "path=/同步目标文件夹路径\n"
    print("写入配置文件/etc/rsyncd.conf")
    with open(rsync_config_file, "a") as file:
        file.write(config_text)
    print("写入密码文件/etc/rsync.pass")
    with open(pass_file, "w+") as passfile:
        passfile.write("user:passwd")
    os.chmod(pass_file,stat.S_IRWXU)
    run_daemon_cmd = "rsync --daemon --config=/etc/rsyncd.conf"
    print("加入开机启动")
    with open(rc_local_file, "a") as rcfile:
        rcfile.write(run_daemon_cmd)
    print("安装成功,后台模式运行")
    os.system(run_daemon_cmd)
    return


def installClient():
    print("安装rsync client")
    os.system("yum install rsync")
    print("写入密码文件/etc/rsync.pass")
    with open(pass_file, "w+") as passfile:
        passfile.write("passwd")
    os.system("rsync --daemon")
    print("安装sersync")
    sersync_path="/usr/local/sersync"
    shutil.copytree("sersync",sersync_path)
    os.chmod(sersync_path+"/sersync2",stat.S_IEXEC)
    print("安装完成")
    print("加入开机启动")
    run_daemon_cmd=sersync_path+"/sersync2 -r -d -o /usr/local/sersync/confxml.xml"
    with open(rc_local_file, "a") as rcfile:
        rcfile.write(run_daemon_cmd)
    print("开始运行")
    os.system(run_daemon_cmd)
    return


if __name__ == "__main__":
    if len(sys.argv) == 0:
        print("请输入参数 0= install server ,1=install client")
        sys.exit()
    else:
        if "0" in sys.argv:
            installServer()
        elif "1" in sys.argv:
            installClient()
        else:
            print("无效的参数")
