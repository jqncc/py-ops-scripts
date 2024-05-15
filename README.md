日常使用脚本整理.

## python脚本说明

1. deploy.py 项目发布脚本. 在同目录deploy.ini中配置好项目属性, 示例: deploy.py my-app
2. deployFabic.py 使用fabric远程执行tomcat项目发布
3. installAllInOn.py centos服务器java web环境一键设置和安装软件的脚本
4. installRsync.py rsync的安装脚本
5. splitExcel.py 拆分excel文件

## shell脚本说明(shell目录下)

1. execsql.sh mysql文件执行脚本. 示例: sh executesql.sh db sqlfile
2. java_start.sh java jar程序启动脚本
3. java_stop.sh java jar程序关闭脚本
4. java_run.sh java程序 启动/停止/重启 脚本
5. clear_tmp.sh 用于清理日志或临时文件
6. mysql_upgrade.sh mysql升级脚本
7. ssl_update.sh openssl升级脚本
8. ssh_update.sh openssh升级脚本
