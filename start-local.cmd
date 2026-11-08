@echo off
"E:\FlyEnv-Data\app\php-7.4.33\php.exe" -S 127.0.0.1:8080 -t "%~dp0public" "%~dp0public\router.php"
