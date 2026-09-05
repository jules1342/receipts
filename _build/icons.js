// Generates app/icon-192.png and app/icon-512.png with no dependencies:
// a navy rounded square with a white receipt (zig-zag bottom edge) and three grey lines.
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

const crcTable = (() => { const t = []; for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; } return t; })();
const crc32 = (buf) => { let c = 0xffffffff; for (let i = 0; i < buf.length; i++) c = crcTable[(c ^ buf[i]) & 0xff] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; };
const chunk = (type, data) => { const len = Buffer.alloc(4); len.writeUInt32BE(data.length); const td = Buffer.concat([Buffer.from(type), data]); const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(td)); return Buffer.concat([len, td, crc]); };

function png(size, pixel) {
  const raw = Buffer.alloc((size * 3 + 1) * size);
  for (let y = 0; y < size; y++) {
    raw[y * (size * 3 + 1)] = 0;
    for (let x = 0; x < size; x++) {
      const [r, g, b] = pixel(x, y);
      const o = y * (size * 3 + 1) + 1 + x * 3;
      raw[o] = r; raw[o + 1] = g; raw[o + 2] = b;
    }
  }
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(size, 0); ihdr.writeUInt32BE(size, 4);
  ihdr[8] = 8; ihdr[9] = 2; ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0;
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ihdr), chunk('IDAT', zlib.deflateSync(raw)), chunk('IEND', Buffer.alloc(0))]);
}

const NAVY = [31, 58, 95], WHITE = [250, 250, 248], GREY = [170, 178, 190];
function draw(size) {
  const s = size;
  const px = (x, y) => {
    // rounded square background
    const r = s * 0.2;
    const inCorner = (cx, cy) => Math.hypot(x - cx, y - cy) > r;
    if ((x < r && y < r && inCorner(r, r)) || (x >= s - r && y < r && inCorner(s - r, r)) || (x < r && y >= s - r && inCorner(r, s - r)) || (x >= s - r && y >= s - r && inCorner(s - r, s - r))) return [0, 0, 0];
    // receipt body
    const left = s * 0.28, right = s * 0.72, top = s * 0.18, bottom = s * 0.80;
    if (x >= left && x < right && y >= top && y < bottom) {
      const zig = s * 0.05;
      const inZig = y > bottom - zig && Math.abs(((x - left) % (zig * 2)) - zig) / zig * zig < (bottom - y);
      if (y > bottom - zig && !inZig) return NAVY;
      // text lines
      const lineH = s * 0.035;
      for (const ly of [0.30, 0.38, 0.46]) {
        const yy = s * ly;
        if (y >= yy && y < yy + lineH && x >= left + s * 0.06 && x < right - s * 0.06) return GREY;
      }
      const yy = s * 0.58;
      if (y >= yy && y < yy + lineH * 1.3 && x >= left + s * 0.06 && x < left + s * 0.24) return NAVY;
      return WHITE;
    }
    return NAVY;
  };
  return png(s, px);
}

const out = path.join(__dirname, '..', 'app');
for (const s of [192, 512]) {
  fs.writeFileSync(path.join(out, `icon-${s}.png`), draw(s));
  console.log('wrote', `icon-${s}.png`);
}
