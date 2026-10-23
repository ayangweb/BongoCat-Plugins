# 为 BongoCat 插件贡献代码

[English](CONTRIBUTING.md) | 简体中文

感谢你改进 BongoCat 插件。请让每次贡献保持聚焦，测试所修改的行为，并同步更新
面向用户或贡献者的中英文文档。

## 仓库与协作方式

本仓库是插件 SDK、官方插件、插件打包、签名和插件发布的唯一来源。不要把插件源码
复制回 BongoCat 主应用仓库。

有上游写权限的维护者可以直接克隆上游仓库。其他贡献者需要先在 GitHub 上 fork，
克隆自己的 fork，并把上游仓库添加为 remote：

```sh
git clone https://github.com/<your-name>/BongoCat-Plugins.git
cd BongoCat-Plugins
git remote add upstream https://github.com/ayangweb/BongoCat-Plugins.git
git fetch upstream
git switch -c fix/plugin-topic upstream/master
```

把分支推送到自己的 fork，然后向 `ayangweb/BongoCat-Plugins:master` 提交 Pull
Request：

```sh
git push -u origin fix/plugin-topic
```

仓库目前只有由 `v*` Tag 触发的发布工作流，Pull Request 依赖本地验证和维护者
审查。不要直接向上游 `master` 推送。

## 环境要求

- Windows x64，并使用 MSVC Rust 工具链；或 Apple Silicon、Intel 的 macOS。
- `rustup`。仓库通过 `rust-toolchain.toml` 固定 Rust `1.97.1`。
- `just`、Python 3 和 Git。
- `cargo-deny` `0.20.2`，`just check` 和发布工作流都会使用：

  ```sh
  cargo install cargo-deny --version 0.20.2 --locked
  ```

- 当前平台需要的原生构建工具：Windows 上的 Visual Studio Build Tools（包含
  C++ 工作负载），或 macOS 上的 Xcode Command Line Tools。

Linux 不是插件开发或发布目标。打包工具会拒绝在错误的操作系统上构建目标，因此
不能用 macOS 构建推断 Windows 行为，反之亦然。

## 仓库结构

```text
crates/bongocat-plugin-sdk/        带版本号的 JSON 进程协议
crates/bongocat-plugin-packaging/  构建、目录、签名和发布检查
plugins/<name>/                    单个插件 crate、manifest 与资源
CHANGELOG*.md                      双语插件发布说明
config/plugin-release.pub          插件目录签名公钥
tools/                             发布辅助脚本与 Python 契约测试
.github/workflows/release.yml      Tag 触发的插件发布工作流
justfile                           唯一受支持的本地构建与验证入口
```

构建后的插件包只包含 `plugin.json`、声明的图标和插件可执行文件。运行时不会加载
插件源码或 SDK。

## 构建与验证

在仓库根目录运行：

```sh
just fmt
just check
cargo test --locked --workspace
just build <host-triple>
just dev-plugins <host-triple>
```

`just check` 会检查格式，运行 SDK 与打包 crate 的 Clippy 和测试，执行
`cargo deny`、Python 契约测试，并校验当前发布说明。`just test` 只覆盖 SDK、
打包 crate 和 Python 测试。修改插件代码后，还要运行完整工作区测试：

```sh
cargo test --locked --workspace
```

使用当前机器的 Rust host triple：

| 主机                | Triple                   |
| ------------------- | ------------------------ |
| Windows x64         | `x86_64-pc-windows-msvc` |
| macOS Apple Silicon | `aarch64-apple-darwin`   |
| macOS Intel         | `x86_64-apple-darwin`    |

`just build` 会把带版本号的 ZIP 写入 `target/plugins/`。`just dev-plugins`
会构建相同的主机插件包，并额外生成供主应用 Development 插件中心使用的未签名
`catalog.json` 和图标副本。两个命令都可以重复写入同一输出目录。

所有受影响平台都要运行相应检查。构建成功不能证明原生权限、界面行为或设备集成
已经正常。

