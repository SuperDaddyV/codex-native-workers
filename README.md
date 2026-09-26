# Codex Native Workers

让 Codex 按任务分工：你选择主代理，GPT-6 Sol 处理较难的子任务，GPT-6 Luna 处理清晰、重复的工作。

[English](README.en.md) · [安装与排错](INSTALLATION.zh-CN.md) · [更新记录](CHANGELOG.md) · [反馈问题](https://github.com/SuperDaddyV/codex-native-workers/issues/new/choose)

[![Validation](https://github.com/SuperDaddyV/codex-native-workers/actions/workflows/validate.yml/badge.svg?branch=master)](https://github.com/SuperDaddyV/codex-native-workers/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/SuperDaddyV/codex-native-workers)](LICENSE)

> **v4.3.0 · GPT-6** — [正式版](https://github.com/SuperDaddyV/codex-native-workers/releases/tag/v4.3.0) · [历史版本](VERSIONS.md)

## 有什么用

| 分工 | 负责什么 |
| --- | --- |
| 主代理（Coordinator） | 理解需求、拆分任务、整合结果、最终验收；主模型由你选择，Astra 是一种选择。 |
| GPT-6 Sol | 范围明确但较难的诊断、实现和跨模块工作。 |
| GPT-6 Luna | 清楚的修改、资料整理、定向检查和重复工作。 |

小任务直接完成，不会为了分工而强行调用子代理。复杂任务通常使用 0–3 个 worker；可以独立进行的工作才并行。Sol 没有固定配额。

优先用经过校验的 ModelDial 数据选档，其次用合格缓存；都没有时进入基础模式，由主代理按任务难度选择可用角色，并明确提示「未采用雷达优化」。不固定 Sol 默认档位。主代理会复核结果；分数和参考成本不代表你本机的表现，也不保证节省额度。

安装内容：10 个 worker 档位、3 个 Skills，以及不超过 2 KiB 的全局规则。保留你的主模型设置、无关配置和旧缓存，提供事务备份、回滚与卸载。

## 安装或升级

适用于 **Windows／macOS 的 Codex 桌面端与 Codex CLI**；Linux 也有自动化测试。需要能执行本地命令的 Codex 任务、Python 3.11+、Git，以及相应模型权限。桌面端安装无需额外安装 CLI；Windows 使用 `python`，macOS／Linux 使用 `python3`。WSL、远程主机和本机分别安装。

在你准备使用的 Codex 环境中新开本地任务，复制：

```text
请为当前 Codex 环境安装或升级 Codex Native Workers v4.3.0。
先核验 https://api.github.com/repos/SuperDaddyV/codex-native-workers/releases/tags/v4.3.0
确为已发布正式版，锁定不可变 tag 的精确 commit，读取该 commit 的 NATIVE_WORKERS_SETUP.md 并执行。
识别 Windows/macOS/Linux、桌面端或 CLI、真实 CODEX_HOME 和用户 Skill 根目录。
先诊断依赖、网络、权限和现有安装；在安装授权范围内主动修复，复查后继续，不要只列问题。
新增系统依赖、永久环境修改或需我登录时，说明具体动作及原因；已有授权不要重复确认。
保留我的主模型、无关文件和旧状态，先 dry-run，再事务安装；不得绕过源码或所有权校验。
按已安装 Skills 分别检查安装状态和真实子代理运行。失败时给出已尝试的方法、最小下一步和续接提示词。
```

同一个提示词适用于新装和升级。安装中遇到问题，让同一任务继续排查即可，不要手动覆盖配置。[详细步骤与恢复方法](INSTALLATION.zh-CN.md) · [安装执行合同](NATIVE_WORKERS_SETUP.md)

## 日常怎么用

继续像平时一样向 Codex 提需求。它会判断是否值得拆分；只看到 Luna，或没有子代理，都可能是正常选择。

- **查状态：** 说「检查 Sol/Luna 状态」，调用 `sol-luna-status`。
- **升级：** 说「升级 Codex Native Workers」，调用 `sol-luna-upgrade`。
- **委派：** `sol-luna-delegate` 负责选档与有界委派，你无需记住角色名。

完成较大任务后，最后一行会简述实际分工，例如：

```text
Coordinator/Workers: delegated · sol_high ×1 · luna_high ×1 · parallel
```

具体档位每天可能不同。`parallel` 只表示该任务中确实有重叠执行。

## 如何确认生效

安装与运行分开看：

1. **安装完整：** 状态显示角色 10/10、Skills 3/3，文件与配置校验通过。
2. **运行可用：** 在实际任务中，Sol 和 Luna 各完成有用的工作，由主代理检查结果。

首次出现 `Today Selection not initialized` 表示尚未选档；`Not checked` 表示未运行相应检查。配置健康不等于运行验收通过。雷达不可用时可以进入基础模式；角色不可用或模型不匹配时由主代理接手。若角色未加载，完整退出并重启对应客户端。

## 常见问题

- **能保证更省额度吗？** 不能。它提供分工和动态选档，效果需要在你的任务上观察。
- **最多能并发多少？** 通常 0–3 个；4–6 个还取决于任务与宿主能力，六 worker 容量未验证。
- **子代理能否继续创建代理？** 项目禁止这样做，但不提供宿主强制递归隔离保证。
- **安装失败怎么办？** 先让 Codex 按[排错流程](INSTALLATION.zh-CN.md#失败后让-codex-继续处理)处理。网络、账号或系统权限问题可能需要你完成一次明确操作。
- **能恢复吗？** 可以，要求 Codex 按本次事务备份回滚，或安全卸载；不要自行删除托管文件。

## 更多信息

[历史版本](VERSIONS.md) · [架构](ARCHITECTURE.md) · [验证记录](RUNTIME_TESTS.md) · [安全边界](SECURITY.md) · [GitHub Releases](https://github.com/SuperDaddyV/codex-native-workers/releases)

反馈请提供系统、客户端、版本和简短错误，勿上传密钥、私人路径或整个 `CODEX_HOME`。[报告问题](https://github.com/SuperDaddyV/codex-native-workers/issues/new?template=bug-report.yml) · [兼容性反馈](https://github.com/SuperDaddyV/codex-native-workers/issues/new?template=compatibility-report.yml) · [功能建议](https://github.com/SuperDaddyV/codex-native-workers/issues/new?template=feature-feedback.yml)

独立社区项目，与 OpenAI、ModelDial 无隶属或背书关系。[MIT License](LICENSE)；ModelDial 数据依 [CC BY 4.0](https://modeldial.com/data-license) 使用，测试数据说明见 [fixtures](fixtures/modeldial/README.md)。
