// End-to-end tests for DoorIntro in real Chromium (Playwright library, no
// test runner needed). Serves ../site as the web root, exactly as Cloudflare
// Pages would, and intercepts the founders portrait with a test fixture.
//
//   cd door-intro && npm install && npm test
//   SCREENSHOTS=/path/to/dir npm test    # also save timeline screenshots
import { createServer } from 'node:http';
import { readFile, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { extname, join, normalize, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import assert from 'node:assert/strict';

const here = dirname(fileURLToPath(import.meta.url));
const siteRoot = join(here, '../../site');
const pkgRoot = join(here, '..');
const fixture = await readFile(join(here, 'fixtures/test-portrait.jpg'));
const PORTRAIT = '/images/door-intro/arrington-founders.jpg';
const shotsDir = process.env.SCREENSHOTS || '';
if (shotsDir) await mkdir(shotsDir, { recursive: true });

const require = createRequire(import.meta.url);
let chromium;
try {
  ({ chromium } = require('playwright'));
} catch {
  ({ chromium } = require('/opt/node22/lib/node_modules/playwright'));
}

// ------------------------------------------------------------ static server
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.jpg': 'image/jpeg', '.jsx': 'text/javascript' };
const server = createServer(async (req, res) => {
  const url = new URL(req.url, 'http://x');
  let path = decodeURIComponent(url.pathname);
  let base = siteRoot;
  if (path.startsWith('/__pkg/')) { base = pkgRoot; path = path.slice(6); }
  if (path.endsWith('/')) path += 'index.html';
  const file = normalize(join(base, path));
  if (!file.startsWith(base)) { res.writeHead(403).end(); return; }
  try {
    const body = await readFile(file);
    res.writeHead(200, { 'content-type': TYPES[extname(file)] || 'application/octet-stream' });
    res.end(body);
  } catch {
    res.writeHead(404).end('not found');
  }
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const ORIGIN = `http://127.0.0.1:${server.address().port}`;

const browser = await chromium.launch();

// ------------------------------------------------------------------ helpers
async function newPage(opts = {}) {
  const { viewport = { width: 1440, height: 900 }, reducedMotion = 'no-preference', userAgent, portrait = 'ok', initConfig, blockScript, context } = opts;
  const ctx = context || await browser.newContext({ viewport, reducedMotion, userAgent, hasTouch: viewport.width < 800 });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) errors.push(m.text()); });
  await page.route('**' + PORTRAIT, (route) => portrait === 'ok'
    ? route.fulfill({ status: 200, contentType: 'image/jpeg', body: fixture })
    : route.fulfill({ status: 404, body: '' }));
  if (blockScript) await page.route('**/door-intro.js', (r) => r.abort());
  await page.addInitScript((cfg) => {
    window.__events = [];
    document.addEventListener('doorintro:start', () => window.__events.push(['start', performance.now()]));
    document.addEventListener('doorintro:complete', (e) => window.__events.push(['complete', performance.now(), e.detail.reason]));
    window.__cls = 0;
    try {
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) if (!entry.hadRecentInput) window.__cls += entry.value;
      }).observe({ type: 'layout-shift', buffered: true });
    } catch (e) {}
    if (cfg) window.DoorIntroConfig = cfg;
  }, initConfig || null);
  return { ctx, page, errors };
}

const overlay = (page) => page.$('#door-intro');
const waitGone = (page, timeout = 7000) => page.waitForSelector('#door-intro', { state: 'detached', timeout });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const results = [];
async function test(name, fn) {
  const t0 = Date.now();
  try {
    await fn();
    results.push({ name, ok: true });
    console.log(`  ✓ ${name} (${Date.now() - t0} ms)`);
  } catch (e) {
    results.push({ name, ok: false });
    console.log(`  ✗ ${name}\n      ${String(e && e.stack || e).split('\n').slice(0, 4).join('\n      ')}`);
  }
}

// -------------------------------------------------------------------- tests
console.log(`DoorIntro e2e — serving ${siteRoot} at ${ORIGIN}\n`);

