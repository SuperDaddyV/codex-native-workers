# 安装与排错

[English](INSTALLATION.md) · [返回首页](README.md)

**v4.3.1 · GPT-6。** 先复制[首页提示词](README.md#安装或升级)，再执行经核验发布 commit 中的 [NATIVE_WORKERS_SETUP.md](NATIVE_WORKERS_SETUP.md)。

## 先认准环境

| 环境 | 检查方式 |
| --- | --- |
| Windows 桌面端 | 在桌面端本地任务中使用 PowerShell、`python` 和 Git，无需另装 CLI。 |
| Windows CLI | 使用实际运行 Codex 的 PowerShell；另查 `codex --version`。 |
| macOS 桌面端 | 在桌面端本地任务中使用 `python3` 和 Git；应用与终端的 PATH 可能不同。 |
| macOS CLI | 使用实际运行 Codex 的终端，检查 `python3`、Git 和 `codex --version`。 |
| Linux／WSL／远程主机 | 安装在任务实际执行的主机；WSL 与 Windows 的目录、依赖和登录分别核对。 |

Python 要求 3.11+ 并包含 `tomllib`。在当前任务环境验证 Skill 真正调用的命令：

```text
Windows: python -c "import sys, tomllib; assert sys.version_info >= (3, 11); print(sys.version)"
macOS/Linux: python3 -c "import sys, tomllib; assert sys.version_info >= (3, 11); print(sys.version)"
所有环境: git --version
仅 CLI: codex --version
```

`py` 可辅助诊断 Windows 安装，但不能证明 `python` 可用。macOS 无需额外配置 `python` 别名。桌面端与 CLI 的角色加载也须分别验证。[官方子代理说明](https://learn.chatgpt.com/docs/agent-configuration/subagents)

## 安装步骤

1. 核验正式 Release、不可变 tag 和精确 commit，不从可变分支直接安装。
2. 确认真实 `CODEX_HOME` 与 `<SKILLS_ROOT>`；升级沿用 manifest 记录的根目录。
3. 收集依赖与网络问题，先处理可恢复项，再检查 dry-run 的实际变更。
4. 事务安装、备份、核对 hash。重复执行应为 `IDEMPOTENT_PASS`，零写入、零新增备份。
5. 重载客户端，分别验证安装完整性与真实 Sol/Luna 工作；保留主模型、无关内容和旧缓存。

默认根目录为用户目录下的 `.codex` 与 `.agents/skills`，但不能覆盖实际环境或已有 manifest。路径必须按对应 shell 正确加引号。安装器通过 `--source-commit` 记录来源；Source code 压缩包不是一键安装器。

## 失败后让 Codex 继续处理

在同一个任务中发送：

```text
继续安装。读取失败点，主动检查当前客户端、Python、Git、根目录、权限和网络。
在已有授权内定位已安装程序、修正当前任务的命令和引号、重新获取失败的临时下载，修复后只重查受影响步骤。
新增依赖、永久 PATH 修改、登录或重启需要我操作时，说明确切动作与原因；能执行且已获授权的直接执行。
不要反复重装、覆盖所有权冲突、关闭 TLS 校验或修改代理/证书来强行通过。
继续到安装与运行分别验证；确实受阻时说明已尝试的方法、一个最小操作和续接提示词。
```

Codex 可运行 `scripts/install_assist.py check/plan/report`。桌面端传 `--client desktop`，CLI 传 `--client cli`，同时指定真实 `--codex-home`。`recover` 只执行经核对且已授权的修复方案并复查。[详细命令](NATIVE_WORKERS_SETUP.md#assistance-and-recovery)

| 问题 | Codex 应如何处理 |
| --- | --- |
| Python／Git 缺失 | 先定位已有安装、核对应用 PATH；确实缺失时准备官方安装方案，获授权后执行并验证。 |
| 桌面端找不到 `codex` | 使用 Desktop 流程，不仅因此要求另装 CLI。 |
| GitHub 连接／下载失败 | 保留有效源码与安装，有限重试；区分网络、认证、证书和身份校验问题。 |
| ModelDial 连接重置／归档 404／hash 不符 | 优先合格缓存，再按明确的基础模式选择宿主可用角色；不得拼接批次或伪称雷达优化。 |
| `OWNERSHIP_CONFLICT`／manifest、TOML 或 hash 错误 | 检查具体冲突，提出可审阅修复；保留用户内容，不删 manifest、不改 hash。 |
| `AGENTS.override.md`／同名角色冲突 | 说明具体阻断并协调已有指令，不自动删除。 |
| Skill 根目录不符 | 核对 manifest 与实际客户端，不转移到另一个 home 强装。 |
| 角色未加载／仍是旧模型 | 核验安装身份后完整退出并重启相应客户端，必要时新开任务。 |
| 只有 Luna／没有 worker | 先判断任务是否值得委派，不强行创建子代理。 |

临时 PATH 修复后，还须验证正常启动的客户端能调用依赖；否则说明重启或持久修复待完成，不能宣布成功。

## 如何判断成功

- **安装完成：** 角色 10/10、Skills 3/3、所有权与配置校验通过，备份已记录。
- **运行验证通过：** 实际宿主加载 GPT-6 角色，两家族完成有用工作，主代理复核结果。注明实时、缓存或基础模式；基础模式通过不代表实时雷达已通过。
- **未验证：** 保留 `Not checked`／`NOT RUN`；`Today Selection not initialized` 是首次选档前的正常状态。

三平台自动化测试不等于所有客户端的原生验收，也不是用户安装成功率统计。[验证记录](RUNTIME_TESTS.md)单独列出覆盖范围。强递归隔离、六 worker 容量和额度节省不作保证。

基础模式会显示 `Degraded` 和 `BASIC_ROUTING_ACTIVE` 原因，档位按任务选择。应查看具体原因；配置错误、原生角色不可用仍需处理，基础模式不会隐藏这些问题。

## 回滚、卸载与反馈

要求 Codex 使用精确事务备份回滚，或按同一版本合同卸载，并指定原有两个根目录。恢复不接受 `--source-commit`；成功回滚会消耗备份。不要手动删除角色、Skills 或 manifest。

[报告问题](https://github.com/SuperDaddyV/codex-native-workers/issues/new?template=bug-report.yml)时提供系统、客户端、版本、简短错误、已尝试步骤和失败点。勿上传凭据、私人路径或整个 `CODEX_HOME`。[历史版本](VERSIONS.md)
