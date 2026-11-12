# Lane B learnings

- 2026-11-07: runs go better when the lane starts the dependency install in the background first thing; `pip install -e ".[dev]"` took about ten minutes here and would have blocked validation if started late.
- 2026-11-07: runs go better when every visual change gets a phone-width screenshot; the first render overflowed at 390px while all 659 tests passed.
- 2026-11-07: runs go better when a test brief says what to assert on (the element), not a raw string; the CSS rule `.op-fixture` is always in `<style>`, so "string absent" was the wrong check. The Sonnet subagent caught it and fixed the test, not the code.
- 2026-11-07: JJ prefers decisions written down as candidates and work continuing, over waiting for an answer while JJ is busy (kickoff instruction; followed here).
- 2026-11-07: runs go better when the kickoff names what to do if the client instance is missing; "use labelled fixture, copy nothing" removed the only real blocker.

## Retro (ranked, most severe first)

1. **A layout break reached a commit-ready state with every test green.** The phone
   overflow was caught only because I took a screenshot. Built: `check_phone_width.js` in
   this folder (fails and names the elements if any preview page is wider than 390px).
   Not yet wired into CI; that is a maintainer call.
2. **The stop hook made me commit a subagent's test file before I had reviewed it.** The
   commit message says "not yet reviewed" and I reviewed it right after, but the history
   now holds an unreviewed commit. Better next time: tell the subagent to write into the
   scratchpad, and move the file into the repo once it is reviewed.
3. **My test brief had a wrong assertion** (test 9, see learnings). It cost one subagent
   iteration. I should check a brief's assertions against the code I just wrote.
4. **Slow install:** about ten minutes for `[dev]`. I worked around it by writing code
   and docs in parallel. A setup script for this repo's environment would remove it;
   that is outside this lane.
5. **No real client instance here**, so v0 cannot show real data. This was expected and handled
   (D2), but the view's real value can't be judged until it reads a real client.