for (const [label, viewport] of [['375px mobile', { width: 375, height: 812 }], ['768px tablet', { width: 768, height: 1024 }], ['1440px desktop', { width: 1440, height: 900 }]]) {
  await test(`normal motion plays full sequence at ${label}`, async () => {
    const { ctx, page, errors } = await newPage({ viewport });
    await page.goto(ORIGIN + '/');
    await page.waitForSelector('#door-intro .di-door--left');
    assert.equal((await page.$$('#door-intro .di-door')).length, 2, 'two doors');
    assert.ok(await page.$('#door-intro .di-handle'), 'gold handles rendered');
    const skip = page.getByRole('button', { name: /skip intro/i });
    assert.ok(await skip.isVisible(), 'skip button visible');
    assert.match(await page.textContent('#door-intro .di-welcome'), /Your Future Begins With an Open Door\./);
    assert.match(await page.textContent('#door-intro .di-wordmark'), /Open Doors Financial Group/);
    assert.equal(await page.$eval('html', (h) => h.classList.contains('door-intro-pending')), false, 'pre-paint guard cleared');

    const shot = async (n) => shotsDir && page.screenshot({ path: join(shotsDir, `${viewport.width}-${n}.png`) });
    await sleep(550); await shot('1-closed');
    await page.waitForSelector('#door-intro.di--open', { timeout: 3000 });
    await sleep(700); await shot('2-opening');
    await page.waitForSelector('#door-intro.di--revealed', { timeout: 3000 });
    assert.ok(await page.$('#door-intro.di--img-ready'), 'portrait decoded and shown');
    assert.match(await page.textContent('#door-intro .di-reveal-text'), /Education\. Protection\. Opportunity\. Legacy\./);
    await sleep(250); await shot('3-revealed');
    await waitGone(page);

    const ev = await page.evaluate(() => window.__events);
    const start = ev.find((e) => e[0] === 'start'); const done = ev.find((e) => e[0] === 'complete');
    assert.equal(done[2], 'complete');
    const total = done[1] - start[1];
    assert.ok(total >= 3000 && total <= 5800, `intro took ${Math.round(total)} ms (target 3–5 s)`);
    assert.equal(await page.$eval('html', (h) => h.className.includes('door-intro')), false, 'html classes cleaned');

    // Site works afterwards: no horizontal overflow, CTA clickable, scroll works.
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    assert.ok(overflow <= 0, `no horizontal scroll (overflow ${overflow}px)`);
    const btn = await page.$('.hero .btn');
    const box = await btn.boundingBox();
    const hit = await page.evaluate(([x, y]) => document.elementFromPoint(x, y)?.className, [box.x + box.width / 2, box.y + box.height / 2]);
    assert.equal(hit, 'btn', 'CTA is the top element under the pointer');
    await btn.click();
    assert.equal(new URL(page.url()).hash, '#services', 'CTA navigates');
    if (await page.evaluate(() => document.documentElement.scrollHeight > window.innerHeight + 50)) {
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.mouse.wheel(0, 600);
      await sleep(300);
      assert.ok(await page.evaluate(() => window.scrollY) > 0, 'page scrolls after intro');
    }
    assert.ok(await page.getByRole('button', { name: 'Replay intro' }).isVisible(), 'replay button shown');
    const cls = await page.evaluate(() => window.__cls);
    assert.ok(cls < 0.01, `no layout shift (CLS ${cls})`);
    assert.deepEqual(errors, [], 'no console errors');
    await ctx.close();
  });
}

await test('plays once per session (sessionStorage) and again in a new session', async () => {
  const { ctx, page } = await newPage();
  await page.goto(ORIGIN + '/');
  await page.waitForSelector('#door-intro');
  await page.getByRole('button', { name: /skip intro/i }).click();
  await waitGone(page, 2000);
  assert.ok(await page.evaluate(() => sessionStorage.getItem('door-intro:seen')), 'seen flag stored');
  await page.reload();
  await sleep(600);
  assert.equal(await overlay(page), null, 'no replay of intro on reload');
  assert.equal(await page.$eval('html', (h) => h.classList.contains('door-intro-pending')), false, 'no pre-paint cover on reload');
  assert.ok(await page.getByRole('button', { name: 'Replay intro' }).isVisible(), 'replay still offered');
  await ctx.close();
  const fresh = await newPage();
  await fresh.page.goto(ORIGIN + '/');
  await fresh.page.waitForSelector('#door-intro');
  await fresh.ctx.close();
});

