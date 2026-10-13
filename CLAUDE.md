# Project rules — mini-exchange

mini-exchange is a small stock exchange in Python and FastAPI. Akash owns it: Akash sets priorities and approves every design, slice plan and commit. Claude drafts the designs, writes the code and keeps the runbook current ([decision #23](runbook/decisions.md)). Code, infrastructure and runbook live in this one repo ([decision #13](runbook/decisions.md)). Work runs as projects: [00-master](runbook/projects/00-master/README.md) holds the overall state, and every phase, feature, bug or research question gets its own folder under [runbook/projects/](runbook/projects/README.md) ([decision #24](runbook/decisions.md)). Start with 00-master to see where things stand.

## Hard rules

These two rules are enforced, not only written. [.claude/hooks/guard.py](.claude/hooks/guard.py) checks every tool call before it runs and blocks any call that breaks them, and [.claude/settings.json](.claude/settings.json) denies the work Atlassian tools outright. When the guard blocks a call, stop and tell Akash. Never reword a command to get past it.

| ID | Rule | How it's enforced |
|---|---|---|
| H1 | **Never touch TPP** (Akash's employer). No TPP AWS profile (`tpp-*`), AWS account, repo, Jira, Confluence or data. P7 uses a personal AWS account with its own profile ([decision #12](runbook/decisions.md)). | The guard blocks shell commands and file paths that mention `tpp`, Atlassian or a TPP account ID. It also blocks every AWS CLI, Terraform or `~/.aws` use until P7 sets up the personal profile, because a command without `--profile` would fall back to the default profile, which could be a TPP one. The account IDs live in the gitignored `.claude/hard-rules.local.json`, so they never reach git. |
| H2 | **Only Akash's personal GitHub account commits or pushes.** This laptop's global git identity and its `gh` login are the work account, so this repo must resolve to the personal identity. Remotes use SSH (`git@github.com:…`), because an HTTPS remote would sign in with the work account's stored credentials. | The guard blocks `git commit` and `git push` unless `git config user.email` equals `personal_git_email` in `.claude/hard-rules.local.json`. It also blocks identity overrides inside a command (`--author`, `-c user.email=`), a push to any remote outside `git@github.com:akashca-pro/`, every `gh` command (gh knows only the work account, so PRs, merges and CI are Akash's on github.com; [decision #17](runbook/decisions.md)), and any attempt to skip git hooks (`--no-verify`, `commit -n`, `hooksPath`). For every git client, not only Claude, the personal git hooks in `~/.githooks-personal/` refuse the same commits and pushes ([decision #16](runbook/decisions.md)). |

Changing the guard, `.claude/settings.json` or `.claude/hard-rules.local.json` is `[A→H]`: Claude proposes and Akash approves first. The guard sees only Claude's tool calls. Akash's own terminal is protected by the per-folder git identity and the personal git hooks, which `~/.gitconfig` loads only for repos under `~/personal/`.

## Rules

1. **Design before code.** No code in a project until Akash has approved its design ([RB-001](runbook/procedures/RB-001-deliver-a-project.md) Steps 2–3). Claude drafts the design; Akash approves it or asks for changes.
2. **Small slices.** One slice covers one change, about 150 changed lines or fewer plus tests, and ends green and committed straight to `main` (decision #25). That keeps "go back to the last green commit" to a single command.
3. **Akash approves every commit message** before the commit is made (RB-001 Step 6).
4. **Never touch TPP.** This is hard rule H1 above, enforced by the guard.
5. **Integers for money and prices** (cents and ticks), never floats (decision #6).
6. **Append, don't rewrite.** `decisions.md` and `changelog.md` are append-only. A reversal adds a new row that says which one it supersedes.
7. **Never infer.** State only what's verified. Mark anything unverified once, as a blockquote: `> [CONFIRM] <what's unverified>`.
8. **The runbook beats generic skills.** RB-001 and these rules win over any plugin skill whose advice differs. Designs go in the project's `design.md` and slice plans in its `progress.md`, in this runbook's format. Don't use `executing-plans` or `subagent-driven-development` to build several slices without Akash approving each commit (rules 2 and 3).

## When you make progress, edit the right file

Akash wants the runbook updated as work happens, not batched at the end.

| When… | Update |
|---|---|
| A phase, feature, bug or research question starts | New folder under `runbook/projects/` ([projects/README.md](runbook/projects/README.md)) and its row in the 00-master **Projects** index |
| A project's status changes | Its README **Status** and its row in the 00-master **Projects** index |
| A phase starts or finishes | The 00-master **Roadmap** table |
| A slice finishes | The project's `progress.md` |
| A decision is made or reversed | [decisions.md](runbook/decisions.md), appended with date and source |
| The architecture changes | [design.md](runbook/design.md) |
| A new command exists | **Commands** below |
| The overall state changes | The 00-master **Status** and **Next**, plus a dated entry in [changelog.md](runbook/changelog.md) |

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
- Write plain English. A sentence a newcomer can't follow counts as a bug.

## Commands

Filled in at the end of P0. There is no code yet.
