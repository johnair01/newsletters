# Phase 3 — Context & Decisions (Content-Addressed Provenance & Faithfulness Gate)

**Goal:** Make traces resistant to source drift and make unfaithful claims structurally unable to
pass as audited — content-address every trace; enforce entailment at the socket boundary for all
backends.

**Requirements:** PROV-01 (content-addressed traces), PROV-02 (faithfulness/entailment gate).

## Decisions (reviewer-approved 2026-06-17, smart-discuss)

1. **Content-addressing scheme** — SHA-256 (stdlib `hashlib`) of the **full Source content**
   (`Source.transcript`), plus **character** offsets (`start`/`end`), plus the **verbatim span text**
   stored in the Trace (the `span` field already exists). Self-verifying: the stored span can be
   re-checked against the offset window of the live source.

2. **STALE detection** — a **computed property**, never a stored mutable flag. A Trace/Claim is
   STALE when the Source's *live* content hash ≠ the hash recorded in the Trace. Deterministic; no
   drift between a flag and reality. Per-claim/per-trace granularity.

3. **Faithfulness gate (no-AI mode)** — **normalized span-containment**: collapse whitespace +
   case-fold, then require the claim text to be contained/supported by its traced evidence span.
   Enforced at the **socket seam** (the injectable faithfulness hook from Phase 1, `semantic.py` /
   the conformance path) so **every** backend passes through it. A claim that cannot be located in
   or entailed by its own trace is routed to `missing[]` — never surfaced as a fact (success
   criterion 3). The gate is **faithful, not suggestive** — it only checks containment, never edits.

4. **Scope & backward-compat** — extend `Trace` with the content-address fields **optionally**
   (so Rev1 sample content + existing tests stay green), and provide a migration/helper that
   computes hashes+offsets for existing sample sources. **AI-mode entailment stays OUT of scope** —
   implement only the deterministic no-AI gate behind the injectable seam (AI entailment is v2,
   AI-01/02). `typer[all]` cleanup from Phase 2 is still deferrable, not part of this phase.

## Key codebase facts (verified against live repo)

- `src/newsletters/semantic.py`: `Source` (id, transcript=content), `Trace` (source_id, locator,
  span), `Claim` (text, evidence: list[Trace], `is_traced`), `Distillation`. The no-auto-publish +
  ≥1-trace-per-published-claim invariants live here.
- Phase 1 added an **injectable faithfulness seam** (conformance suite + `_enforce`-style hook) and
  the coverage manifest / `unextracted[]` contract — the faithfulness gate plugs into that seam,
  it does NOT introduce a parallel enforcement path.
- `locators.py`: typed `Locator` union (`FreeLocator`, `SessionLocator`) — content-address fields
  are additive to `Trace`, orthogonal to the locator.
- AI-optional invariant (Phase 2): the gate is stdlib-only (`hashlib`, string ops); zero AI. The
  import-linter contract + bare-install CI gate must stay green.

## Hard rules in play

- Faithful, not suggestive (the gate checks containment; it must never rewrite/editorialize).
- Every published claim traces to evidence; unsubstantiated → `missing[]`, shown to reviewer.
- AI-optional core — gate is deterministic stdlib; keep import-linter + bare-install green.
- No auto-publish — unchanged; this phase strengthens what "audited" means before the gate.
