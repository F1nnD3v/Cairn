// Renders Cairn's default wallpaper as JPEGs in KDE's wallpaper-package layout.
//
//   node brand/tools/make_wallpaper.js brand/wallpaper/Cairn
//
// Writes contents/images/<W>x<H>.jpg (light) and contents/images_dark/<W>x<H>.jpg (dark).
// Plasma shows images_dark when the colour scheme is dark, which is Cairn's default.
// Needs Playwright (Chromium) because the drawing runs on an HTML canvas.

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT = process.argv[2] || 'brand/wallpaper/Cairn';
const SIZES = [[3840, 2160], [2560, 1600], [1920, 1080]];

const MODES = {
  dark: {
    top: '#191B1F', bottom: '#0E0F12', line: '236,237,239', lineAlpha: 0.2,
    glow: '244,166,42', glowAlpha: 0.22, stoneA: '#5E646D', stoneB: '#9AA0A8', honey: '#F4A62A',
  },
  light: {
    top: '#F9F9FA', bottom: '#E3E5E8', line: '24,25,28', lineAlpha: 0.15,
    glow: '208,130,0', glowAlpha: 0.16, stoneA: '#4A4F57', stoneB: '#80868F', honey: '#D08200',
  },
};

// Runs inside the browser page.
function draw(w, h, m) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  const ctx = c.getContext('2d');

  const g = ctx.createLinearGradient(0, 0, w, h);
  g.addColorStop(0, m.top); g.addColorStop(1, m.bottom);
  ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);

  // Pointy-top honeycomb, the same cell shape as the logo.
  const r = w / 30;
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
  const centre = (col, row) => [col * colStep + ((row & 1) ? colStep / 2 : 0), row * rowStep];

  // The field fades out away from the lower right.
  const fx = 0.78 * w, fy = 0.7 * h, maxD = Math.hypot(w, h) * 0.62;
  ctx.lineWidth = Math.max(1, w / 1920);
  ctx.lineJoin = 'round';
  for (let row = -1; row * rowStep < h + r; row++) {
    for (let col = -1; col * colStep < w + r; col++) {
      const [x, y] = centre(col, row);
      const a = 1 - Math.hypot(x - fx, y - fy) / maxD;
      if (a <= 0) continue;
      hex(x, y, r * 0.9);
      ctx.strokeStyle = `rgba(${m.line},${(a * a * m.lineAlpha).toFixed(3)})`;
      ctx.stroke();
    }
  }

  // The logo, built from real cells of the grid: 3 stones, 2 stones, honey on top.
  const brow = Math.round((0.78 * h) / rowStep);
  const bcol = Math.round((0.8 * w - ((brow & 1) ? colStep / 2 : 0)) / colStep);
  const [X, Y] = centre(bcol, brow);
  const cells = [
    [X - colStep, Y, m.stoneA], [X, Y, m.stoneA], [X + colStep, Y, m.stoneA],
    [X - colStep / 2, Y - rowStep, m.stoneB], [X + colStep / 2, Y - rowStep, m.stoneB],
    [X, Y - 2 * rowStep, m.honey],
  ];
  const gy = Y - 2 * rowStep;
  const rg = ctx.createRadialGradient(X, gy, 0, X, gy, r * 4.5);
  rg.addColorStop(0, `rgba(${m.glow},${m.glowAlpha})`);
  rg.addColorStop(1, `rgba(${m.glow},0)`);
  ctx.fillStyle = rg; ctx.fillRect(X - r * 5, gy - r * 5, r * 10, r * 10);
  for (const [x, y, colour] of cells) {
    hex(x, y, r * 0.84);
    ctx.fillStyle = colour; ctx.fill();
    ctx.strokeStyle = colour; ctx.lineWidth = r * 0.1; ctx.stroke();
  }
  return c.toDataURL('image/jpeg', 0.92);
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const [mode, dir] of [['light', 'images'], ['dark', 'images_dark']]) {
    const outDir = path.join(OUT, 'contents', dir);
    fs.mkdirSync(outDir, { recursive: true });
    for (const [w, h] of SIZES) {
      const url = await page.evaluate(draw.toString().replace(/^function draw/, '(function') + `)(${w}, ${h}, ${JSON.stringify(MODES[mode])})`);
      const file = path.join(outDir, `${w}x${h}.jpg`);
      fs.writeFileSync(file, Buffer.from(url.split(',')[1], 'base64'));
      console.log(file, Math.round(fs.statSync(file).size / 1024) + ' KiB');
    }
  }
  await browser.close();
})();