await test('skip button ends the intro immediately', async () => {
  const { ctx, page } = await newPage();
  await page.goto(ORIGIN + '/');
  await page.waitForSelector('#door-intro');
  await sleep(400);
  const t0 = Date.now();
  await page.getByRole('button', { name: 'Skip intro and go to the website' }).click();
  await waitGone(page, 1500);
  assert.ok(Date.now() - t0 < 1200, 'gone in under 1.2 s');
  const ev = await page.evaluate(() => window.__events);
  assert.equal(ev.at(-1)[2], 'skip');
  await ctx.close();
});

await test('keyboard: skip is first tab stop, Enter skips, Escape skips, focus is not trapped', async () => {
  const { ctx, page } = await newPage();
  await page.goto(ORIGIN + '/');
  await page.waitForSelector('#door-intro');
  await page.keyboard.press('Tab');
  assert.ok(await page.evaluate(() => document.activeElement.classList.contains('di-skip')), 'skip button focused first');
  await page.keyboard.press('Tab');
  assert.equal(await page.evaluate(() => document.activeElement.closest('#door-intro')), null, 'Tab leaves the overlay');
  await page.keyboard.press('Shift+Tab');
  await page.keyboard.press('Enter');
  await waitGone(page, 1500);
  assert.notEqual(await page.evaluate(() => document.activeElement.className), 'di-skip');
  // Escape on a forced replay.
  await page.goto(ORIGIN + '/?doorintro=1');
  await page.waitForSelector('#door-intro');
  await page.keyboard.press('Escape');
  await waitGone(page, 1500);
  await ctx.close();
});

await test('clicking or scrolling anywhere skips (input never trapped)', async () => {
  const { ctx, page } = await newPage({ initConfig: { playMode: 'always' } });
  await page.goto(ORIGIN + '/');
  await page.waitForSelector('#door-intro');
  await page.mouse.click(300, 300);
  await waitGone(page, 1500);
  await page.reload();
  await page.waitForSelector('#door-intro');
  await page.mouse.wheel(0, 400);
  await waitGone(page, 1500);
  await ctx.close();
});

await test('replay button and [data-door-intro-replay] replay the intro', async () => {
  const { ctx, page } = await newPage();
  await page.goto(ORIGIN + '/');
  await page.waitForSelector('#door-intro');
  await page.keyboard.press('Escape');
  await waitGone(page, 1500);
  await page.getByRole('button', { name: 'Replay intro' }).click();
  await page.waitForSelector('#door-intro .di-door');
  assert.equal(await page.$('.di-replay'), null, 'replay button hidden while playing');
  await page.keyboard.press('Escape');
  await waitGone(page, 1500);
  await page.evaluate(() => {
    const a = document.createElement('a');
    a.href = '#'; a.textContent = 'Watch the intro again'; a.setAttribute('data-door-intro-replay', '');
    document.querySelector('footer').appendChild(a);
  });
  await page.click('[data-door-intro-replay]');
  await page.waitForSelector('#door-intro');
  await page.keyboard.press('Escape');
  await waitGone(page, 1500);
  await ctx.close();
});

await test('reduced motion: no 3D doors, short opacity-only fade, still skippable', async () => {
  const { ctx, page, errors } = await newPage({ reducedMotion: 'reduce', viewport: { width: 375, height: 812 } });
  await page.goto(ORIGIN + '/');
  await page.waitForSelector('#door-intro.di-reduced');
  assert.equal(await page.$('#door-intro .di-door'), null, 'no doors rendered');
  if (shotsDir) { await sleep(500); await page.screenshot({ path: join(shotsDir, '375-reduced.png') }); }
  await waitGone(page, 3500);
  const ev = await page.evaluate(() => window.__events);
  const total = ev.find((e) => e[0] === 'complete')[1] - ev.find((e) => e[0] === 'start')[1];
  assert.ok(total < 2800, `reduced intro ${Math.round(total)} ms`);
  assert.deepEqual(errors, []);
  await ctx.close();
});

