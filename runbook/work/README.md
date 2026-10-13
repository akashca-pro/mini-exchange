# Work

Every unit of work gets its own folder here, named `YYYY-MM-DD_<name>` after the date it opened, not the date it finished. This is the TPP runbook's `projects/` convention (`tpp/runbook/docs/operations/projects-guide.md`). Each folder starts from [templates/work-readme.md](../templates/work-readme.md).

## Kinds of work

| Kind | Name pattern | Opened when | Core heading in its README |
|---|---|---|---|
| Phase | `YYYY-MM-DD_pN-<name>` | [RB-001](../procedures/RB-001-build-a-phase.md) Step 1 | How it works |
| Feature | `YYYY-MM-DD_feat-<name>` | A stretch feature or a new idea is picked up | How it works |
| Research | `YYYY-MM-DD_research-<topic>` | A question has to be answered before anything can be designed | What we found |
| Bug | `YYYY-MM-DD_bug-<name>` | A real bug turns up that doesn't belong to a slice in progress | Root cause |

A phase folder looks like this:

```
2026-10-20_p1-matching-engine/
├── README.md       lede, status, primer, retro, next
├── design.md       Akash's one-pager and Claude's review
├── progress.md     slice table, predictions, surprises
├── teach-back.md   Akash's explanations and Claude's corrections
└── drills/         one report per drill (RB-002)
```

A research folder answers one question. Its README holds:

- the question;
- the sources, with links;
- what we found, verified and dated;
- what it means for our design;
- a proposed row for [decisions.md](../decisions.md).

Feature and bug folders start as a single README and split files out only when they outgrow it, the same rule TPP projects follow.

## Index

| Folder | Kind | Status |
|---|---|---|
| [2026-10-13_bug-guard-not-firing](2026-10-13_bug-guard-not-firing/README.md) | Bug | `done`: fix verified mid-session and in a fresh session |
