---
name: mysql-dev-db
description: "读取项目配置并连接本地开发 MySQL，检查表结构、执行查询或已授权的 SQL 变更；适用于 FastAdmin 的 .env 数据库配置与本地数据库排错。"
license: MIT
---

# 本地 MySQL 开发数据库

使用本技能自带的 [mysql_dev_db.py](scripts/mysql_dev_db.py) 检查本地开发库。连接优先使用 MySQL CLI；缺少 CLI 时，单条 SQL 可使用已安装的 PyMySQL。脚本需要 Python 3.10 或更新版本。

## 配置与边界

- 明确项目根目录和目标库。只处理已确认的本地开发环境；配置指向远程或生产环境时，停止此技能流程并按用户指定的环境方案处理。
- 同一配置项的优先级为 `.env.development`、`.env.local`、`.env`、`.ai/config.json` 的 `mysql_dev_db`、数据库专用环境变量。缺少项继续读取下一来源；显式空密码不继承其他来源的密码。无效 JSON 会报错，先修复配置再继续。
- 支持 `MYSQL_*`、`DB_*`、`DATABASE_URL`、ThinkPHP 的 `database.*` 和 `[DATABASE]` 段。格式见 [配置示例](references/env-examples.md)。
- 使用 `config` 查看脱敏摘要；不要打印或提交 `.env`、明文数据库密码。不要把密码放进命令行参数。
- 查询用真实表名，先检查项目配置的前缀；示例中的 `fa_user` 仅适用于配置前缀为 `fa_` 的项目。

## 在当前仓库执行

以下命令从 FastAdmin 项目根目录执行，适用于 PowerShell、cmd 和 Bash 的单行调用；`python` 应替换为当前可用的 Python 程序。

```text
python .agents/skills/mysql-dev-db/scripts/mysql_dev_db.py config
python .agents/skills/mysql-dev-db/scripts/mysql_dev_db.py ping
python .agents/skills/mysql-dev-db/scripts/mysql_dev_db.py tables
python .agents/skills/mysql-dev-db/scripts/mysql_dev_db.py describe fa_user
python .agents/skills/mysql-dev-db/scripts/mysql_dev_db.py query "SELECT COUNT(*) AS count FROM fa_user"
```

从其他目录使用技能实际路径调用脚本，并指定 `--project <项目根目录>`。

MySQL 客户端从 `MYSQL_BIN` 或 PATH 查找。若客户端在 FlyEnv 等工具目录中，先定位实际 `mysql.exe`，再在当前进程设置 `MYSQL_BIN`；路径有空格时按当前 shell 正确引用。PyMySQL 只是可选兜底，已有 MySQL CLI 时无需安装 Python 数据库依赖。

## 查询与变更

1. 执行 `config`、`ping`，核对脱敏配置与目标库；配置不全时明确缺少项，不猜数据库账号或库名。
2. 结构检查用 `tables`、`schema`、`describe`；数据检查使用满足任务的最小 `SELECT`、`SHOW`、`EXPLAIN`。
3. 写入或结构变更前说明目标库、SQL 文件和影响。用户已有的明确授权继续有效；检查技能不会自动授权删除、清空或重置数据库。
4. SQL 文件必须通过 MySQL CLI 执行，避免用字符串分割器解析存储过程、引号中的分号或注释。缺少 CLI 时先解决客户端路径，不将导入偷偷改成 PyMySQL 批量执行。
5. 变更后使用表结构检查或关键查询验证。SQL 文件内事务、DDL 与回滚能力以 MySQL 实际行为为准，不承诺失败后自动回滚。

已授权 SQL 文件的调用方式：

```text
python .agents/skills/mysql-dev-db/scripts/mysql_dev_db.py file database/change.sql
```

结果简要说明配置来源、连接方式、目标库、执行内容、验证结论及未完成项；不复述敏感数据。
