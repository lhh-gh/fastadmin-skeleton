# 数据库设计和字段命名

## 读取时机

涉及新表、新字段、新索引、新状态值、外键关系、字段注释、SQL 或 CRUD 生成前字段设计时读取。数据库设计完成后，才能决定是否使用 `php think crud`。

## 必查来源

- 当前项目数据库配置和表前缀。
- 当前项目已有相近业务表结构。
- 当前项目 `application/admin/command/Crud.php` 的字段识别规则。
- 当前项目已有控制器、模型、JS、视图对字段的使用方式。

SQL 和查询使用实际表名；本项目 CRUD 的 `--table`、`--relation` 参数不带配置前缀。例如实际表为 `fa_product`，生成参数为 `--table=product`。

## 设计顺序

1. 确认表前缀、业务表命名、主键字段。
2. 确认时间字段：`createtime`、`updatetime`、需要软删除时的 `deletetime`。
3. 确认状态字段：字段名、枚举值、默认值、是否用于列表筛选或状态切换。
4. 确认排序字段：优先检查项目使用 `weigh` 还是自定义排序字段。
5. 确认外键字段：通常使用 `xxx_id`；同时记录关联表、关联主键、列表显示字段。
6. 确认图片、文件、富文本、开关、城市、JSON、标签等组件字段是否符合 `Crud.php` 后缀识别。
7. 确认唯一索引、组合索引、普通索引、软删除下唯一性和旧数据兼容。

## 字段命名与默认页面组件映射

最终以当前项目 `application/admin/command/Crud.php` 为准。字段设计按下表降低生成后修补量。

| 字段或后缀 | 生成倾向 | 约束 |
| --- | --- | --- |
| `createtime`、`updatetime`、`deletetime` | 时间字段、时间格式化 | 用于模型时间戳和列表时间展示。 |
| `weigh` | 排序字段 | 适合权重排序。 |
| `status` | 状态格式化、顶部筛选、状态切换 | 适合 `normal`、`hidden` 等值。 |
| `image`、`images`、`avatar`、`avatars` | 图片上传和展示 | 复数字段通常表示多图。 |
| `file`、`files` | 文件上传 | 复数字段通常表示多文件。 |
| `content` | 富文本编辑器 | 适合详情正文。 |
| `switch` | 开关组件 | 需结合字段类型和默认值确认。 |
| `city` | 城市选择 | 适合地区字段。 |
| `range` | 时间区间 | 适合范围字符串。 |
| `json`、`array` | 键值/数组编辑 | 适合结构化配置。 |
| `tag`、`tags` | 标签输入或标签展示 | 适合标签字段。 |
| `_id` | Selectpage 单选 | 适合外键字段。 |
| `_ids` | Selectpage 多选 | 适合多关联 ID 字符串。 |
| enum + `status`、`state`、`data` | radio 或状态类组件 | 以当前 `Crud.php` 为准。 |
| set + `status`、`state`、`data` | checkbox 或多选组件 | 以当前 `Crud.php` 为准。 |

## 外键和关联显示

- 表单选择外键：字段用 `xxx_id`，CRUD 可自动生成 selectpage。
- 新 CRUD 列表显示关联字段：在生成阶段准备 `--relation` 参数。调整已有列表时修改现有模型关联和查询，不为了补关联重新覆盖生成文件。
- `belongsto` 中 `--relationforeignkey` 是主表外键字段，如 `product_category_id`；`--relationprimarykey` 是关联表主键，通常是 `id`。
- 设计 SQL 时记录：主表、关联表、主表外键、关联表主键、列表显示字段。

## 树形字段

- 树形父级字段默认使用 `pid`。
- 不为了触发 `_id` 组件把 `pid` 改成 `product_category_id`、`category_id` 或其他本表名外键。
- `pid` 表达本表内部父子关系；其他表引用该表时才使用 `xxx_id`。
- `pid` 的下拉、树形列表、禁止选择自身或子级属于 CRUD 后改造或可选命令优化，不属于字段改名理由。

## 输出字段

数据库设计完成后输出：

- 表名和表前缀处理方式
- 字段清单、类型、默认值、注释
- 索引和唯一性策略
- 状态值和时间字段策略
- 外键关系和需要显示的关联字段
- 是否适合 `php think crud`
