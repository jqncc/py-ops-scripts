#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import time
import sys
import shutil as sh
from fabric.api import *
import fabric.contrib.files as fabfiles

'''
使用fabric远程执行tomcat项目发布脚本
'''

# 备份目录
backupDir = "/proj/bak/"
# 项目根目录
projRootDir = "/proj/webapps/"
# 上传文件目录
jenkinsWorkDir = "/proj/work"
now = time.strftime("%Y%m%d%H%M%S", time.localtime())
jarpath = "/usr/jdk1.8/bin/jar"

# 要连接的远程主机信息
hosts = ['oper@10.18.3.94', 'devuser@10.18.3.175']
env.passwords = {'oper@10.18.3.94:22': '668899', 'devuser@10.18.3.175:22': '666888'}
projInfoDict = {
    'shop': {'dir': 'shop', 'hosts': [], 'tomcats': []}
}


def backup(proj):
    proj_dir = proj['dir']
    proj_full_path = projRootDir + proj_dir;
    if fabfiles.exists(proj_full_path):
        with cd(projRootDir):
            print("备份项目:" + proj_dir)
            bakname = "%s_%s.tar" % (proj_dir, now)  # 备份文件名=项目名+当前时间点
            bakpath = os.path.join(backupDir, proj_dir, bakname)
            run("tar -cf bakname proj_dir")
            print("备份完成，备份文件路径：" + bakpath)
    else:
        print("不存在项目：" + proj)  # 原项目不存在，可能是新发版


def publish(projwar, proj):
    '''
    发布项目
    :param projwar:
    :param proj:
    :return:
    '''
    os.chdir(jenkinsWorkDir)
    if os.access(projwar, os.F_OK):
        print("解压新项目包")
        # 使用jar -xf x.war 命令解压，该命令只能解压到当前目录，所以新建一个目录
        extract_dir = os.path(now, proj)
        os.chdir(extract_dir)
        extract_cmd = "%s -xf %s/%s.war" % (jarpath, jenkinsWorkDir, proj)
        os.system(extract_cmd)
        # 停止tomcat服务
        print(env.host_string)
        os.system("sudo systemctl stop tomcat")
        projpath = os.path.join(projRootDir, proj)
        # 删除原项目
        if os.path.exists(projpath):
            sh.rmtree(projpath)
        # 移动新项目
        sh.move(os.path.join(jenkinsWorkDir, extract_dir), projRootDir)
        os.system("sudo systemctl start tomcat")
        print("发布完成")
        os.chdir(jenkinsWorkDir)
        sh.rmtree(now)
    else:
        print("项目包不存在" + projwar)


@task
def deploy(proj_name, restart=False):
    if proj_name in projInfoDict:
        projInfo = projInfoDict[proj_name]
        env.hosts = projInfo['hosts']

        backup(proj)
        publish(projWarName, proj)
    else:
        print("项目%s 信息未找到" % proj_name)
        sys.exit(1)


if __name__ == "__main__":
    argvLen = len(sys.argv)
    if argvLen == 0:
        print("请输入要发布的项目名，可以多个")
    else:
        projWarName = sys.argv[1]
        if projWarName in projDict:
            proj = projDict[projWarName]
            backup(proj)
            publish(projWarName, proj)
        else:
            print("项目%s不存在" % projWarName)
