/* ============ 1. 颜色解析 ============ */

const clamp = (v, min, max) => Math.min(max, Math.max(min, v));

// 常用颜色名兜底（linear-gradient 里可能写 white / black / transparent）
const NAMED_COLORS = {
  transparent: { r: 0, g: 0, b: 0, a: 0 },
  white:   { r: 255, g: 255, b: 255, a: 1 },
  black:   { r: 0,   g: 0,   b: 0,   a: 1 },
  silver:  { r: 192, g: 192, b: 192, a: 1 },
  gray:    { r: 128, g: 128, b: 128, a: 1 },
  grey:    { r: 128, g: 128, b: 128, a: 1 },
  red:     { r: 255, g: 0,   b: 0,   a: 1 },
  maroon:  { r: 128, g: 0,   b: 0,   a: 1 },
  yellow:  { r: 255, g: 255, b: 0,   a: 1 },
  olive:   { r: 128, g: 128, b: 0,   a: 1 },
  lime:    { r: 0,   g: 255, b: 0,   a: 1 },
  green:   { r: 0,   g: 128, b: 0,   a: 1 },
  aqua:    { r: 0,   g: 255, b: 255, a: 1 },
  cyan:    { r: 0,   g: 255, b: 255, a: 1 },
  teal:    { r: 0,   g: 128, b: 128, a: 1 },
  blue:    { r: 0,   g: 0,   b: 255, a: 1 },
  navy:    { r: 0,   g: 0,   b: 128, a: 1 },
  fuchsia: { r: 255, g: 0,   b: 255, a: 1 },
  magenta: { r: 255, g: 0,   b: 255, a: 1 },
  purple:  { r: 128, g: 0,   b: 128, a: 1 },
  orange:  { r: 255, g: 165, b: 0,   a: 1 },
  pink:    { r: 255, g: 192, b: 203, a: 1 },
  brown:   { r: 165, g: 42,  b: 42,  a: 1 },
  gold:    { r: 255, g: 215, b: 0,   a: 1 },
  indigo:  { r: 75,  g: 0,   b: 130, a: 1 },
  violet:  { r: 238, g: 130, b: 238, a: 1 },
};

// 一次性扫描出所有颜色 token：#fff / rgb(...) / hsl(...) / 颜色名
const COLOR_TOKEN_RE = new RegExp(
  [
    '#[0-9a-fA-F]{3,8}\\b',
    '(?:rgba?|hsla?)\\([^)]*\\)',
    '\\b(?:' + Object.keys(NAMED_COLORS).join('|') + ')\\b',
  ].join('|'),
  'gi'
);

function parseHex(hex) {
  let h = hex.slice(1);
  if (h.length === 3 || h.length === 4) {
    h = h.split('').map((c) => c + c).join('');
  }
  if (h.length !== 6 && h.length !== 8) return null;
  return {
    r: parseInt(h.slice(0, 2), 16),
    g: parseInt(h.slice(2, 4), 16),
    b: parseInt(h.slice(4, 6), 16),
    a: h.length === 8 ? parseInt(h.slice(6, 8), 16) / 255 : 1,
  };
}

const splitArgs = (body) => body.trim().split(/[\s,/]+/).filter(Boolean);

function parseChannel(v) {
  const n = parseFloat(v);
  if (Number.isNaN(n)) return null;
  return v.endsWith('%') ? clamp((n / 100) * 255, 0, 255) : clamp(n, 0, 255);
}

function parseAlpha(v) {
  const n = parseFloat(v);
  if (Number.isNaN(n)) return 1;
  return v.endsWith('%') ? clamp(n / 100, 0, 1) : clamp(n, 0, 1);
}

function parseRgbArgs(parts) {
  if (parts.length < 3) return null;
  const r = parseChannel(parts[0]);
  const g = parseChannel(parts[1]);
  const b = parseChannel(parts[2]);
  if (r === null || g === null || b === null) return null;
  return { r, g, b, a: parts[3] !== undefined ? parseAlpha(parts[3]) : 1 };
}

function parseHslArgs(parts) {
  if (parts.length < 3) return null;
  const h = parseFloat(parts[0]);
  const s = clamp(parseFloat(parts[1]) / 100, 0, 1);
  const l = clamp(parseFloat(parts[2]) / 100, 0, 1);
  if (Number.isNaN(h) || Number.isNaN(s) || Number.isNaN(l)) return null;

  const c = (1 - Math.abs(2 * l - 1)) * s;
  const hp = (((h % 360) + 360) % 360) / 60;
  const x = c * (1 - Math.abs((hp % 2) - 1));
  let r1, g1, b1;
  if (hp < 1) [r1, g1, b1] = [c, x, 0];
  else if (hp < 2) [r1, g1, b1] = [x, c, 0];
  else if (hp < 3) [r1, g1, b1] = [0, c, x];
  else if (hp < 4) [r1, g1, b1] = [0, x, c];
  else if (hp < 5) [r1, g1, b1] = [x, 0, c];
  else [r1, g1, b1] = [c, 0, x];
  const m = l - c / 2;

  return {
    r: (r1 + m) * 255,
    g: (g1 + m) * 255,
    b: (b1 + m) * 255,
    a: parts[3] !== undefined ? parseAlpha(parts[3]) : 1,
  };
}

function parseColorToken(token) {
  const t = token.toLowerCase();
  if (NAMED_COLORS[t]) return { ...NAMED_COLORS[t] };
  if (t[0] === '#') return parseHex(t);

  const m = t.match(/^(rgba?|hsla?)\(([^)]*)\)$/);
  if (!m) return null;
  const parts = splitArgs(m[2]);
  return m[1].startsWith('rgb') ? parseRgbArgs(parts) : parseHslArgs(parts);
}

/* ============ 2. 亮度计算（WCAG 相对亮度） ============ */

function srgbToLinear(c) {
  c /= 255;
  return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}

function relativeLuminance({ r, g, b }) {
  return (
    0.2126 * srgbToLinear(r) +
    0.7152 * srgbToLinear(g) +
    0.0722 * srgbToLinear(b)
  );
}

/* ============ 3. 主函数 ============ */

/**
 * 判断一个 CSS 颜色值是亮色还是暗色
 * 支持：#fff / #ffffff / #ffffffff / rgb() / rgba() / hsl() / hsla() /
 *       linear-gradient(...) / 常用颜色名
 *
 * @param {string} str   CSS 颜色值
 * @param {number} [threshold=0.4] 亮度阈值（0~1），越大越"偏爱"亮色
 * @returns {boolean}  true = 亮色，false = 暗色
 */
function isLightColor(str, threshold = 0.4) {
  if (typeof str !== 'string' || !str.trim()) return true;

  const tokens = str.match(COLOR_TOKEN_RE) || [];
  const colors = tokens.map(parseColorToken).filter(Boolean);

  // 解析不出颜色（如 var(--x)），默认按亮色处理
  if (!colors.length) return true;

  // 多个颜色（渐变）按 alpha 加权求平均亮度
  let sum = 0;
  let weight = 0;
  for (const c of colors) {
    sum += relativeLuminance(c) * c.a;
    weight += c.a;
  }
  if (weight === 0) return true; // 全透明

  return sum / weight > threshold;
}

window.isLightColor = isLightColor;