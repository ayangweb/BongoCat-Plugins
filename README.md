# BongoCat Plugins

This repository is the independent source for the BongoCat plugin SDK, the
official plugins, their packages, and the signed plugin catalog.

## Repositories

The application consumes the SDK as an exact Git revision. It does not need a
published crate or an application release:

```toml
[workspace.dependencies]
bongocat-plugin-sdk = {
    git = "https://github.com/ayangweb/BongoCat-Plugins",
    rev = "<full commit SHA>"
}
```

Pin the full 40-character SHA. Advancing the `rev` is an explicit application
change and can be reviewed independently from plugin releases.

The application only keeps its plugin host, UI, and runtime. The SDK and the
official `pomodoro`, `key-sounds`, and `input-source` plugins live here.

## Release model

A `v*` tag publishes one plugin batch. Every plugin keeps its own SemVer in
`plugins/<name>/plugin.json`; a tag does not need to equal any plugin version.

The workflow:

1. Validates the tag, source, manifests, changelogs, Rust tests, and packaging
   tests.
2. Builds all three plugins on Windows x64, macOS arm64, and macOS x64.
3. Reuses the exact historical ZIP bytes for an unchanged plugin version.
4. Rejects source changes that do not have a plugin version bump.
5. Rejects SemVer regressions and retains the last released state of removed
   plugins so retired versions cannot be reintroduced.
6. Signs the canonical catalog with the plugin-owned Minisign key and verifies
   both catalog and package bytes with the committed public key.
7. Uploads every asset to a draft GitHub Release, downloads and rechecks the
   catalog, state, three-platform matrix, and ZIP digests, then
   publishes it.

The public catalog endpoint is independent from the application:

```text
https://github.com/ayangweb/BongoCat-Plugins/releases/latest/download/plugins.json
```

The catalog and versioned ZIP/PNG files are immutable. A release never moves a
tag, and an existing release name is rejected instead of overwritten.

## GitHub setup

Create the repository at `ayangweb/BongoCat-Plugins` and protect `master`.
Configure these Actions secrets in that repository only:

- `PLUGIN_SIGNING_PRIVATE_KEY`: the complete Minisign private-key box, copied
  verbatim from the generated local key at `.secrets/plugin-release.key`.
- `PLUGIN_SIGNING_KEY_PASSWORD`: password for that key. Use an empty value if
  the key was generated without a password.

The committed public key is `config/plugin-release.pub`. Do not copy the
application's `SIGNING_PRIVATE_KEY` or `RELEASE_SIGNING_KEY` into this
repository.

The workflow uses the repository's automatic `GITHUB_TOKEN` and needs
`contents: write` only in the publish job.

## Local verification

```sh
just check
just build aarch64-apple-darwin
just dev-plugins aarch64-apple-darwin
just release-notes v1.0.0 target/release-notes.md
```

`just build` writes all packages for one platform to `target/plugins/`.
`just dev-plugins` builds the same packages and adds the unsigned local
`catalog.json` and icons that the application's Development Plugin Center reads.
Use the Rust host triple for your machine; a build must run on the matching
operating system.

Run target builds on the matching operating system. In particular, do not
infer Windows plugin behavior from a macOS cross-build.

To develop against this checkout from the application repository, either let
the application clone it under `target/plugin-dev/BongoCat-Plugins`, or point
the application at this checkout before running its development command:

```sh
BONGOCAT_PLUGINS_ROOT=/path/to/BongoCat-Plugins just dev
```

The application's `just dev` and `just dev-smoke` invoke this repository's
`catalog dev` command, then set the generated directory as the host's local
plugin source. No plugin source, release tag, signing key, or application
release is required for this path.

The local suite also runs with
`python3 -m unittest discover -s tools/tests -p 'test_*.py' -v`, covering catalog
signing, the three-platform matrix, version regression, draft asset lookup, and
workflow constraints. A full GitHub Actions release still requires the real
repository, all three runners, and the signing secrets.

`catalog dev`, `catalog sign`, and package builds are repeatable in the same
output directory. Identical output is left in place and changed development
catalogs are atomically replaced, so a failed rebuild does not require deleting
the previous catalog. Published release assets remain immutable and are checked
against their recorded digests.

## Publishing

1. Bump every changed plugin's manifest and matching Cargo package version.
2. Add one entry to each bilingual plugin changelog for the new version.
3. Run `just check` and build the change on the affected target.
4. Commit the source.
5. Create and push an annotated `v*` tag on that commit.

The tag starts the GitHub Actions release. A release failure leaves the
previous GitHub `latest` release and `plugins.json` untouched; the draft is not
promoted. Delete the failed draft before retrying the same tag, or use a new
tag. Never move or reuse a published tag. A published release never falls back
to older versions if an asset is manually deleted; fix it with a new tag.

## Rollback

Plugin installations are selected by SemVer. To roll back a bad plugin, publish
a new higher version that restores the previous behavior. Do not overwrite an
existing ZIP, PNG, catalog, or release. The workflow intentionally refuses
those mutations.

## Limits

- Catalog, ZIP, and PNG downloads are bounded by the host and publisher limits.
- Release asset download through the workflow is capped at 17 MiB per asset.
- Plugin binaries are not Authenticode-signed and macOS archives are not
  notarized; the catalog uses Minisign trust and SHA-256 digest checks.
- The first release requires an existing repository and the two signing
  secrets. The workflow cannot create or configure its GitHub repository.
- Workflow verification covers the GitHub Actions execution path; local checks
  cannot replace final builds on the Windows, Intel macOS, and Apple Silicon
  runners.
- Local development builds execute plugin binaries directly and are not
  notarized, signed, or isolated from the host's user account. Treat plugins as
  trusted local code during development.
- Switching the application to this repository's SDK `rev`, plugin catalog URL,
  and plugin public key is separate application integration work.
