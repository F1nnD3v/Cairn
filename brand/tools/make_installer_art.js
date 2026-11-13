// Renders the artwork for Cairn's installer (Anaconda) sidebar.
//
//   node brand/tools/make_installer_art.js brand/installer/pixmaps
//
// Writes:
//   sidebar-bg.png       400x2000, the sidebar background (honeycomb + the Cairn cells)
//   sidebar-logo.png     the wordmark at 1x (160 px wide)
//   sidebar-logo@2x.png  the wordmark at 2x, for high-resolution screens
// Needs Playwright (Chromium).

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT = process.argv[2] || 'brand/installer/pixmaps';
const WORDMARK = path.resolve(__dirname, '../logo/cairn-wordmark.svg');

const C = {
  top: '#16171A', bottom: '#0E0F12', line: '236,237,239',
  stoneA: '#5E646D', stoneB: '#9AA0A8', honey: '#F4A62A', glow: '244,166,42',
};

// Runs inside the browser page.
function drawSidebar(w, h, c) {
  const cv = document.createElement('canvas');
  cv.width = w; cv.height = h;
  const ctx = cv.getContext('2d');
  const g = ctx.createLinearGradient(0, 0, 0, h);
  g.addColorStop(0, c.top); g.addColorStop(1, c.bottom);
  ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);

  const r = w / 7.5;
  const colStep = Math.sqrt(3) * r, rowStep = 1.5 * r;
  const hex = (x, y, rad) => {
    ctx.beginPath();
    for (let k = 0; k < 6; k++) {
      const a = (Math.PI / 180) * (-90 + 60 * k);
      const px = x + rad * Math.cos(a), py = y + rad * Math.sin(a);
      k ? ctx.lineTo(px, py) : ctx.moveTo(px, py);
    }
    ctx.closePath();
  };
  // Anchor the grid so the bottom-centre cell sits on a lattice point.
  const X0 = w / 2, Y0 = h - 2.4 * r;
  const centre = (col, row) => [X0 + col * colStep + ((row & 1) ? colStep / 2 : 0), Y0 - row * rowStep];

  // Honeycomb that fades out towards the top.
  ctx.lineWidth = 2; ctx.lineJoin = 'round';
  for (let row = -2; row * rowStep < h + r; row++) {
    for (let col = -4; col <= 4; col++) {
      const [x, y] = centre(col, row);
      const a = Math.max(0, 1 - (h - y) / (h * 0.55));
      if (a <= 0) continue;
      hex(x, y, r * 0.9);
      ctx.strokeStyle = `rgba(${c.line},${(a * a * 0.18).toFixed(3)})`;
      ctx.stroke();
    }
  }

  // The Cairn cells: 3 stones, 2 stones, honey on top.
  const cells = [
    [X0 - colStep, Y0, c.stoneA], [X0, Y0, c.stoneA], [X0 + colStep, Y0, c.stoneA],
    [X0 - colStep / 2, Y0 - rowStep, c.stoneB], [X0 + colStep / 2, Y0 - rowStep, c.stoneB],
    [X0, Y0 - 2 * rowStep, c.honey],
  ];
  const gy = Y0 - 2 * rowStep;
  const rg = ctx.createRadialGradient(X0, gy, 0, X0, gy, r * 4);
  rg.addColorStop(0, `rgba(${c.glow},0.22)`); rg.addColorStop(1, `rgba(${c.glow},0)`);
  ctx.fillStyle = rg; ctx.fillRect(0, gy - r * 4, w, r * 8);
  for (const [x, y, colour] of cells) {
    hex(x, y, r * 0.84);
    ctx.fillStyle = colour; ctx.fill();
    ctx.strokeStyle = colour; ctx.lineWidth = r * 0.1; ctx.stroke();
  }
  return cv.toDataURL('image/png');
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage();

  const url = await page.evaluate(
    drawSidebar.toString().replace(/^function drawSidebar/, '(function') + `)(400, 2000, ${JSON.stringify(C)})`);
  fs.writeFileSync(path.join(OUT, 'sidebar-bg.png'), Buffer.from(url.split(',')[1], 'base64'));

  // The wordmark, rendered from the SVG on a transparent background.
  const svg = fs.readFileSync(WORDMARK, 'utf8');
  const vb = svg.match(/viewBox="([^"]+)"/)[1].split(/\s+/).map(Number);
  for (const [name, width] of [['sidebar-logo.png', 160], ['sidebar-logo@2x.png', 320]]) {
    const height = Math.round(width * vb[3] / vb[2]);
    const sized = svg.replace(/<svg([^>]*?)\swidth="[^"]*"\sheight="[^"]*"/, `<svg$1 width="${width}" height="${height}"`);
    await page.setViewportSize({ width, height });
    await page.setContent(`<html><body style="margin:0;background:transparent">${sized}</body></html>`);
    await page.screenshot({ path: path.join(OUT, name), omitBackground: true, clip: { x: 0, y: 0, width, height } });
  }
  await browser.close();
  for (const f of fs.readdirSync(OUT)) console.log(path.join(OUT, f), fs.statSync(path.join(OUT, f)).size, 'bytes');
})();
