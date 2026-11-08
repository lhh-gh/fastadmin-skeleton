# unibest 移动端开发

本项目由官方 `create-unibest@4.0.18` 创建，基于 unibest 4.4.1，使用 Vue 3、TypeScript、Vite 5、UnoCSS、Wot UI、Pinia 和 z-paging。目标为移动 H5、微信小程序、Android 与 iOS。

## 本机启动

所有移动端命令在 `E:\code\note\project\fastadmin\unibest` 中执行。项目使用 `pnpm@10.10.0`，本机已安装 Node.js 24.9.0。

```powershell
Set-Location 'E:\code\note\project\fastadmin\unibest'
& 'D:\node\node_cache\pnpm.cmd' install --frozen-lockfile
& 'D:\node\node_cache\pnpm.cmd' dev:h5
```

浏览器访问 [http://127.0.0.1:9000/](http://127.0.0.1:9000/)。同一局域网的手机可使用这台电脑的局域网 IP 加 `:9000` 访问。

在其他机器上安装 Node.js 和项目声明版本的 pnpm 后，可直接使用下表中的 `pnpm` 命令。端口已被占用时先检查已有服务；端口配置在 `env/.env` 的 `VITE_APP_PORT`。

## 平台命令与产物

| 平台 | 开发命令 | 构建命令 | 生产产物 |
| --- | --- | --- | --- |
| 移动 H5 | `pnpm dev:h5` | `pnpm build:h5` | `dist/build/h5/` |
| 微信小程序 | `pnpm dev:mp-weixin` | `pnpm build:mp-weixin` | `dist/build/mp-weixin/` |
| Android / iOS App | `pnpm dev:app` | `pnpm build:app` | `dist/build/app/` |

开发产物分别位于 `dist/dev/mp-weixin/` 和 `dist/dev/app/`。各平台构建顺序执行，共用的 `src/pages.json` 和 `src/manifest.json` 会随构建重新生成。

H5 发布时将 `dist/build/h5/` 的内容放到 Web 服务器。默认使用 hash 路由；部署到子路径时，在 `env/` 中设置 `VITE_APP_PUBLIC_BASE`，然后重新构建。

## AppID 与接口配置

环境文件位于 `env/`，本地配置可以写入已被 Git 忽略的 `env/.env.local`。按模式覆盖时使用 `.env.development.local` 或 `.env.production.local`。

- `VITE_UNI_APPID`：目前为本地编译占位符 `__UNI__0000000`。App 真机调试、云打包前，改为自己在 DCloud 注册的 AppID。
- `VITE_WX_APPID`：目前留空，生成游客预览配置。微信上传或需要登录等平台能力时，填写自己的微信小程序 AppID。
- `VITE_SERVER_BASEURL`：目前留空，基础页面不依赖后台。接入业务时填写完整接口地址，并对齐 `src/api/`、`src/http/` 中的接口路径、响应格式和认证方式。

FastAdmin 后台已有独立的本地部署；移动端还没有对接其登录或业务 API。手机上的 `127.0.0.1` 指向手机自身，本机 API 调试需使用电脑的局域网地址；微信正式版配置真实 HTTPS 服务域名。

## 微信小程序

运行 `pnpm dev:mp-weixin` 后，在微信开发者工具中导入 `dist/dev/mp-weixin/`。也可导入生产目录 `dist/build/mp-weixin/` 进行检查。

项目会尝试自动打开微信开发者工具。若安装位置不同，在 `env/.env.local` 配置 `WECHAT_DEVTOOLS_CLI_PATH`，并启用开发者工具的服务端口。仅编译、不打开工具时，在同一个 PowerShell 会话使用：

```powershell
$env:SKIP_OPEN_DEVTOOLS = 'true'
pnpm build:mp-weixin
Remove-Item Env:SKIP_OPEN_DEVTOOLS
```

游客模式用于基础预览；真机预览、登录、上传和发布需要自己的 AppID、开发者权限及对应平台配置。

## Android 与 iOS

`pnpm build:app` 编译的是 App 资源，后续通过 HBuilderX 生成原生安装包。

1. 在 `env/` 配置自己的 DCloud AppID，在 `manifest.config.ts` 设置应用标识、图标、原生模块和实际需要的权限。
2. 调试：运行 `pnpm dev:app`。iOS 可在 HBuilderX 导入 `dist/dev/app/`；Android 热更新按官方流程导入整个 `unibest/` 项目。
3. 打包：运行 `pnpm build:app`，在 HBuilderX 导入 `dist/build/app/`，选择“发行 → 原生 App 云打包”。
4. Android 配置自己的包名与签名证书；iOS 配置 Bundle ID、Apple 开发者证书和描述文件。iOS 本地模拟器需要 macOS/Xcode，Windows 可准备资源并使用符合条件的云打包流程。

## 检查与源码位置

先执行一次构建，生成路由、清单和类型声明，再运行：

```powershell
pnpm type-check
pnpm lint
pnpm test:run
```

页面在 `src/pages/`，导航在 `src/tabbar/config.ts`，状态在 `src/store/`，接口在 `src/api/`。修改 `pages.config.ts`、`manifest.config.ts` 和源文件，不手改生成的 JSON 或类型声明。

Wot UI 固定为 `1.14.0`。该版本的图片上传和 Picker 依赖类型存在两处上游错误，已通过 `patches/wot-design-uni@1.14.0.patch` 修复类型，运行逻辑不变。安装时 pnpm 自动应用补丁；版本升级时一并检查补丁和上述门禁，保留 `package.json`、补丁文件及 `pnpm-lock.yaml`。

2026-11-08 本机初始化验证：类型检查、ESLint、6 组共 51 项测试通过；H5、微信小程序、App 资源构建通过，App 清单包含 Android、iPhone 和 iPad。H5 开发服务及生产产物均完成手机尺寸的首页/“我的”导航检查，未发现浏览器脚本错误。微信开发者工具运行、原生真机测试和签名发布尚未进行。

官方文档：[快速开始](https://unibest.tech/base/2-start)、[运行与发布](https://unibest.tech/base/11-build)、[App 专题](https://unibest.tech/base/18-app)。上游 MIT 许可与作者署名保留在项目中。