await test('reducedMotion: "skip" bypasses the intro entirely', async () => {
  const { ctx, page } = await newPage({ reducedMotion: 'reduce', initConfig: { reducedMotion: 'skip' } });
  await page.goto(ORIGIN + '/');
  await sleep(500);
  assert.equal(await overlay(page), null);
  assert.equal(await page.$eval('html', (h) => h.classList.contains('door-intro-pending')), false);
  await ctx.close();
});

await test('playMode "always" replays on reload; "once" persists in localStorage', async () => {
  const a = await newPage({ initConfig: { playMode: 'always' } });
  await a.page.goto(ORIGIN + '/');
  await a.page.waitForSelector('#door-intro'); await a.page.keyboard.press('Escape'); await waitGone(a.page, 1500);
  await a.page.reload();
  await a.page.waitForSelector('#door-intro');
  await a.ctx.close();
  const b = await newPage({ initConfig: { playMode: 'once' } });
  await b.page.goto(ORIGIN + '/');
  await b.page.waitForSelector('#door-intro'); await b.page.keyboard.press('Escape'); await waitGone(b.page, 1500);
  assert.ok(await b.page.evaluate(() => localStorage.getItem('door-intro:seen')));
  await b.page.evaluate(() => sessionStorage.clear());
  await b.page.reload(); await sleep(500);
  assert.equal(await overlay(b.page), null, '"once" survives a new session');
  await b.ctx.close();
});

await test('URL overrides: ?doorintro=0 disables, ?doorintro=1 forces', async () => {
  const { ctx, page } = await newPage();
  await page.goto(ORIGIN + '/?doorintro=0');
  await sleep(500);
  assert.equal(await overlay(page), null);
  assert.equal(await page.$eval('html', (h) => h.classList.contains('door-intro-pending')), false);
  await page.goto(ORIGIN + '/?doorintro=1');
  await page.waitForSelector('#door-intro');
  await ctx.close();
});

