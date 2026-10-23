# BongoCat Plugins Agent Guide

开始前先读 `CONTRIBUTING.zh-CN.md`、根 `Cargo.toml`、`justfile` 和相关插件源码。

- 本仓库是插件 SDK、官方插件、打包、签名和发布的唯一来源。不要把插件源码复制回
  BongoCat 主应用，也不要建立第二套打包或发布流程。
- 只用 `just` 执行受支持的构建入口。常规修改至少运行 `just check`；改插件代码时
  还要运行 `cargo test --locked --workspace`，并在目标操作系统执行
  `just build <host-triple>`。
- `plugin.json` 的 `version` 与 Cargo package 版本保持一致；`entry` 必须对应真实
  binary，`icon` 必须指向真实本地文件。新增插件还要加入 workspace members 和两份
  根目录 `CHANGELOG*.md`。
- 插件只通过 `bongocat-plugin-sdk` 的强类型协议与宿主通信。stdout 只能输出协议帧；
  错误使用有界、本地化的 `PluginError`。界面文案只支持英文和简体中文。
- capability、协议或 SDK 公共 API 变化会同时影响主应用。必须说明兼容影响，并让
  主应用固定上游合并后的完整 40 位 revision；不要用插件 Tag 代替该集成步骤。
- 未经用户明确要求，不 commit、push、打 Tag 或发布 Release。不得移动已发布 Tag、
  覆盖 Release 资产或修改签名配置；不得提交 `.secrets/`。
- README 与 CONTRIBUTING 的中英文版本必须同步修改。完成时报告实际运行的检查、
  未运行的平台验证和剩余风险。
