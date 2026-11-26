# OpenClaw Control Plane

Build a persistent OpenClaw assistant that carries work from a chat request to a
verified result. This repository combines a reconstructable custom runtime,
operating instructions, account-aware tool routing and host maintenance helpers.

It is a reference for engineers comfortable with Git, Python and Node.js.
Runtime reconstruction supports Linux and macOS; the host-service examples target
macOS. Supply your own accounts, permissions and private configuration.

## How it works

```mermaid
flowchart LR
    User[Request in chat or app] --> Gateway[OpenClaw gateway]
    Gateway --> Agent[Model and tools]
    Context[Instructions, memory and account routes] --> Agent
    Agent --> Work[Direct work or delegated tasks]
    Work --> Result[Verify the result]
    Result --> Reply[Progress and final answer]
    Reply --> User
    Host[Host maintenance and recovery] --> Gateway
```

The runtime owns sessions, delegation, compaction and delivery. The workspace
supplies identity, preferences, project knowledge and operating procedures.
Tools act on the selected account; the agent reads back the result before
reporting completion. [Architecture](docs/04-system-architecture.md) explains the
boundaries, and the [calendar example](docs/07-worked-example.md) follows one task.

## Start here

| Your goal | Read |
| --- | --- |
| Understand the design in a few minutes | [Introduction](docs/00-start-here.md) and [architecture](docs/04-system-architecture.md) |
| Build your own installation | [Adoption guide](docs/17-adoption-guide.md) and [runtime reconstruction](runtime/README.md) |
| Adapt instructions, memory and account routing | [Policy](docs/05-policy-and-authority.md), [context](docs/08-memory-and-context.md) and [integrations](docs/11-integrations-and-capability-routing.md) |
| Operate long tasks, voice and scheduled work | [Continuation](docs/06-execution-and-durable-lanes.md), [delivery](docs/13-delivery-and-control-surface.md) and [scheduling](docs/12-scheduling-and-background-work.md) |
| Review measured results and possible improvements | [Evaluation and future work](docs/22-evaluation-and-future-work.md) |
| Find a specific component or procedure | [Documentation index](docs/README.md) and [runtime source map](docs/20-runtime-source-changes.md) |

## What you can reproduce

- **Runtime:** the **R96** gateway source from 13 November 2026, reconstructed
  from official OpenClaw **v2026.10.4**, plus regression tests and the managed
  **Codex 0.160.0** native package.
- **Workspace:** operating instructions, source/account routing, release
  activation, maintenance and recovery helpers.
- **Integration patterns:** configuration and fictional company examples for
  connecting your own services and devices.
- **Operating workflow:** build, install, verify and recover a selected release.

The [manifest](runtime/manifest.json) pins the public build, including the source
for Mac companion **508**. The delivery and evaluation guides also report field
tests of later releases. To reproduce the public gateway or companion, use the
corresponding [source target](runtime/README.md#source-identities). Supply the
companion's local Bun security payload separately.
For the October 2026 native releases, see the [download and reconstruction notes](docs/21-native-runtime-reconstruction.md#october-2026-native-releases).

Company Alpha, Company Beta and the Personal Data Project are fictional. Example
readiness records start unverified. Enrollment and a real workflow check complete
an installation.

## Results and direction

In the frozen November comparison, the custom OpenClaw candidate and native
Codex both earned full marks on 16 of 17 qualified pairs. On the remaining
pair, OpenClaw scored 75 and Codex scored 100.
Codex finished faster in 16 pairs. A separate compaction change cut the number
of summary calls in half. The evaluation guide gives the scores, timings and
proposed changes to the execution engine. [Results and lessons](docs/22-evaluation-and-future-work.md#measured-results)

## Verify and contribute

```bash
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/native-reference-checks.test.mjs
```

[CONTRIBUTING](CONTRIBUTING.md) covers workspace fixtures, runtime checks,
confidentiality review and publication. The
[reference workflow](https://github.com/josephbergvinson-projects/openclaw-control-plane/actions/workflows/verify-reference.yml)
reconstructs and builds the pinned runtime. Use the checks attached to the commit
you adopt, then verify your installation through an ordinary task.

Designed for one trusted operator, with explicit audience and account boundaries
for shared conversations. See the [security model](docs/16-security-and-trust-model.md).
MIT licensed; retain [LICENSE](LICENSE), [runtime notices](runtime/THIRD_PARTY_NOTICES.md)
and [native resource notices](runtime/native160/README.md).
