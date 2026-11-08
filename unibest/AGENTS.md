# AGENTS.md

本文件适用于 `unibest/` 及其子目录，同时遵循父目录的 [AGENTS.md](../AGENTS.md)。默认使用简体中文沟通，用户明确要求优先。父目录的 PHP、RequireJS 和 Grunt 规则适用于 FastAdmin 后台；移动端使用本文件约定。

## 项目与目录

项目由官方 unibest 4.4.1 模板创建，使用 uni-app、Vue 3、TypeScript、Vite 5、UnoCSS、Wot UI、Pinia 和 z-paging。目标平台为移动 H5、微信小程序、Android 和 iOS。当前未启用登录拦截与国际化，也未接入 FastAdmin 业务 API。

| 路径 | 用途与修改入口 |
| --- | --- |
| `src/pages/`、`src/layouts/` | 页面与布局；页面配置写在 `definePage` 宏中 |
| `src/tabbar/config.ts` | 底部导航配置 |
| `src/api/`、`src/http/` | 接口定义、请求封装和拦截器 |
| `src/store/`、`src/hooks/` | Pinia 状态与组合式函数 |
| `src/static/`、`src/style/` | 静态资源与公共样式 |
| `pages.config.ts`、`manifest.config.ts` | 全局页面配置与应用清单源码 |
| `vite.config.ts`、`uno.config.ts` | 构建、自动导入和 UnoCSS 配置 |
| `env/` | 按运行模式加载的环境配置 |
| `patches/`、`pnpm-lock.yaml` | 依赖补丁与锁定版本 |

## 开发约定

- 沿用现有页面、请求层、状态管理和组件写法；UI 使用已安装的 Wot UI，列表沿用 z-paging，样式优先 UnoCSS。保留移动端安全区与可访问性。
- Vue 文件按 `<script setup lang="ts">`、`<template>`、`<style scoped>` 排列。页面内的 `definePage` 放在脚本最上方；类型导入使用 `import type`，不靠新增 `any` 消除类型错误。
- 新页面放在 `src/pages/模块名/页面名.vue`；修改导航时同时核对 `src/tabbar/config.ts`、页面路径与图标。分包规则见下方 SOP。
- 编译期可确定的平台差异使用 `#ifdef H5`、`#ifdef MP-WEIXIN`、`#ifdef APP-PLUS`。浏览器专用 API 限于 H5；跨端行为优先使用 uni-app API。
- 请求复用 `src/http/`，接口类型放在 `src/api/`。在 HTTP 响应、缓存、路由参数和第三方回调入口校验外部数据；接入 FastAdmin 时核对真实接口、响应格式与认证规则。
- **不手改生成文件**：`src/pages.json`、`src/manifest.json`、`src/types/*.d.ts` 和 `dist/`。修改对应配置、页面、组件或 hooks 后重新生成；OpenAPI 生成的 `src/service/` 通过生成流程更新。
- **不直接修改 `node_modules/`**。Wot UI 当前固定为 `1.14.0`，类型修复维护在 [patches/wot-design-uni@1.14.0.patch](./patches/wot-design-uni@1.14.0.patch)。升级时一起核对补丁、`package.json` 与 `pnpm-lock.yaml`。
- 本地环境覆盖写入已忽略的 `env/.env.local` 或对应模式的 `.local` 文件。`VITE_*` 会进入客户端产物，只放允许公开的配置；密码、私钥和签名材料不得写入、输出或提交到前端仓库。

## 运行与验证

所有命令从本目录执行，使用 [package.json](./package.json) 声明的 `pnpm@10.10.0`；Node.js 要求 `>=20`。本机 PowerShell 的程序路径和启动步骤见 [LOCAL-DEVELOPMENT.md](./LOCAL-DEVELOPMENT.md)。H5 默认端口为 `9000`，已有服务时先检查并复用。

| 用途 | 命令 | 产物或结果 |
| --- | --- | --- |
| 按锁文件安装 | `pnpm install --frozen-lockfile` | 自动应用依赖补丁 |
| H5 开发 | `pnpm dev:h5` | `http://127.0.0.1:9000/` |
| 微信开发 | `pnpm dev:mp-weixin` | `dist/dev/mp-weixin/` |
| App 开发资源 | `pnpm dev:app` | `dist/dev/app/` |
| H5 构建 | `pnpm build:h5` | `dist/build/h5/` |
| 微信构建 | `pnpm build:mp-weixin` | `dist/build/mp-weixin/` |
| App 资源构建 | `pnpm build:app` | `dist/build/app/` |
| 类型检查 | `pnpm type-check` | `vue-tsc --noEmit` |
| 代码规范 | `pnpm lint` | ESLint 检查 |
| 单次测试 | `pnpm test:run` | Vitest 测试 |

H5、微信和 App 构建顺序执行，共用的生成配置会随平台切换而改写。首次安装或新增页面、组件、hooks 后，先运行目标平台构建生成配置与类型，再执行类型检查；`type-check` 自身不负责生成文件。

代码交付前执行类型检查、lint 和相关测试，并构建受影响的平台。页面改动检查实际访问、导航、交互、手机布局和控制台错误。纯文档修改核对链接、路径与命令即可。交付说明实际完成的检查及未验证项。

## 平台与发布

- 微信开发产物用微信开发者工具导入。空微信 AppID 只用于游客预览；平台登录、上传和发布需要真实 AppID 与开发者权限。
- `pnpm build:app` 生成 App 资源。真机运行与原生安装包使用 HBuilderX，配置真实 DCloud AppID、包名及签名材料；iOS 本地模拟器需要 macOS/Xcode。
- 手机上的 `127.0.0.1` 指向手机自身，本机接口调试使用电脑局域网地址；微信正式版使用配置好的 HTTPS 服务域名。
- 资源构建通过不能代表微信真机、原生 App 或签名发布通过，交付时分别说明验证结果。

## 参考文档与技能

按任务查阅 [Hermes 规范](./hermes/README.md)，涉及行为时核对当前源码与配置。当前关闭的登录策略不得按模板文档自动启用。

| 场景 | 文档 |
| --- | --- |
| 生成物、目录分层与校验边界 | [hermes/architecture.md](./hermes/architecture.md) |
| Vue、TypeScript、样式与状态 | [hermes/conventions.md](./hermes/conventions.md) |
| 平台差异与条件编译 | [hermes/platforms.md](./hermes/platforms.md) |
| 请求层与认证方案参考 | [hermes/api.md](./hermes/api.md) |
| 新页面、组件、分包与导航 | [hermes/sop-new-page.md](./hermes/sop-new-page.md) |
| 包体积与性能 | [hermes/performance.md](./hermes/performance.md) |
| 上传、环境切换与版本管理 | [hermes/release.md](./hermes/release.md) |

相关任务先读取对应技能入口，再按需加载参考文件；仅调用当前会话实际提供的工具。

- uni-app 文档、生命周期与条件编译：[uni-app/SKILL.md](./.agents/skills/uni-app/SKILL.md)。
- 官方组件、API 与跨端兼容：[uniapp-project/SKILL.md](./.agents/skills/uniapp-project/SKILL.md)。
- 微信开发者工具操作：[wechatide-skill/SKILL.md](./.agents/skills/wechatide-skill/SKILL.md)。
