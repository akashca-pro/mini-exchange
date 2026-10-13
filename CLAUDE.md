# Project rules — mini-exchange

This is a learning project. Akash owns the designs and has to understand them; Claude implements and teaches. Code, infrastructure and runbook live in this one repo ([decision #13](runbook/decisions.md)). Start with [README.md](README.md) to see where things stand.

## Hard rules

These two rules are enforced, not only written. [.claude/hooks/guard.py](.claude/hooks/guard.py) checks every tool call before it runs and blocks any call that breaks them, and [.claude/settings.json](.claude/settings.json) denies the work Atlassian tools outright. When the guard blocks a call, stop and tell Akash. Never reword a command to get past it.

| ID | Rule | How it's enforced |
|---|---|---|
| H1 | **Never touch TPP** (Akash's employer). No TPP AWS profile (`tpp-*`), AWS account, repo, Jira, Confluence or data. P7 uses a personal AWS account with its own profile ([decision #12](runbook/decisions.md)). | The guard blocks shell commands and file paths that mention `tpp`, Atlassian or a TPP account ID. It also blocks every AWS CLI, Terraform or `~/.aws` use until P7 sets up the personal profile, because a command without `--profile` would fall back to the default profile, which could be a TPP one. The account IDs live in the gitignored `.claude/hard-rules.local.json`, so they never reach git. |
| H2 | **Only Akash's personal GitHub account commits or pushes.** This laptop's global git identity and its `gh` login are the work account, so this repo must resolve to the personal identity. Remotes use SSH (`git@github.com:…`), because an HTTPS remote would sign in with the work account's stored credentials. | The guard blocks `git commit` and `git push` unless `git config user.email` equals `personal_git_email` in `.claude/hard-rules.local.json`. It also blocks identity overrides inside a command (`--author`, `-c user.email=`), a push to any remote outside `git@github.com:akashca-pro/`, every `gh` command (gh knows only the work account, so PRs, merges and CI are Akash's on github.com; [decision #17](runbook/decisions.md)), and any attempt to skip git hooks (`--no-verify`, `commit -n`, `hooksPath`). For every git client, not only Claude, the personal git hooks in `~/.githooks-personal/` refuse the same commits and pushes ([decision #16](runbook/decisions.md)). |

Changing the guard, `.claude/settings.json` or `.claude/hard-rules.local.json` is `[A→H]`: Claude proposes and Akash approves first. The guard sees only Claude's tool calls. Akash's own terminal is protected by the per-folder git identity and the personal git hooks, which `~/.gitconfig` loads only for repos under `~/personal/`.

## Rules

1. **Teach, don't just deliver.** For every slice, explain in plain words what each part does, why it has this shape, what the alternative was and why we didn't take it, and which concept it shows (for example, "this is the single-writer principle"). Akash is new to Python, so explain Python idioms the first time they appear.
2. **Design before code.** No phase code until Akash's phase design has been reviewed ([RB-001](runbook/procedures/RB-001-build-a-phase.md) Steps 3–4). Claude reviews the design and can explain concepts, but does not write Akash's design.
3. **Small slices.** One slice covers one concept, about 150 changed lines or fewer plus tests, and ends green and committed. That keeps "go back to the last green commit" to a single command.
4. **Drills belong to Akash.** During a drill ([RB-002](runbook/procedures/RB-002-run-a-debug-drill.md)), give hints only when asked, one ladder level at a time. Never fix the planted fault, and never merge a `drill/*` branch.
5. **Never touch TPP.** This is hard rule H1 above, enforced by the guard.
6. **Integers for money and prices** (cents and ticks), never floats (decision #6).
7. **Append, don't rewrite.** `decisions.md`, `changelog.md` and drill reports are append-only. A reversal adds a new row that says which one it supersedes.
8. **Never infer.** State only what's verified. Mark anything unverified once, as a blockquote: `> [CONFIRM] <what's unverified>`.
9. **The runbook beats generic skills.** RB-001, RB-002 and these rules win over any plugin skill whose advice differs. Don't use `superpowers:brainstorming` or `superpowers:writing-plans` to write a phase design (rule 2). Don't use `executing-plans` or `subagent-driven-development` to build several slices without the predict and teach-back steps (rule 3). Never let `finishing-a-development-branch` merge a `drill/*` branch (rule 4).

## When you make progress, edit the right file

Akash wants the runbook updated as work happens, not batched at the end.

| When… | Update |
|---|---|
| A phase, feature, research question or bug starts | New folder under `runbook/work/` ([work/README.md](runbook/work/README.md)) and its row in that index |
| A phase starts or finishes | [plan.md](runbook/plan.md) status table |
| A slice finishes | The work folder's `progress.md` |
| Akash explains a slice back | The work folder's `teach-back.md` |
| A drill finishes | The work folder's `drills/<name>.md` |
| A decision is made or reversed | [decisions.md](runbook/decisions.md), appended with date and source |
| The architecture changes | [design.md](runbook/design.md) |
| A new command exists | **Commands** below |
| Status changes | [README.md](README.md) **Status**, plus a dated entry in [changelog.md](runbook/changelog.md) |

## Executor tags

The runbooks tag every step with who carries it out:

| Tag | Who |
|---|---|
| `[H]` | Akash |
| `[A]` | Claude |
| `[A→H]` | Claude prepares or proposes, and Akash approves before it takes effect |

## Writing docs

Same style as the TPP runbook (`tpp/runbook/CLAUDE.md`, section "Doc Authoring"), condensed:

- Lead with the fact. No throat-clearing, no outros.
- Keep the causal words (because, so, which means). They carry the reasoning.
- Use tables for parallel facts, and prose for reasoning, sequence and cause.
- State each fact once, and have other files link to it.
- Explain a term at its first use in each file, or link [glossary.md](runbook/glossary.md).
- Write plain English. Akash is learning, so a sentence a beginner can't follow counts as a bug.

## Commands

Filled in at the end of P0. There is no code yet.
