# Contributing to BongoCat Plugins

English | [简体中文](CONTRIBUTING.zh-CN.md)

Thank you for improving BongoCat plugins. Keep each contribution focused, test
the behavior you change, and update both language versions of user-facing or
contributor-facing documentation.

## Repository and collaboration

This repository is the only source for the plugin SDK, official plugins, plugin
packaging, signing, and plugin releases. Do not copy plugin source back into the
BongoCat application repository.

Maintainers may clone the upstream repository directly. Other contributors must
fork it on GitHub, clone their fork, and add the upstream repository as a remote:

```sh
git clone https://github.com/<your-name>/BongoCat-Plugins.git
cd BongoCat-Plugins
git remote add upstream https://github.com/ayangweb/BongoCat-Plugins.git
git fetch upstream
git switch -c fix/plugin-topic upstream/master
```

Push the branch to your fork and open a pull request against
`ayangweb/BongoCat-Plugins:master`:

```sh
git push -u origin fix/plugin-topic
```

The only workflow currently defined runs on `v*` tags; pull requests rely on
local validation and maintainer review. Do not push to upstream `master`
directly.

## Requirements

- Windows x64 with the MSVC Rust toolchain, or macOS on Apple Silicon or Intel.
- `rustup`. The repository pins Rust `1.97.1` in `rust-toolchain.toml`.
- `just`, Python 3, and Git.
- `cargo-deny` `0.20.2`, which is used by `just check` and the release workflow:

  ```sh
  cargo install cargo-deny --version 0.20.2 --locked
  ```

- Native build tools required by Rust for the host platform: Visual Studio Build
  Tools with the C++ workload on Windows, or Xcode Command Line Tools on macOS.

Linux is not a supported plugin development or release target. The packaging
tool refuses to build a target on the wrong operating system, so do not infer
Windows behavior from a macOS build or the reverse.

## Repository layout

```text
crates/bongocat-plugin-sdk/        Versioned JSON process protocol
crates/bongocat-plugin-packaging/  Build, catalog, signing, and release checks
plugins/<name>/                    One plugin crate and its manifest/resources
CHANGELOG*.md                      Bilingual plugin release notes
config/plugin-release.pub          Public key for the signed catalog
tools/                             Release helpers and Python contract tests
.github/workflows/release.yml      Tag-triggered plugin release workflow
justfile                           Supported local build and validation commands
```

A built package contains only `plugin.json`, the declared icon, and the plugin
executable. Plugin source and the SDK are not loaded at runtime.

## Build and validation

Use these commands from the repository root:

```sh
just fmt
just check
cargo test --locked --workspace
just build <host-triple>
just dev-plugins <host-triple>
```

`just check` checks formatting, runs Clippy and tests for the SDK and packaging
crate, runs `cargo deny`, executes the Python contract tests, and validates the
current release notes. `just test` covers only the SDK, packaging crate, and
Python tests. When plugin code changes, also run the full workspace tests:

```sh
cargo test --locked --workspace
```

Use the triple for the machine running the build:

| Host                | Triple                   |
| ------------------- | ------------------------ |
| Windows x64         | `x86_64-pc-windows-msvc` |
| macOS Apple Silicon | `aarch64-apple-darwin`   |
| macOS Intel         | `x86_64-apple-darwin`    |

`just build` writes versioned ZIPs to `target/plugins/`. `just dev-plugins`
builds the same host packages and also writes an unsigned `catalog.json` plus
the icon copies used by the application's Development Plugin Center. Both
commands may be rerun in the same output directory.

Run the relevant checks on every affected platform. A successful build is not
evidence that native permissions, UI behavior, or device integrations work.

## Plugin manifest

Each directory under `plugins/` with a `plugin.json` is discovered and packaged.
The file has one top-level `metadata` object:

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

Manifest rules enforced by packaging:

- `id` is unique and contains only ASCII letters, digits, `.`, `_`, and `-`.
- `name` and `description` are the English copy and must not be empty.
- `localizations` may add a complete `zh-CN` name/description pair. Do not add
  `en-US`, because the top-level copy is already English. Only Simplified
  Chinese and English are currently supported.
- `version` is SemVer. Keep it synchronized with the plugin crate's
  `[package].version`.
- `app_versions` is a valid SemVer requirement.
- `protocol_version` matches the SDK's current protocol version (`1`).
- `entry` names the executable binary and uses only ASCII letters, digits, `_`,
  and `-`. It must match the Cargo binary name.
- `icon` must be a safe relative path to an existing local file. Use
  `resources/icon.png`.
- `capabilities` must use SDK capability values. Declare only the capabilities
  the plugin handles.

Unknown manifest fields are rejected. Do not add a parallel packaging or
manifest format.

## Development conventions

- A plugin is a standalone Rust process. Communicate with the host only through
  `bongocat-plugin-sdk`; no application Rust types or ABI cross the boundary.
- Keep business rules, configuration validation, persistent state, view text,
  and user-facing errors inside the plugin.
- Stdout is exclusively the framed protocol. Never write logs or diagnostics to
  stdout. Return bounded `PluginError` values with stable IDs and localized
  messages; do not expose raw OS errors, paths, or protocol details.
