# GPT-6 v4.3.0 cross-client release checkpoint — 2026-09-26

v4.3.0 remains an unpublished candidate. The user authorized publication after
acceptance and requested reliable Windows/macOS, CLI/Desktop setup with active
recovery. This checkpoint preserves the earlier evidence below; it does not turn
configuration, mocked preflight or CI into native execution proof.

- **PASS — source and fake-home:** 472 standard-library tests in 103.983 seconds.
  Six new tests cover the Windows/macOS/Linux and CLI/Desktop preflight matrix,
  missing dependencies, source verification, recovery-plan client identity,
  Desktop's separate native gate, and actual-shell execution of rendered commands
  with spaces, dollar signs, backticks and apostrophes in paths. Windows uses
  `python`; macOS/Linux use `python3`. Desktop setup requires no separate CLI.
- **PASS — public documentation:** both homepages are 84 lines; both installation
  guides are 78 lines. Six current documents passed GitHub Markdown rendering;
  navigation, immutable historical links, privacy checks and issue-form YAML
  parsing passed. Rendering is not a native installation test.
- **PASS — prior exact candidate CI and real installation:** repair commit
  `3a42719448a2320ee9ccd5ec30f5738e3e2eba1f` passed
  [Windows, Ubuntu and macOS CI](https://github.com/SuperDaddyV/codex-native-workers/actions/runs/35988146575).
  Its transaction changed six managed files; a matching repeat wrote nothing and
  created no backup. All 15 owned payload hashes passed; ten preserved files kept
  their hashes and timestamps. These results identify that commit only.
- **BLOCKED — installed native selection:** the one installed selection at
  2026-09-26 17:40:39 Beijing time returned both families unavailable. API and index
  were reachable, but the indexed exact archive for batch
  `evaluation-e4d046fe829a446b0ab74f613b34735d643c3cfbd294a1a73940071377e16645`
  returned HTTP 404. The latest alias named a different batch and was rejected.
  No archive substitution, state import or native child was used.
- **NOT RUN at this pre-commit checkpoint:** exact-commit CI and real installation
  of the cross-client changes. Record their final commit, checks and installation
  receipt in the candidate pull request. Useful native GPT-6 Sol/Luna work remains
  blocked by data selection; Stable publication depends on that acceptance.

Local evidence is under `.var/v430-release-20260926/`, including the full test log,
rendered-document hashes, transactional receipts and sanitized acquisition results.
Do not publish raw local receipts containing private paths. macOS/CLI/Desktop
end-user native installation coverage and an installation success rate have not
been measured. Host isolation and maximum capacity retain their historical limits.

---

# GPT-6 v4.3.0 local publication-verification repair — 2026-09-24

This is uncommitted repository work on top of candidate
`937957768f31b8bcc487fc3080df5348f233f4a4`. It does not update real CODEX_HOME,
installed Skills or Global instructions. No commit, tag, push or publication was
performed. The earlier candidate evidence remains unchanged and is not evidence
for this repaired tree.

The independently reproduced API/archive score mismatch and unverified Sol-axis
findings are repaired. Backend identity, score, scale and selection latency must
match the exact hashed full archive. Frontend, reasoning and general each require
their exact benchmark-index record, archive hash and matching selection inputs.
An invalid source disables that view and dependent general selection; it cannot
be rescued as quality-only. Malformed axis-source objects also leave independently
verified backend/Luna selection available. Missing comparable costs alone still
permits quality-only after score verification.

Active state uses `gpt6-v4` with publication verification version 1. Earlier
`gpt6-v3` files are preserved and rejected as fallback, including copies moved
into the new namespace. Offline Worker inputs must supply the same indexed
publication bundle as the network path. The daily selection algorithm, ten native
profiles, strict installation inventory and Global byte budget are unchanged.

Current results:

- **PASS — source and fake-home:** 17 targeted publication-binding regressions;
  final full standard-library suite, 466 tests in 103.822 seconds. Coverage includes
  corruption and missing-archive rejection, family/view independence, old-cache
  rejection, verified fallback, repeat zero-write, installation lifecycle,
  preservation, exact rollback, Skill validation and public documentation.
- **PASS — downloaded public archive replay:** the seven public JSON documents
  acquired earlier in this task passed the repaired verification pipeline in
  isolated repository state. Backend batch
  `evaluation-fe161e59016664151e0e4e38607a0213e6aa42b91b2edab9cc7f7badd75fa786`,
  digest `sha256:a717dd9b66a0cb825cd83348ae364bf425880894d17ca4c2c1d5cb9f69c628c8`;
  overall batch `overall-bf7f1c53d2c0a20d465133da`, digest
  `sha256:df5d447738beb20460a27662370a7f6e037001b5f0d66c92ca73e8a6e0737924`.
  Luna selected xhigh quality-only; all four Sol views selected xhigh, backend
  cost-optimized and the other three quality-only. No fallback was used. This is
  reference-data evidence, not local billing, installed or native execution.
- **BLOCKED — latest live acquisition:** at 2026-09-24 10:24:39 UTC, the first
  ModelDial API request failed with `URLError` / `WinError 10054` (connection reset).
  A fresh isolated state correctly reported both families unavailable. The final
  seven-request live pipeline therefore did not complete; archive replay and
  mocked transport tests do not turn this into a live PASS.
- **NOT RUN — repaired-candidate exact-commit CI, real-home installation and
  native GPT-6 worker acceptance.** Earlier candidate CI and installed evidence
  cannot be reused as exact evidence for these uncommitted repairs.

Commands: `python -X utf8 -B -m unittest discover -s tests -p test_publication_binding.py -q`
and `python -X utf8 -B -m unittest discover -s tests -q`. Ignored local evidence is
under `.var/v430-integrity-repair/`: `full-tests-final.log`,
`archive-replay-validation.json` (input and source hashes), and
`live-20260924T102439Z/validation.json` (raw transport failure).
Data source: [ModelDial Radar](https://modeldial.com/radar),
[backend index](https://modeldial.com/api/v1/radar/index.json) and
[benchmark index](https://modeldial.com/data/benchmark-snapshots/index.json),
[CC BY 4.0](https://modeldial.com/data-license). New test bundles are synthetic,
not measured model results. Historical records below retain their original scope.

---

# GPT-6 v4.3.0 acceptance candidate — 2026-09-24

User requested a stop before final Stable publication for acceptance. No new
Release or tag has been created. Initial installed runtime was v4.2.0-rc1 on
Desktop 0.155.0-alpha.16; PATH CLI was separately 0.146.0. The active task initially
advertised only GPT-5.6 custom roles, so initial preparation was Coordinator-owned.
At the resumed pre-commit checkpoint the host advertises GPT-6 custom roles, but
native execution has not yet run. Final installed/native/CI results belong to the
separate exact-commit candidate evidence; historical results below keep their labels.

Official sources rechecked: [GPT-6 Sol](https://developers.openai.com/api/docs/models/gpt-6-sol),
[GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna),
[model migration](https://developers.openai.com/api/docs/guides/latest-model),
[Codex custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents).
Model/effort availability in a catalogue is not proof of custom-agent loading.

ModelDial [Radar](https://modeldial.com/radar), [OpenAPI contract](https://modeldial.com/openapi-v1.json),
[publication index](https://modeldial.com/api/v1/radar/index.json) and
[data licence](https://modeldial.com/data-license) were checked. The API carried
all five GPT-6 efforts for each family. The exact indexed full archive returned
404; its older latest alias was not joined to the API. The final transport rejects
all live choices unless the exact indexed full archive passes its content hash;
only a qualified GPT-6 cache may then supply fallback. Full JSON content hashes are
recomputed using the publisher's [canonical algorithm](https://github.com/tianwdong/modeldial/blob/062dd79ab3894db9a419f35b63b64d3cd10f7376/scanner/reference_snapshot.py#L575).
It was independently reproduced against a downloaded public full snapshot.
Data source: ModelDial Radar, CC BY 4.0; synthetic regression fixtures are modified
artificial data, not measured GPT-6 evidence or endorsement.

A fresh source-only fetch on 2026-09-24 matched the current index and complete
archive (batch evaluation-90c639ed7259e54f2e9e3a079b861db79f8deb6fdc3deec371e29050818afafd).
It selected Luna/xhigh and Sol/xhigh in all four views. Sol backend had complete
matching reference cost coverage; other views and Luna were quality-only. No LKG
fallback was used. This supersedes the earlier 404 only for this later fetch.
It is public reference selection, not native execution or local billing evidence.

Local source regression after strict archive acquisition and cache integrity changes:
448 standard-library tests PASS in 100.895 seconds, including fresh/rc1/Stable
upgrade, cross-generation rejection, qualified fallback, idempotence, preservation,
conflict zero-write and exact rollback gates. Exact-commit CI and installed/native
results are recorded separately after they actually complete. Earlier PASS values
below are historical.

---

# Native Runtime Test Protocol

Status: `v4.2.0 — CURRENT STABLE TARGET`; installation requires its published Stable Release. Earlier records below retain their original versions and scope.

These results describe only the recorded environments and scenarios below. They do not imply runtime validation across every operating system, Codex client, account, or user environment.

## v4.2.0 Stable promotion — 2026-09-19

The user explicitly requested formal publication and the previously agreed
repository rename to `SuperDaddyV/codex-native-workers`. The supported product
remains native configuration, bounded routing and transactional installation.
All rc1 host limitations remain: Sol tool-visibility FAIL, nested invocation not
verified, six-worker capacity not run, and no measured local savings. Formal
publication is not a claim that these failures or unrun checks passed.

The Stable source keeps rc1 worker definitions, selector algorithms and Global
policy. Version/User-Agent metadata and the upgrade Skill's canonical repository
endpoint change. Assistance now verifies the literal `python` command, and the
schema-4 compatibility report calls its limited result core product compatibility.
Reused rc1 native evidence remains explicitly rc1 evidence;
source and fake-home checks cannot become new installed/native claims. The
sanitized Stable Release validation record binds final checks to one exact commit.

Historical release-time status: `v4.1.4 — CURRENT STABLE RELEASE / DEFAULT INSTALLATION TARGET` described the v4.1.4 publication only; it is now the previous Stable baseline.

## v4.2.0-rc1 preview acceptance contract — approved 2026-09-19

The user approved narrowing this preview to native profile/routing/install
support. Historical local.2 leaf isolation failures remain FAIL. Strong recursive
isolation is unsupported. The separate historical protocol below is preserved;
its blanket stop on tool exposure does not govern independent core checks under
this new contract. Stable v4.1.4 and its immutable evidence remain unchanged.

Required preview gates:

1. Source regressions, three Skill validators, Global managed policy <=2,048 UTF-8
   bytes, strict manifest inventories, installation/upgrade/rollback integrity.
2. Exact published-source identity for install, owned hashes, preserved unrelated
   user content and Coordinator settings, second-apply idempotence.
3. One valid installed Worker selection per delegation workflow; current Beijing
   date, explicit benchmark identity and reference-only/quality-only limits.
4. Fresh direct Sol and Luna children with verified model/effort, useful independent
   outputs, actual overlap for a mixed task, and Coordinator review/integration.
5. Small work remains direct; task-specific selection adjustments obey allowed
   roles; read-only status never initializes profiles or probes native behavior.

Report host capabilities separately: configuration request, child-observed tool
visibility, actual invocation enforcement, observed overlap and maximum capacity.
`Not checked`, unknown or configuration Ready cannot become a native PASS. A known
tool-visibility failure does not stop unrelated core checks, but any unexpected
worker delegation, wrong model/effort, unsafe write or ownership drift stops the
affected check. No nested invocation is required to publish this limited preview.
Six-child capacity/overflow and comparative quota/cost remain unclaimed unless
separately demonstrated. Source CI is never native-runtime proof.

### rc1 source validation — 2026-09-19 (before publication)

The working-tree standard-library suite passed **430 tests in 116.342 seconds**.
Three Skill validators passed in Python UTF-8 mode. The rendered Global managed
block is **2,044 UTF-8 bytes**, including markers and final newline. Focused
documentation/policy checks passed after final wording corrections. These are
source and fake-home checks, not installed-runtime acceptance.

Three direct native workers overlapped during this implementation: two Sol/max
workers handled diagnostics and bilingual documentation; one Luna/max worker
handled bounded policy/Skill edits. Parent-visible session metadata confirmed
the requested model/effort and direct depth-1 parentage. Their writes had disjoint
ownership and the Coordinator reviewed the results. These workers used the
pre-rc1 installed role definitions; this is observed three-worker overlap, not
an rc1 installation test or proof of the configured six-worker maximum.

The first rc1 candidate CI passed on Windows but failed two historical ownership
tests on Ubuntu/macOS: their stale text replacement made no change, while Windows
newline rewriting accidentally supplied the expected corruption. The fixtures
now mutate one byte inside the owned block without changing line endings and
assert that bytes changed. Installer rejection and no-write assertions remain.
No installer enforcement was relaxed; the failed CI run remains historical.

An authorized unpublished-candidate transaction installed rc1 with six owned
changes and a verified backup. Twelve payloads and three rendered Skills matched
source and manifest. Nonmanaged user content, daily state and unrelated Skills
were unchanged. A single read-only status call returned schema 4 Healthy,
10/10 agents and 3/3 Skills; all four native capability fields stayed Not checked.
The final Release evidence binds this payload to the final tested source commit.

After that installation, fresh direct Sol/max and Luna/max workers overlapped:
Sol checked source/manifest/installed identity; Luna repaired the two ownership
fixtures. Parent-visible metadata confirmed gpt-5.6-sol/max and gpt-5.6-luna/max,
both at depth 1. The Coordinator reviewed the audit and fixture changes. Sol
again reported six collaboration tools present. Luna reported those collaboration
definitions absent but a task-messaging tool present. Neither invoked delegation;
neither observation establishes a host-wide invocation guard or strict isolation.

Post-commit CI and installation/native acceptance are recorded in the sanitized
Release evidence for the exact published commit. This section does not claim
those later steps have already run.

### Updated-host observation — 2026-09-19 (before rc1 installation)

Desktop's running binary reports **0.155.0-alpha.9.2**, updated from the earlier
0.154.0-alpha.6.2. Two newly created children have parent-visible direct depth-1
metadata: Sol/max and Luna/max, multi-agent v2. Both ran concurrently and returned
useful results. Twelve installed payload hashes matched source/manifest; all
three Skill ownership hashes matched. The policy payload was byte-identical to
its source template. No child invoked collaboration tools.

**FAIL (tool absence):** Sol explicitly reported spawn_agent, followup_task,
send_message, interrupt_agent, list_agents and wait_agent. **UNKNOWN (Luna):** the
follow-up report said definitions were not provided and marked its observation
unknown. Do not infer either an invocation bypass or successful invocation guard.
**NOT RUN:** nested calls, six-worker capacity and overflow. Issue 45066 remained
open without comments at this check. This observation belongs to local.2, not an
rc1 install. During the window the whole user configuration hash changed; its
owned agents block still matched the manifest. No whole-config immutability claim
is made; the checking workflow did not modify that configuration.

## Upstream submission — 2026-09-13

The user authorized publishing the sanitized report to the official tracker:
[openai/codex issue 45066](https://github.com/openai/codex/issues/45066).
Creation succeeded; a separate read verified the exact submitted title/body and
open state. The report distinguishes child-observed visibility from a server-side
tool registry and does not claim successful nested execution. Private paths,
session identifiers, credentials and raw session attachments were excluded.
The earlier draft is retained below as historical evidence. Native leaf FAIL,
root-cause BLOCKED and downstream NOT RUN are unchanged by submission.

## Documentation repair — 2026-09-12

The user approved redacting the private backup path in PLANS.md. The public
record now uses a portable placeholder; original documents and exact recovery
information remain in ignored local evidence, and the backup still exists.
All four repository-safety tests PASS; the full standard-library suite passes
**423 tests in 101.355 seconds**. Final evidence-text edits receive another focused
repository check and diff validation before delivery. The earlier failed run
below remains a truthful historical result, rather than current acceptance.

This documentation repair does not change native leaf FAIL or root-cause BLOCKED.
No new native children, nested calls, capacity checks or runtime/configuration
changes occurred. The upstream report remains a draft and has not been submitted.

## Local.2 installed acceptance — 2026-09-12

The explicitly approved real local installation completed: `UPGRADED` to
`v4.2.0-local.2`, manifest schema 3. Source regression passed 423 tests; installed
ownership verified twelve source-identical files and three rendered Skills.
Global non-managed bytes, configured Astra/high and legacy Daily/LKG hashes were
preserved. The managed Global block is 1,882 bytes including its final newline.

The installed selector initialized the new Worker profile from current public
reference data: Luna max; Sol general max, backend xhigh, frontend high and
reasoning max. Both families report `cloudflare-reference/custom_endpoint` and
`reference_only`. Missing same-batch complete data leaves every Sol view in
`quality_only` mode. No local performance, billing or quota advantage is proven.

The read-only installed status reports `Healthy` / `OK`, agents 10/10, Skills
3/3 and native-leaf configuration `Ready`. It reports native runtime and actual
capacity `Not checked`; configured `max_parallel=6` is not observed concurrency.
The backup remains available; see `PLANS.md` for the installation record.

## Historical upstream report draft — before submission

**Title:** Custom Sol/Luna child agents report collaboration tools despite
agents.enabled=false on Desktop host 0.154.0-alpha.6.2 (multi-agent v2)

**Environment:** Windows, Codex Desktop, bundled executable
0.154.0-alpha.6.2; child turn metadata reports multi_agent_version=v2. The
separate PATH CLI version is not the tested host.

**Observed setup and reproduction:**

1. Parent/project configuration enables agents with a six-child concurrency cap.
   Project and personal role copies are byte-identical. sol_max uses
   gpt-5.6-sol/max; luna_max uses gpt-5.6-luna/max. Each role has
   `[agents] enabled = false` and instructions prohibiting further delegation.
2. Create fresh direct children using native agent_type, without model or effort
   overrides. Assign useful bounded read-only checks and ask each to report its
   actual available tool names without invoking delegation.
3. Parent metadata verifies expected models/efforts, direct depth-1 parentage and
   v2 runtime. The children return useful check results and report collaboration
   tools still visible, including spawn_agent and followup_task.
4. Fully restart Desktop and repeat with new children. The reported exposure
   persists; process restart and fresh child identities were verified locally.

**Expected:** multi-agent tools disabled for these custom children, consistent
with the documented agents.enabled setting. See the official configuration and
subagent references in the diagnosis section below.

**Evidence limitation:** visibility is reported by the children, not a captured
server-side tool registry. No nested tool was invoked and no successful nested
spawn or invocation rejection is alleged. This could be a settings-precedence,
tool-filtering, or observation problem; a specific host defect is not proven.

**Requested maintainer check:** inspect final child agents.enabled and its layer
origin, tool definitions actually emitted to each child, and any independent
invocation guard. Compare fresh spawn and continuation under multi-agent v2.

**Impact:** local tool-absence acceptance fails; downstream six-worker capacity
acceptance was stopped, rather than weakening the criterion. Package ownership
and useful native execution succeed. No model performance or quota claim is made.

**Additional diagnostic inspection:** the host's experimental server/diagnostics
schema contains process memory information and named unsigned-integer gauges;
it exposes no typed child effective-config/tool-registry response. The agents
command is a session browser. Doctor's help advertises auth as part of its health
inspection and provides no scoped child-inspection option; it was not executed.
No feedback/upload request was sent. This draft intentionally contains no user
paths, session identifiers, credentials or raw session attachments.

**Disposition:** draft ready for review/submission; not sent externally. Native
leaf remains FAIL, exact root cause BLOCKED, nested and capacity checks NOT RUN.
Further identical local runs have no identified new evidence target.

## Post-restart native leaf check — 2026-09-12 — FAIL

User-confirmed Desktop restart was corroborated by a host process start at
23:44:52 BJT. The executable version remains 0.154.0-alpha.6.2. Installed owned
file/source/manifest checks and all three Skill ownership hashes match; selected
Sol/Luna role files still have agents.enabled=false.

The new post-restart workflow ran the installed Skill selection command exactly
once. It returned the current Beijing-date schema-2/reference-policy-1 profile:
Sol general sol_max and Luna luna_max, retaining the public reference route
cloudflare-reference/custom_endpoint. No per-child selection or override occurred.

- **PASS, bounded:** two fresh direct children (not resumed old children) ran as
  gpt-5.6-sol/max and gpt-5.6-luna/max, confirmed by parent-visible turn metadata.
  Both use multi_agent_version=v2 on the same host version and depth 1. A parent
  snapshot establishes simultaneous running. Both returned useful file checks
  and RESTART_SOL_LEAF_COMPLETE / RESTART_LUNA_LEAF_COMPLETE sentinels.
- **FAIL — Sol leaf:** the new child reports spawn_agent, followup_task,
  send_message, interrupt_agent, list_agents and wait_agent in its actual
  collaboration tool definitions.
- **FAIL — Luna leaf:** the new child reports collaboration.spawn_agent and
  collaboration.followup_task as visible. It separately reports Codex task tools;
  those are not needed to establish the native collaboration absence failure.
- Neither child invoked delegation. Tool exposure remains a child-observed,
  parent-received report, not independently captured server-side registration.
  No successful nested execution or invocation rejection is claimed.
- **NOT RUN / downstream acceptance BLOCKED:** six-worker capacity, overflow and
  remaining acceptance, stopped after the fresh Sol failure. Observed concurrency
  is at least two; the actual upper capacity remains unverified.

Restart plus fresh children did not resolve the reported exposure. This narrows
the old-process explanation but does not establish the exact filtering defect
or exclude all persistent state. Preserve the existing FAIL and obtain the host
diagnostic evidence described below before proposing configuration changes.
No global config, installation or Git mutation occurred. `git diff --check`
passes. The previously recorded full-suite failure remains; no new source change
or new test concern justified rerunning that suite for this evidence-only update.

## Leaf diagnosis — host interface evidence

This follow-up leaves the native leaf FAIL below unchanged. The Desktop binary
and both tested child session headers report `0.154.0-alpha.6.2`, with child
`multi_agent_version=v2`. The separately installed PATH CLI reports `0.146.0`;
its behavior is not evidence for this Desktop host. Recorded developer messages
contain the selected role's prohibition on further delegation, and recorded
model/effort values match; this excludes complete role-loading failure only.

Official [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
defines agents.enabled as enabling/disabling multi-agent tools. Official
[subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents)
allows normal supported configuration keys in custom-agent layers. The key and
the intended configuration mechanism are supported; actual precedence and tool
filtering for these child turns remain unobserved.

The exact running host executable exported its experimental app-server protocol
using `app-server generate-json-schema --experimental`. Local schema artifacts
are under ignored `.var/leaf-diagnostic-schema/`. Inspection found:

- ConfigReadParams: cwd and includeLayers only, no child/thread selector.
- ThreadReadParams: threadId and includeTurns; its Thread response has no typed
  effective agents configuration or complete native tool-registry field.
- ClientRequest: config/read and thread/read exist; no generic native tools/list
  or per-child effective-configuration inspection method is advertised. MCP tool
  operations do not establish the built-in collaboration tool surface.

No proxy connection or new app-server daemon was started: these documented
request shapes cannot supply the missing child-specific evidence. Session logs
also did not serialize a complete tool registry. Binary string inspection did
not establish control flow and is not used as proof of the implementation.

**BLOCKED — exact root cause:** available evidence cannot discriminate a setting
precedence issue, missing filtering, and tool advertisement with a separate
invocation guard. **NOT RUN — nested invocation:** deliberately unexercised.
Minimum host diagnostic should expose final child agents.enabled with its layer
origin, emitted native tool names and the corresponding invocation guard. Until
that evidence exists, no repair or capacity PASS is justified. No global config,
credentials, agent execution, package installation or Git publication was touched.

Documentation diff validation passes; the previously recorded full-suite failure
on the pre-existing private path remains unresolved. Tests were not rerun solely
for this additional evidence record; no source implementation changed.

## Local.2 resumed native acceptance — 2026-09-12 — FAIL

This explicitly authorized continuation supersedes the interrupted attempt's
missing-output/leaf status below, while preserving that historical attempt.
Fingerprint verification found no installed or source drift and the date remained
2026-09-12 BJT. The two original children resumed; the original single Worker
selection was reused. No new selection, model override or child was introduced.

| Gate | Result | Actual evidence and limitation |
| --- | --- | --- |
| Installed integrity and selection | PASS | Original hashes unchanged except the two evidence documents; same-day schema-2/reference-policy-1 profile reused. |
| Sol native useful output | PASS | Policy comparison returned SOL_BOUNDARY_CHECK_COMPLETE; template and installed managed block match, DiffCount=0. Resumed turn metadata: gpt-5.6-sol/max. |
| Luna native useful output | PASS | Ten names/model/effort/leaf configurations and ten source/installed hashes match; zero mismatches; LUNA_ROLE_CHECK_COMPLETE. Resumed turn metadata: gpt-5.6-luna/max. |
| Sol native leaf | FAIL | Child reports actual exposure of collaboration.spawn_agent, followup_task, send_message, interrupt_agent, list_agents and wait_agent. |
| Luna native leaf | FAIL | Child reports actual exposure of collaboration.spawn_agent and collaboration.followup_task. |
| Direct parentage and mixed overlap | PASS, bounded | Original depth-1 metadata and both-running parent snapshot; useful results now returned for disjoint read-only scopes. Overall mixed acceptance remains BLOCKED by leaf failure. |
| Status read-only behavior | PASS | One installed Skill status command: schema 3, Healthy/OK, agents 10/10, Skills 3/3, native_leaf Ready, max_parallel 6, native_runtime/runtime_max_parallel Not checked. Protected file and all four Daily/LKG JSON hashes unchanged. |
| Six Workers and overflow behavior | NOT RUN / acceptance BLOCKED | First substantive leaf failure stopped downstream native work. Host advertises seven total slots; configured Workers six; observed concurrency at least two, maximum unverified. |
| Small-task routing and permitted Sol adjustment | NOT RUN | Downstream of the failed native gate. |
| Equivalent-task benchmark and attributable cost/usage | NOT RUN | Downstream of the failed gate; no efficiency or savings claim. |

Tool exposure is evidence reported by the two children and visible to the parent
in their returned results. The parent did not independently introspect the host's
tool registry. Neither child invoked delegation, and no grandchild was created;
the captured child call records contain no collaboration calls. Therefore this
run establishes failure of the required *tool-absence* gate, not proof that a
nested spawn would execute successfully. Configuration alone cannot close it.

The Coordinator accepted the useful file checks and rejected leaf acceptance.
The Luna result's own delegated receipt is not child-count evidence; the parent
retains the observed two direct children and zero grandchildren. Status Healthy
and native_leaf Ready describe installed configuration, not native enforcement.

Minimum follow-up is a scoped diagnosis of native custom-agent tool filtering
when `agents.enabled=false`. Do not relax the tool-absence criterion, alter global
configuration, reinstall, or use nested/top-level workarounds to obtain PASS.
This run performs no such repair, credential access or Git publication operation.

### Resumed delivery validation

- `git diff --check`: PASS.
- `python -m unittest discover -s tests -q`: **FAIL**, 423 tests, 97.110 seconds,
  one failure in
  `test_no_private_paths_installation_ids_or_secret_material`. It detects the
  absolute private user backup path in PLANS.md's historical installation record,
  already present in the initial task baseline. Historical evidence was preserved;
  no test was bypassed and no unrelated cleanup was performed. All other tests
  completed without a reported failure; there were no reported skips.
- The earlier 423-test PASS is historical source/fake-home evidence and does not
  replace this current failure or establish native runtime acceptance.

## Local.2 fresh-task attempt — 2026-09-12 — BLOCKED (interrupted)

This authorized read-only native attempt was interrupted before either Worker
returned useful output. The parent subsequently observed both children as
`interrupted`. This is incomplete acceptance, not a substantive runtime FAIL.

- **PASS — installed integrity and discovery:** manifest version
  `v4.2.0-local.2`, schema 3; twelve owned files match source bytes and manifest
  hashes; three installed Skills match rendered source and ownership hashes.
  Both managed blocks pass ownership verification; Global policy is 1,882 bytes.
  All ten native roles are discoverable and their files pin the expected family,
  effort and `agents.enabled=false`. This last check is configuration evidence.
- **PASS — one installed selection:** the exact installed delegation Skill
  command ran once and reused the valid 2026-09-12 profile, schema 2/reference
  policy 1, selected at 22:59:38 BJT. Luna selected `luna_max`; Sol general
  `sol_max`, backend `sol_xhigh`, frontend `sol_high`, reasoning `sol_max`.
  Both families retain `cloudflare-reference/custom_endpoint`, `reference_only`,
  fallback false and capability_degraded false. Sol uses `quality_only`;
  reference costs and local savings are not established. Luna uses the backend
  score; Sol general uses overallScore. Source generated at 09:46:52.323 UTC.
- **PASS — native invocation, identity and direct parentage only:** parent-visible
  session metadata and turn contexts establish one `sol_max` / `gpt-5.6-sol` /
  max child and one `luna_max` / `gpt-5.6-luna` / max child, each at depth 1 under
  this Coordinator. No model or effort override was supplied. The current parent
  is `gpt-6-astra` / medium; historical Astra/high is not this task's setting.
- **PASS — two-family overlap observation only:** one parent `list_agents`
  snapshot showed both direct children `running` simultaneously. Sol was assigned
  policy-boundary synthesis; Luna was assigned ten-role inventory verification.
  Both scopes were read-only. This proves observed concurrency of at least two,
  not completed mixed-task acceptance or the maximum runtime capacity.
- **BLOCKED — useful outputs, native leaf and complete mixed acceptance:** neither
  child returned a commentary/final result before interruption. Tool absence
  cannot be inferred from TOML; native leaf enforcement remains unverified.
- **NOT RUN — six independent Workers and cap overflow:** the host advertises
  seven total slots and the installed/project configuration allows six Workers.
  Six-way overlap and rejection/queuing of a seventh Worker were not exercised.
  Small-task routing, permitted Sol role adjustment, read-only status execution,
  equivalent-task comparison and attributable usage/cost checks were not run.
- **FAIL:** no substantive failure was observed in the completed checks.
- **Preservation:** before recording this result, all 97 captured repository and
  protected installed-file/state fingerprints were unchanged, including Global
  policy/config, manifest, roles, Skills and all four Daily/LKG JSON records.
  No reinstall, global configuration mutation, credentials, Git mutation or
  publication occurred. Source/fake-home tests were not rerun in this attempt;
  the historical 423-test result remains separate evidence.

Resume the incomplete native gates in an explicitly continued acceptance run;
no implementation repair is justified by interruption alone. Preserve the
first-substantive-failure stop rule below. The protocol and handoff remain valid.

## Local.2 native acceptance protocol

The combined `v4.2.0-local.2` source candidate requires fresh evidence beyond the
historical Luna-only protocol. Run only after a separately authorized installation
of the exact reviewed payload (completed above). Do not copy authentication or mutate unrelated
configuration to make a test pass. Native checks must use the real installed
selector; a synthetic snapshot is fixture evidence, not live acceptance.

1. Verify source/installed owned hashes and all ten native role configurations,
   three Skills and manifest schema 3. Confirm user Global rules outside the
   managed block and parent model/effort are unchanged.
2. In a fresh task, read the installed delegation Skill and obtain one Worker
   profile. Record source identity, axis, freshness, route and degradation. If
   no valid Sol data/LKG exists, mark Sol-dependent tests BLOCKED; do not substitute
   a different route or force a guessed role.
3. Delegate one bounded read-only task to selected Sol and another to selected
   Luna. Parent-visible evidence must establish actual model, effort, direct
   parentage, useful output and absence of delegation tools in both children.
4. Verify a normal mixed parallel task, disjoint ownership and acceptance. Then
   use six genuinely independent read-only tasks to verify six overlapping direct
   Workers and rejection/queuing beyond the configured cap. If the host exposes a
   lower cap, report that actual value; configuration text is not a PASS.
5. Verify small work does not load the delegation Skill or run a selector merely
   for a receipt; verify a task-local permitted Sol role adjustment records the
   reason without changing the daily default. Status must stay read-only.
6. Compare representative equivalent tasks against the previous Astra/Luna setup,
   holding inputs and acceptance fixed. Report correctness, elapsed time, rework
   and available attributable usage. Missing usage does not prove quota savings.

Stop downstream native acceptance on the first substantive failure and report the
minimum repair boundary. No source test or legacy one-child smoke closes these
gates. Publishing and production use remain unapproved by this test protocol.

### Fresh-task handoff

Open a fresh task in this project so it loads the installed native role catalog.
The current task cannot hot-reload new roles or its original host agent capacity.
Copy this prompt:

```text
在 D:\codex-sol-luna-worker 执行 v4.2.0-local.2 新任务原生验收。
先读 AGENTS.md、PLANS.md 和 RUNTIME_TESTS.md 的最新安装记录，遵循实际已安装的 sol-luna-delegate Skill，保存一次真实 Worker selection。
我授权本轮进行只读原生子代理验收，以及将真实结果写入项目现有 PLANS.md、RUNTIME_TESTS.md。
核验已安装版本/所有权与实际可发现角色；用选出的原生 Sol 和 Luna 各执行有用的、范围明确的只读检查，核验模型、档位、leaf 工具边界、直接父子关系和混合并行。
容量检查仅在实际工具允许时运行六个独立只读子任务：分别核对角色配置、全局轻量策略、Skill 约束、来源验证、缓存隔离、安装回滚保护。任务边界须具体，不为凑数重复工作。记录真实重叠及容量上限；宿主仍限制三子时如实标为 BLOCKED，不通过模型覆盖、嵌套或新建顶层任务绕过限制。
比较任务基准只有在可构造等价输入与验收标准时才运行；无法归因的用量或费用标为未验证。首次实质失败后停止依赖它的验收并报告最小修复边界。
不要重新安装或修改全局配置，不读取凭据，不创建 commit/branch/tag/PR，不 push 或发布 GitHub。最终明确区分 PASS、FAIL、BLOCKED、NOT RUN。
```

## Local candidate repairs — 2026-09-07

Repository regressions cover corrupted or missing later backup payloads in
either root, invalid or duplicate restore entries, legacy single-root backup
compatibility, incomplete schema-2 Skill ownership, pre-existing empty Skill
roots and parents, and uninstall failure after the Skill phase has completed.
Diagnostic tests reject inconsistent or malformed schema-2 Skill inventories
and preserve uninitialized selection combined with installation errors.

These are source and isolated fake-home checks. See `PLANS.md` for the completed
local test results. The repairs were not applied to the real installation;
native-leaf runtime tool visibility remains unverified. Historical runtime and
remote CI results below do not certify this modified candidate.

## v4.1.4 Stable promotion — source and fake-home evidence

`v4.1.4` is the published Stable release and default public installation target.
Stable Source Commit A is
`6a537b445ad6f17a9600c05e655f51a2844bfcc8`. Exact-SHA CI run `33264634602`
passed on Windows, Ubuntu, and macOS and reported `366` tests all `PASS`.
The immutable Setup anchor is `bf01c438eae66f5ef9a27d401c6ee845f89d5d59`;
the current public Assisted Installation anchor is
`7494d47574ac751e76a231033a0ed91686899a07`. The immutable `v4.1.4` tag retains
the release-time Assisted anchor `5e1ce80d3ed444834f700ac0154bfe444dec8cd3`.

Repository fake-home lifecycle tests cover v4.1.3-to-v4.1.4 dry-run, apply,
the selector-plus-manifest ownership boundary, transaction backup,
second-apply idempotency, exact rollback, and modified-owned-selector conflict
with zero writes. Uninstall regression tests prove that backup verification
failure preserves the exact installed tree and that an exception after one
effective uninstall operation restores the exact pre-uninstall tree.

This is repository and fake-home validation only. No real Global v4.1.4
installer apply, authentication test, Daily state write, or fresh-task smoke
was performed. The v4.1.4 GitHub Release is non-draft and non-prerelease, and
the public bilingual README uses the immutable anchors recorded above.

`V414_SOURCE_SHA = 6a537b445ad6f17a9600c05e655f51a2844bfcc8`;
`V414_EXACT_SHA_CI = PASS`;
`V414_FAKE_HOME_LIFECYCLE = PASS`;
`V414_UNINSTALL_TRANSACTION = PASS`;
`V414_REAL_GLOBAL_APPLY = NOT_RUN`;
`V414_FRESH_TASK_COMPATIBILITY = NOT_RUN`;
`V414_PUBLIC_RELEASE = STABLE`.

## v4.1.3 previous immutable Stable — historical source and fake-home evidence

`v4.1.3` is the previous published immutable Stable release.
Stable Source Commit A is
`71894e2ef5007c9ba3e6f9d9efbf91cbdad302b4`. Exact-SHA CI run `33253340074`
passed on Windows, Ubuntu, and macOS and reported `363` tests all `PASS`.
Current-master evidence commit `bafc41b50269a0b65aba64594e850f6171a714ac`
passed CI run `33253429974` on the same three source-validation platforms. The
evidence commit is not Source Commit A and is not an installer source substitute.
The immutable Setup anchor is `5c29abc9aed340f4a7c45c22a0f8b36242b920bb`;
the immutable Assisted Installation anchor is
`23eeba1a5fb21e0483f4140aeca18b483f3e85bf`.

Repository fake-home lifecycle tests cover v4.1.2-to-v4.1.3 dry-run, apply,
the selector-plus-manifest ownership boundary, transaction backup,
second-apply idempotency, exact rollback, and modified-owned-selector conflict
with zero writes. Read-only live checks on 2026-08-29 exercised the ModelDial
API v1.1 and Full Snapshot paths independently and confirmed the intended
backend-axis selection and comparable reference-cost projection.

This is repository, fake-home, and read-only network validation only. No real
Global v4.1.3 installer apply, real authentication test, Daily state write, or
candidate fresh-task smoke was performed. The v4.1.3 GitHub Release is
non-draft and non-prerelease, and the historical bilingual README used the
immutable anchors recorded above.

`V413_SOURCE_SHA = 71894e2ef5007c9ba3e6f9d9efbf91cbdad302b4`;
`V413_EXACT_SHA_CI = PASS`;
`V413_CURRENT_MASTER_EVIDENCE_CI = PASS`;
`V413_FAKE_HOME_LIFECYCLE = PASS`;
`V413_REAL_GLOBAL_APPLY = NOT_RUN`;
`V413_FRESH_TASK_COMPATIBILITY = NOT_RUN`;
`V413_PUBLIC_RELEASE = STABLE`.

## v4.1.2 older immutable Stable — historical setup and runtime evidence

`v4.1.2` is an older published immutable Stable release.
Source Commit A is
`551520c2435aca94d60132f292edbd53cc975cbe`. Exact-SHA CI run `32717295801`
passed on Windows, Ubuntu, and macOS and reported `357` tests all `PASS`.
Current-master evidence commit `fac118ac5ca096aaf1ef8d68b79bfc1372998a5a`
passed CI run `32717520585` on the same three source-validation platforms. The
current-master evidence commit is not Source Commit A and is not an installer
source substitute. The immutable Setup anchor is
`4b2a6004fb92b6661166cb73e656cc2888b0a2ef`; the immutable Assisted
Installation anchor is `a130c676fa5924e44034dc8c27f3dc0abfc3bcad`.

The recorded real Global baseline was `v4.1.0-rc6`, source
`50ff886d1004ac3dd43b1f4ce531a2a8af8f7a49`. From a detached exact Source A
checkout, dry-run returned `DRY_RUN_PASS`, `writes NO`, `effective_changes 2`,
and five-effort capability `PASS`. Apply returned `UPGRADED`,
`configuration_preserved true`, `effective_changes 2`, changed only the
selector and install manifest, and created one transaction backup. Second apply
returned `CURRENT_INSTALLATION_PASS`, `writes NO`, `effective_changes 0`, and
`backup NONE`.

Daily selector proof returned a legal role and matching effort; the specific
day's effort is intentionally not recorded. Same-day Profile and LKG were not
rewritten. Exactly one fresh-task compatibility smoke ran for about `169.4`
seconds with `codex-cli 0.146.0`, exited `0`, and passed `CLI`, `Luna
capability`, `Selector`, `Delegation`, `Protected state`, `Runtime contract`,
and final `Compatibility`. Pre/post protected hashes for `AGENTS.md`,
configuration, the five agents, selector, manifest, Profile, LKG, and lock were
unchanged; the smoke created no backup.

This record is limited to one native Windows Codex environment. Windows,
Ubuntu, and macOS CI are source validation only, not three-platform real-runtime
validation. The v4.1.2 GitHub Release is non-draft and non-prerelease, and its
historical public README and assisted-installation entry used the immutable
anchors recorded above.

`V412_SOURCE_SHA = 551520c2435aca94d60132f292edbd53cc975cbe`;
`V412_EXACT_SHA_CI = PASS`;
`V412_CURRENT_MASTER_EVIDENCE_CI = PASS`;
`V412_DRY_RUN = DRY_RUN_PASS`;
`V412_APPLY = UPGRADED`;
`V412_SECOND_APPLY = CURRENT_INSTALLATION_PASS`;
`V412_FRESH_TASK_COMPATIBILITY = PASS`;
`V412_PUBLIC_RELEASE = STABLE`.

## v4.1.1 older immutable Stable — historical promotion evidence

Stable Source Commit A2 is
`ca8e9e4caf5564ffe8d0a11fe376047594f8a748`; its exact-SHA CI passed on
Windows, Ubuntu, and macOS. The installer payload is `v4.1.1` with manifest
schema `1`.

- `v4.1.0` -> `v4.1.1` fake-home lifecycle coverage changes only
  `sol-luna-v4/install-manifest.json` and byte-preserves the selector, Global
  policy, five Luna agents, config, Daily Profile, and LKG.
- Local coverage verifies dry-run zero writes, transaction backup,
  second-apply idempotency, exact rollback, downgrade refusal, and ownership
  conflict fail-closed behavior.
- After explicit Daily selection initialization, an independent one-run
  pre-publication fresh-task compatibility smoke exited `0` after about 144.2
  seconds and passed `CLI`, `Luna capability`, `Selector`, `Delegation`,
  `Protected state`, `Runtime contract`, and final `Compatibility` checks
  against the unchanged installed product runtime.
- No real Global `v4.1.1` apply was performed. The Stable promotion reuses the
  separately accepted product payload and changes only installed manifest
  version/source metadata.
- `V410_TO_V411_INSTALLED_BEHAVIOR_CHANGED = NO`;
  `ACCEPTANCE_CONTRACT_CHANGED = YES`.

This promotion evidence does not broaden RC6's recorded runtime scope or imply
real-runtime validation on all three CI platforms, every Codex client, every
account, or every user environment. Stable publication remains a separate
immutable tag and non-draft, non-prerelease GitHub Release fact.

`V411_SOURCE_COMMIT_CREATED = YES`;
`V411_SOURCE_SHA = ca8e9e4caf5564ffe8d0a11fe376047594f8a748`;
`V411_EXACT_SHA_CI = PASS`;
`V411_FRESH_TASK_COMPATIBILITY = PASS`.

## v4.1.0-rc6 historical Preview — recorded fresh-task runtime acceptance

RC6 Source Commit A is
`50ff886d1004ac3dd43b1f4ce531a2a8af8f7a49`; exact-SHA CI passed on Windows,
Ubuntu, and macOS. The installer payload is `v4.1.0-rc6` with manifest schema
`1`. RC6 remains an immutable historical GitHub Prerelease / Preview / Public
Beta. Its reviewed setup contract remains pinned through an exact immutable
documentation commit that is distinct from Source Commit A.

- RC5 -> RC6 fake-home lifecycle coverage expects only
  `sol-luna-v4/selector.py` and `sol-luna-v4/install-manifest.json` to change;
  local tests cover idempotency, backup, exact rollback, and ownership
  fail-closed behavior.
- The selector normalizes malformed URL parsing, hostname, and port `ValueError`
  cases to `SnapshotInvalid`, preserving the API -> snapshot -> LKG ->
  fail-closed source order.
- Compatibility-smoke baseline coverage uses dual exact rollout roots and
  bounded writer-settle/fail-closed evidence. The harness does not modify
  product runtime.
- `PRODUCT_RUNTIME_CHANGED = YES`; `ACCEPTANCE_CONTRACT_CHANGED = YES`.
- The separately authorized real RC5 -> RC6 Global upgrade is recorded `PASS`
  in one native Windows Codex environment. It returned `UPGRADED`, changed only
  the installed selector and ownership manifest, and was followed by a
  zero-write `IDEMPOTENT_PASS`. The installer-owned rollback snapshot exists
  under the owned backup root and its recorded hashes verify.
- Compatibility smoke, O1-O10 acceptance, Final O4/O9 re-certification, and
  Runtime Cases A/B/C/D are recorded `PASS` in the documented environment.
  This is not three-platform real-runtime validation, a universal compatibility
  claim, or standalone Stable evidence. RC6 publication is a separate immutable
  tag and historical Prerelease fact.

- O1 Natural-language healthy status — `PASS`
- O2 No-profile healthy status — `PASS`
- O3 Degraded LKG Receipt and status — `PASS`
- O4 Capability-degraded selected-effort Receipt and status — `PASS`
- O5 Unavailable evidence status — `PASS`
- O6 Misconfigured precedence — `PASS`
- O7 Safe diagnostic report — `PASS`
- O8 Latest prerelease immutable discovery and notice — `PASS`
- O9 Fail-soft observability selection, status, and Receipt omission — `PASS`
- O10 Fresh-session delegation and Receipt suffixes — `PASS`

### RC6 evidence boundary

- The installed manifest reported `v4.1.0-rc6`, schema `1`, and Source Commit A.
  The installed selector was byte-identical to Source Commit A; five Luna agent
  payloads, native-leaf settings, Global policy, and managed config validated.
- The compatibility smoke passed CLI, Luna capability, selector, delegation,
  protected-state, and runtime-contract checks. It remained a separate baseline
  and was not used as a substitute for O1-O10.
- The formal O2/O4/O9 harness installed Source Commit A into an independent fake
  `CODEX_HOME`, copied authentication to a distinct file identity, redirected
  home/application-data/temp/XDG paths, and verified actual parent and direct
  child rollout metadata. O2 used one native Luna child; O4 selected the bounded
  capability-degraded effort; O9 preserved selection while omitting invalid or
  missing ref-cost metadata and classified profile read failure as
  `Misconfigured / DAILY_PROFILE_READ_FAILED`.
- Final O4/O9 re-certification passed. Across O2/O4/O9, the real protected
  Sol/Luna inventory and root identity were unchanged, observed unknown paths
  were zero, isolated runtime paths were fully classified within the documented
  snapshot boundary, and owned acceptance artifacts had zero residuals.
- O3 ran a separate isolated LKG case with one completed native Luna child,
  depth `1`, zero grandchildren, matching role/model/effort metadata, a
  `Degraded / LKG_FALLBACK_ACTIVE` status, and an `LKG` Receipt suffix derived
  from the saved selection. Receipt generation added no selector, network, or
  state work.
- O5 and controlled Case D used isolated state. Case D produced
  `NO_LUNA_PROFILE_AVAILABLE` with parent-visible evidence; removing that
  evidence forbade `Luna unavailable`. The real selector, state, account, and
  Global configuration were not damaged or reconfigured.
- O8 enumerated all published Releases, accepted only non-draft strict SemVer
  entries with matching prerelease flags, selected the then-current RC5
  prerelease, and read its tag twice to the same peeled commit. Because the
  installed RC6 was newer, the workflow performed no downgrade, write, or
  backup.
- Runtime Case A completed with zero children and the reasoning/architecture
  Receipt. Runtime Case B used two actual direct Luna children with verified
  overlap and zero grandchildren. Runtime Case C used read-only sequential work,
  zero children, no selector, and no availability evidence. Controlled Case D
  verified both positive and negative availability-evidence gates.
- Parent-visible rollout metadata, not Receipt text alone, established child
  presence or absence, role/model/effort/depth, direct-child count, leaf behavior,
  overlap where claimed, completion, and descendant count. Sol performed final
  acceptance.

## v4.1.0-rc5 historical Preview — bounded documented-environment O1-O10 record

RC5 `Observability & UX` Source Commit A is
`5ae88ff9190b31174c55a6136c0c8c8611d0b34c`. Its historical immutable setup
contract is available at documentation commit
`ccd9d84da2f74df9ca2d919729b75eebf2dac27a`. The documented-environment RC5
O1-O10 record below is bounded evidence from one recorded Codex environment;
it is not a final O4/O9 re-certification or a universal runtime claim.

- O1 Natural-language healthy status — `PASS`
- O2 No-profile healthy status — `PASS`
- O3 Degraded LKG Receipt and status — `PASS`
- O4 Capability-degraded selected-effort Receipt and status — `PASS`
- O5 Unavailable evidence status — `PASS`
- O6 Misconfigured precedence — `PASS`
- O7 Safe diagnostic report — `PASS`
- O8 Latest prerelease immutable discovery and notice — `PASS`
- O9 Fail-soft observability selection, status, and Receipt omission — `PASS`
- O10 Fresh-session delegation and Receipt suffixes — `PASS`

RC4→RC5 fake-home installer lifecycle validation is a separate recorded
`PASS` and has no O-number. RC5 real Global upgrade, idempotency, and rollback
readiness remain a separately authorized operation and are `NOT RUN`. Final
O4/O9 re-certification was not obtained due to
`CODEX_ROLLOUT_EVIDENCE_COMPATIBILITY`; no confirmed product-runtime
regression is reported.

`RC5_SOURCE_COMMIT_CREATED = YES`;
`RC5_SOURCE_SHA = 5ae88ff9190b31174c55a6136c0c8c8611d0b34c`;
`RC5_SETUP_CONTRACT_COMMIT = ccd9d84da2f74df9ca2d919729b75eebf2dac27a`;
`RC5_RUNTIME_ACCEPTANCE_COMPLETED = YES`;
`RC5_RUNTIME_CATEGORY_MODEL_FIXED = YES`.

`RC6_SOURCE_COMMIT_CREATED = YES`;
`RC6_SOURCE_SHA = 50ff886d1004ac3dd43b1f4ce531a2a8af8f7a49`;
`RC6_SETUP_CONTRACT_REVIEWED = YES`;
`RC6_RUNTIME_ACCEPTANCE_COMPLETED = YES`;
`RC6_FINAL_O4_O9_RECERTIFICATION = PASS`;
`RC6_REAL_GLOBAL_UPGRADE = PASS`.

For the historical RC5 acceptance-boundary record, the product runtime payload
was frozen at
`src/selector.py`, `scripts/install.py`, `templates/AGENTS.global.md`, and
`.codex/agents/*`. This file, `CODEX_SOL_LUNA_SETUP.md`, `ARCHITECTURE.md`, and
`SECURITY.md` are the acceptance contract and may track acceptance redesigns.
`PRODUCT_RUNTIME_CHANGED = NO`; `ACCEPTANCE_CONTRACT_CHANGED = YES`.

The committed repeatable harness runs O2, O4, and O9 from Source Commit A under
a unique owned acceptance root. O4 and O9 execute with an isolated
`CODEX_HOME`, home/profile, application-data, temporary-storage, and XDG
environment. The harness constructs one `isolated_runtime_env`; selector
subprocesses, `codex exec`, installer and repository subprocesses receive it
explicitly, while in-process O9 fail-soft and status/health checks run under
that same environment with the caller environment restored afterward. No
O4/O9 path inherits the real process environment. Before any installer write
or credential copy, the harness
validates that the acceptance root is outside the real runtime, is not a
user-controlled symlink, junction, reparse point, or mount, and contains no
hardlink into the real runtime. The fixed macOS `/var` system alias is
recognized so canonical platform temp directories remain usable. A per-run
ownership marker, token, and directory identity gate cleanup; cleanup removes
reparse entries without traversing them and fails closed if ownership or
identity changes.

The real `CODEX_HOME` is used only for pre/post protected-state integrity and
root-identity verification. Managed Sol/Luna policy, configuration, agents,
selector, manifest, and the complete `sol-luna-v4/state/**` tree must remain
unchanged. The state inventory covers the Daily Profile, LKG, `selector.lock`,
and every other state entry; before/after hash, object type, device/file
identity, link count, and reparse status are compared. Unrelated real-home
runtime activity is not an RC5 runtime-attribution source and does not fail
acceptance.

Runtime attribution is confined to the isolated home. The existing explicit
Codex session, session-index, app-cache, and active-exec namespaces remain
narrowly allowlisted. `CODEX_PLATFORM_RUNTIME_STATE` additionally accepts only
the exact root-level `.sandbox_migration` safe regular file, safe ordinary
objects under the exact `skills/**` and
`plugins/.remote-plugin-install-staging/**` trees, structurally valid entries
under `browser/sessions/**`, `cache/remote_plugin_catalog/**`,
`plugins/cache/**`, `tmp/arg0/**`, and a validated runtime subtree under
`visualizations/`; their broader parent trees are not allowlisted. A normal
remote-plugin install clears staging descendants but may retain the empty exact
staging root, so the contract does not require that root to disappear. An
internal `plugins/cache/**` directory reparse is allowed only when its resolved
target remains inside both the isolated `CODEX_HOME` and plugin-cache
namespace, does not overlap protected state, and does not loop. Reparses are
not allowed in the new staging or skills trees.
Root SQLite storage is restricted to the `goals`, `logs`, `memories`, `queue`,
`state`, and `thread_history` ID families with `-wal` and `-shm` sidecars coupled
to a safe base. Global `*.sqlite` and `*.db` suffix rules are forbidden.

Any isolated-home reparse escape, unexpected hardlink, invalid runtime type,
change to protected real state, or write outside the exact isolated runtime
categories fails the harness.
Authentication bytes are copied only to the isolated fake home with a distinct
file identity; they are not committed, printed, or included in the result. The
Codex child receives a fixed minimal inherited environment plus fake-home
values for home, application data, temporary storage, and XDG roots, so
unrelated user credential variables are not forwarded. All real, fake,
temporary, repository, and executable paths are symbolized before the JSON
evidence is printed; remaining user-home path shapes and credential-shaped
values are redacted.

This is environment- and scenario-bounded evidence for the published RC5
Preview. It is not three-platform real-runtime validation, a tag, a Stable
claim, or a Stable promotion. Windows, Ubuntu, and macOS CI remain source
validation only.

`SELECTOR_URL_EXCEPTION_HARDENING = DEFERRED_TO_PRE_STABLE` describes the RC5
record; the published RC6 Preview implements this normalization.

Native Runtime Tests 1-5 passed in fresh project sessions after the project custom-agent configuration and `AGENTS.md` policy were loaded. This document records generic results only; it intentionally omits session IDs, usernames, absolute paths, rollout IDs, and installation IDs.

Static validation and Native Runtime validation remain separate gates. The runtime tests do not grant Luna planning, architecture, orchestration, or final-acceptance authority. Sol owns those responsibilities.

## v4.1.0-rc4 published prerelease — Receipt reason evidence-gating

RC4 fixes one policy classification defect: without current-task parent-visible Luna availability failure evidence, a Sol-only Receipt must not report `Luna unavailable`. The five-outcome taxonomy and delegation threshold are unchanged. Receipt generation remains decision-neutral and must not create evidence through selector invocation, capability probes, tools, children, network access, state, telemetry, or repository writes.

- Source validation commit `95cfd53200a3fc53b50a48fe7ab251dcc6d5e00b`: Windows, Ubuntu, and macOS `PASS`; full repository suite `114/114 PASS`.
- Final source pin `d17bea49fdb0710bb2101f1577045bed2477ff79`: Windows, Ubuntu, and macOS `PASS`.
- RC3→RC4 fake-home lifecycle: upgrade, backup, idempotency, exact rollback, and ownership-conflict fail-closed `PASS`.
- Frozen selector, five Luna agents, config, state schema, Daily Profile, and LKG: unchanged by the RC4 payload.

### Real RC3 → RC4 Global upgrade — `PASS`

- Result: `UPGRADED`; effective changes: `2`.
- Only the managed Global `AGENTS.md` block and install manifest changed.
- Selector, five Luna agents, Global config, Daily Profile, and LKG remained unchanged.
- A second apply returned `IDEMPOTENT_PASS`.
- Rollback readiness passed.

### Runtime Case A — `PASS`

- Actual direct-child count: `0`.
- Final line: `Sol/Luna: Sol-only · reasoning/architecture task`.

### Runtime Case B — `PASS`

- Selected role: `luna_max`; actual direct children: `3`.
- Child model: `gpt-5.6-luna` ×3; effort: `max` ×3.
- Parallel overlap: verified; grandchildren: `0`.
- Final line: `Sol/Luna: delegated · luna_max ×3 · parallel`.

### Runtime Case C — `PASS`

- Selector invoked: `NO`; delegation attempted: `NO`.
- Availability evidence: `NONE`; actual direct-child count: `0`.
- Final line: `Sol/Luna: Sol-only · no independent bounded work`.
- This is the direct regression for the RC3 misclassification: without availability evidence, `Luna unavailable` is forbidden.

### Runtime Case D — controlled / isolated — `PASS`

- Selector result: `NO_LUNA_PROFILE_AVAILABLE`; availability evidence: `PRESENT`.
- With genuine parent-visible availability evidence, `Luna unavailable` is allowed.
- Negative control: availability evidence `NONE`; `Luna unavailable` is forbidden.
- The controlled case did not modify the real `.codex` environment.

The recorded RC4 runtime evidence applies only to the environments in which it was observed. It is not three-platform real Codex runtime validation and does not claim validation for every operating system, client, account, or user.

### Additional recorded Public Beta runtime evidence

These records were obtained after the RC4 release source and tag were fixed. They are post-release Public Beta evidence, not release-source evidence, a new release gate, a tag change, or a Stable promotion.

#### Day-2 cross-day end-to-end — `PASS`

- Status: `DAY_2_CROSS_DAY_END_TO_END_PASS`.
- Beijing date: `2026-08-14`; installed version: `v4.1.0-rc4`.
- Today's profile already existed when this test began. It had refreshed naturally from the prior-day recorded state before the test, and the normal delegation path reused the same-day cache.
- `CROSS_DAY_REFRESH_OCCURRED_NATURALLY = YES`.
- `CURRENT_TEST_OBSERVED_REFRESH_EVENT_DIRECTLY = NO`.
- `CURRENT_TEST_VERIFIED_REFRESH_RESULT = YES`.
- Today's role: `luna_max`; source: `modeldial_api_v1`.
- Actual direct children: `3`; agent: `luna_max` ×3; model: `gpt-5.6-luna` ×3; effort: `max` ×3.
- Parallel overlap: verified; grandchildren: `0`; native leaf: `PASS`; Sol acceptance: `PASS`.
- The Receipt matched the actual role, direct-child count, and parallel runtime metadata.
- The repository and installed runtime payload were unchanged by the test.

#### Day-2 new-session same-day persistence — `PASS`

- Status: `DAY_2_SAME_DAY_NEW_SESSION_PERSISTENCE_PASS`.
- Fresh Codex session: `YES`; Beijing date: `2026-08-14`.
- Existing profile role: `luna_max`; effort: `max`; source: `modeldial_api_v1`.
- Normal-path selector calls: `1`; acquisition: `same-day cache`.
- Profile SHA before and after: unchanged; profile mtime before and after: unchanged; LKG: unchanged; profile regenerated: `NO`.
- Actual direct children: `3`; agent: `luna_max` ×3; model: `gpt-5.6-luna` ×3; effort: `max` ×3.
- Parallel overlap: verified; grandchildren: `0`; native leaf: `PASS`; Sol acceptance: `PASS`.
- The Receipt role, direct-child count, and parallel marker all matched the runtime metadata.
- This demonstrates that the recorded same-day persisted profile survived a completely new Codex session. It does not establish universal persistence across all Codex clients or user environments.

### Historical RC4 pre-stable hardening record

`SELECTOR_URL_EXCEPTION_HARDENING = DEFERRED_TO_PRE_STABLE`

Malformed port or malformed IPv6-style URL input could surface a `ValueError` without unified normalization in RC4. RC6 resolved this item by normalizing those URL parsing, hostname, and port cases to `SnapshotInvalid`; Stable preserves that fix unchanged.

## v4.1.0-rc3 real upgrade and Receipt acceptance — `PASS`

The published RC3 prerelease passed its separately authorized real upgrade and fresh-session Receipt acceptance in one recorded Codex environment. The full repository suite passed `109/109`, and Windows, Ubuntu, and macOS CI passed for the release source.

### Real RC1 → RC3 Global upgrade — `PASS`

- Result: `UPGRADED`; effective changes: `2`.
- The managed Global `AGENTS.md` block and install manifest changed.
- Selector, five Luna agents, Global config, selector state and schema, Daily Profile, and LKG remained unchanged.
- A second apply returned `IDEMPOTENT_PASS`.
- Rollback readiness passed.

### Sol-only Receipt — `PASS`

- Actual direct-child count: `0`.
- Final line: `Sol/Luna: Sol-only · reasoning/architecture task`.

### Delegated Receipt — `PASS`

- Selected role: `luna_max`; actual direct children: `3`.
- Child model: `gpt-5.6-luna` ×3; effort: `max` ×3.
- Parallel overlap: verified; grandchildren: `0`.
- Final line: `Sol/Luna: delegated · luna_max ×3 · parallel`.

In both Receipt cases, parent-visible runtime metadata established child absence or presence. Receipt text remains a user-facing execution summary and is not runtime attestation by itself. Native leaf, parallel delegation, and Sol Acceptance all passed.

## Safety boundary

- The tests use a fresh project session and the current Beijing-date Daily Profile.
- Routine test runs do not alter global Codex configuration, global agents, Hooks, or environment variables.
- Installer lifecycle tests write only to explicit fake homes. Separately approved real global upgrades and fresh-session runtime acceptance were recorded for the stable source, RC3, and RC4 prereleases without widening routine repository-test permissions.

## Test results

### Test 1: project custom-agent discovery — `PASS`

The fresh project session discovered all five formal native custom Luna agents, including the canonical role names. No runtime identifier is recorded here.

### Test 2: explicit native spawn — `PASS`

A named native custom agent ran as GPT-5.6 Luna at its configured selected effort and returned the required test sentinel. The result confirms native `agent_type`/custom-agent spawning; it does not establish a direct model override path.

### Test 3: `AGENTS.md` policy delegation — `PASS`

Sol read the current Daily Profile, delegated the bounded read-heavy task to its `selected_role`, and performed the final acceptance. The role was selected by policy rather than by a Hook Router, registry, or direct model override.

### Test 4: native leaf — `PASS`

Each formal Luna custom agent loads `[agents] enabled = false`. The child tool surface contains no multi-agent or delegation tools, so the native leaf boundary is enforced. Luna remains a bounded execution worker.

### Test 5: parallel native delegation — `PASS`

Two independent bounded read-only checks were delegated according to the current policy, both used the selected role, stayed within the project concurrency limit, and were consolidated and accepted by Sol.

## Global Runtime results

- G1 Global Discovery — `PASS`
- G2 Selector + Explicit Luna — `PASS`
- G3 Automatic Delegation — `PASS`
- G4 Native Leaf — `PASS`
- G5 Native Parallel — `PASS`
- G6 Sol Acceptance — `PASS`
- G7 Legacy Absence — `PASS`

Daily Selector same-day cache reuse and no-`ultra` checks passed. LKG and fail-closed behavior are validated by the test suite. The global record is generic and contains no machine- or session-specific identifiers.

## Result rule

Native Runtime Tests 1-5 and Global Runtime G1-G7 provide the generic runtime evidence for stable `v4.0.0` in the tested Codex Desktop/App Server environment. The RC3 and RC4 upgrade and Receipt results above apply only to the recorded environments in which they were observed. They do not promise compatibility with future Codex versions or establish real runtime PASS for every operating system, client, account, or user.
