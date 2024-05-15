#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
import subprocess
import time
import collections
import os
import sys
import psutil

'''
项目发布脚本(适用本机,非远程),脚本将打包备份原项目,发布新项目后自动重启
须预先在脚本中配置好项目属性,执行命令: deploy.py 项目名. 
'''

# 定义一个命名元组,设置环境属性
Env = collections.namedtuple('Env', 'jarPath backupDir projBaseDir updateTempDir')

remove_old_files = False


class ProjCfg:

    def __init__(self, name, proj_file="", proj_dir="", start_exec="", stop_exec=""):
        self.name = name
        self.projFile = proj_file

        self.startExec = start_exec
        self.stopExec = stop_exec
        self.projDir = proj_dir
        # self.user = _user
        # self.group = _group

    def check(self):
        if not os.path.exists(self.projFile):
            raise Exception("项目文件不存在:" + self.projFile)
        if not os.path.exists(self.projDir):
            os.makedirs(self.projDir)


def backup(proj):
    """
    备份原项目
    :param proj:
    :return:
    """
    if os.path.exists(proj.projDir) and len(os.listdir(proj.projDir)) > 0:
        print("备份项目:" + proj.projDir)
        now = time.strftime("%Y%m%d%H%M", time.localtime())
        # 生成唯一备份文件名,避免覆盖之前备份.文件名=项目名+当前时间点
        bakname = "%s_%s.tgz" % (os.path.basename(proj.projFile), now)
        os.chdir(DeployEnv.backupDir)
        os.system("tar -czf %s %s" % (bakname, proj.projDir))
        print("备份完成，备份文件路径：", DeployEnv.backupDir, bakname)
    else:
        print("原项目[%s]不存在：" % proj)  # 原项目不存在，可能是新发版


def publish(proj):
    """
    发布新项目
    :param proj:
    :return:
    """
    print("开始发布新项目")
    ext = os.path.splitext(proj.projFile)[-1]  # 取扩展名
    if pCfg.stopExec != "":
        print("关闭原进程")
        ret = subprocess.call(pCfg.stopExec, shell=True)
        print(ret)
        time.sleep(2)
    else:
        if ".jar"==ext:
            stopJavaProcessByJarname(os.path.basename(proj.projFile))
            time.sleep(2)

    extract_cmd = None
    if '.war' == ext:
        extract_cmd = "%s -xf %s" % (DeployEnv.jarPath, proj.projFile)
    elif ext in ['.tar', '.tgz']:
        extract_cmd = "tar -xf %s" % proj.projFile
    elif ext == '.gz':
        if proj.projFile.endswith('.tar.gz'):
            extract_cmd = "tar -zxf %s" % proj.projFile
        else:
            extract_cmd = "gzip -d %s" % proj.projFile
    elif ext == '.zip':
        extract_cmd = "unzip -o %s" % (proj.projFile)

    if remove_old_files:
        print("删除原项目文件")
        os.system("rm -rf {}/*".format(proj.projDir))
    if extract_cmd is not None:
        os.chdir(proj.projDir)
        print("解压新项目文件")
        os.system(extract_cmd)
    else:
        print("移动新文件")
        if os.path.isdir(proj.projFile):
            os.system("mv -f {}/* {}".format(proj.projFile, proj.projDir))
        else:
            os.system("mv -f {} {}".format(proj.projFile, proj.projDir))
    if proj.startExec is not None:
        print("开始启动: " + proj.startExec)
        os.system(proj.startExec)
    print("发布完成")


def readCfg(cfgfile, proj):
    """
    读取配置文件
    """
    iniCfg = ConfigParser.ConfigParser()
    iniCfg.read(cfgfile)

    jdkpath = iniCfg.get("env", "jdk")
    if jdkpath == "" or not os.path.exists(jdkpath):
        jdkpath = os.getenv("JAVA_HOME")
    if jdkpath is not None:
        jdkpath = os.path.join(jdkpath, "bin/jar")

    updateTempDir = iniCfg.get("env", "updateTempDir")
    if updateTempDir is None or updateTempDir == "":
        updateTempDir = os.getcwd()

    projBaseDir = iniCfg.get("env", "projBaseDir")
    if projBaseDir == "" or projBaseDir is None:
        raise Exception("请配置项目部署的基目录:projBaseDir")

    backupDir = iniCfg.get("env", "backupDir")

    global DeployEnv
    DeployEnv = Env(jarPath=jdkpath, backupDir=backupDir, projBaseDir=projBaseDir, updateTempDir=updateTempDir)
    # 读取要发布的项目配置
    if iniCfg.has_section(proj):
        cfg = ProjCfg(proj)

        cfg.projFile = iniCfg.get(proj, "projFile")
        if cfg.projFile[0] != '/':
            cfg.projFile = os.path.join(DeployEnv.updateTempDir, cfg.projFile)
        cfg.projDir = iniCfg.get(proj, "projDir")
        if cfg.projDir[0] != '/':
            cfg.projDir = os.path.join(DeployEnv.projBaseDir, cfg.projDir)
        cfg.startExec = iniCfg.get(proj, "startExec")
        cfg.stopExec = iniCfg.get(proj, "stopExec")

        cfg.check()
        return cfg
    else:
        raise Exception("没有项目[" + proj + "]的配置")


def stopJavaProcessByJarname(processname):
    pl = psutil.pids()
    for pid in pl:
        proc = psutil.Process(pid)
        if proc.name() == "java" and processname in proc.cmdline():
            proc.kill()
            print("关闭进程,PID:%d, %s" % (pid, processname))


if __name__ == "__main__":
    argvLen = len(sys.argv)
    if argvLen == 0:
        print("请输入要发布的项目名")
    else:
        projName = sys.argv[1]
        for arg in sys.argv:
            if arg == "-r":
                remove_old_files = True
        pCfg = readCfg("deploy.ini", projName)

        if pCfg is not None:
            backup(pCfg)
            publish(pCfg)
        else:
            print("项目%s未配置" % projName)
