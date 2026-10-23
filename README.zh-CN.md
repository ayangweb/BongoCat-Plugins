# BongoCat 插件

[English](README.md) | 简体中文

本仓库独立维护 BongoCat 插件 SDK、官方插件、打包与签名工具，以及签名插件目录。
主应用通过固定的 Git commit 引入 SDK。

## 插件

|                                        图标                                         | 插件                               | 简介                                                   |
| :---------------------------------------------------------------------------------: | ---------------------------------- | ------------------------------------------------------ |
|    <img src="plugins/pomodoro/resources/icon.png" alt="番茄时钟图标" width="56">    | [番茄时钟](plugins/pomodoro)       | 通过专注计时帮助你保持专注、合理安排时间。             |
|   <img src="plugins/key-sounds/resources/icon.png" alt="按键音效图标" width="56">   | [按键音效](plugins/key-sounds)     | 为键盘和鼠标操作添加生动的声音反馈，让每次交互更有趣。 |
| <img src="plugins/input-source/resources/icon.png" alt="输入法状态图标" width="56"> | [输入法状态](plugins/input-source) | 实时显示当前使用的输入法，方便随时了解输入状态。       |

## 开发

开发目标是 Windows x64，以及 Apple Silicon 或 Intel 的 macOS。构建必须在目标
操作系统上运行。

```sh
just check
cargo test --locked --workspace
just build <host-triple>
just dev-plugins <host-triple>
```

## 如何贡献

先 fork 本仓库，从 `upstream/master` 创建主题分支，完成并测试修改后提交 Pull
Request。环境配置、插件规范、构建测试和主应用联调见
[CONTRIBUTING.zh-CN.md](CONTRIBUTING.zh-CN.md)。
