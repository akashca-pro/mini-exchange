# Guard hook doesn't block

The PreToolUse hook that enforces hard rules H1 and H2 (`.claude/hooks/guard.py`, decision #15) blocked nothing in the first session after the repo moved into `~/personal/`. Four tool calls it should have stopped all ran. The cause is the shell between Claude Code and the script: Windows PowerShell turns the guard's "block" exit code 2 into 1, and Claude Code treats 1 as "the hook broke, allow the call". The fix below makes every result except an explicit "allow" block the call. It was verified live, first mid-session and then in a fresh session. The personal git hooks, which protect commits and pushes for every git client, were verified in that session too.

## Owner

Akash · infra (hard rules) · covers H1, H2, decision #15

## Status

`done` — 2026-10-13. Fix approved by Akash and applied (decision #21). The guard blocked all four probes twice: once after Claude Code reloaded the settings mid-session, and again in session 4, a fresh session. An ordinary call ran both times. The fresh-session run proves the hook also loads when Claude Code starts. One gap stays open and is not scheduled (see **Also found**).

## Root cause

A hook is a program Claude Code starts before each tool call, with the call's details as JSON on its standard input. Claude Code reads only the program's **exit code**, the number a program returns when it finishes:

| Exit code | Claude Code does |
|---|---|
| 0 | allows the call |
| 2 | blocks the call and shows the hook's error text to Claude |
| anything else | treats it as a broken hook, allows the call, and shows the error only in the transcript |

So the contract fails open: any result that isn't exactly 2 lets the call through.

On this laptop git is MinGit, which has no Git Bash, so Claude Code runs hook commands in Windows PowerShell 5.1. In `-Command` mode, PowerShell doesn't pass on the exit code of the program it ran. It returns its own: 0 if the last command succeeded, 1 if it failed. The guard decided "block" and exited 2; PowerShell reported 1; Claude Code allowed the call.

Reproduced by piping a `gh --version` event into the guard three ways. The guard printed its H2 block message every time:

| How the guard was run | Exit code Claude Code would see |
|---|---|
| `python .claude\hooks\guard.py` directly | 2 (block) |
| `powershell -Command "python .claude/hooks/guard.py"`, the shape in `settings.json` | **1 (allow)** |
| the same, ending with `; exit $LASTEXITCODE` | 2 (block) |

The 22/22 tests from session 2 passed because they ran `python` directly. They tested the script but not the path Claude Code uses to reach it. The same flaw made the guard's fail-closed design fail open: a crash, a missing `python` or a wrong relative path all exit non-zero, PowerShell turns that into 1, and the call is allowed.

> [CONFIRM] Still inferred: that Claude Code starts hooks with `powershell -Command` specifically. The docs say only that PowerShell is used when Git Bash isn't installed. The fix working fits this cause, but the exact flags were never observed.

### Evidence

Four probes were sent in the live session. Each one is harmless if it runs, so a guard failure couldn't do damage:

| Probe | Guard branch it tests | Expected | Actual |
|---|---|---|---|
| PowerShell `Write-Output "tpp"` | H1, work word in a command | blocked | ran, printed `tpp` |
| PowerShell `gh --version` | H2, any `gh` command | blocked | ran, printed the version (no login used) |
| PowerShell `git commit --dry-run --no-verify` | H2, skipping hooks | blocked | ran; a dry run, nothing committed |
| Glob `**/tpp*` | H1, path and pattern fields | blocked | ran, no files found |

Causes ruled out:

| Check | Result |
|---|---|
| `guard.py` fed an event by hand | exit 2 with the H2 reason, so the script's logic works |
| `.claude/settings.json` | valid JSON, one PreToolUse entry. No `matcher` is fine, because the docs say an omitted matcher matches every tool |
| `~/.claude/settings.json`, `~/.claude/remote-settings.json` | no `hooks`, `disableAllHooks` or `allowManagedHooksOnly` |
| `managed-settings.json` | doesn't exist |
| Workspace trust | `~/.claude.json` has no entry for this path, but the docs say trust gates project allow rules, not hooks |

## Fix (approved by Akash and applied 2026-10-13, decision #21)

The hook entry in `.claude/settings.json` is now:

```json
{
  "type": "command",
  "shell": "powershell",
  "command": "python \"$env:CLAUDE_PROJECT_DIR/.claude/hooks/guard.py\"; if ($LASTEXITCODE -eq 0) { exit 0 } else { exit 2 }",
  "timeout": 10,
  "statusMessage": "Checking hard rules"
}
```

What each part does:

- `if ($LASTEXITCODE -eq 0) { exit 0 } else { exit 2 }`. `$LASTEXITCODE` is PowerShell's built-in variable holding the exit code of the last program it ran. Only an explicit 0 means "allow"; everything else, including a crash or `python` not being found (which leaves the variable empty), becomes 2, "block". This is default-deny, the same idea as a security group that drops anything without an allow rule.
- `$env:CLAUDE_PROJECT_DIR` is the project root that Claude Code passes to hooks. The old relative path `.claude/hooks/guard.py` worked only while the current folder was the project root.
- `"shell": "powershell"` pins the shell. If Git Bash were installed later, Claude Code would switch to it by default, and this command is PowerShell syntax that bash can't run.

Tested outside Claude Code with `powershell -NoProfile -Command`, run from `%TEMP%` to show the folder no longer matters:

| Case | Exit code | Wanted |
|---|---|---|
| event the guard blocks (`gh --version`) | 2 | 2 |
| event the guard allows (Read of README.md) | 0 | 0 |
| `python` not found | 2 | 2 |
| guard script missing | 2 | 2 |

Verified live, in the same session, after Claude Code reloaded the changed settings:

| Call | Result |
|---|---|
| PowerShell: `python` reads `settings.json` (an ordinary call) | ran |
| PowerShell `Write-Output "tpp"` | blocked, H1 work-word reason |
| PowerShell `gh --version` | blocked, H2 `gh` reason |
| PowerShell `git commit --dry-run --no-verify` | blocked, H2 hook-skipping reason |
| Glob `**/tpp*` | blocked, H1 path reason |

That also shows Claude Code accepts `"shell": "powershell"` and sets `CLAUDE_PROJECT_DIR` for command hooks.

Verified again in session 4, a fresh session. The settings were loaded at startup, not reloaded mid-session:

| Call | Result |
|---|---|
| PowerShell: `python` prints the hook entry from `settings.json` (an ordinary call) | ran, and printed the fixed entry above |
| PowerShell `Write-Output "tpp"` | blocked, H1 work-word reason |
| PowerShell `gh --version` | blocked, H2 `gh` reason |
| PowerShell `git commit --dry-run --no-verify` | blocked, H2 hook-skipping reason |
| Glob `**/tpp*` | blocked, H1 path reason |

Alternatives considered:

| Option | Why not |
|---|---|
| End with `; exit $LASTEXITCODE` (pass the code through) | Fails open when `python` isn't found: the variable is empty and `exit` with nothing returns 0. Also passes through a Python crash before `main()` starts, which exits 1 |
| Exec form (`command: python`, no shell in between) | Code 2 reaches Claude Code intact, but a crash still exits 1 and is allowed |
| Guard prints a JSON "deny" decision instead of using exit codes | Makes the decision independent of exit codes, but a crash still prints nothing and is allowed |

## Also found

The guard checks the git identity of the session's folder, not of the repo a command targets. `check_git_identity` runs `git -C <session cwd> config user.email`, so `git -C <other repo> commit` is judged by this repo's identity. This was read from the code, not seen live. The personal git hooks cover the gap, because they run inside the target repo. Worth fixing in the same `[A→H]` change or a later one.

## Next

Nothing left for this bug. If the **Also found** gap is fixed later, it is its own `[A→H]` guard change, because it changes the guard.
