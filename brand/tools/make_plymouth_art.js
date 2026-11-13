// Renders the images for Cairn's boot animation (Plymouth "two-step" theme).
//
//   node brand/tools/make_plymouth_art.js brand/plymouth/cairn
//
// Writes:
//   watermark.png          the Cairn wordmark, centred on screen during boot
//   throbber-0001..0024    three honey cells lighting up in turn (the same motif as the
//                          login splash); Plymouth plays the frames in a loop
// The other images the theme needs (lock, entry, bullet, ...) are copied from Fedora's
// spinner theme during the image build.
// Needs Playwright (Chromium).

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT = process.argv[2] || 'brand/plymouth/cairn';
const WORDMARK = path.resolve(__dirname, '../logo/cairn-wordmark.svg');
const FRAMES = 24;

// Runs in the browser: one throbber frame as a PNG data URL.
function drawFrame(i, frames) {
  const cell = 22, gap = 8, w = 3 * cell + 2 * gap, h = cell;
  const c = document.createElement('canvas');
  c.width = w * 2; c.height = h * 2;          // 2x for crisp edges on high-resolution screens
  const ctx = c.getContext('2d');
  ctx.scale(2, 2);
  const hex = (x, y, r) => {
    ctx.beginPath();
    for (let k = 0; k < 6; k++) {
      const a = (Math.PI / 180) * (-90 + 60 * k);
      const px = x + r * Math.cos(a), py = y + r * Math.sin(a);
      k ? ctx.lineTo(px, py) : ctx.moveTo(px, py);
    }
    ctx.closePath();
  };
  const t = i / frames;                       // 0..1 over one loop
  for (let k = 0; k < 3; k++) {
    // Each cell peaks a third of a loop after the previous one.
    const phase = (t - k / 3 + 1) % 1;
    const glow = Math.max(0, Math.cos(phase * 2 * Math.PI)) ** 2;
    hex(cell / 2 + k * (cell + gap), h / 2, cell / 2);
    ctx.fillStyle = `rgba(244,166,42,${(0.22 + 0.78 * glow).toFixed(3)})`;
    ctx.lineJoin = 'round'; ctx.lineWidth = 2; ctx.strokeStyle = ctx.fillStyle;
    ctx.fill(); ctx.stroke();
  }
  return c.toDataURL('image/png');
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage();

  for (let i = 0; i < FRAMES; i++) {
    const url = await page.evaluate(
      drawFrame.toString().replace(/^function drawFrame/, '(function') + `)(${i}, ${FRAMES})`);
    const name = `throbber-${String(i + 1).padStart(4, '0')}.png`;
    fs.writeFileSync(path.join(OUT, name), Buffer.from(url.split(',')[1], 'base64'));
  }

  // Wordmark, 320 px wide, transparent background (Plymouth draws it over the graphite colour).
  const svg = fs.readFileSync(WORDMARK, 'utf8');
  const vb = svg.match(/viewBox="([^"]+)"/)[1].split(/\s+/).map(Number);
  const width = 320, height = Math.round(width * vb[3] / vb[2]);
  const sized = svg.replace(/<svg([^>]*?)\swidth="[^"]*"\sheight="[^"]*"/, `<svg$1 width="${width}" height="${height}"`);
  await page.setViewportSize({ width, height });
  await page.setContent(`<html><body style="margin:0;background:transparent">${sized}</body></html>`);
  await page.screenshot({ path: path.join(OUT, 'watermark.png'), omitBackground: true, clip: { x: 0, y: 0, width, height } });

  await browser.close();
  console.log(fs.readdirSync(OUT).length, 'files in', OUT);
})();
