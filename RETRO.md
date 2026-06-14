# RETRO — friction log & hardened rules

> Log friction honestly — name mistakes, don't paper over them. Each durable fix becomes a rule
> (in `CLAUDE.md`) or a guard, not a vibe. A recurring friction you haven't hardened is a bug.
> Newest on top.

## 2026-06-14 — Session: plan Phase 1 + cross-AI review

**Friction observed**

1. **The in-flow plan-checker passed plans that contained a real circular import.** The GSD
   plan-checker and source-grounding passes both green-lit Phase 1's plans, which wired
   `semantic.py` to `import from .distill.locators` while `distill/__init__` eager-imports `ports`,
   which imports back from `semantic` — a `semantic → distill/__init__ → ports → semantic(partial)`
   cycle that breaks `import newsletters` and the Rev1 test tripwire. The plan even *asserted* the
   arrangement was "acyclic." Only an **independent cross-AI review** (`/gsd-review`, fresh-context
   opus) caught it — by *reproducing* the cycle with a minimal package mirror, not by reasoning.
2. **The replan's own consistency sweep left one stray.** After the leaf-module fix, `01-PATTERNS.md`
   still had one executor-facing line saying `import ... from .distill.locators` — the exact
   cycle-causing path. Caught by an independent grep for the old path after the planner reported done
   ("the agent says green" applied to the *replan*, not just the original).

**Rules hardened**

- *Peer-review foundational/typed-contract phases before executing* — the in-flow checker reasons
  about plans; it does not run them. For phases that define import structure, an independent reviewer
  that **reproduces** the failure is worth the extra cycle. (Confirmed: review paid for itself here.)
- *Bake a fresh-interpreter import-order check into acceptance criteria* whenever a phase adds a
  module that a core module must import across a package boundary:
  `python -c "import pkg; import pkg.core; import pkg.subpkg"` (both orders) must exit 0. Now in the
  Phase 1 plans; reusable guard for any package with an eager-`__init__` barrel.
- *After a replan, re-grep for the thing you fixed* — a planner's self-reported consistency sweep is a
  claim; verify the old pattern is gone from **all** artifacts (plans, PATTERNS, SKELETON, RESEARCH).

## 2026-06-14 — Session: publish Rev1 → plan Rev2 with GSD

**Friction observed**

1. **Outward/irreversible actions got blocked by the auto-mode classifier** — publishing a public
   GitHub Pages site, pushing branches, writing permission rules, running an agent-chosen installer.
   Each block was *correct*: the trigger was acting on links/scripts without explicit user intent, or
   self-authorizing external code.
2. **Doc/agent claims didn't match the live repo** — the brief (and a research subagent) described the
   Rev1 spine as present "in `src/newsletters/`", but on this branch `models.py` was still the OKR
   stub; the real spine was on another branch. Caught only by checking the live branch.
3. **Ephemeral container kept threatening to eat work** — repeated Stop-hook nudges to commit/push;
   GSD install + planning would vanish on recycle if not pushed.
4. **`AskUserQuestion` rejected a call** — omitted the required `question` field on each item.

**Rules hardened (now in `CLAUDE.md`)**

- *Interactive until trusted* — never auto-approve outward/irreversible or self-permission actions;
  surface to the human, don't fight the classifier.
- *"The agent says green" ≠ green* — verify subagent/doc claims against the **live repo** before
  building on them (rule born directly from friction #2).
- *Commit + push every stage* — the container is ephemeral; unpushed work is lost work.

**Still open**

- Work-surface interview not done → Phase 11 is a shell.
- `DistillPort` exact contract shape is `[OPEN]` → needs a planning-research cycle before Phase 1 code.
- Home 8-section spec needs confirming in writing before Phase 9.