- Use the SDK's typed `PluginView`, `UiNode`, `Configuration`, `HostMessage`,
  and `PluginOutput` types. Validate outputs and respect node, text, state, and
  configuration limits.
- Localize plugin-published UI in English and Simplified Chinese. Keep the
  manifest's `zh-CN` metadata complete or omit it entirely.
- Isolate native platform code in `cfg` modules or the platform adapter layer.
  Keep `unsafe` to the smallest native boundary and document its invariants.
- Prefer existing SDK helpers and workspace dependencies. Pin new dependencies,
  check their license against `deny.toml`, and avoid dependencies with a smaller
  platform scope than the plugin.
- Add provenance and redistribution terms for bundled media or other
  third-party assets.

Add focused unit tests for behavior and configuration validation. Add or update
a real-process test under `tests/process.rs` when protocol framing, lifecycle,
localization, or shutdown behavior changes. The existing plugins provide
working templates for both styles.

## Adding a plugin

1. Create `plugins/<name>/` with `Cargo.toml`, `plugin.json`, `src/main.rs`, and
   `resources/icon.png`.
2. Add the crate to `members` in the workspace `Cargo.toml`.
3. Set the Cargo package name to the intended executable name, or declare an
   explicit binary whose name matches manifest `entry`.
4. Set `[package].version` and manifest `version` to the same SemVer.
5. Use a globally unique plugin ID and an `app_versions` range that reflects the
   host APIs you rely on.
6. Implement `bongocat_plugin_sdk::Plugin` and start the process with
   `bongocat_plugin_sdk::run(&mut YourPlugin::default())`.
7. Add English metadata and, if available, complete `zh-CN` metadata and UI copy.
8. Add the plugin to `CHANGELOG.md` and `CHANGELOG.zh-CN.md` under the current
   version heading. Keep one current entry per plugin.
9. Run `just check`, `cargo test --locked --workspace`, and
   `just build <host-triple>`. Verify the resulting ZIP contains the manifest,
   icon, and executable.

Packaging scans every `plugins/*/plugin.json`; no separate registry entry is
needed. Duplicate plugin IDs or a missing icon/binary fail the build.

## Integration with BongoCat

Plugin-only changes do not require changing the application's SDK revision.
Point the application at your plugin checkout, including uncommitted changes:

```sh
BONGOCAT_PLUGINS_ROOT=/path/to/BongoCat-Plugins just dev
BONGOCAT_PLUGINS_ROOT=/path/to/BongoCat-Plugins just plugin-tests
```

The application's automatic checkout under `target/plugin-dev/BongoCat-Plugins`
must stay clean and is pinned to the SDK revision in the application's
`Cargo.toml`.

SDK, protocol, or host-interface changes affect both repositories. Open the
plugin-repository pull request first. For local integration testing, the
application may temporarily use a path dependency or a full commit from your
fork, but those dependency and lockfile changes must not be committed. After the
plugin change is merged upstream, the application pins the merged full
40-character revision:

```toml
bongocat-plugin-sdk = {
  git = "https://github.com/ayangweb/BongoCat-Plugins",
  rev = "<full-upstream-commit-sha>"
}
```

Then run `cargo update --workspace`, `just check`, and `just plugin-tests` in the
application repository. This integration uses a Git revision, not a plugin Tag
or Release.

## Release process

Only maintainers publish plugins. A release is independent of the BongoCat
application release and requires no application tag, version bump, or workflow.

Before tagging:

1. Bump every changed plugin's manifest and matching Cargo package version.
2. Update its current entry in both root changelogs. `just release-notes`
   validates that every current manifest has a bilingual entry.
3. Run `just check`, `cargo test --locked --workspace`, and a host build.
4. Let CI verify the Windows x64, macOS arm64, and macOS x64 builds.
5. Commit the source, create an annotated SemVer tag such as `v1.0.1` on a commit
   reachable from `master`, and push the tag.

The workflow validates the tag and release metadata, builds all three platform
packages, reuses immutable packages for unchanged plugin versions, signs the
catalog, creates a draft Release, verifies every downloaded asset and digest,
and only then publishes it. Published tags, Releases, ZIPs, PNGs, and catalogs
are immutable. To roll back behavior, publish a higher plugin version; never
move a tag or overwrite an asset.

The repository-owned signing public key is `config/plugin-release.pub`. GitHub
Actions requires these repository secrets:

- `PLUGIN_SIGNING_PRIVATE_KEY`: the complete base64 Minisign private-key box.
- `PLUGIN_SIGNING_KEY_PASSWORD`: its password. The workflow accepts an empty
  password only if the key was generated without one.

These are plugin-owned values. Never copy the application's
`SIGNING_PRIVATE_KEY` or `RELEASE_SIGNING_KEY` into this repository, and never
commit `.secrets/`.

## Commits and pull requests

Use Conventional Commits, for example `fix(key-sounds): preserve release
sounds`. A pull request should state the problem, the behavior changed, the
affected platforms, validation commands and results, and any checks that could
not be run. Keep unrelated formatting or refactoring out of the same change.
