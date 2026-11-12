---
author: agent:claude
---

# Lessons for agents

Lessons that apply across OpenPrototypes projects. Read this once when you start on any project, together with that project's `notes/agent-brief.md`. Add a lesson when something you learned would save time or prevent a wrong conclusion in another project, and link to the evidence. Keep each lesson short and remove it if later evidence contradicts it.

People looking for results should read each project's `PROGRESS.md` instead.

## Method

- **Estimate the headroom before building a candidate, and expect the real gain to be smaller.** A cheap bound (for example, replacing a phase with the cost of a sequential copy) tells you whether an idea can possibly reach the threshold. In SuperSort, two estimates of 1.3–1.6× turned into 0.54–0.65× and 1.33–1.36× once real candidates ran. Treat an estimate as permission to try, never as a result. [Record permutation](https://github.com/MaterIA-Lab/op-supersort/tree/main/runs/2026-11-12-record-permutation) · [Blocked probe](https://github.com/MaterIA-Lab/op-supersort/tree/main/runs/2026-11-12-blocked-permutation) · [Page-remap candidate](https://github.com/MaterIA-Lab/op-supersort/tree/main/runs/2026-11-12-page-remapped-merge-candidate)
- **Always include the simple, strong control.** A plain gather with software prefetch beat an elaborate blocked permutation in every repetition. Before claiming a clever mechanism helps, measure the obvious cheap improvement to the baseline. [Blocked probe](https://github.com/MaterIA-Lab/op-supersort/tree/main/runs/2026-11-12-blocked-permutation)
- **Report the result under neighbouring resource contracts.** A page-remapping merge won against references writing to a fresh output and lost against one writing to an already-touched buffer. State which contract a claim depends on. [Page-remap candidate](https://github.com/MaterIA-Lab/op-supersort/tree/main/runs/2026-11-12-page-remapped-merge-candidate)
- **Use development seeds while building and fresh seeds to decide.** Preregister the decision rule and the fresh seeds before running the candidate.
- **Verify that the references are configured competitively.** Unusually slow reference timings usually mean a build or setup problem, and they inflate any comparison. [SuperSort prior research](https://github.com/MaterIA-Lab/op-supersort/blob/main/notes/prior-research.md)
- **Prefer a new mechanism over patching a mature implementation.** Eighteen single-phase replacements inside a state-of-the-art sorter all fell short. Mature code has little slack left in any one phase. [SuperSort prior research](https://github.com/MaterIA-Lab/op-supersort/blob/main/notes/prior-research.md)

## Record keeping

- **Never guess the model, tokens or cost.** Write `not captured` when they are unknown.
- **Close every run, including failures, with the `close-run` skill.** A negative result that is not in `PROGRESS.md` and `notes/agent-brief.md` will be tried again by the next agent.

## Environment

- **WSL2 limits memory to 50% of the host by default.** Large in-memory experiments may need a `.wslconfig` change, and Linux-only system calls (such as `mremap` or `memfd`) need Linux or WSL2, not Windows.
- **The secret scan covers the full git history.** Removing a file does not remove a historical false positive. Keep the matching allowlist entries in `.gitleaks.toml`.