## 插件 manifest

`plugins/` 下每个包含 `plugin.json` 的目录都会被发现和打包。文件顶层只有一个
`metadata` 对象：

```json
{
  "metadata": {
    "id": "com.example.plugin",
    "name": "Example Plugin",
    "description": "One concise English description.",
    "version": "1.0.0",
    "app_versions": ">=2.3.1",
    "protocol_version": 1,
    "entry": "bongocat-example-plugin",
    "icon": { "type": "local_image", "value": "resources/icon.png" },
    "capabilities": ["configuration", "localized_views_v1"],
    "localizations": {
      "zh-CN": {
        "name": "示例插件",
        "description": "一句简洁的中文简介。"
      }
    }
  }
}
```

打包工具会强制检查以下规则：

- `id` 必须唯一，且只能包含 ASCII 字母、数字、`.`、`_` 和 `-`。
- `name` 与 `description` 是英文文案，不能为空。
- `localizations` 可以添加完整的 `zh-CN` 名称与简介，但不要再添加 `en-US`，
  因为顶层文案已经是英文。当前只支持简体中文和英文。
- `version` 必须是 SemVer，并与插件 crate 的 `[package].version` 保持一致。
- `app_versions` 必须是有效的 SemVer 版本要求。
- `protocol_version` 必须与 SDK 当前协议版本一致（当前为 `1`）。
- `entry` 是可执行文件名，只能包含 ASCII 字母、数字、`_` 和 `-`，并必须与
  Cargo binary 名称一致。
- `icon` 必须是指向现有本地文件的安全相对路径。当前约定使用
  `resources/icon.png`。
- `capabilities` 必须使用 SDK 定义的 capability，并且只声明插件真正处理的
  能力。

未知 manifest 字段会被拒绝。不要增加并行的打包方式或 manifest 格式。

## 开发约定

- 插件是独立的 Rust 进程，只能通过 `bongocat-plugin-sdk` 与宿主通信；应用内部
  Rust 类型或 ABI 不得跨边界。
- 业务规则、配置校验、持久状态、界面文案和用户可见错误都由插件自己维护。
- stdout 只用于带帧的协议，绝不能向 stdout 写日志或诊断信息。通过有界
  `PluginError` 返回稳定 ID 和本地化消息，不要暴露原始系统错误、路径或协议细节。
- 使用 SDK 的 `PluginView`、`UiNode`、`Configuration`、`HostMessage` 和
  `PluginOutput` 类型，并校验输出及节点、文本、状态、配置上限。
- 插件发布的界面必须支持英文和简体中文。manifest 的 `zh-CN` 文案要么完整，
  要么完全不提供。
- 原生平台代码放在 `cfg` 模块或平台适配层。把 `unsafe` 限制在最小的原生边界，
  并说明其安全不变量。
- 优先复用 SDK helper 和工作区依赖。新增依赖必须固定版本、检查 `deny.toml`
  允许的许可证，并确认其平台范围与插件一致。
- 随包分发媒体或其他第三方资源时，补充来源和再分发条款。

为行为与配置校验添加聚焦的单元测试。协议帧、生命周期、本地化或退出行为变化时，
还要更新 `tests/process.rs` 中的真实进程测试。现有插件同时提供了这两类测试模板。

## 新增插件

1. 创建 `plugins/<name>/`，包含 `Cargo.toml`、`plugin.json`、`src/main.rs` 和
   `resources/icon.png`。
2. 把 crate 加入根 `Cargo.toml` 的 `members`。
3. 将 Cargo package 名称设为预期的可执行文件名，或声明一个名称与 manifest
   `entry` 一致的显式 binary。
4. 让 `[package].version` 与 manifest `version` 使用同一个 SemVer。
5. 使用全局唯一的插件 ID，并让 `app_versions` 准确反映所依赖的宿主 API 范围。
6. 实现 `bongocat_plugin_sdk::Plugin`，并通过
   `bongocat_plugin_sdk::run(&mut YourPlugin::default())` 启动进程。
