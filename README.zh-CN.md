# BongoCat 插件

这个仓库是 BongoCat 插件 SDK、官方插件、插件包和签名插件目录的独立来源。

## 仓库关系

主应用通过固定 Git revision 引入 SDK，不需要发布 crate，也不需要等待主应用发版：

```toml
[workspace.dependencies]
bongocat-plugin-sdk = {
    git = "https://github.com/ayangweb/BongoCat-Plugins",
    rev = "<完整的 40 位 commit SHA>"
}
```

必须固定完整 SHA。升级 `rev` 是主应用一次明确、可审查的变更，与插件 Release 相互独立。

主应用只保留插件宿主、设置界面和运行时；SDK 以及 `pomodoro`、`key-sounds`、`input-source` 三个官方插件都由本仓库维护。

## 发布模型

推送一个 `v*` Tag 会发布一批插件。每个插件在 `plugins/<name>/plugin.json` 中维护自己的 SemVer，Tag 不必等于任何插件版本。

工作流依次完成：

1. 校验 Tag、源码、manifest、更新日志、Rust 测试和打包测试。
2. 在 Windows x64、macOS arm64、macOS x64 上构建三个插件。
3. 版本未变化时复用完全相同的 ZIP 字节。
4. 源码发生变化但插件版本未提升时拒绝发布。
5. 按 SemVer 拒绝版本回退；插件被移除后仍保留最后发布状态，阻止已退役版本被重新引入。
6. 使用插件专用 Minisign 私钥签名规范化目录，并用仓库内公钥校验目录和全部插件包。
7. 先把全部资产上传到草稿 Release，下载后逐项复核目录、状态、三平台矩阵和 ZIP 摘要，通过后再正式发布。

公共插件目录地址与主应用独立：

```text
https://github.com/ayangweb/BongoCat-Plugins/releases/latest/download/plugins.json
```

目录、版本化 ZIP 和 PNG 均为不可变资产。发布流程不会移动 Tag，也不会覆盖已有 Release。

## GitHub 配置

在 `ayangweb/BongoCat-Plugins` 创建仓库并保护 `master`。只在该仓库配置两个 Actions Secret：

- `PLUGIN_SIGNING_PRIVATE_KEY`：完整 Minisign 私钥 box 的 Base64；本地生成文件为 `.secrets/plugin-release.key`。
- `PLUGIN_SIGNING_KEY_PASSWORD`：该私钥的密码；无密码时设置为空值。

仓库内公钥是 `config/plugin-release.pub`。不要把主应用的 `SIGNING_PRIVATE_KEY` 或 `RELEASE_SIGNING_KEY` 复制到本仓库。

工作流使用仓库自动提供的 `GITHUB_TOKEN`，只有发布 Job 需要 `contents: write`。

## 本地验证

```sh
just check
just build aarch64-apple-darwin
just release-notes v1.0.0 target/release-notes.md
```

`just build` 将单个平台的全部插件包写入 `target/plugins/`。

目标构建必须在对应操作系统上运行，不能用 macOS 交叉编译推断 Windows 插件行为。

本地还可以运行 `python3 -m unittest discover -s tools/tests -p 'test_*.py' -v`
覆盖目录签名、三平台矩阵、版本回退、草稿资产查询和发布工作流约束。完整的
GitHub Actions 发布仍需要真实仓库、三个 Runner 和签名 Secret。

## 发布与回滚

1. 提升每个有变化插件的 manifest 与对应 Cargo 包版本。
2. 在两份插件更新日志中为每个新版本各写一条记录。
3. 运行 `just check`，并在受影响平台构建验证。
4. 提交源码。
5. 在该提交上创建并推送附注 `v*` Tag。

发布失败时，旧的 GitHub `latest` Release 和 `plugins.json` 保持可用，草稿不会转为正式 Release。重试同一 Tag 前删除失败草稿，或使用新 Tag；永远不要移动或复用已发布的 Tag。已发布 Release 即使资产被人工删除也不会回退到旧版本；请修复并发布新 Tag。

插件安装按 SemVer 选择版本。回滚错误插件时应发布一个更高版本恢复旧行为，而不是覆盖已有 ZIP、PNG、目录或 Release；工作流会拒绝这些改写。

## 限制

- 插件下载受宿主与发布端的大小限制约束。
- 工作流下载单个 Release 资产的上限为 17 MiB。
- 插件不提供 Windows Authenticode 签名，macOS 包也不做公证；信任来自目录 Minisign 签名和插件包 SHA-256 校验。
- 首次发布要求仓库已经存在并配置好两个签名 Secret；工作流不能创建或配置 GitHub 仓库。
- 工作流验证的是 GitHub Actions 执行链路；本地无法代替真实 Runner 完成 Windows、Intel macOS 和 Apple Silicon 三平台最终产物验证。
- 主应用切换 SDK 到本仓库的固定 `rev`、把插件目录地址和插件公钥改成本仓库地址，属于主应用的后续集成工作，不在本仓库的发布流程内。
