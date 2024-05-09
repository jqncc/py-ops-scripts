#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import collections
import shutil as sh
import os
import uuid
import sys

'''
项目发布脚本(适用本机,非远程),脚本将打包备份原项目,发布新项目后自动重启
须预先在脚本中配置好项目属性,执行命令: deploy.py 项目名. 
'''

# 备份目录
backupDir = "/proj/bak/"
# 项目部署根目录
projRootDir = "/proj/bin/"
# 软件包存放目录
packageDir = "/proj/package"
# 解压java的war包命令,不是war包可忽略设置
jarpath = "/usr/jdk1.8/bin/jar"

# 定义一个命名元组,设置项目属性:软件包名(package)、发布目录(target,非/开头则默认是相对于部署根目录)、启动命令(boot)，停止命令(stop)
Project = collections.namedtuple('Project', 'package target boot stop')

cms = Project(target='cms', package='cms.war', boot='sh /tomcat/startup.sh', stop='sh /tomcat/shutdown.sh')
shop = Project(target='shop', package='shop.tar', boot='sh shop.sh start', stop='sh shop.sh stop')

# 定义项目名与项目属性关联
projDict = {"cms_v1": cms, "wxshop": shop}


def backup(proj):
    """
    备份原项目
    :param proj:
    :return:
    """
    if not os.path.isabs(proj.target):
        projFullPath = projRootDir + proj.target
    else:
        projFullPath = proj.target
    pname = os.path.basename(projFullPath)
    if os.path.exists(projFullPath):
        print("备份项目:" + pname)
        now = time.strftime("%Y%m%d%H%M", time.localtime())
        # 生成唯一备份文件名,避免覆盖之前备份.文件名=项目名+当前时间点+UUID
        bakname = "%s_%s_%s.tgz" % (pname, now, uuid.uuid1())
        bakpath = os.path.join(backupDir, pname, bakname)
        os.chdir(projRootDir)
        os.system("tar -czf %s %s" % (bakname, bakpath))
        print("备份完成，备份文件路径：" + bakpath)
    else:
        print("原项目[%s]不存在：" % proj)  # 原项目不存在，可能是新发版


def publish(proj):
    """
    发布新项目
    :param proj:
    :return:
    """
    packageFullPath = os.path.join(packageDir, proj.package)
    if os.access(packageFullPath, os.F_OK):
        tmpDir = os.path.join(packageDir, str(uuid.uuid1()))
        ext = os.path.splitext(packageFullPath)[-1]  # 取扩展名
        extract_cmd = None
        # 如果是压缩包解压
        if '.war' == ext:
            print("[%s]解压中..." % proj.package)
            extract_cmd = "%s -xf %s" % (jarpath, packageFullPath)
        elif ext in ['.tar', '.tgz']:
            extract_cmd = "tar -xf %s" % packageFullPath
        elif ext == '.gz':
            if proj.package.endswith('.tar.gz'):
                extract_cmd = "tar -zxf %s" % packageFullPath
            else:
                extract_cmd = "gzip -d %s" % packageFullPath
        elif ext == '.zip':
            extract_cmd = "unzip %s" % packageFullPath

        pname = os.path.basename(proj.target)
        os.chdir(tmpDir)
        if extract_cmd is not None:
            os.mkdir(pname)
            os.chdir(pname)
            os.system(extract_cmd)
        else:
            # 不需要解压的直接copy文件
            if os.path.isdir(packageFullPath):
                sh.copyfile(packageFullPath, tmpDir)
                if proj.package != pname:
                    os.rename(proj.package, pname)
            else:
                sh.copy(packageFullPath, pname)
        # 停止
        os.system(proj.stop)
        if not os.path.isabs(proj.target):
            projpath = os.path.join(projRootDir, proj.target)
        else:
            projpath = proj.target
        # 删除原项目
        if os.path.exists(projpath):
            sh.rmtree(projpath)
        # 移动新项目
        sh.move(os.path.join(tmpDir, pname), projRootDir)
        print("启动中...")
        os.system(proj.boot)
        print("发布完成")
        sh.rmtree(tmpDir, True)
    else:
        print("发布失败!项目包[%s]不存在" % proj.package)


def executeSql(db_host, db_user, db_passwd, db_name, sql_file):
    """
    执行sql脚本文件,执行日志写入sql_file.log文件
    :param db_host: 数据库地址
    :param db_user: 数据库用户名
    :param db_passwd: 数据库密码
    :param db_name: 数据库名
    :param sql_file: 要执行的sql文件绝对路径
    :return:
    """
    logFile = sql_file + ".log"
    dbinfo = {"host": db_host, "user": db_user, "pwd": db_passwd, "db": db_name, "sqlFile": sql_file, "log": logFile}
    runSqlCmd = 'mysql -h {host} -u{user} -p{pwd} {db} < {sqlFile} > {log}'
    os.system(runSqlCmd.format(**dbinfo))


if __name__ == "__main__":
    argvLen = len(sys.argv)
    if argvLen == 0:
        print("请输入要发布的项目名")
    else:

        projName = sys.argv[1]
        curProj = projDict.get(projName.strip())
        if curProj is not None:
            backup(curProj)
            publish(curProj)
        else:
            print("项目%s未配置" % projName)
