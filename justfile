help:
    @just --list

fmt:
    cargo fmt --all -- --check

test:
    cargo test --locked -p bongocat-plugin-sdk -p bongocat-plugin-packaging
    python3 -m unittest discover -s tools/tests -p 'test_*.py'

check: fmt
    cargo clippy --locked -p bongocat-plugin-sdk -p bongocat-plugin-packaging --all-targets -- -D warnings
    cargo test --locked -p bongocat-plugin-sdk -p bongocat-plugin-packaging
    cargo deny --locked check licenses sources bans
    python3 -m unittest discover -s tools/tests -p 'test_*.py'
    python3 tools/release_notes.py --root . --tag v1.0.0 --output target/release-notes.md

build triple:
    cargo run --locked -p bongocat-plugin-packaging -- build --root . --target {{triple}} --output target/plugins

dev-plugins triple:
    cargo run --locked -p bongocat-plugin-packaging -- catalog dev --root . --target {{triple}} --output target/plugins

keygen private public:
    cargo run --locked -p bongocat-plugin-packaging -- keygen --private {{private}} --public {{public}}

release-notes tag output:
    python3 tools/release_notes.py --root . --tag {{tag}} --output {{output}}

verify catalog state:
    cargo run --locked -p bongocat-plugin-packaging -- verify --catalog {{catalog}} --state {{state}} --public-key config/plugin-release.pub
