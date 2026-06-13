#!/usr/bin/env node
/**
 * record-master.js — record the FULL iMessage chat as a single continuous
 * Playwright video (no per-scene reloading). The continuous timeline + smooth
 * auto-scroll avoids the three failure modes of scene-by-scene recording:
 *   - micro-flicker at every cut
 *   - "scrolling" faked by dropping older bubbles between scenes
 *   - SFX cues racing the page-load event
 *
 * Reads (from the project dir):
 *   <project>/threads/full-thread.json   the script as data
 *   <project>/timeline.json              the recording schedule + SFX cues
 *   <project>/assets/flat-lay-bg.jpg     framed background (FRAMED mode only)
 * Writes:
 *   <project>/clips/master-chat.mp4      raw chat recording (no audio)
 *   <project>/clips/master-chat.sfx.json deterministic cue list
 *
 * Usage:
 *   node scripts/record-master.js --project ./my-ad
 *   node scripts/record-master.js --project ./my-ad --full-bleed   # DEPRECATED look
 *   node scripts/record-master.js --project ./my-ad --zoom 2.10
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const { chromium } = require('playwright');
// generate.js is bundled in this scripts/ folder (it resolves ./templates/ on its own).
const { renderHTML } = require('./generate.js');

function parseArgs(argv) {
  const a = { framed: true, zoom: 2.10 };
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === '--project') a.project = argv[++i];
    else if (argv[i] === '--full-bleed') a.framed = false;   // DEPRECATED full-bleed look
    else if (argv[i] === '--zoom') a.zoom = parseFloat(argv[++i]);
  }
  if (!a.project) {
    console.error('Usage: node scripts/record-master.js --project <dir> [--full-bleed] [--zoom 2.10]');
    process.exit(1);
  }
  a.project = path.resolve(a.project);
  return a;
}

const ARGS = parseArgs(process.argv);
const PROJECT = ARGS.project;

const VIEW_W = 720;
const VIEW_H = 1280;

// === Output format — FRAMED (Variant B) is the standard ======================
// FRAMED (default): render inside a visible iPhone bezel + Dynamic Island +
// status bar, sitting on a flat-lay desk background. This is the standard look.
// The full-bleed (no-frame) path is DEPRECATED — pass --full-bleed ONLY to
// reproduce the old primitive version. Framed requires <project>/assets/flat-lay-bg.jpg
// (generate it with scripts/gen-flat-lay-bg.py).
const FRAMED = ARGS.framed;
const ZOOM = ARGS.zoom;                  // 514 logical * 2.10 ≈ 1080 output width
const OUT_W = FRAMED ? 1080 : VIEW_W;
const OUT_H = FRAMED ? 1920 : VIEW_H;

function dataURI(p) {
  const buf = fs.readFileSync(p);
  const ext = path.extname(p).slice(1).toLowerCase();
  const mime = ext === 'jpg' ? 'image/jpeg' : `image/${ext}`;
  return `data:${mime};base64,${buf.toString('base64')}`;
}

// Inline image attachments as data: URIs.
function inlineAttachments(thread, baseDir) {
  for (const m of thread.messages || []) {
    if (m.type === 'attachment' && m.src && !m.src.startsWith('data:')) {
      const abs = path.resolve(baseDir, m.src);
      const buf = fs.readFileSync(abs);
      const ext = path.extname(abs).slice(1).toLowerCase();
      const mime = ext === 'jpg' ? 'image/jpeg' : `image/${ext}`;
      m.src = `data:${mime};base64,${buf.toString('base64')}`;
    }
  }
  return thread;
}

// =============================================================================
// TIMELINE — one source of truth for both recording and SFX cue generation.
// Lives in <project>/timeline.json so this script stays generic. Each event is
// { t: <seconds>, kind: <type>, ... }. See references/timeline-schema.md.
//
// kinds:
//   'pop'         — pop in a message bubble already in the DOM (by id)
//   'typing-pop'  — pop in a typing-dots bubble (placeholder for upcoming msg)
//   'typing-swap' — replace a typing bubble in-place with the actual text bubble
//   'composer'    — type characters into the composer over `dur` seconds
//   'composer-clear' — wipe composer (e.g. after send)
//   'scroll'      — smooth-scroll conversation to bottom over `dur` ms
//   'noop'        — hold (tail beat before the end-card cut)
// =============================================================================

function loadTimeline() {
  const p = path.join(PROJECT, 'timeline.json');
  if (!fs.existsSync(p)) {
    console.error(`Missing ${p}. Copy examples/timeline.example.json to <project>/timeline.json and adapt it.`);
    process.exit(1);
  }
  const tl = JSON.parse(fs.readFileSync(p, 'utf-8'));
  return { events: tl.events || [], total: tl.total_duration != null ? tl.total_duration : 17.4 };
}

const { events: TIMELINE, total: TOTAL_DURATION } = loadTimeline();

// =============================================================================
// Build the static HTML (full thread, all messages with pop-pending classes).
// Then inject the driver script that walks TIMELINE in real time.
// =============================================================================

function buildFullThread() {
  const fullPath = path.join(PROJECT, 'threads', 'full-thread.json');
  const thread = JSON.parse(fs.readFileSync(fullPath, 'utf-8'));
  inlineAttachments(thread, path.dirname(fullPath));
  // Mark every message pop-pending. The driver unhides them on schedule.
  for (const m of thread.messages) {
    if (m.type === 'text' || m.type === 'typing' || m.type === 'attachment') {
      m.popState = 'pending';
    }
  }
  thread.composer = { text: '' };
  return thread;
}

function makeDriverScript() {
  // Embedded as a string so we can inject directly into the page.
  return `
  <script>
  (() => {
    const TIMELINE = ${JSON.stringify(TIMELINE)};
    const sleep = ms => new Promise(r => setTimeout(r, ms));
    function findRow(id) { return document.querySelector('[data-anim-id="' + id + '"]'); }

    function popBubble(row) {
      if (!row) return;
      // Bring the row back into layout (was display:none via data-pending).
      row.removeAttribute('data-pending');
      const b = row.classList.contains('bubble') ? row : row.querySelector('.bubble');
      if (b) {
        b.classList.remove('pop-pending');
        void b.offsetWidth;
        b.classList.add('pop-now');
      }
      // Reveal the matching Delivered caption (sits next to the row).
      const id = row.getAttribute('data-anim-id');
      if (id) {
        const cap = document.querySelector('.delivered-caption[data-cap-id="' + id + '"]');
        if (cap) {
          cap.removeAttribute('data-pending');
          cap.classList.remove('pop-pending');
          cap.classList.add('pop-now');
        }
      }
      // attachment row carries pop-pending on the row itself
      if (row.classList.contains('row') && row.classList.contains('pop-pending')) {
        row.classList.remove('pop-pending');
        row.classList.add('pop-now');
      }
    }

    // Replace a typing-dots bubble with the actual text bubble (in place).
    function swapTyping(typId, textId) {
      const typRow = findRow(typId);
      const textRow = findRow(textId);
      if (!typRow || !textRow) return;
      typRow.style.display = 'none';
      popBubble(textRow);
    }

    function smoothScroll(durMs) {
      const conv = document.querySelector('.conversation');
      if (!conv) return;
      // Use the body/window scroll since stage is the scroll container in our layout.
      const scroller = document.scrollingElement || document.documentElement;
      const target = scroller.scrollHeight - scroller.clientHeight;
      const start = scroller.scrollTop;
      if (target <= start + 2) return;
      const t0 = performance.now();
      function tick(t) {
        const p = Math.min(1, (t - t0) / durMs);
        const ease = 1 - Math.pow(1 - p, 3);
        scroller.scrollTop = start + (target - start) * ease;
        if (p < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    }

    async function typeComposer(text, durSec) {
      const span = document.querySelector('[data-composer-text]');
      const input = document.querySelector('.keyboard .input');
      if (!span || !input) return;
      input.classList.add('has-text');
      span.textContent = '';
      const perChar = (durSec * 1000) / Math.max(1, text.length);
      for (const ch of text) {
        span.textContent += ch;
        await sleep(perChar * (0.7 + Math.random() * 0.6));
      }
    }

    function clearComposer() {
      const span = document.querySelector('[data-composer-text]');
      const input = document.querySelector('.keyboard .input');
      if (span) span.textContent = '';
      if (input) input.classList.remove('has-text');
    }

    async function run() {
      const t0 = performance.now();
      for (const ev of TIMELINE) {
        const target = t0 + ev.t * 1000;
        const wait = target - performance.now();
        if (wait > 0) await sleep(wait);
        switch (ev.kind) {
          case 'pop':          popBubble(findRow(ev.id)); break;
          case 'typing-pop':   popBubble(findRow(ev.id)); break;
          case 'typing-swap':  swapTyping(ev.id, ev.toId); break;
          case 'composer':     typeComposer(ev.text, ev.dur); break;
          case 'composer-clear': clearComposer(); break;
          case 'scroll':       smoothScroll(ev.dur); break;
          case 'noop':         break;
        }
      }
    }

    // Mark window as ready when the document has loaded so the recorder can
    // start its real-time clock at the right moment.
    window.__driverReady = true;
    window.__startDriver = run;
  })();
  </script>`;
}

// =============================================================================
// Compute SFX cue list from the TIMELINE (deterministic — no race).
// =============================================================================

function buildCueList() {
  const cues = [];
  for (const ev of TIMELINE) {
    if (ev.sfx) cues.push({ t: ev.t, name: ev.sfx, soft: !!ev.soft });
  }
  return cues;
}

// =============================================================================
// Main
// =============================================================================

async function main() {
  const tmpDir = fs.mkdtempSync(path.join(require('os').tmpdir(), 'imessage-master-'));
  const thread = buildFullThread();
  const html = renderHTML(thread, { mode: FRAMED ? 'with-iphone-frame' : 'with-keyboard' });
  const driverHtml = html.replace('</body>', makeDriverScript() + '\n</body>');

  // Pin the keyboard so it doesn't scroll out of view as the conversation grows.
  // Do this with an extra <style> tag rather than touching the shared CSS.
  const styleOverride = `
    <style>
      /* Master-recording layout: keyboard fixed bottom, conversation scrolls. */
      body.theme-dark .stage { min-height: 100vh; padding-bottom: 80px; }
      body.theme-dark .keyboard {
        position: fixed; left: 0; right: 0; bottom: 0; z-index: 50;
        background: #000; padding: 10px 12px 14px;
      }
      body.theme-dark .conv-header {
        position: fixed; left: 0; right: 0; top: 0; z-index: 40;
        background: rgba(0,0,0,0.75); backdrop-filter: blur(20px);
        /* Tall enough to contain the avatar(44) + 2px gap + name-pill(~22) stack
           without the avatar getting clipped above the viewport top.
           See SKILL.md > Failure modes > "Receiver avatar clipped at top". */
        min-height: 110px; padding-top: 14px; padding-bottom: 10px;
      }
      body.theme-dark .conv-header .center {
        top: 14px;
        transform: translateX(-50%);  /* anchor from top, not transform centroid */
      }
      body.theme-dark .conv-header .center .avatar {
        width: 44px; height: 44px; font-size: 18px;
      }
      body.theme-dark .conv-header .center .name-pill { font-size: 13px; padding: 2px 8px; }
      body.theme-dark .conv-header .left, body.theme-dark .conv-header .right {
        align-self: flex-start; padding-top: 6px;
      }
      body.theme-dark .conversation { padding-top: 124px; }
      /* Pre-render scroll: no jump, just glide. */
      html { scroll-behavior: auto; }
    </style>
  `;
  // Framed (default, Variant B): iPhone bezel on a flat-lay desk background.
  // The atom emits <body class="framed theme-dark"> natively for dark threads.
  const framedStyle = `
    <style>
      html { zoom: ${ZOOM}; scroll-behavior: auto; height: 914px; }
      body.framed { padding: 0; margin: 0; height: 914px; min-height: 914px;
        background: url('${FRAMED ? dataURI(path.join(PROJECT, 'assets', 'flat-lay-bg.jpg')) : ''}') center/cover no-repeat; }
      body.framed.theme-dark .stage { height: 100%; min-height: 100%; }
      body.framed .conv-header { min-height: 66px; }
      body.framed .conv-header .center { transform: translate(-50%, -50%); }
      body.framed .conv-header .center .avatar { width: 42px; height: 42px; font-size: 17px; }
      body.framed .conv-header .center .name-pill { font-size: 13px; }
      body.framed .conversation { flex: 1; overflow: hidden; }
    </style>`;
  // NOTE: `styleOverride` above is the DEPRECATED full-bleed layout (--full-bleed only).
  const finalHtml = driverHtml.replace('</head>', (FRAMED ? framedStyle : styleOverride) + '\n</head>');

  const browser = await chromium.launch();
  const ctx = await browser.newContext({
    viewport: { width: OUT_W, height: OUT_H },
    deviceScaleFactor: 1,
    recordVideo: { dir: tmpDir, size: { width: OUT_W, height: OUT_H } },
  });
  const page = await ctx.newPage();
  await page.setContent(finalHtml, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__driverReady === true, { timeout: 5000 });
  // Kick off the timeline NOW; the page-video has already started.
  await page.evaluate(() => window.__startDriver());
  await page.waitForTimeout(TOTAL_DURATION * 1000);
  const videoPath = await page.video().path();
  await ctx.close();
  await browser.close();

  // Convert webm → mp4 at 30fps yuv420p.
  const outDir = path.join(PROJECT, 'clips');
  fs.mkdirSync(outDir, { recursive: true });
  const outMp4 = path.join(outDir, 'master-chat.mp4');
  execSync(
    `ffmpeg -y -i "${videoPath}" -t ${TOTAL_DURATION} -r 30 ` +
    `-vf "scale=${OUT_W}:${OUT_H}" -c:v libx264 -pix_fmt yuv420p -movflags +faststart "${outMp4}"`,
    { stdio: 'pipe' }
  );
  fs.writeFileSync(outMp4.replace(/\.mp4$/, '.sfx.json'), JSON.stringify(buildCueList(), null, 2));
  fs.rmSync(tmpDir, { recursive: true, force: true });
  console.log(`mp4  → ${path.relative(process.cwd(), outMp4)}`);
  console.log(`sfx  → ${buildCueList().length} cues`);
}

main().catch(e => { console.error(e); process.exit(1); });
