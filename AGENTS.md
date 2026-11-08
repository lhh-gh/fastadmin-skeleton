# AGENTS.md

本文件适用于本仓库。子目录存在 `AGENTS.md` 时，同时遵循对应范围的规则；用户明确指定的路径、实现方案和已有授权优先。默认使用简体中文沟通，代码、命令、配置键和错误信息保留原文。

## 项目与目录

后台项目是 FastAdmin 1.6.7，使用 ThinkPHP 5.0.29、PHP 7.4、Bootstrap 3、jQuery 和 RequireJS。PHP 代码保持 7.4 兼容，后台 JS 沿用现有 AMD 模块与组件。

`unibest/` 是独立的 uni-app 移动端项目，使用 Vue 3、TypeScript、Vite、UnoCSS 和 Wot UI，目标为 H5、微信小程序、Android 与 iOS。移动端遵循 [unibest/AGENTS.md](unibest/AGENTS.md)，本文件的 PHP、RequireJS 和 Grunt 约定适用于后台目录。

| 路径 | 用途 |
| --- | --- |
| `application/admin/` | 后台控制器、模型、验证器、视图、语言包和命令 |
| `application/common/` | 公共控制器、模型、业务库和行为 |
| `application/api/`、`application/index/` | API 与前台模块 |
| `public/assets/js/backend/` | 后台页面 JS |
| `public/assets/js/`、`public/assets/css/` | 公共脚本、RequireJS 入口和样式 |
| `addons/`、`extend/` | 插件与扩展 |
| `thinkphp/`、`vendor/` | 框架与依赖 |
| `runtime/`、`public/uploads/` | 运行文件与用户上传内容 |
| `tests/` | 独立的 PHP、Node.js 和 Python 检查 |
| `unibest/` | uni-app 移动端源码、配置与独立的 pnpm 依赖 |
| `.agents/skills/` | 当前仓库的 Codex 技能 |

## 技能入口

- FastAdmin 开发、CRUD、字段设计、关联模型、菜单权限或后台页面排错：读取 [.agents/skills/fastadmin/SKILL.md](.agents/skills/fastadmin/SKILL.md)，再按任务加载其中的参考文件。
- 本地 MySQL 配置、表结构、查询或已授权的 SQL 变更：读取 [.agents/skills/mysql-dev-db/SKILL.md](.agents/skills/mysql-dev-db/SKILL.md)，使用该技能配套脚本。
- `fastadmin-ai-skills/` 保存原始技能来源；整理后的 Codex 技能维护在 `.agents/skills/`。普通业务修改无需改动技能来源目录。

<!-- CODEGRAPH_START -->
## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source. If it's listed but deferred, load it by name via tool search.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` prints the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.
<!-- CODEGRAPH_END -->

没有 CodeGraph 索引时，用 `rg`、`rg --files` 定位相关代码；按任务读取调用方、模板、JS、语言包和字段定义。

## 本机运行与工具

运行步骤见 [LOCAL-DEPLOYMENT.md](LOCAL-DEPLOYMENT.md)，启动脚本为 [start-local.cmd](start-local.cmd)。先在 FlyEnv 启动 MySQL，再启动网站；检查 `127.0.0.1:8080` 已有监听时避免重复启动。

- 网站根目录：`public/`；首页：`http://127.0.0.1:8080/`。
- 当前后台入口：`http://127.0.0.1:8080/PtysLhIGwW.php`；入口以实际部署文件为准。
- 当前环境已安装，沿用 `.env` 和安装锁。重装、清空数据库、覆盖配置或移除安装锁需有针对该操作的明确授权。
- 本机终端为 PowerShell。以下是当前已确认的程序路径，换机器时重新定位；PHP 路径也可从启动脚本确认。

```powershell
$fastadminPhp = 'E:\FlyEnv-Data\app\php-7.4.33\php.exe'
$fastadminNode = 'D:\node\node.exe'
$fastadminPython = 'D:\python\python.exe'
```

后台命令从项目根目录执行，带引号的程序路径使用 PowerShell 调用运算符 `&`。MySQL CLI 从 `MYSQL_BIN` 或 PATH 查找，具体方式见数据库技能。

移动端命令从 `unibest/` 执行，使用项目声明的 pnpm 版本；启动与各平台构建见 [unibest/LOCAL-DEVELOPMENT.md](unibest/LOCAL-DEVELOPMENT.md)。H5 默认端口为 `9000`，H5、微信和 App 构建顺序执行，避免同时改写生成配置。

## 开发要点

- 新增后台功能默认使用原生 `application/admin/`、后台 JS 和语言包目录；修改已有功能沿用原文件归属。用户指定插件方案时按其要求实现。
- CRUD 或菜单生成前读取当前命令的 `--help`，检查目标文件和权限节点。`--table`、`--relation` 使用不带配置前缀的表名；SQL 使用带实际前缀的真实表名。
- 控制器、模型、验证器、视图、JS、语言包和菜单 URL 共同使用一致的字段与路径。生成器的 `--force`、`--delete` 会覆盖文件或删除节点，使用前核对影响和授权。
- 后台页面沿用 `Table.api`、`Form.api`、Selectpage、上传组件及已有鉴权方式。数据库字段与关联规则优先参考相近业务和本地技能。
- 普通模板文本保持 HTML 转义。内联 JavaScript 配置用 `json_encode($config, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT)` 输出，避免 JSON 被转义成 `&quot;`；可信的服务端生成菜单 HTML 才使用 `|raw`。
- 修改源 JS/CSS 后，按实际加载方式决定是否重建。`npm run build` 调用 Grunt，会复制依赖到 `public/assets/libs/` 并生成前后台 `.min.js`、`.min.css`；构建前按 `package-lock.json` 准备依赖，完成后检查产物。
- `.env`、数据库密码和安装记录中的凭据不得输出或提交。数据库检查先用技能脚本的脱敏 `config` 和 `ping` 确认目标库。
- 运行缓存按具体问题清理；保留 `runtime/local-install.txt`、`runtime/local-install-backup/` 和用户上传内容。

## 验证与交付

仅执行与本次改动相关的检查。使用上面的 PowerShell 程序变量：

| 改动范围 | 检查命令 |
| --- | --- |
| PHP 文件 | `& $fastadminPhp -l <文件路径>` |
| JS 文件语法 | `& $fastadminNode --check <文件路径>` |
| 模板转义、内联 JSON、菜单输出 | `& $fastadminPhp tests/template-output.php` |
| 附件与公共 formatter | `& $fastadminNode --test tests/attachment-formatters.test.js` |
| 仓库技能引用与 MySQL 配置脚本 | `& $fastadminPython -B tests/codex-skills.test.py` |
| CRUD 或菜单参数 | `& $fastadminPhp think crud --help`、`& $fastadminPhp think menu --help` |

页面变更后检查实际访问、浏览器脚本错误，以及相应列表、表单或菜单权限。测试通过只证明其覆盖的行为；说明关键修改、实际验证结果和未验证项。
