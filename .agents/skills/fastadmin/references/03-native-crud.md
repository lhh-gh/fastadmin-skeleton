# 原生 CRUD 生成和复核

## 读取时机

新增标准后台数据管理模块时读取。本规则只服务 FastAdmin 原生目录新增，不用于插件目录新增功能板块。

## 前置条件

- 已读取 `references/01-ownership.md`，且归属为原生新增。
- 涉及表结构时已读取 `references/02-database-design.md`，并完成字段设计。
- 当前工作目录是 FastAdmin 项目根，或已定位项目根。
- 已检查 `php think`、`application/admin/command/Crud.php`、`application/admin/command/Menu.php`。

## 适用和排除

- 适用：标准列表、添加、编辑、删除、批量更新、状态筛选、菜单权限、表结构驱动的后台管理模块。
- 排除：统计页、仪表盘、向导页、批处理页、纯接口、修改已有控制器、修改插件源文件。

## 命令构造顺序

1. 基础命令优先：`php think crud --table=<table>`。
2. 非必要不加 `--controller`；需要项目层级归属时才加。
3. 需要模型目录清晰时，同步加 `--model=<ModelPath>`。
4. 列表需要显示关联字段时，加 `--relation` 系列参数。
5. 富文本、忽略字段、排序字段、固定列等参数只在明确需要时加。
6. 菜单优先随 CRUD 用 `--menu=1`，或 CRUD 后单独执行 `php think menu --controller=<controller>`。

## 控制器层级

这些是项目约定，不是 FastAdmin 官方默认行为。执行前先对齐当前项目已有控制器、模型、视图和 JS 层级。

- 单功能表：默认不加 `--controller`。
- 两段表名：默认可不加 `--controller`，如 `product_category` 生成 `product/category`。
- 三段及以上表名：指定控制器，只拆第一段为模块目录，后续转大驼峰控制器名；如 `product_category_attr` 使用 `--controller=product/CategoryAttr --model=Product/CategoryAttr`。
- 大功能主表需要挂在模块父级下时，可指定 `--controller=product/Product --model=Product/Product`。
- `--controller` 只处理模块层级归属；禁止用于解决字段组件、`pid`、selectpage 或减少页面改造。

## 关联模型

触发条件：列表需要显示关联表名称、标题、昵称、编号等字段，而不是只显示外键 ID。

`belongsto` 命令模板：

```bash
php think crud --table=product \
  --relation=product_category \
  --relationmode=belongsto \
  --relationforeignkey=product_category_id \
  --relationprimarykey=id \
  --relationfields=name
```

这是 Bash 的续行语法。PowerShell、cmd 可使用同参数的单行命令；真实表前缀从数据库配置读取，不写入这两个生成器参数。

参数语义：

- `--relation`：不带数据库配置前缀的关联表名。
- `--relationmode=belongsto`：主表通过外键属于关联表。
- `--relationforeignkey`：主表外键字段；禁止误写成关联表主键，除非主表外键字段确实叫 `id`。
- `--relationprimarykey`：关联表主键字段，通常是 `id`。
- `--relationfields`：列表需要显示的关联表字段。

生成后复核：

- 模型有关联方法，如 `belongsTo(...)`。
- 控制器列表启用关联查询，如 `relationSearch = true`、`with([...])` 或项目等价写法。
- JS 列表存在关联字段列，如 `category.name`、`user.nickname`。
- 外键 ID 列按业务决定隐藏或保留。
- 关联字段搜索可用。

## 菜单生成

- `--menu=1` 使用 CRUD 解析后的最终控制器路径生成菜单。
- 未指定 `--controller` 时，菜单跟随表名默认层级。
- 指定 `--controller=product/CategoryAttr` 时，最终控制器 URL 通常为 `product/category_attr`，菜单节点也使用该 URL。
- 单独补菜单必须使用最终控制器 URL：`php think menu --controller=product/category_attr`。
- 多控制器菜单命令使用重复参数：`php think menu --controller=product/product --controller=product/category --controller=product/category_attr`。
- 执行前以当前项目 `Menu.php` 或 `php think menu --help` 确认是否支持重复 `--controller`。

## 特殊参数边界

- `--selectpagesuffix=pid` 只能作为树形父级下拉的可选优化，不是默认策略。
- 使用 `--selectpagesuffix=pid` 前检查是否覆盖默认 `_id`、`_ids` 识别。
- 使用 `--selectpagesuffix=pid` 后检查 `data-source` 是否正确。
- 即使 `pid` 生成下拉，也仍需树形列表、层级展示、父子限制和控制器逻辑。

## 生成后复核

- SQL：表结构、字段、索引、默认值、注释、幂等性。
- 控制器：路径、类名、权限方法、查询条件、关联查询、删除策略。
- 模型：表名、时间戳、软删除、关联方法、获取器、修改器。
- 验证器：必填、长度、唯一性、数值范围、枚举范围、场景。
- 视图：`index`、`add`、`edit` 字段、提交路径、组件类型。
- 后台 JS：`Table.api.init`、列定义、搜索字段、formatter、事件绑定。
- 语言包：字段 key、状态文本、错误提示。
- 菜单权限：父级菜单、控制器路径、按钮权限、图标、排序、`auth_rule`。
- 关联显示：`with` 查询、关联字段列、外键 ID 显示策略、关联字段搜索。

## 复杂场景触发后再展开

- 树形分类：保留 `pid`，补树结构、父子删除限制、层级展示、父级下拉、禁止选择自身或子级。
- 关联筛选：补关联查询、筛选字段、隐藏搜索列、模型关联。
- 弹窗详情：补按钮权限、弹窗写法、详情视图。
- 软删除：补 `deletetime`、唯一索引策略、回收站权限。
- 导入导出：补依赖、权限、字段映射、数据校验。
