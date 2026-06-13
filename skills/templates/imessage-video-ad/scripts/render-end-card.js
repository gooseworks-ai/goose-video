#!/usr/bin/env node
/**
 * render-end-card.js — render the end-card HTML to a static PNG then
 * ffmpeg-convert to a 3.5s MP4. No Ken-Burns — the brand slate must land hard.
 *
 * Two end-card variants ship in this scripts/ folder (pick with --variant):
 *   glow      → end-card.html          (abstract glow + product; playful brands)
 *   photo-bg  → end-card-photo-bg.html  (athlete/persona photo; grounded brands)
 * See references/end-card-recipe.md for which to pick.
 *
 * Injection placeholders handled in either template:
 *   {{BRAND_LOGO_SVG}}  — contents of --logo SVG (XML prolog/doctype stripped). REQUIRED.
 *   {{HERO_IMG_DATA}}   — data: URL of --hero image (photo-bg variant). OPTIONAL.
 *   {{PRODUCT_IMG}}     — <img> for --product (glow variant card image). OPTIONAL.
 *
 * Reads:  --logo <svg>, optional --hero <img>, the chosen variant HTML
 * Writes: <project>/clips/end-card.png, <project>/clips/scene-09-endcard.mp4
 *
 * Usage:
 *   node scripts/render-end-card.js --project ./my-ad --logo ./my-ad/assets/brand-logo.svg
 *   node scripts/render-end-card.js --project ./my-ad --variant photo-bg \
 *     --logo ./my-ad/assets/brand-logo.svg --hero ./my-ad/assets/hero.png
 */
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');
const { chromium } = require('playwright');

function parseArgs(argv) {
  const a = { variant: 'glow' };
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === '--project') a.project = argv[++i];
    else if (argv[i] === '--variant') a.variant = argv[++i];   // glow | photo-bg
    else if (argv[i] === '--logo') a.logo = argv[++i];
    else if (argv[i] === '--hero') a.hero = argv[++i];
    else if (argv[i] === '--product') a.product = argv[++i];
  }
  if (!a.project || !a.logo) {
    console.error('Usage: node scripts/render-end-card.js --project <dir> --logo <svg> [--variant glow|photo-bg] [--hero <img>] [--product <img>]');
    process.exit(1);
  }
  a.project = path.resolve(a.project);
  return a;
}

const ARGS = parseArgs(process.argv);

function readLogoSvg(p) {
  if (!fs.existsSync(p)) {
    throw new Error(`Missing brand logo SVG at ${p}. Drop the real wordmark there (Wikimedia / brandfetch).`);
  }
  let svg = fs.readFileSync(p, 'utf-8');
  // Strip XML prolog + doctype so the SVG can be inlined directly.
  return svg.replace(/<\?xml[\s\S]*?\?>/, '').replace(/<!DOCTYPE[\s\S]*?>/, '').trim();
}

function readImageDataUrl(p) {
  if (!p || !fs.existsSync(p)) return null;
  const buf = fs.readFileSync(p);
  const ext = path.extname(p).slice(1).toLowerCase();
  const mime = ext === 'jpg' ? 'image/jpeg' : `image/${ext}`;
  return `data:${mime};base64,${buf.toString('base64')}`;
}

(async () => {
  const htmlFile = ARGS.variant === 'photo-bg' ? 'end-card-photo-bg.html' : 'end-card.html';
  const html = fs.readFileSync(path.join(__dirname, htmlFile), 'utf-8');

  const logoSvg = readLogoSvg(path.resolve(ARGS.logo));
  let inlinedHtml = html.replace('<!--{{BRAND_LOGO_SVG}}-->', logoSvg);

  const heroDataUrl = readImageDataUrl(ARGS.hero ? path.resolve(ARGS.hero) : null);
  if (heroDataUrl) {
    inlinedHtml = inlinedHtml.replace('<!--{{HERO_IMG_DATA}}-->', heroDataUrl);
  }

  // Glow variant: optional product/hook image inlined as a data URI (setContent
  // has no base URL, so relative <img src> would not load — inline or omit).
  const productDataUrl = readImageDataUrl(ARGS.product ? path.resolve(ARGS.product) : null);
  inlinedHtml = inlinedHtml.replace('<!--{{PRODUCT_IMG}}-->',
    productDataUrl ? `<img src="${productDataUrl}" alt="">` : '');

  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 720, height: 1280 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  await page.setContent(inlinedHtml, { waitUntil: 'load' });
  await page.waitForTimeout(150);
  const outDir = path.join(ARGS.project, 'clips');
  fs.mkdirSync(outDir, { recursive: true });
  const outPng = path.join(outDir, 'end-card.png');
  await page.screenshot({ path: outPng });
  await browser.close();
  console.log('  png  →', path.relative(process.cwd(), outPng));

  // Static still — no Ken-Burns. The brand slate should land hard, not drift.
  // Output at the FRAMED standard 1080x1920 so it matches the chat clip for the
  // xfade in stitch.sh. The PNG is captured at deviceScaleFactor 2 (1440x2560),
  // so this is a crisp downscale. (stitch.sh also scales to the chat dims as a
  // safety net for the deprecated full-bleed 720x1280 path.)
  const outMp4 = path.join(outDir, 'scene-09-endcard.mp4');
  execSync(
    `ffmpeg -y -loop 1 -i "${outPng}" -t 3.5 -r 30 ` +
    `-vf "scale=1080:1920,format=yuv420p" ` +
    `-c:v libx264 -pix_fmt yuv420p -movflags +faststart "${outMp4}"`,
    { stdio: 'pipe' }
  );
  console.log('  mp4  →', path.relative(process.cwd(), outMp4));
})();
