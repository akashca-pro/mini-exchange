# Changelog

Dated history, newest first. Append-only.

## 2026-10-13

- Project opened. A mini stock exchange is the single learning project (decision #1).
- Runbook written: requirements, design, an eight-phase plan, decisions #1–#12, a glossary, the procedures RB-001 (build a phase) and RB-002 (run a debug drill), and templates for the phase design, the drill report and the work-folder README.
- Environment checked: Python 3.13.12 (the default `python`) and 3.14.5 (`py`), Docker 29.6.1 on WSL2, and git 2.54 are installed. uv is not installed.
- Git repo initialised on `main`. Nothing committed yet.
- Session 2: decision #13, one repo for the runbook, code and infrastructure.
- Hard rules H1 (never touch TPP) and H2 (personal GitHub account only, SSH remotes) added to [CLAUDE.md](../CLAUDE.md). They are enforced by `.claude/hooks/guard.py`, a PreToolUse hook that fails closed, plus permission deny rules for the two work Atlassian servers (decisions #14 and #15). CLAUDE.md rule 9: the runbook wins over generic plugin skills.
- Personal git identity configured (decisions #16–#18). `~/.gitconfig` (backed up to `~/.gitconfig.bak`) now loads `~/.gitconfig-personal` only for repos under `~/personal/`; that file sets the personal name and email, the personal SSH key and the personal git hooks (`~/.githooks-personal/`). Verified: inside `~/personal/`, git resolves to the personal identity; outside it, to the work identity. The guard now also blocks `gh`, hook skipping, and pushes outside `git@github.com:akash-ca/`. Guard: 22/22 pipe tests pass; hook logic: 7/7. Still to do: the SSH key, and moving the repo into `~/personal/`.
- Personal SSH key generated: ed25519, no passphrase, fingerprint `SHA256:JX0KKKjHVDf6dc3SapZPqIUtVfERI36p+e+nW7GqdX4`, to be added as a deploy key on `akash-ca/mini-exchange` (decision #19).
- `~/.ssh/known_hosts` created from GitHub's published host keys (fetched from `api.github.com/meta` over HTTPS). `ssh -T` with the personal deploy key succeeded, but GitHub greeted `akashca-pro/mini-exchange`, not `akash-ca/mini-exchange`. The hooks and guard allow only `akash-ca`, so the repo owner name must be confirmed before the first push.
- Owner confirmed as `akashca-pro` (decision #20). The guard config, both personal git hooks, `~/personal/CLAUDE.md` and CLAUDE.md H2 now allow only `git@github.com:akashca-pro/`.
- Session 3, the first after the move into `~/personal/`. Inside the repo, git resolves `user.email`, `core.hooksPath` and `core.sshCommand` from `~/.gitconfig-personal`.
- Personal git hooks verified in a real commit, in a throwaway repo under `~/personal/`. Git's trace shows it starting `~/.githooks-personal/pre-commit`, and the commit landed with the personal email as author and committer. After a non-personal remote was added, the hook refused the next commit. The throwaway repo was then deleted. The pre-push hook still has only its direct tests; its first real run is the first push.
- The guard blocked none of four live probes. Root cause: Windows PowerShell, which runs hooks here because MinGit has no Git Bash, turns the guard's exit code 2 (block) into 1, and Claude Code allows the call on any code but 2. Bug folder [2026-10-13_bug-guard-not-firing](work/2026-10-13_bug-guard-not-firing/README.md) opened, with a fix tested outside Claude Code and waiting for Akash's approval.
- Guard fix approved by Akash and applied (decision #21). The hook now runs in pinned PowerShell, finds the script through `$env:CLAUDE_PROJECT_DIR`, and turns every exit code except 0 into 2. Claude Code reloaded the settings mid-session; all four probes were then blocked with the right reasons, and an ordinary call still ran. A fresh-session check remains before the bug folder closes.
- Session 4, a fresh session. The guard blocked all four probes with the right reasons, and an ordinary call ran, so the hook also loads when Claude Code starts. Bug folder [2026-10-13_bug-guard-not-firing](work/2026-10-13_bug-guard-not-firing/README.md) closed as `done`. The gap it found (the guard checks the session folder's git identity, not the target repo's) stays open and unscheduled.
