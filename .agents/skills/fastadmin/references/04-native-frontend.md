# 原生前端与已有前端修改

## 读取时机

新增 FastAdmin 原生页面、修改原生后台 JS/视图、补表单组件、补列表列、补按钮交互时读取。

## 路径

- 视图：`application/admin/view`
- 后台 JS：`public/assets/js/backend`
- 语言包：`application/admin/lang`
- 路径始终按当前项目实际结构解析。

## 新增原生页面

- 新增独立页面、统计页、批处理页、配置页、非 CRUD 页面，默认放原生目录。
- 默认使用项目已有 Bootstrap、RequireJS、`define([...])`、`Table.api`、`Form.api`、上传组件、选择器、弹窗和表单提交方式。
- 同步检查控制器方法、视图路径、JS 路径、语言包 key、菜单权限。
- 参考插件页面但新增独立页面时，仍按原生前端规则实现。

## 修改已有前端

- 先读取当前 JS/视图和相邻同类文件。
- 沿用当前文件的模块定义、事件绑定、formatter、searchList、operate、表单校验、提交方式。
- 不替换技术栈，不重写无关页面，不为了统一风格重排大段代码。
- 如果当前文件属于插件源文件且用户明确要求修改插件，转入 `references/05-existing-source-change.md`。

## 字段联动

- 列表字段、搜索字段、隐藏字段、表单字段、语言包 key 必须一致。
- 外键字段使用 selectpage 时，检查 `data-source`、`data-field`、多选配置和默认值。
- 列表显示关联字段时，优先显示关联列，如 `category.name`；外键 ID 列按业务隐藏或保留。
- 图片、文件、时间、状态、开关、富文本字段使用项目已有组件写法。

## 复核

- 模板中的普通文本保持 HTML 转义；仅已确认由服务端生成的可信菜单等 HTML 使用 `|raw`。
- 内联 JavaScript 配置使用 JSON 输出，例如 `{:json_encode($config, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT)}`。不要让默认 HTML 过滤器把 JSON 引号变为 `&quot;`，也不要全局关闭 HTML 转义。
- RequireJS 报配置或 `version` 未定义时，先检查实际渲染的 `var require` 与配置 JSON，再检查资源请求和模块加载。

- JS 路径、控制器 URL、视图目录、菜单节点一致。
- 按钮、弹窗、导出、批量操作有后端方法和权限节点。
- 表单提交、文件上传、选择器、开关、时间字段可用。
- 页面没有引用不存在的语言包 key、控制器路径或字段名。
