# RETRO — friction log & hardened rules

> Log friction honestly — name mistakes, don't paper over them. Each durable fix becomes a rule
> (in `CLAUDE.md`) or a guard, not a vibe. A recurring friction you haven't hardened is a bug.
> Newest on top.

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
