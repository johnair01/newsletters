// Lane B check: the operator view preview must not scroll sideways on a phone.
// Why: the first render overflowed at 390px and all 659 tests still passed; only a
// screenshot caught it. Run from the repo root:
//   node docs/runs/2026-11-07/lanes/B-operator-view/check_phone_width.js
// Exits 1 and names the overflowing elements if any page is wider than the viewport.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const dir = path.join(__dirname, 'preview');
  const files = [path.join(dir, 'operator.html')];
  for (const d of fs.readdirSync(dir, { withFileTypes: true }))
    if (d.isDirectory()) for (const f of fs.readdirSync(path.join(dir, d.name))) files.push(path.join(dir, d.name, f));
  const b = await chromium.launch();
  let bad = 0;
  for (const f of files) {
    const p = await b.newPage({ viewport: { width: 390, height: 900 } });
    await p.goto('file://' + f);
    const r = await p.evaluate(() => ({
      sw: document.documentElement.scrollWidth,
      over: [...document.querySelectorAll('body *')]
        .filter(e => e.getBoundingClientRect().right > window.innerWidth + 2 && !e.closest('.op-scroll'))
        .slice(0, 5).map(e => e.tagName + '.' + e.className),
    }));
    const ok = r.sw <= 390;
    if (!ok) bad++;
    console.log((ok ? 'ok   ' : 'FAIL ') + path.relative(dir, f) + ' scrollWidth=' + r.sw + (ok ? '' : ' ' + r.over.join(', ')));
    await p.close();
  }
  await b.close();
  process.exit(bad ? 1 : 0);
})();