await test('crawlers see the untouched page (no overlay, no cover, no replay button)', async () => {
  const { ctx, page } = await newPage({ userAgent: 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)' });
  await page.goto(ORIGIN + '/');
  await sleep(500);
  assert.equal(await overlay(page), null);
  assert.equal(await page.$('.di-replay'), null);
  assert.equal(await page.$eval('html', (h) => h.classList.contains('door-intro-pending')), false);
  assert.match(await page.textContent('h1'), /Arrington Abundance Architects/);
  await ctx.close();
});

await test('missing portrait falls back to the branded scene without errors', async () => {
  const { ctx, page, errors } = await newPage({ portrait: 'missing' });
  await page.goto(ORIGIN + '/');
  await page.waitForSelector('#door-intro.di--no-img', { timeout: 3000 });
  assert.ok(await page.isVisible('#door-intro .di-fallback'), 'fallback scene visible');
  await waitGone(page);
  assert.deepEqual(errors, []);
  await ctx.close();
});

await test('if door-intro.js fails to load, the pre-paint cover removes itself within 3 s', async () => {
  const { ctx, page } = await newPage({ blockScript: true });
  await page.goto(ORIGIN + '/');
  const before = await page.evaluate(() => getComputedStyle(document.documentElement, '::before').visibility);
  assert.equal(before, 'visible', 'cover painted while waiting');
  await sleep(3300);
  const after = await page.evaluate(() => getComputedStyle(document.documentElement, '::before').visibility);
  assert.equal(after, 'hidden', 'cover gone after failsafe');
  await page.click('.hero .btn');
  assert.equal(new URL(page.url()).hash, '#services');
  await ctx.close();
});

await test('existing page handlers and analytics listeners keep working', async () => {
  const { ctx, page } = await newPage();
  await page.addInitScript(() => {
    window.__clicks = 0;
    document.addEventListener('click', (e) => { if (e.target.closest('.btn')) window.__clicks++; });
  });
  await page.goto(ORIGIN + '/');
  await waitGone(page);
  await page.click('.hero .btn');
  assert.equal(await page.evaluate(() => window.__clicks), 1);
  assert.equal(await page.evaluate(() => document.querySelectorAll('section, header, footer').length), 4, 'page structure untouched');
  await ctx.close();
});

await test('sound never autoplays; it plays only after the visitor presses the toggle', async () => {
  const { ctx, page } = await newPage({ initConfig: { soundUrl: '/__pkg/tests/fixtures/silence.wav', playMode: 'always' } });
  await page.addInitScript(() => {
    window.__plays = 0;
    const orig = HTMLMediaElement.prototype.play;
    HTMLMediaElement.prototype.play = function () { window.__plays++; return orig.call(this).catch(() => {}); };
  });
  await page.goto(ORIGIN + '/');
  await page.waitForSelector('#door-intro .di-sound');
  await sleep(800);
  assert.equal(await page.evaluate(() => window.__plays), 0, 'no autoplay');
  await page.click('#door-intro .di-sound');
  assert.equal(await page.evaluate(() => window.__plays), 1);
  assert.ok(await overlay(page), 'pressing sound does not skip the intro');
  await ctx.close();
});

await test('JS API: destroy() removes everything; reset() clears the seen flag', async () => {
  const { ctx, page } = await newPage();
  await page.goto(ORIGIN + '/');
  await page.waitForSelector('#door-intro');
  await page.evaluate(() => window.DoorIntro.destroy());
  assert.equal(await overlay(page), null);
  assert.equal(await page.$('.di-replay'), null);
  assert.equal(await page.evaluate(() => window.DoorIntro.isPlaying()), false);
  await page.evaluate(() => { sessionStorage.setItem('door-intro:seen', '1'); window.DoorIntro.reset(); });
  assert.equal(await page.evaluate(() => sessionStorage.getItem('door-intro:seen')), null);
  await ctx.close();
});

await test('playground: neutral preset, glass and modern door styles render and play', async () => {
  const { ctx, page, errors } = await newPage({ viewport: { width: 768, height: 1024 } });
  await page.goto(ORIGIN + '/__pkg/demo/index.html');
  await sleep(300);
  assert.equal(await overlay(page), null, 'data-auto-init="false" respected');
  for (const style of ['glass', 'modern']) {
    await page.selectOption('select[name=preset]', 'neutral');
    await page.selectOption('select[name=doorStyle]', style);
    await page.fill('input[name=brandName]', 'Acme Advisors');
    await page.click('button[type=submit]');
    await page.waitForSelector(`#door-intro.di-style-${style} .di-door`);
    if (shotsDir) { await sleep(600); await page.screenshot({ path: join(shotsDir, `768-style-${style}.png`) }); }
    assert.match(await page.textContent('#door-intro .di-wordmark'), /Acme Advisors/);
    await page.keyboard.press('Escape');
    await waitGone(page, 1500);
  }
  assert.match(await page.textContent('#out'), /"doorStyle": "modern"/);
  assert.deepEqual(errors, []);
  await ctx.close();
});

if (existsSync(join(here, 'react-smoke/dist/bundle.js'))) {
  await test('React component mounts under StrictMode, plays once, cleans up on unmount', async () => {
    const { ctx, page, errors } = await newPage();
    await page.goto(ORIGIN + '/__pkg/tests/react-smoke/index.html');
    await page.waitForSelector('#door-intro .di-door');
    assert.equal((await page.$$('#door-intro')).length, 1, 'exactly one overlay under StrictMode');
    await page.evaluate(() => window.__unmount());
    await sleep(50);
    assert.equal(await overlay(page), null, 'overlay removed on unmount');
    assert.deepEqual(errors, []);
    await ctx.close();
  });
}

await browser.close();
server.close();
const failed = results.filter((r) => !r.ok).length;
console.log(`\n${results.length - failed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
