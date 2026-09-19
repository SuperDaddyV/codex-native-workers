# Codex Native Workers

由你选择的 Coordinator 掌握任务，原生 GPT-5.6 Sol 与 Luna worker 执行值得委派、边界清楚的工作。

[English](README.md)

[![Stable: v4.1.4](https://img.shields.io/badge/stable-v4.1.4-blue)](https://github.com/SuperDaddyV/codex-sol-luna-worker/releases/tag/v4.1.4)
[![Validation](https://github.com/SuperDaddyV/codex-sol-luna-worker/actions/workflows/validate.yml/badge.svg?branch=master)](https://github.com/SuperDaddyV/codex-sol-luna-worker/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/SuperDaddyV/codex-sol-luna-worker)](LICENSE)

> [!IMPORTANT]
> 这是独立的社区项目，与 OpenAI、ModelDial 均无隶属、赞助或背书关系。

## 这是什么

Codex Native Workers 把用户选择的 **Coordinator** 与两类直属原生 worker 分开：

- **Coordinator 掌握整个任务。** 它负责需求、范围、架构、歧义处理、路由、整合、最终验收和最终答复。Astra 只是 Coordinator 的一个示例；本项目不会选择或安装 Coordinator 模型。
- **Sol 执行复杂的边界任务。** 适合诊断、综合、跨模块推理，以及其他范围清楚但难度较高的执行工作。
- **Luna 执行清楚的边界任务。** 适合定义充分的实现、提取、定向检查、测试、构建和重复性工作。

新的只是展示名称。仓库 slug `codex-sol-luna-worker`、安装路径、托管标记和三个 `sol-luna-*` Skill 名称保持向后兼容。

## v4.2.0-rc1 预览版

**Preview target：**[`v4.2.0-rc1`](https://github.com/SuperDaddyV/codex-sol-luna-worker/releases/tag/v4.2.0-rc1)。它是 Prerelease 目标，不会取代 `v4.1.4` 的当前 Stable 版本和默认 Stable 安装地位。

使用下面的提示词前，先阅读 [v4.2.0-rc1 预览版安装合同](NATIVE_WORKERS_PREVIEW.md)：

```text
仅当已发布、非 draft 的 GitHub Prerelease 存在时，安装 Codex Native
Workers v4.2.0-rc1 预览版。

读取该已发布 Release。把 tag v4.2.0-rc1 解析到一个精确的 40-hex commit，
获取干净的 detached checkout，然后再次读取远端 tag；如有移动立即停止。
从该精确 commit 读取 NATIVE_WORKERS_PREVIEW.md，检查并遵循其中的合同。
不得从 master、target_commitish、可变分支或未经验证的 tag 安装。任何写入前，
披露此目标是 Prerelease / Public Beta，并说明宿主强制阻止 worker 递归委派
的能力尚不受支持。
```

这份 README 不声称预览版 Release 已经发布。发布后，现有安装可通过明确的升级请求使用已安装的 `sol-luna-upgrade` Skill；升级仍须经过 Release discovery、不可变 tag 校验、dry-run 和事务 apply。

预览版在每个 worker role 中保留 `[agents] enabled = false`，并明确禁止 worker 继续委派。这些是配置与策略请求，不是宿主强制执行的证明。与预览版有关的当前宿主证据记录于 rc1 安装前的 Desktop `0.155.0-alpha.9.2`：Sol tool visibility 为 **FAIL**，Luna tool report 为 **UNKNOWN**，nested invocation 为 **NOT RUN**。因此，强递归隔离仍不受支持。

## Coordinator 与 worker 如何协作

Coordinator 只委派值得执行的独立边界任务。它发送包含 Goal、Scope、Constraints、Acceptance Criteria 和 Verification 的 Task Contract，然后复核每一份返回结果。

```mermaid
flowchart TD
    U[用户提出任务] --> C[用户选择的 Coordinator 规划并设定验收标准]
    C --> J{是否有值得委派的独立边界任务}
    J -->|否| O[Coordinator 直接完成]
    J -->|是| F{按任务需要选择 family}
    F -->|复杂诊断或综合| S[直属 Sol worker]
    F -->|清楚的常规或重复工作| L[直属 Luna worker]
    S --> R[返回结果和证据]
    L --> R
    R --> V[Coordinator 复核并整合]
    O --> A[Coordinator 给出最终答复]
    V --> A
```

- **路由：** 先按任务需要选择 family，再检查可用性。Sol 默认使用 `general`，工作明确匹配时可用 `backend`、`frontend` 或 `reasoning` view；Luna 每天只有一个 Daily role。
- **并行：** 通常使用 0–3 个 worker。只有任务全部就绪、彼此独立、写入范围不重叠且宿主实际容量支持时，才扩展到 4–6 个。当前已观察到三个 worker 重叠执行；配置上限六个尚未验证。
- **串行：** 有依赖的工作或重叠修改按顺序执行。
- **Coordinator-only：** 小任务、歧义、架构、无法安全拆分的工作和最终验收由 Coordinator 保留。

Sol 没有固定配额。不能仅因可用性就在 Sol 与 Luna 之间切换任务。Daily Selector 决定当前 worker profile 与 effort；它不选择 Coordinator，也不决定工作是否值得委派。已安装的 profile 使用 `low`、`medium`、`high`、`xhigh` 或 `max`，不使用 `ultra`。

所有 agent 共享当前工作区，因此并行 writer 必须拥有互不重叠的范围。worker 被要求保持直属 leaf，不得继续 spawn 或 delegate；但配置本身不等于 runtime enforcement。

对于非简单工作流，最后一行按当前格式报告实际执行方式：

```text
Coordinator/Workers: delegated · sol_high ×1
Coordinator/Workers: delegated · luna_high ×2 · parallel
Coordinator/Workers: Coordinator-only · too small
Coordinator/Workers: Coordinator-only · no independent work
```

Receipt 只汇总已观察到的任务事实，不是 runtime attestation，也不会声称节省额度。

## 核心价值

- **原生 worker：** 使用 Codex custom agents 和 subagents，不需要 Hook Router 或自建编排引擎。
- **精简 Global 策略：** 托管 Global block 不超过 2 KiB，条件工作流放在 `sol-luna-delegate`、`sol-luna-status` 和 `sol-luna-upgrade` 中。
- **经过校验的每日路由：** 根据公共 benchmark reference data 选择 Sol 与 Luna profile。`reference_only` 选择不是本地 runtime 证据；缺少可比成本时使用 quality-only 选择，绝不据此声称实际账单或额度节省。
- **配置保护和可恢复：** 保留无关用户配置，遇到冲突 fail closed，并通过事务备份支持受控回滚和安全卸载。

## 系统要求

- Codex Desktop，或其他支持 custom agent 与 subagent 的当前 Codex 客户端。
- 当前任务环境可执行 `codex` 命令；如果 `codex --version` 不能运行，仅安装 Codex Desktop 还不够。
- 账号可使用用户选择的 Coordinator 模型；使用预览版时，还须可使用所需 effort 的 GPT-5.6 Sol 与 GPT-5.6 Luna。
- Python 3.11 或更高版本并包含 `tomllib`，以及用于不可变精确 commit checkout 的 Git。
- 能以只读 HTTPS 访问本公开 GitHub 仓库。
- Windows、Ubuntu/Linux 或 macOS。WSL 应视为独立 Linux 环境。

## Stable 安装（默认）

使用能力合适的 Coordinator 新建一个 Codex 任务，然后只粘贴下面这一个提示词：

```text
请读取并严格执行以下安装协助合同：

https://raw.githubusercontent.com/SuperDaddyV/codex-sol-luna-worker/7494d47574ac751e76a231033a0ed91686899a07/CODEX_SOL_LUNA_INSTALL_ASSIST.md

安装固定的 v4.1.4 Stable 目标。一次性诊断全部彼此独立的前置条件。
只自动执行合同允许的安全修复。安装软件包、提升管理员权限或持久修改环境前，
先给出一份来自官方来源的准确修复方案并等待我的明确确认。获得确认后自动复检并续跑。
不得修改认证、代理、证书信任、sandbox、组织策略或无关用户配置。
Ready: YES 后严格执行合同固定的 setup contract 和现有安装器。
安装后告诉我如何重新加载 Codex，并给出新任务 smoke 的续接内容。
```

固定的 [Assisted Installation contract](https://github.com/SuperDaddyV/codex-sol-luna-worker/blob/7494d47574ac751e76a231033a0ed91686899a07/CODEX_SOL_LUNA_INSTALL_ASSIST.md) 是 Stable 安装入口；[中文审阅版](CODEX_SOL_LUNA_INSTALL_ASSIST.zh-CN.md)仅供核对。它把安装固定到经过审查的 [v4.1.4 Setup contract](https://github.com/SuperDaddyV/codex-sol-luna-worker/blob/bf01c438eae66f5ef9a27d401c6ee845f89d5d59/CODEX_SOL_LUNA_SETUP.md) 和已验证源 `6a537b445ad6f17a9600c05e655f51a2844bfcc8`，避免 Codex 从可变分支安装。

> [!WARNING]
> 不得把 Stable 的不可变安装 URL 改成 `master`、tag 或其他可变入口。系统变更必须获得明确确认。安装器在 ownership 冲突时 fail closed，并在变更前创建事务备份；但任何安装都不能承诺绝对无风险。

安装完成后，按提示重新加载 Codex 并新建任务，让全局 instructions、agents 和 configuration 进入新任务。

## 日常使用

像平时一样使用 Codex。Coordinator 判断任务是否包含值得委派的边界工作，以及哪类 worker 匹配；不是每个提示词都应创建 worker。

```text
请审查这个项目，在值得委派时把复杂诊断和常规测试修复路由给合适的 worker，
然后验证并整合结果。
```

```text
请检查这些模块是否存在不一致的配置，只报告发现，不要修改文件。
```

```text
在安全的前提下，把前端、后端和测试作为独立范围审查，最后给我一份统一结论。
```

路由、重叠范围处理、结果复核和最终答复仍由 Coordinator 负责。

## 如何确认生效

在新的 Codex 任务中运行这条只读 status 命令：

```text
检查 Sol/Luna 状态
```

对于 `v4.2.0-rc1`，diagnostic schema 4 把安装/配置与原生 runtime 证据分开。`Status Healthy`、`Agents 10/10 Ready`、`Skills 3/3 Ready` 和 `leaf_config Ready`只说明配置状态。实际 native delegation、tool isolation、invocation guard 行为和观察到的最大并发量需要单独进行 runtime 检查。配置上限六个不等于实测容量。

v4.1.4 Stable 的 status 结构可能显示 `Agents 5/5 Ready`。其历史 compatibility smoke 只覆盖 Luna-only 行为，不是双 family v4.2 预览版的验收。

安装后或 Codex 更新后，需要更深入检查时，按 [Runtime 检查](RUNTIME_TESTS.md) 执行。status、source test 或 receipt 本身都不等于完整 runtime acceptance。

## 升级、回滚与卸载

- **升级：** 预览版发布后，现有安装可以说「升级 Sol/Luna 到最新版本」。已安装的 `sol-luna-upgrade` Skill 会发现包括 Prerelease 在内的已发布版本，并只应用经过验证的不可变目标。
- **回滚：** 使用 installer 返回的精确 transaction backup；成功回滚会恢复经过校验的变更前状态。
- **卸载：** 使用 installer 的 manifest-owned uninstall 流程，不要手工编辑托管 TOML、Skill 或 agent 文件。

升级、回滚或卸载后重新加载 Codex 并新建任务。Stable 的具体命令、停止条件、ownership 规则和 backup 行为仍以不可变 [v4.1.4 Setup contract](https://github.com/SuperDaddyV/codex-sol-luna-worker/blob/bf01c438eae66f5ef9a27d401c6ee845f89d5d59/CODEX_SOL_LUNA_SETUP.md)为准。

## 技术文档

- [v4.2.0-rc1 预览版安装](NATIVE_WORKERS_PREVIEW.md)
- [Stable 安装、升级、回滚与卸载](https://github.com/SuperDaddyV/codex-sol-luna-worker/blob/bf01c438eae66f5ef9a27d401c6ee845f89d5d59/CODEX_SOL_LUNA_SETUP.md)
- [架构说明](ARCHITECTURE.md)
- [Runtime 证据](RUNTIME_TESTS.md)
- [安全边界](SECURITY.md)
- [版本历史](CHANGELOG.md)
- [GitHub Releases](https://github.com/SuperDaddyV/codex-sol-luna-worker/releases)

## 反馈

- [Bug Report](https://github.com/SuperDaddyV/codex-sol-luna-worker/issues/new?template=bug-report.yml)
- [Compatibility Report](https://github.com/SuperDaddyV/codex-sol-luna-worker/issues/new?template=compatibility-report.yml)
- [Feature / Feedback](https://github.com/SuperDaddyV/codex-sol-luna-worker/issues/new?template=feature-feedback.yml)

提交前删除或脱敏秘密与私有信息，只分享最小必要日志，不要上传整个 `CODEX_HOME`。

## License

[MIT](LICENSE)

`fixtures/modeldial/` 下由 ModelDial 数据派生的测试 fixture 依 CC BY 4.0 在[独立说明](fixtures/modeldial/README.md)中署名；项目源码许可证仍为 MIT。
