# 安装与排错 — Codex Native Workers

[English](INSTALLATION.md) · [选择版本](README.zh-CN.md#选择版本)

请复制 README 中的完整安装提示词。本页解释前置检查和恢复步骤，不是替代安装器，也不授权从 `master` 安装。
Preview 以不可变的 [rc1 安装合同](https://github.com/SuperDaddyV/codex-sol-luna-worker/blob/527b174df13643a38bfe29652208eaa00f63fbf7/NATIVE_WORKERS_PREVIEW.md)为准；Stable 使用 README 中单独锁定的 assisted/setup 合同。

## 1. 只选一个目标版本

| 当前情况 | 应该怎么做 |
| --- | --- |
| 新用户，希望自选主脑，同时使用 Sol 和 Luna 子代理 | 使用 **v4.2.0-rc1 Preview** 提示词，并接受已披露的限制。 |
| 已安装 v4.1.4，希望增加 Sol 子代理 | 只运行 Preview 提示词，升级现有安装。 |
| 希望使用旧版 Sol 主控／Luna worker 方案 | 使用 **v4.1.4 Stable** 提示词。它只有 5 个 Luna 档位，没有 Sol 子代理档位，也没有新版三个 Skills 的流程。 |
| 已安装 rc1 | 本次文档更新无需重新安装；有疑问时检查状态即可。 |

GitHub 的 **Latest** 指 Stable；rc1 是已发布的预览版。Source code ZIP 不是一键安装包。
首次安装不要把两个提示词都运行一遍，不要手工复制托管文件，也不要自动降级已有的新版本。

## 2. 在 Codex 实际使用的环境中检查

让本地 Codex 任务在它自己的 shell 中执行以下只读检查。在另一个终端、Windows 用户或 WSL 环境中通过，不代表当前任务已经就绪。

```text
codex --version
git --version
python -c "import sys, tomllib; assert sys.version_info >= (3, 11); print(sys.version)"
```

- `codex` 和 Git 必须可执行。仅安装 Desktop，不能证明当前任务的 PATH 能找到 CLI。缺少 CLI 时参考 [Codex 官方安装说明](https://learn.chatgpt.com/docs/codex/cli)；安装依赖或持久修改环境需要授权。
- **必须检查名为 `python` 的命令。** 已发布的 policy／Skill 选择器命令固定使用它。仅有 `py`、`python3`、只在另一个终端生效的 alias，或用其他解释器启动安装器，都不够。apply 前必须确认当前环境的 `python` 为 3.11+ 且能导入 `tomllib`。不要通过修改已安装的托管命令掩盖这个问题。
- 本地客户端必须支持[原生 custom agents 和 subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)。通过 Codex 正常界面或 CLI 登录；本项目不提供模型权限或额度。Preview 需要 `gpt-5.6-sol`、`gpt-5.6-luna` 各自的 `low`、`medium`、`high`、`xhigh`、`max` 五档。CLI／模型预检不等于原生 worker 已运行。
- 任务需要通过 HTTPS 访问 GitHub，核验 Release 和源码；首次 Daily 选择还需要 ModelDial 的公开数据。基准网站可访问和账号有模型权限是两回事。不要为了通过检查更改代理、证书信任、凭据或组织策略。
- 写入前确认实际客户端使用的绝对 `CODEX_HOME` 和用户 Skill 根目录。通常为 `<HOME>/.codex` 与 `<HOME>/.agents/skills`；自定义 `CODEX_HOME` 必须显式处理。升级时沿用现有 manifest 记录的 Skill 根目录，不要装进临时 checkout 或其他用户目录。WSL 应按独立 Linux 环境处理。

本项目不承诺一个通用的 Desktop 最低版本，也不声称所有平台都完成原生运行验证。角色加载失败时，应记录实际客户端版本和错误。

## 3. 安装一次，分阶段确认

把所选 README 提示词复制到能执行本地 shell、且获准修改本项目用户级文件的 Codex 任务中。任务应核验已发布 Release，取得锁定 commit 的干净 detached 源码，检查 dry-run，再执行事务安装并保留精确备份位置。纯网页聊天不能完成这些本地写入；系统依赖修复是另一项操作。

合同中带 `<CODEX_HOME>`、`<SKILLS_ROOT>` 等名称的命令是模板。Codex 必须替换为核验后的绝对路径，并按实际 shell 正确引用，尤其是含空格的路径；不要把占位符原样执行。

Preview 管理 Global AGENTS 托管块、归它所有的 Codex agent 配置、10 个角色文件、2 个选择器文件、3 个 Skills 及 manifest。它保留无关用户内容，不需要修改业务项目代码。dry-run、apply 和恢复都要显式使用同一组根目录；备份路径保留在本地。

| 检查点 | 证据及含义 |
| --- | --- |
| 源码身份 | 已发布 `v4.2.0-rc1`，tag 解析为 `527b174df13643a38bfe29652208eaa00f63fbf7`，checkout 干净且 detached，并再次核对远端 tag。后续文档 commit 不是这个 runtime 的源码。 |
| dry-run／apply | 变更路径符合预期，事务及备份验证完整。冲突应在覆盖前阻断安装。 |
| 安装身份 | 版本／source 正确，12 个 payload、3 个 Skills 与托管块完整；第二次匹配的 apply 为 `IDEMPOTENT_PASS`，不写文件、不新增备份。 |
| 只读状态 | 请求“检查 Sol/Luna 状态”。Preview 通常显示 `Status Healthy`、`Agents 10/10 Ready`、`Skills 3/3 Ready`、`leaf_config Ready`，这些都是配置结果。Stable 只有 5 个 Luna agent，状态结构不同。 |
| 首次有价值的委派 | 宿主尚未加载角色时，重载并新开任务。按已安装的 `sol-luna-delegate` 选择一次并复用结果，检查直属 Sol／Luna 的有用产出，由 Coordinator 复核。 |

刚装完出现 `Today Selection not initialized` 可以是正常情况。状态 Skill 只读，不拉取数据，也不初始化选择；首次值得执行的委派才初始化 Daily 状态。选择缺失／无效或角色不可用时，由 Coordinator 保留工作并说明原因，不要重复调用选择器或猜测角色来凑验收通过。

diagnostic schema 4 有意把原生委派、工具隔离、调用防护和最大并发显示为 `Not checked`，因为状态读取器没有运行这些测试。实际运行证据应单独记录在任务结果中。单个 worker 成功、一行 receipt，或旧版只测 Luna 的 smoke，都不能证明 Preview 两个 worker 家族已验收。

## 4. 常见问题与下一步

| 现象 | 下一步 |
| --- | --- |
| 找不到 `codex`／无法运行 | 在同一任务环境中检查命令定位；按官方安装说明或经明确授权修复 PATH，然后重查失败项。 |
| 找不到 `python`、版本不符或缺少 `tomllib` | 经授权使当前环境中真正的 `python` 命令可用。只验证 `python3`／`py` 不能解决此问题。 |
| 角色／模型／effort 不支持 | 核对账号权限和精确客户端错误；安装后需要时重载。工作暂由 Coordinator 执行，不静默换家族或覆盖已选档位。 |
| GitHub 或 ModelDial 不可访问 | 保留简短错误，访问恢复后再试。首次使用可能没有可复用的有效选择；不要关闭 HTTPS 校验或伪造数据。 |
| `OWNERSHIP_CONFLICT`、hash 不符或 TOML 无效 | 停止并在本地检查报错文件。不要删除 manifest、改 hash 或覆盖用户内容；同版本重装不能修复所有权冲突。 |
| 非空 `AGENTS.override.md`，或用户已有 agent 配置／同名文件冲突 | 这是安装器有意阻断。先确定如何保留、协调用户配置，再继续；不要自动删除。 |
| Skill 根目录不匹配 | 沿用现有 manifest 的绝对 Skill 根目录；无法与实际客户端对应时停止，不要把升级重定向到另一个 home。 |
| 配置健康，但当前任务找不到角色／Skills | 确认任务使用刚检查的根目录，重载客户端并新开任务。源码 checkout 或 `.var` 副本不是已安装权威来源。 |
| 只看到 Luna | 先看版本：Stable 不安装 Sol 子代理。Preview 也可能因任务适合 Luna 而只用 Luna；状态健康、模型可用都不意味着必须用 Sol。 |
| 没有 worker | 小任务或没有独立边界的工作由 Coordinator 执行。验证两个家族时，可明确要求有价值且互相独立的 Sol 诊断与 Luna 检查。 |
| worker 能看到委派工具 | rc1 不支持强递归隔离保证。工具可见不等于嵌套调用成功；不要声称或依赖宿主隔离。 |

求助时提供渠道／版本、OS、Codex／Python 版本、失败检查点、简短错误和复现步骤。使用 [Bug Report](https://github.com/SuperDaddyV/codex-sol-luna-worker/issues/new?template=bug-report.yml) 或 [Compatibility Report](https://github.com/SuperDaddyV/codex-sol-luna-worker/issues/new?template=compatibility-report.yml)。删除密钥、账号信息和私有路径，不要上传整个 `CODEX_HOME`。

```text
继续当前目标版本的安装。先读取最后失败的检查点，说明精确错误、可能原因和最小下一步。
保留已经核验的源码、现有安装根目录和无关用户内容。修复后只重查受影响的前置条件。
遇到所有权冲突就停止，不要为了通过而从头重装、降级、覆盖文件或修改系统设置。
```

## 5. 恢复与证据边界

只在用户要求时执行 rollback 或 uninstall。使用已核验版本的安装器；回滚使用该次安装返回的精确事务备份，恢复使用同一组显式根目录。Preview 恢复必须提供两个根目录，不接受 `--source-commit`；Stable 使用其 setup 合同中的单根目录命令。成功回滚会消耗该备份。两种流程都会验证所有权并保留无关内容。遵循对应不可变版本合同，不要随意换源码压缩包、手动删除角色或移除 manifest 来重置所有权。恢复后重载客户端。

[rc1 验证记录](https://github.com/SuperDaddyV/codex-sol-luna-worker/releases/download/v4.2.0-rc1/native-workers-rc1-validation.json)包含 Windows、Ubuntu、macOS 源码 CI 和一组 Windows 已安装／原生运行场景。发布时每个平台发现 430 项测试：Windows 全部通过；Ubuntu／macOS 跳过 13 项 Windows junction 测试，其余通过。这不等于所有平台都完成原生安装验收，也不是用户安装成功率统计。强递归隔离、六 worker 容量、实际账单／额度节省仍不受支持或未验证；各项检查见[运行证据](RUNTIME_TESTS.md)。
