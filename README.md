# CS4928 Group Project — Decomposing God Classes (ClassSplitter)

Paper: Chen et al., *A Position-Aware Approach to Decomposing God Classes*, ASE 2024.
Upstream artefact: https://github.com/ClassSplitter/ClassSplitter, imported verbatim into `upstream/`
at commit `459d796` (tag `UPSTREAM_IMPORT`).

## Repository layout

| Path | What lives there |
| --- | --- |
| `upstream/` | Verbatim upstream copy. Edit only when needed, and log each edit in `docs/DEVIATIONS.md`. |
| `repro/` | Our RQ1 reproduction scripts. |
| `results/` | Raw outputs (CSV and JSON environment records). Commit these; they are the evidence. |
| `extension/` | RQ2 work (feature extractor, perturbation experiments, etc.). |
| `design/` | The design / refactoring decision (M4) and its verification. |
| `docs/` | Deviations log, AI-use log, preregistration notes. |

Every change we have made to upstream code is shown by:

```
git diff UPSTREAM_IMPORT -- upstream/
```

## Setup (each team member, once)

1. **Install**
   - Git.
   - Python 3.12.
   - JDK 21 (e.g. Eclipse Temurin). Check that `java -version` works in a *new* terminal, because upstream shells out to `java`.
2. **Clone and create the environment**

   ```bash
   git clone <our-repo-url> && cd <repo>
   python -m venv .venv
   # macOS/Linux: source .venv/bin/activate
   # Windows:     .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Smoke test** (3 classes, under a minute):

   ```bash
   python repro/run_repro.py --ids 1 2 3 --out results/smoke_<yourname>.csv
   ```

   Delete your smoke output afterwards rather than committing it.

## Rules we agreed

- Work on a branch, open a PR, and have one teammate review it before merging to `main`.
- Never move or delete a milestone tag once pushed: `M1_PLAN`, `M2_REPRO`, `PRE_EVENT_A`, `PRE_EVENT_B`, `FINAL`.
- Create milestone tags as annotated tags and push them:

  ```bash
  git tag -a M1_PLAN -m "..."
  git push origin M1_PLAN
  ```

- Don't run two experiments at once from the same checkout. Upstream writes `group.rsf` and `example.rsf` into its own folder on every call.
- Any results we cite must come from a committed script run on a committed state. Check `git_dirty` in the JSON record.
- Log material AI contributions in `docs/AI_USE.md`, one line each.
