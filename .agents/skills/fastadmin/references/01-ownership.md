# 任务归属判断

## 读取时机

按任务确认归属，再读取数据库、CRUD、前端或已有源文件规则。以下是本项目的默认组织约定；用户明确指定的路径、插件新增或实现方案优先。

## 判定优先级

1. 用户明确要求修改插件原控制器、原页面、原组件、原接口、原业务链路、原模型或其他插件源文件：判定为插件源文件修改。
2. 用户要求在某个已有控制器、模型、服务、验证器、JS、视图或组件中加方法或改逻辑：判定为已有源文件修改。
3. 用户要求新增控制器、页面、菜单、管理模块、统计页、批量操作页、独立功能、标准 CRUD：判定为原生新增。
4. 只是参考插件、复用插件业务概念、项目中存在插件、功能与插件业务相关，但没有明确修改插件原文件：仍判定为原生新增。

## 落点规则

- 原生新增：落到 FastAdmin 原生目录，如 `application/admin/controller`、`application/admin/model`、`application/admin/validate`、`application/admin/view`、`public/assets/js/backend`、`application/admin/lang`。
- 已有源文件修改：按当前文件所在目录、命名、调用链和风格修改。
- 插件源文件修改：修改 `addons/<plugin>` 下目标文件及必要调用方，沿用插件已有结构。

## 禁止项

- 未指定插件方案时，不把独立新功能放入 `addons/<plugin>`。
- 不因为业务相关或参考插件就把新增功能放入插件目录。
- 不把新增标准管理模块硬塞进已有控制器。
- 不在归属未判定前执行 CRUD、建表、改文件或生成菜单。

## 输出字段

实现前简要说明涉及的归属、目标目录、数据和菜单影响；复杂新增任务可使用这些字段：

- `ownership`: `native_new` / `existing_source_change` / `plugin_source_change`
- `reason`: 判定依据
- `backend_target`: 后端落点
- `frontend_target`: 前端落点
- `sql_target`: 表或字段落点
- `menu_target`: 菜单权限落点
