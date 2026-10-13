"""Claude Code PreToolUse hook that enforces the hard rules in CLAUDE.md.

H1: never touch TPP (work) resources.
H2: only the personal GitHub identity commits or pushes.

Claude Code sends each pending tool call to this script as JSON on stdin.
Exit code 0 lets the call run. Exit code 2 blocks it, and Claude Code shows
stderr to Claude as the reason.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

# Gitignored, so the TPP account IDs and personal email never reach git.
LOCAL_CONFIG = Path(__file__).resolve().parent.parent / "hard-rules.local.json"

SHELL_TOOLS = {"Bash", "PowerShell"}
PATH_FIELDS = ("file_path", "path", "notebook_path", "url")
WORK_MCP_PREFIXES = ("mcp__atlassian", "mcp__claude_ai_Atlassian")

# "tpp" at the start of a word (tpp-dev, --profile tpp, \tpp\runbook), or the work Atlassian site.
WORK_WORD = re.compile(r"(?<![a-z0-9])tpp|atlassian", re.IGNORECASE)
# Running the AWS CLI or Terraform, or reading ~/.aws, where the TPP profiles live.
AWS_USE = re.compile(r"(?:^|[;&|(])\s*(?:aws|terraform|terragrunt)\b|\.aws[\\/]", re.IGNORECASE | re.MULTILINE)
# gh is logged in only to the work account (decision #17), so any gh command here would act as work.
GH_USE = re.compile(r"(?:^|[;&|(])\s*gh(?:\.exe)?(?=\s|$)", re.IGNORECASE | re.MULTILINE)
# Skipping the personal git hooks: --no-verify, its short form -n on commit, or overriding hooksPath.
HOOK_BYPASS = re.compile(r"--no-verify|hookspath|\bcommit\b[^;&|\n]*\s-[a-z]*n[a-z]*\b", re.IGNORECASE)
GIT_COMMIT_OR_PUSH = re.compile(r"\bgit\b[^;&|\n]*\b(commit|push)\b", re.IGNORECASE)
IDENTITY_OVERRIDE = re.compile(r"--author|user\.(?:email|name)\s*=|GIT_(?:AUTHOR|COMMITTER)_(?:EMAIL|NAME)", re.IGNORECASE)


def load_config() -> dict:
    if not LOCAL_CONFIG.exists():
        return {}
    return json.loads(LOCAL_CONFIG.read_text(encoding="utf-8"))


def touches_work(text: str, config: dict) -> bool:
    if WORK_WORD.search(text):
        return True
    return any(account_id in text for account_id in config.get("blocked_aws_account_ids", []))


def git(cwd: str, *args: str) -> str:
    result = subprocess.run(["git", "-C", cwd, *args], capture_output=True, encoding="utf-8")
    return result.stdout.strip()


def check_git_identity(command: str, cwd: str, config: dict) -> str | None:
    match = GIT_COMMIT_OR_PUSH.search(command)
    if not match:
        return None
    if IDENTITY_OVERRIDE.search(command):
        return "H2: don't override the git identity inside a command; it comes from git config only."
    expected = config.get("personal_git_email")
    if not expected:
        return f"H2: personal_git_email is not set in {LOCAL_CONFIG}, so commits and pushes are blocked."
    actual = git(cwd, "config", "user.email")
    if actual.lower() != expected.lower():
        return f"H2: git user.email is '{actual}', not the personal address '{expected}'."
    if match.group(1).lower() == "push":
        user = config.get("personal_github_user")
        if not user:
            return f"H2: personal_github_user is not set in {LOCAL_CONFIG}, so pushes are blocked."
        allowed = f"git@github.com:{user}/"
        for line in git(cwd, "remote", "-v").splitlines():
            url = line.split()[1]
            if not url.startswith(allowed):
                return f"H2: remote '{url}' is not the personal GitHub account over SSH ({allowed}...)."
    return None


def reason_to_block(event: dict, config: dict) -> str | None:
    tool = event.get("tool_name", "")
    tool_input = event.get("tool_input") or {}

    if tool.startswith(WORK_MCP_PREFIXES):
        return f"H1: {tool} is a work (TPP) tool."

    if tool in SHELL_TOOLS:
        command = tool_input.get("command", "")
        if touches_work(command, config):
            return "H1: the command mentions TPP, Atlassian or a TPP account ID."
        if AWS_USE.search(command):
            return "H1: AWS CLI, Terraform and ~/.aws stay blocked until P7 sets up the personal AWS profile."
        if GH_USE.search(command):
            return "H2: gh is logged in only to the work account. PRs, merges and CI are Akash's, on github.com."
        if HOOK_BYPASS.search(command):
            return "H2: skipping or redirecting the personal git hooks is not allowed."
        return check_git_identity(command, event.get("cwd") or ".", config)

    fields = PATH_FIELDS + ("pattern",) if tool == "Glob" else PATH_FIELDS
    for field in fields:
        value = str(tool_input.get(field) or "")
        if touches_work(value, config) or AWS_USE.search(value):
            return f"H1: '{value}' is a TPP, Atlassian or AWS config location."
    return None


def main() -> int:
    try:
        event = json.load(sys.stdin.buffer)
        reason = reason_to_block(event, load_config())
    except Exception as error:  # fail closed: a broken guard blocks rather than allows
        reason = f"guard.py itself failed ({error!r}), so the call is blocked to be safe."
    if reason:
        print(f"Blocked by a hard rule in CLAUDE.md. {reason} Stop and tell Akash.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
