# Previous versions / 历史版本

[中文首页](README.md) · [English](README.en.md)

Use the current published Stable release unless you explicitly need an older version.
优先使用已发布的正式版；历史合同只能安装其指定版本，不要混用当前源码。

| Version | Scope | Instructions and evidence |
| --- | --- | --- |
| v4.3.0 | Current Stable, GPT-6 / 当前正式版 | [Release](https://github.com/SuperDaddyV/codex-native-workers/releases/tag/v4.3.0) · [Instructions](NATIVE_WORKERS_SETUP.md) · [Evidence](https://github.com/SuperDaddyV/codex-native-workers/releases/download/v4.3.0/native-workers-v4.3.0-validation.json) |
| v4.2.0 | Previous Stable / 旧正式版，GPT-5.6 | [Release](https://github.com/SuperDaddyV/codex-native-workers/releases/tag/v4.2.0) · [Instructions](https://github.com/SuperDaddyV/codex-native-workers/blob/v4.2.0/NATIVE_WORKERS_SETUP.md) · [Evidence](https://github.com/SuperDaddyV/codex-native-workers/releases/download/v4.2.0/native-workers-v4.2.0-validation.json) |
| v4.2.0-rc1 | Previous Preview / 旧预览版 | [Release](https://github.com/SuperDaddyV/codex-native-workers/releases/tag/v4.2.0-rc1) · [Immutable contract](https://github.com/SuperDaddyV/codex-native-workers/blob/527b174df13643a38bfe29652208eaa00f63fbf7/NATIVE_WORKERS_PREVIEW.md) · [Evidence](https://github.com/SuperDaddyV/codex-native-workers/releases/download/v4.2.0-rc1/native-workers-rc1-validation.json) |
| v4.1.4 | Legacy Stable, Luna workers only / 仅 Luna 子代理 | [Release](https://github.com/SuperDaddyV/codex-native-workers/releases/tag/v4.1.4) |

## v4.1.4 immutable installation chain

- [Assisted Installation contract](https://github.com/SuperDaddyV/codex-sol-luna-worker/blob/7494d47574ac751e76a231033a0ed91686899a07/CODEX_SOL_LUNA_INSTALL_ASSIST.md)
- [Setup contract](https://github.com/SuperDaddyV/codex-sol-luna-worker/blob/bf01c438eae66f5ef9a27d401c6ee845f89d5d59/CODEX_SOL_LUNA_SETUP.md)
- Runtime source: `6a537b445ad6f17a9600c05e655f51a2844bfcc8`
- [Chinese translation](CODEX_SOL_LUNA_INSTALL_ASSIST.zh-CN.md) / 中文审阅版

The project was renamed from `codex-sol-luna-worker` to **Codex Native Workers**.
Old repository links redirect; installation paths and `sol-luna-*` Skill names remain compatible.
项目更名无需搬迁本机目录。历史验收保留原版本标签，不能代替当前版本的运行证据。

The historical compatibility smoke exercises Luna-only behavior; it is not
acceptance of the two-family v4.2 product or the GPT-6 v4.3 migration.
历史 compatibility smoke 只覆盖 Luna-only 行为，不是双 family v4.2 产品的验收，
也不是 GPT-6 v4.3 迁移的原生验收。See [runtime evidence](RUNTIME_TESTS.md).
