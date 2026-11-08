---
name: fastadmin
description: "用于 FastAdmin/ThinkPHP 后台开发与排错，处理 CRUD、数据库字段与模型关联、菜单权限，以及既有 PHP、RequireJS、视图和插件代码修改。任务需要这些框架约定时使用。"
license: MIT
---

# FastAdmin 开发

在当前项目已有的 FastAdmin/ThinkPHP 结构中完成开发和修复。默认使用简体中文说明结果，代码、命令、路径和错误信息保留原文。

## 定位项目与工具

- 项目根目录应包含 `think`、`application/`、`addons/`、`public/`。框架路径相对于该根目录；本技能的参考文件相对于本技能目录。
- 使用 Codex 当前可用的文件、搜索和终端工具。已有 `.codegraph/` 时遵循项目的 CodeGraph 规则，否则用 `rg` 定位相关代码。
- 执行命令时明确工作目录。先确认可用的 PHP；若 `php` 不在 PATH，可从项目的 `start-local.cmd` 或本机工具配置确认实际程序，使用当前 shell 的调用语法。
- CRUD 和菜单生成前读取相应命令的 `--help` 及 `application/admin/command/Crud.php`、`Menu.php`，以本项目支持的参数为准。

## 按任务读取参考

先用 [任务归属](references/01-ownership.md) 确定目标文件，再按需读取：

| 任务 | 参考 |
| --- | --- |
| 新表、字段、索引、状态值或关联关系 | [数据库设计](references/02-database-design.md) |
| 新增标准后台列表及增删改模块 | [原生 CRUD](references/03-native-crud.md) |
| 页面、表单、列表组件和后台 JS 联动 | [前端约定](references/04-native-frontend.md) |
| 修改已有 PHP、JS、视图或插件源文件 | [已有代码修改](references/05-existing-source-change.md) |

## 开发约定

- 新功能默认使用 `application/admin/`、`public/assets/js/backend/` 和 `application/admin/lang/`。修改已有功能时沿用原文件归属；用户明确指定的路径和插件方案优先于默认约定。
- 先设计数据库字段，再生成 CRUD。当前命令的 `--table`、`--relation` 使用**不带配置前缀**的表名，SQL 中的真实表名使用数据库配置中的前缀。
- 列表需要关联名称、标题或昵称时，在生成前明确关联表、主表外键、关联主键和显示字段，按项目支持情况使用 `--relation` 系列参数。
- 树形父级字段默认保留 `pid`。`--controller` 处理控制器层级，不用于代替表单组件或树形逻辑改造。
- 菜单使用最终控制器 URL：通过 `--menu=1` 或 `php think menu --controller=<url>` 生成，并复核按钮权限节点。
- 生成器可能覆盖代码或改变权限数据；先检查目标文件和节点。`--force`、`--delete`、重装数据库不属于普通开发的默认动作。
- 本地数据库检查可使用仓库内 `mysql-dev-db` 技能及其脚本；若不可用，使用已有 MySQL 工具完成必要检查，不依赖全局技能安装路径。

## 验证与交付

- 核对控制器、模型、验证器、视图、后台 JS、语言包、字段名和菜单路径的一致性。
- 对修改运行相关 PHP 语法检查和已有测试；新业务逻辑补最小有效检查。页面变更后刷新并检查脚本错误、列表或表单，以及相应权限。
- 简要说明目标、关键改动、实际执行的生成或迁移命令、验证结果与未验证项。普通修复无需输出完整 CRUD 规划表。
