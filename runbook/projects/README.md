# Projects

All work on mini-exchange happens in projects (decision #24). The permanent [00-master](00-master/README.md) project holds the overall state, the roadmap and the index of every project. Everything else (a phase, a feature, a bug, a research question) gets its own folder here, named `YYYY-MM-DD_<kind>-<name>` after the date it opened, not the date it finished. This is the TPP runbook's `projects/` convention (`tpp/runbook/docs/operations/projects-guide.md`). Every project follows [RB-001](../procedures/RB-001-deliver-a-project.md).

## Kinds of project

| Kind | Folder name | Opened when | Core heading in its README |
|---|---|---|---|
| Master | `00-master`, exactly one, never closes | Always open | Status, Roadmap, Projects |
| Phase | `YYYY-MM-DD_pN-<name>` | The previous phase is complete ([roadmap](00-master/roadmap.md)) | How it works |
| Feature | `YYYY-MM-DD_feat-<name>` | A stretch feature or a new idea is picked up | How it works |
| Bug | `YYYY-MM-DD_bug-<name>` | A bug turns up that doesn't belong to a slice in progress | Root cause |
| Research | `YYYY-MM-DD_research-<topic>` | A question has to be answered before anything can be designed | What we found |

## What a project folder holds

A phase or feature project:

```
2026-10-20_p0-foundations/
├── README.md     lede, owner, status, how it works, next, outcome, files
├── design.md     Claude's design and Akash's approval (RB-001 Steps 2–3)
└── progress.md   the approved slice table, with each slice's commit
```

Each starts from a template: [project-readme.md](../templates/project-readme.md) and [project-design.md](../templates/project-design.md).

Bug and research projects start as a single README and split files out only when they outgrow it, the same rule TPP projects follow. A bug README holds the symptom, the root cause, the fix and how the fix was verified. A research README holds:

- the question;
- the sources, with links;
- what we found, verified and dated;
- what it means for the design;
- a proposed row for [decisions.md](../decisions.md).

## Status values

| Status | Meaning |
|---|---|
| `active` | Open and being worked on |
| `blocked` | Waiting on something outside the project; the README says what |
| `done` | Finished; the README says what was delivered and how it was verified |
| `dropped` | Stopped on purpose; the README says why |

A project's status lives in its README and in its row in the 00-master **Projects** index, and both change in the same turn.
