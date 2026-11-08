# 本机运行

首页：http://127.0.0.1:8080/

后台：http://127.0.0.1:8080/PtysLhIGwW.php

管理员账号是 `admin`，安装器生成的密码保存在 `runtime/local-install.txt`。

重启电脑后，先在 FlyEnv 启动 MySQL，再双击 `start-local.cmd`。运行窗口需要保持打开；关闭窗口会停止网站。已经启动时，无需重复运行。

本机使用 FlyEnv 的 PHP 7.4.33 和 MySQL 8.2.0，数据库为 `fastadmin`，网站目录为 `public`。PHP 路径固定在启动脚本中，移动或卸载 FlyEnv 后需要更新。

安装前的配置备份保存在 `runtime/local-install-backup`。安装器已生成安装锁、随机化后台入口并移除安装页面。

此启动方式仅供本机开发使用，监听 `127.0.0.1:8080`，不会自动随系统启动。公网部署需要独立配置 Web 服务和 HTTPS。