7. 添加英文 metadata；如有需要，再添加完整的 `zh-CN` metadata 和界面文案。
8. 在根目录 `CHANGELOG.md` 与 `CHANGELOG.zh-CN.md` 中，把插件加入其当前版本
   标题下。每个插件只保留一条当前记录。
9. 运行 `just check`、`cargo test --locked --workspace` 和
   `just build <host-triple>`，确认 ZIP 包含 manifest、图标和可执行文件。

打包工具会扫描所有 `plugins/*/plugin.json`，不需要额外注册。插件 ID 重复、
图标或可执行文件缺失都会使构建失败。

## 与 BongoCat 联调

只修改插件行为时，不需要修改主应用的 SDK revision。把主应用指向当前插件仓库，
即可测试包括未提交改动在内的内容：

```sh
BONGOCAT_PLUGINS_ROOT=/path/to/BongoCat-Plugins just dev
BONGOCAT_PLUGINS_ROOT=/path/to/BongoCat-Plugins just plugin-tests
```

主应用自动管理的 `target/plugin-dev/BongoCat-Plugins` checkout 必须保持干净，
并固定在主应用 `Cargo.toml` 声明的 SDK revision。

修改 SDK、协议或宿主接口会同时影响两个仓库。请先合并插件仓库的 Pull Request。
本地联调时，主应用可以临时使用 path 依赖或贡献者 fork 的完整 commit，但这些依赖
和 lockfile 改动不得提交。插件改动在上游合并后，主应用再固定合并后的完整 40 位
revision：

```toml
bongocat-plugin-sdk = {
  git = "https://github.com/ayangweb/BongoCat-Plugins",
  rev = "<full-upstream-commit-sha>"
}
```

然后在主应用仓库运行 `cargo update --workspace`、`just check` 和
`just plugin-tests`。这条集成链路使用 Git revision，不需要插件 Tag 或 Release。

## 发布流程

只有维护者可以发布插件。插件发布与 BongoCat 主应用发布相互独立，不需要主应用
Tag、版本号或工作流。

打 Tag 前：

1. 提升每个有变化插件的 manifest 与对应 Cargo package 版本。
2. 在根目录两份更新日志中更新该插件的当前记录。`just release-notes` 会校验每个
   当前 manifest 都有双语记录。
3. 运行 `just check`、`cargo test --locked --workspace`，并在本机构建。
4. 由 CI 验证 Windows x64、macOS arm64 和 macOS x64 构建。
5. 提交源码，在可从 `master` 到达的提交上创建附注 SemVer Tag（例如
   `v1.0.1`），并推送该 Tag。

工作流会校验 Tag 和发布元数据，构建三个平台的插件包，复用版本未变化插件的不可变
ZIP，签名目录，创建草稿 Release，下载并复核全部资产和摘要，最后才正式发布。
已发布的 Tag、Release、ZIP、PNG 和目录均不可变。回滚行为时应发布更高版本，
绝不能移动 Tag 或覆盖资产。

仓库使用的签名公钥是 `config/plugin-release.pub`。GitHub Actions 需要以下仓库
Secret：

- `PLUGIN_SIGNING_PRIVATE_KEY`：完整的 base64 Minisign 私钥 box。
- `PLUGIN_SIGNING_KEY_PASSWORD`：该私钥的密码。只有私钥本身没有密码时才能为空。

这些值由插件仓库独立持有。不要把主应用的 `SIGNING_PRIVATE_KEY` 或
`RELEASE_SIGNING_KEY` 复制到本仓库，也不要提交 `.secrets/`。

## 提交与 Pull Request

使用 Conventional Commits，例如 `fix(key-sounds): preserve release sounds`。
Pull Request 应说明问题、修改后的行为、受影响平台、验证命令与结果，以及无法运行
的检查。不要混入无关的格式化或重构。
