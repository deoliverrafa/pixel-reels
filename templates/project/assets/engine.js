// Motor pixel art do pixel-reels. Tudo é função pura do tempo: render(t) sempre desenha o mesmo quadro.
// Regra de ouro: texto dentro de caixa passa por boxText, que quebra linha e reduz até caber.
(function () {
  const W = 1080, H = 1920;
  const cv = document.getElementById('c');
  const g = cv.getContext('2d');
  // ---------- utilidades
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lin = (a, b, t) => clamp((t - a) / (b - a));
  const eo = (a, b, t) => { const k = lin(a, b, t); return k === 1 ? 1 : 1 - Math.pow(2, -10 * k); };
  const bo = (a, b, t, c = 1.7) => { const k = lin(a, b, t); return 1 + (c + 1) * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2); };
  const ei = (a, b, t) => { const k = lin(a, b, t); return k * k * k; };
  const io = (a, b, t) => { const k = lin(a, b, t); return k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2; };
  const stp = (k, n) => Math.round(k * n) / n;
  const lerp = (a, b, k) => a + (b - a) * k;
  const rnd = i => { const x = Math.sin(i * 12.9898 + 78.233) * 43758.5453; return x - Math.floor(x); };
  const q = (v, s = 2) => Math.round(v / s) * s;
  const fr = t => Math.floor(t * 30);
  const step12 = t => Math.floor(t * 12) / 12;


  // ---------- paleta (vem de assets/style.js)
  const ST = window.PIXEL_STYLE;
  const K = ST.shadow, CREAM = ST.cream, CREAM2 = ST.creamShade, CREAM3 = ST.creamLight, RED = ST.accent, REDD = ST.accentDark, REDL = ST.accentLight, INKP = ST.ink, WHITE = '#fffaf0', MUTE = ST.mute;
  const rgba = (hex, a) => `rgba(${parseInt(hex.slice(1, 3), 16)},${parseInt(hex.slice(3, 5), 16)},${parseInt(hex.slice(5, 7), 16)},${a})`;
  const CHARACTERS = window.PIXEL_CHARACTERS || {};
  const DEFAULT_CHARACTER = { skin: '#e3a77b', skinShade: '#b97b52', hair: '#1b1410', hairLight: '#3a2e26', hairStyle: 'up', glasses: 'none', beard: 'none', shirt: '#22305e', shirtLight: '#34478a', pants: '#2b2b36', shoes: '#e9e3d3' };

  // ---------- canvas fora da tela
  const offs = {};
  function off(key, w, h) {
    let c = offs[key];
    if (!c) { c = document.createElement('canvas'); c.width = w; c.height = h; offs[key] = c; }
    const x = c.getContext('2d'); x.setTransform(1, 0, 0, 1, 0, 0); x.globalCompositeOperation = 'source-over'; x.globalAlpha = 1; x.clearRect(0, 0, c.width, c.height);
    return c;
  }
  let G = g;
  const R = (x, y, w, h, c) => { G.fillStyle = c; G.fillRect(Math.round(x), Math.round(y), Math.round(w), Math.round(h)); };
  const pen = (ox, oy, u = 1) => ({
    r: (x, y, w, h, c) => R(ox + x * u, oy + y * u, w * u, h * u, c),
    b: (x, y, w, h, c) => { R(ox + (x - 1) * u, oy + (y - 1) * u, (w + 2) * u, (h + 2) * u, K); R(ox + x * u, oy + y * u, w * u, h * u, c); }
  });
  function shadowOf(c, key, col = 'rgba(0,0,0,0.55)') {
    const s = off('sh_' + key, c.width, c.height); const x = s.getContext('2d');
    x.drawImage(c, 0, 0); x.globalCompositeOperation = 'source-in'; x.fillStyle = col; x.fillRect(0, 0, s.width, s.height);
    return s;
  }
  function blit(c, key, x, y, s, o = {}) {
    const ax = o.ax ?? .5, ay = o.ay ?? .5, rot = o.rot || 0, sho = o.sh ?? Math.max(8, s * 1.2);
    const w = c.width * s, h = c.height * s;
    g.save(); g.imageSmoothingEnabled = false;
    g.translate(q(x), q(y)); if (rot) g.rotate(rot);
    if (sho) g.drawImage(shadowOf(c, key), -w * ax + sho, -h * ay + sho, w, h);
    g.drawImage(c, -w * ax, -h * ay, w, h);
    g.restore();
  }

  // ---------- fundo estático: quase-preto quente, holofote terracota, vinheta
  let BG = null, PAPER = null;
  function buildStatic() {
    BG = document.createElement('canvas'); BG.width = W; BG.height = H;
    const b = BG.getContext('2d');
    b.fillStyle = ST.bgDeep; b.fillRect(0, 0, W, H);
    let gr = b.createRadialGradient(540, 940, 40, 540, 940, 1100);
    gr.addColorStop(0, ST.spot); gr.addColorStop(0.35, ST.spotMid); gr.addColorStop(0.75, ST.bg); gr.addColorStop(1, ST.bgEdge);
    b.fillStyle = gr; b.fillRect(0, 0, W, H);
    gr = b.createRadialGradient(540, 940, 20, 540, 940, 760);
    gr.addColorStop(0, rgba(RED, 0.20)); gr.addColorStop(0.5, rgba(RED, 0.08)); gr.addColorStop(1, rgba(RED, 0));
    b.fillStyle = gr; b.fillRect(0, 0, W, H);
    gr = b.createRadialGradient(540, 960, 600, 540, 960, 1250);
    gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, 'rgba(0,0,0,0.65)');
    b.fillStyle = gr; b.fillRect(0, 0, W, H);
    for (let i = 0; i < 2600; i++) { b.fillStyle = rnd(i * 3.1) < .5 ? 'rgba(0,0,0,0.10)' : rgba(RED, 0.035); b.fillRect(q(rnd(i) * W, 4), q(rnd(i * 7.7) * H, 4), 4, 4); }
    const p = document.createElement('canvas'); p.width = 128; p.height = 128; const x = p.getContext('2d');
    x.fillStyle = CREAM; x.fillRect(0, 0, 128, 128);
    for (let i = 0; i < 900; i++) { x.fillStyle = rnd(i * 1.7) < .7 ? 'rgba(110,100,80,0.11)' : 'rgba(255,255,255,0.4)'; x.fillRect(q(rnd(i * 2.3) * 128, 2), q(rnd(i * 5.9) * 128, 2), 2, 2); }
    PAPER = g.createPattern(p, 'repeat');
  }

  // ---------- texto
  function font(kind, size) { return kind === 'p' ? `${size}px "Press Start 2P"` : kind === 'sb' ? `700 ${size}px "Silkscreen"` : `400 ${size}px "Silkscreen"`; }
  const ACC = { 'Á': ['A', 'a'], 'É': ['E', 'a'], 'Í': ['I', 'a'], 'Ó': ['O', 'a'], 'Ú': ['U', 'a'], 'Ã': ['A', 't'], 'Õ': ['O', 't'], 'Â': ['A', 'c'], 'Ê': ['E', 'c'], 'Ô': ['O', 'c'], 'À': ['A', 'g'], 'Ç': ['C', 'd'] };
  function glyphs(s, x, y, size, al) {
    let base = '', marks = [];
    for (let i = 0; i < s.length; i++) { const a = ACC[s[i]]; if (a) { base += a[0]; marks.push([i, a[1]]); } else base += s[i]; }
    const cw = size, w = cw * base.length, x0 = al === 'center' ? x - w / 2 : al === 'right' ? x - w : x;
    const rects = []; const p = size / 8, top = y - size * 0.5 - p * 0.4;
    for (const [i, k] of marks) {
      const cx = x0 + i * cw + cw / 2 - p / 2;
      if (k === 'd') { const by = y + size * 0.5; rects.push([cx - 0.5 * p, by, 2 * p, p], [cx - 1.5 * p, by + p, 2 * p, p]); }
      if (k === 'a') { rects.push([cx, top - 2 * p, 2 * p, p], [cx - p, top - p, 2 * p, p]); }
      if (k === 'g') { rects.push([cx - p, top - 2 * p, 2 * p, p], [cx, top - p, 2 * p, p]); }
      if (k === 'c') { rects.push([cx - 0.5 * p, top - 2 * p, 2 * p, p], [cx - 1.5 * p, top - p, p * 1.2, p], [cx + 1.3 * p, top - p, p * 1.2, p]); }
      if (k === 't') { rects.push([cx - 2.5 * p, top - p, p, p], [cx - 1.5 * p, top - 2 * p, 2 * p, p], [cx + 0.5 * p, top - p, 2 * p, p], [cx + 2.5 * p, top - 2 * p, p, p]); }
    }
    return { base, rects };
  }
  function gpass(s, x, y, size, al, col) {
    const { base, rects } = glyphs(s, x, y, size, al);
    g.fillStyle = col; g.fillText(base, Math.round(x), Math.round(y));
    for (const [rx, ry, rw, rh] of rects) g.fillRect(Math.round(rx), Math.round(ry), Math.ceil(rw), Math.ceil(rh));
  }
  function txt(s, x, y, size, col, o = {}) {
    const f = o.f || 'p';
    g.font = font(f, size); g.textAlign = o.al || 'center'; g.textBaseline = o.bl || 'middle';
    if (f !== 'p') {
      if (o.sh) { g.fillStyle = o.shc || K; g.fillText(s, Math.round(x + o.sh), Math.round(y + o.sh)); }
      g.fillStyle = col; g.fillText(s, Math.round(x), Math.round(y)); return;
    }
    if (o.sh) gpass(s, x + o.sh, y + o.sh, size, o.al || 'center', o.shc || K);
    gpass(s, x, y, size, o.al || 'center', col);
  }
  function tw(s, size, f = 'p') { g.font = font(f, size); return g.measureText(s).width; }
  function outl(s, x, y, size, col, f = 'sb', o = 4) { // texto com contorno escuro e sombra dura
    g.font = font(f, size); g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillStyle = K;
    g.fillText(s, x + o * 2, y + o * 2);
    for (const [dx, dy] of [[-o, 0], [o, 0], [0, -o], [0, o], [-o, -o], [o, o], [-o, o], [o, -o]]) g.fillText(s, x + dx, y + dy);
    g.fillStyle = col; g.fillText(s, x, y);
  }

  function creamTitle(s, x, y, size) {
    let sz = size; while (tw(s, sz) > 880 && sz > 20) sz -= 2;
    g.font = font('p', sz); g.textAlign = 'center'; g.textBaseline = 'middle';
    const o = Math.max(4, Math.round(sz * 0.08));
    gpass(s, x + o * 1.9, y + o * 1.9, sz, 'center', K);
    for (const [dx, dy] of [[-o, 0], [o, 0], [0, -o], [0, o], [-o, -o], [o, o], [-o, o], [o, -o]]) gpass(s, x + dx, y + dy, sz, 'center', K);
    gpass(s, x, y, sz, 'center', CREAM);
    g.save(); g.beginPath(); g.rect(0, y + sz * 0.12, W, sz); g.clip(); gpass(s, x, y, sz, 'center', CREAM2); g.restore();
  }
  function nrect(x, y, w, h, n, c) { R(x + n, y, w - 2 * n, h, c); R(x, y + n, w, h - 2 * n, c); }
  function nrect2(x, y, w, h, n) { g.fillRect(x + n, y, w - 2 * n, h); g.fillRect(x, y + n, w, h - 2 * n); }
  function banner(s, x, y, size, col = RED, dark = REDD, light = REDL) {
    let sz = size; while (tw(s, sz) + sz * 1.6 > 900 && sz > 16) sz -= 2;
    const w = tw(s, sz) + sz * 1.6, h = sz + sz * 1.3;
    const bx = Math.round(x - w / 2), by = Math.round(y - h / 2);
    nrect(bx + 12, by + 14, w, h, 12, 'rgba(0,0,0,0.6)');
    nrect(bx - 6, by - 6, w + 12, h + 12, 12, K);
    nrect(bx, by, w, h, 6, col);
    R(bx + 6, by + 4, w - 12, 6, light);
    R(bx + 6, by + h - 10, w - 12, 6, dark);
    txt(s, x, y + 2, sz, CREAM, { sh: Math.max(3, Math.round(sz * 0.1)) });
  }
  function popScale(t, t0, t1, d = 0.3) {
    if (t < t0 || t >= t1) return 0;
    let s = stp(bo(t0, t0 + d, t, 2.2), 6);
    if (t > t1 - 0.14) s *= stp(1 - lin(t1 - 0.14, t1, t), 3);
    return s;
  }
  function withScale(cx, cy, s, rot, fn) { if (s <= 0.01) return; g.save(); g.translate(cx, cy); if (rot) g.rotate(rot); g.scale(s, s); g.translate(-cx, -cy); fn(); g.restore(); }
  function card(cx, cy, w, h, rot, sc, fn) {
    if (sc <= 0.01) return;
    g.save(); g.translate(cx, cy); g.rotate(rot); g.scale(sc, sc);
    nrect(-w / 2 + 14, -h / 2 + 18, w, h, 10, 'rgba(0,0,0,0.55)');
    nrect(-w / 2 - 4, -h / 2 - 4, w + 8, h + 8, 10, K);
    g.fillStyle = PAPER; nrect2(-w / 2, -h / 2, w, h, 8);
    R(-w / 2 + 8, h / 2 - 8, w - 16, 8, CREAM2); R(w / 2 - 8, -h / 2 + 8, 8, h - 16, CREAM3);
    fn(); g.restore();
  }
  function star(x, y, p, col = CREAM) { R(x - p / 2, y - p * 1.5, p, p * 3, col); R(x - p * 1.5, y - p / 2, p * 3, p, col); }
  // disco "pixelado": faixas horizontais em degraus de 8 px
  function pdisk(cx, cy, r, col, st = 8) {
    for (let dy = -r; dy < r; dy += st) {
      const yy = dy + st / 2, hw = q(Math.sqrt(Math.max(0, r * r - yy * yy)), st);
      if (hw > 0) R(cx - hw, cy + dy, hw * 2, st, col);
    }
  }
  function pdiskPath(cx, cy, r, st = 8) {
    g.beginPath();
    for (let dy = -r; dy < r; dy += st) { const yy = dy + st / 2, hw = q(Math.sqrt(Math.max(0, r * r - yy * yy)), st); if (hw > 0) g.rect(cx - hw, cy + dy, hw * 2, st); }
  }

  // ---------- caixa com texto que sempre cabe
  function wrap(s, size, f, maxW) {
    g.font = font(f, size); const ws = s.split(' '), out = []; let cur = '';
    for (const w of ws) { const tt = cur ? cur + ' ' + w : w; if (g.measureText(tt).width > maxW && cur) { out.push(cur); cur = w; } else cur = tt; }
    if (cur) out.push(cur); return out;
  }
  function boxText(s, x, y, w, h, col, o = {}) {
    const f = o.f || 'sb', pad = o.pad ?? 24, min = o.min ?? 40; let size = o.size || 46, lines;
    const fits = sz => { lines = wrap(s, sz, f, w - pad * 2); g.font = font(f, sz); return lines.every(l => g.measureText(l).width <= w - pad * 2) && lines.length * sz * 1.3 <= h - pad; };
    while (!fits(size) && size > min) size -= 2;
    if (!fits(size)) (window.__pixelWarnings = window.__pixelWarnings || []).push(`Texto não cabe na caixa: "${s}" (${w}x${h}). Encurte o texto ou aumente a caixa.`);
    const lh = size * 1.3, top = y + h / 2 - (lines.length - 1) * lh / 2, al = o.al || 'left', tx = al === 'center' ? x + w / 2 : x + pad;
    lines.forEach((l, i) => txt(l, tx, top + i * lh, size, col, { f, al, sh: o.sh ?? 3 }));
    return size;
  }
  function bubble(s, x, y, w, h, o = {}) { // balão de chat
    const col = o.col || RED, top = o.light || REDL;
    nrect(x + 12, y + 14, w, h, 10, 'rgba(0,0,0,0.5)'); nrect(x - 6, y - 6, w + 12, h + 12, 10, K); nrect(x, y, w, h, 8, col); R(x + 10, y + 6, w - 20, 6, top);
    R(x + w - 70, y + h + 4, 40, 20, K); R(x + w - 64, y + h, 28, 16, col); R(x + w - 34, y + h + 18, 20, 20, K);
    boxText(s, x, y, w, h, o.text || CREAM, o);
  }

  // ---------- poeira de pixel
  function dust(t, amt = 1) {
    for (let i = 0; i < 64 * amt; i++) {
      const sp = 10 + rnd(i * 1.3) * 22;
      const x = q(((rnd(i * 3.7) * 1120 + Math.sin(t * 0.5 + i) * 18) % 1120), 4) - 20;
      const y = q((((rnd(i * 7.1) * 2000 - t * sp) % 2000) + 2000) % 2000 - 40, 4);
      const sz = rnd(i * 5.3) < .72 ? 4 : 6;
      const lv = (Math.floor(t * 5 + i * 3) % 4) / 3;
      g.globalAlpha = 0.3 + 0.55 * lv;
      R(x, y, sz, sz, rnd(i * 11.9) < .6 ? RED : CREAM);
    }
    g.globalAlpha = 1;
  }


  // ---------- personagens
  function personSprite(key, st) {
    const c = off(key, 26, 40); G = c.getContext('2d'); const P = pen(3, 3);
    const ch = st.character || CHARACTERS[key] || DEFAULT_CHARACTER;
    const SKIN = ch.skin, SKIND = ch.skinShade, hair = ch.hair, shirt = ch.shirt, shirtL = ch.shirtLight, PANTS = ch.pants, SOLE = ch.shoes;
    const wk = st.walk ? Math.floor(st.walk * 8) % 2 : -1;
    if (wk < 0) { P.r(4, 25, 12, 6, K); P.r(5, 25, 10, 5, PANTS); P.r(10, 26, 1, 4, K); P.r(3, 30, 6, 3, K); P.r(11, 30, 6, 3, K); P.r(4, 31, 4, 1, SOLE); P.r(12, 31, 4, 1, SOLE); }
    else {
      const a = wk ? 1 : 0;
      P.r(4, 25, 12, 5, K); P.r(5, 25, 10, 4, PANTS); P.r(10, 26, 1, 3, K);
      P.r(4, 29 - a, 5, 3, K); P.r(5, 29 - a, 3, 2, PANTS); P.r(3, 31 - a, 6, 2, K); P.r(4, 31 - a, 4, 1, SOLE);
      P.r(11, 29 - (1 - a), 5, 3, K); P.r(12, 29 - (1 - a), 3, 2, PANTS); P.r(11, 31 - (1 - a), 6, 2, K); P.r(12, 31 - (1 - a), 4, 1, SOLE);
    }
    // tronco
    P.r(3, 14, 14, 12, K); P.r(4, 15, 12, 10, shirt); P.r(4, 15, 12, 1, shirtL); P.r(8, 15, 4, 1, SKIND);
    if (st.tie ?? ch.tie) { P.r(9, 16, 2, 6, K); P.r(9, 16, 2, 5, RED); }
    if (st.badge ?? ch.badge) { P.r(6, 16, 1, 4, RED); P.r(13, 16, 1, 4, RED); P.r(11, 19, 4, 4, K); P.r(12, 20, 2, 2, WHITE); }
    // braços
    const arm = (side, mode) => {
      const L = side === 'L', ax = L ? 0 : 16;
      if (mode === 'wave') { const up = st.wave ? 1 : 0; P.r(L ? 0 : 16, 6 + up, 4, 10, K); P.r(L ? 1 : 17, 9 + up, 2, 6, shirt); P.r(L ? 1 : 17, 7 + up, 2, 2, SKIN); }
      else if (mode === 'hold') { P.r(L ? 1 : 15, 15, 4, 7, K); P.r(L ? 2 : 16, 16, 2, 4, shirt); P.r(L ? 3 : 14, 19, 3, 3, K); P.r(L ? 4 : 14, 20, 2, 1, SKIN); }
      else if (mode === 'up') { P.r(L ? -1 : 17, 4, 4, 12, K); P.r(L ? 0 : 18, 7, 2, 8, shirt); P.r(L ? 0 : 18, 5, 2, 2, SKIN); }
      else { P.r(L ? 1 : 16, 15, 3, 9, K); P.r(L ? 2 : 16, 16, 2, 6, shirt); P.r(L ? 2 : 16, 22, 2, 2, SKIN); }
    };
    arm('L', st.armL); arm('R', st.armR);
    // cabeça
    P.r(4, 3, 12, 12, K); P.r(5, 4, 10, 10, SKIN); P.r(3, 8, 1, 3, K); P.r(16, 8, 1, 3, K); P.r(4, 8, 1, 2, SKIND); P.r(15, 8, 1, 2, SKIND);
    const hs = st.messy ? 'messy' : ch.hairStyle;
    const HL = ch.hairLight;
    if (hs === 'messy') {
      P.r(3, 1, 14, 4, K); P.r(2, 0, 3, 3, K); P.r(15, 0, 3, 3, K); P.r(6, -1, 3, 2, K); P.r(11, -2, 3, 3, K);
      P.r(4, 2, 12, 2, hair); P.r(3, 1, 1, 1, hair); P.r(16, 1, 1, 1, hair); P.r(7, 0, 1, 2, hair); P.r(12, -1, 1, 3, hair); P.r(5, 4, 2, 2, hair); P.r(13, 4, 2, 2, hair); P.r(9, 4, 2, 1, hair);
    } else if (hs === 'short') {
      P.r(4, 1, 12, 4, K); P.r(5, 2, 10, 3, hair); P.r(5, 4, 1, 2, hair); P.r(14, 4, 1, 2, hair); P.r(7, 2, 4, 1, HL);
    } else if (hs === 'long') {
      P.r(3, 1, 14, 5, K); P.r(2, 4, 3, 14, K); P.r(15, 4, 3, 14, K); P.r(4, 2, 12, 3, hair); P.r(3, 5, 2, 12, hair); P.r(15, 5, 2, 12, hair); P.r(5, 4, 2, 2, hair); P.r(13, 4, 2, 2, hair); P.r(7, 2, 4, 1, HL);
    } else if (hs === 'bun') {
      P.r(7, -3, 6, 4, K); P.r(8, -2, 4, 3, hair); P.r(4, 1, 12, 4, K); P.r(5, 2, 10, 3, hair); P.r(5, 4, 1, 3, hair); P.r(14, 4, 1, 3, hair); P.r(8, -2, 2, 1, HL);
    } else if (hs === 'curly') {
      P.r(3, -2, 14, 1, K); P.r(2, -1, 16, 7, K); P.r(1, 1, 18, 7, K); P.r(4, -1, 12, 1, hair); P.r(3, 0, 14, 5, hair); P.r(2, 2, 16, 5, hair); P.r(5, 5, 2, 1, hair); P.r(13, 5, 2, 1, hair); P.r(6, 0, 2, 1, HL); P.r(11, 1, 2, 1, HL); P.r(4, 3, 1, 1, HL); P.r(15, 3, 1, 1, HL);
    } else if (hs === 'bald') {
      P.r(5, 2, 10, 2, K); P.r(6, 3, 8, 1, SKIN); P.r(7, 3, 3, 1, '#ffffff33');
    } else { // up: topete para cima
      P.r(4, 0, 12, 4, K); P.r(6, -2, 9, 3, K); P.r(9, -3, 6, 2, K);
      P.r(5, 1, 10, 3, hair); P.r(7, -1, 7, 2, hair); P.r(10, -2, 4, 1, hair); P.r(5, 4, 1, 3, hair); P.r(14, 4, 1, 3, hair); P.r(8, -1, 2, 1, HL);
    }
    if (st.brow === 'up') { P.r(5, 5, 4, 1, hair); P.r(11, 5, 4, 1, hair); }
    else if (st.brow === 'sorry') { P.r(5, 6, 3, 1, hair); P.r(8, 5, 1, 1, hair); P.r(12, 6, 3, 1, hair); P.r(11, 5, 1, 1, hair); }
    else if (st.brow === 'flat') { P.r(5, 6, 4, 1, hair); P.r(11, 6, 4, 1, hair); P.r(5, 7, 4, 1, SKIND); P.r(11, 7, 4, 1, SKIND); }
    else { P.r(5, 6, 4, 1, hair); P.r(11, 6, 4, 1, hair); }
    const gz = st.gaze || 'n';
    const pup = gz === 'side' ? [3, 0] : gz === 'left' ? [1, 0] : gz === 'down' ? [2, 1] : gz === 'up' ? [2, -0] : [2, 0];
    const gl = st.glasses ?? ch.glasses;
    if (gl === 'sun') {
      for (const ox of [4, 11]) { P.r(ox, 7, 5, 4, K); P.r(ox + 1, 8, 1, 1, '#6a6a72'); }
      P.r(9, 8, 2, 1, K);
    } else if (gl === 'clear' || gl === true) {
      // óculos de grau: armação fina, lentes CLARAS, olhos visíveis
      for (const ox of [4, 11]) { P.r(ox, 7, 5, 1, K); P.r(ox, 10, 5, 1, K); P.r(ox, 7, 1, 4, K); P.r(ox + 4, 7, 1, 4, K); P.r(ox + 1, 8, 3, 2, ch.skinLight || SKIN); P.r(ox + 1, 9, 3, 1, '#f6efe6'); }
      P.r(9, 8, 2, 1, K);
      for (const ox of [4, 11]) P.r(ox + pup[0], 8 + pup[1], 1, gz === 'down' ? 1 : 2, '#2a1a10');
      for (const ox of [4, 11]) P.r(ox + 1, 8, 1, 1, 'rgba(255,255,255,0.95)');
    } else {
      for (const ox of [5, 11]) { P.r(ox, 8, 3, 2, '#f6f1e8'); P.r(ox + (gz === 'side' ? 2 : gz === 'left' ? 0 : 1), 8, 1, 2, '#2a1a10'); }
    }
    if (ch.beard === 'full') { P.r(5, 11, 10, 3, hair); P.r(6, 13, 8, 1, hair); P.r(8, 12, 4, 1, SKIN); }
    else if (ch.beard === 'stubble') { for (let bx = 5; bx < 15; bx += 2) P.r(bx, 13, 1, 1, SKIND); }
    if (st.mouth === 'o') { P.r(9, 11, 2, 2, '#5a2010'); }
    else if (st.mouth === 'smile') { P.r(8, 12, 4, 1, '#7a2c18'); P.r(7, 11, 1, 1, '#7a2c18'); P.r(12, 11, 1, 1, '#7a2c18'); }
    else if (st.mouth === 'grin') { P.r(7, 11, 6, 2, '#7a2c18'); P.r(8, 11, 4, 1, '#f2efe6'); }
    else if (st.mouth === 'wavy') { P.r(7, 12, 1, 1, '#7a2c18'); P.r(8, 11, 1, 1, '#7a2c18'); P.r(9, 12, 2, 1, '#7a2c18'); P.r(11, 11, 1, 1, '#7a2c18'); P.r(12, 12, 1, 1, '#7a2c18'); }
    else P.r(8, 12, 4, 1, SKIND);
    G = g; return c;
  }
  function drawPerson(key, cx, by, s, st = {}) { R(cx - 8 * s, by - s * 0.6, 16 * s, s * 1.2, 'rgba(0,0,0,0.35)'); blit(personSprite(key, st), key, cx, by, s, { ax: .5, ay: 1 }); }
  // assistente genérico, sem logo de marca
  function robotSprite(st) {
    const c = off('robo', 26, 34); G = c.getContext('2d'); const P = pen(2, 4);
    const bl = st.t !== undefined && (Math.floor(st.t * 10) % 31 === 0);
    P.r(9, -4, 4, 3, K); P.r(10, -3, 2, 1, st.glow ? '#ffd2b8' : RED); P.r(10, -2, 2, 3, K);
    P.r(0, 5, 2, 4, K); P.r(20, 5, 2, 4, K); P.r(0, 6, 1, 2, RED); P.r(21, 6, 1, 2, RED);
    P.r(2, 1, 18, 11, K); P.r(3, 2, 16, 9, CREAM); P.r(3, 2, 16, 1, '#ffffff'); P.r(3, 10, 16, 1, CREAM2); P.r(18, 3, 1, 7, CREAM2);
    P.r(5, 4, 12, 5, K); P.r(6, 5, 10, 3, INKP);
    if (st.eyes === 'happy') { for (const ex of [7, 13]) { P.r(ex, 6, 1, 1, RED); P.r(ex + 1, 5, 1, 1, RED); P.r(ex + 2, 6, 1, 1, RED); } }
    else if (bl) { P.r(7, 6, 3, 1, RED); P.r(13, 6, 3, 1, RED); }
    else { const dx = st.look === 'left' ? -1 : st.look === 'right' ? 1 : 0; P.r(7 + dx, 5, 2, 2, RED); P.r(13 + dx, 5, 2, 2, RED); P.r(7 + dx, 5, 1, 1, REDL); P.r(13 + dx, 5, 1, 1, REDL); }
    P.r(9, 12, 4, 1, K);
    P.r(4, 13, 14, 10, K); P.r(5, 14, 12, 8, CREAM3); P.r(5, 14, 12, 1, '#ffffff'); P.r(5, 21, 12, 1, CREAM2);
    P.r(9, 16, 4, 3, K); P.r(10, 17, 2, 1, st.glow ? '#ffd2b8' : RED);
    const arm = (L, mode) => {
      const x = L ? 1 : 18;
      if (mode === 'wave') { const up = st.wave ? 1 : 0; P.r(x, 5 + up, 3, 10, K); P.r(x + 1, 6 + up, 1, 8, CREAM2); }
      else if (mode === 'hold') { P.r(x, 14, 3, 6, K); P.r(x + 1, 15, 1, 4, CREAM2); P.r(L ? 3 : 16, 18, 3, 3, K); }
      else { P.r(x, 14, 3, 8, K); P.r(x + 1, 15, 1, 6, CREAM2); }
    };
    arm(true, st.armL); arm(false, st.armR);
    P.r(6, 23, 4, 4, K); P.r(12, 23, 4, 4, K); P.r(7, 23, 2, 3, '#55524d'); P.r(13, 23, 2, 3, '#55524d'); P.r(5, 26, 6, 2, K); P.r(11, 26, 6, 2, K);
    G = g; return c;
  }
  function drawRobot(cx, by, s, st) { R(cx - 9 * s, by - s * 0.8, 18 * s, s * 1.2, 'rgba(0,0,0,0.35)'); blit(robotSprite(st), 'robo', cx, by, s, { ax: .5, ay: 1 }); }

  // ---------- objetos e interface
  function paper(x, y, w, h, n = 8) { // folha creme com borda e sombra
    nrect(x + 12, y + 14, w, h, n, 'rgba(0,0,0,0.5)'); nrect(x - 5, y - 5, w + 10, h + 10, n, K);
    g.fillStyle = PAPER; nrect2(x, y, w, h, n - 2); R(x + 6, y + h - 8, w - 12, 8, CREAM2);
  }
  function winFrame(x, y, w, h, title, o = {}) { // janela genérica pixel
    nrect(x + 16, y + 20, w, h, 12, 'rgba(0,0,0,0.55)');
    nrect(x - 6, y - 6, w + 12, h + 12, 12, K);
    nrect(x, y, w, h, 8, CREAM);
    R(x + 6, y, w - 12, 86, INKP); R(x, y + 6, w, 80, INKP); R(x, y + 86, w, 6, K);
    for (let k = 0; k < 3; k++) { R(x + 28 + k * 40, y + 30, 26, 26, K); R(x + 31 + k * 40, y + 33, 20, 20, k === 0 ? RED : k === 1 ? REDL : CREAM2); }
    txt(title, x + 160, y + 46, o.ts || 46, CREAM, { f: 'sb', al: 'left' });
  }
  function cursorAt(x, y, s, pressed) { const c = off('cur', 10, 15); G = c.getContext('2d'); cursorSprite(0, 0, pressed); G = g; blit(c, 'cur', x, y, s, { ax: 0, ay: 0, sh: 8 }); }
  function cursorSprite(x, y, pressed) {
    const rows = ['K.........', 'KK........', 'KCK.......', 'KCCK......', 'KCCCK.....', 'KCCCCK....', 'KCCCCCK...', 'KCCCCCCK..', 'KCCCCCCCK.', 'KCCCCKKKKK', 'KCCKCK....', 'KCK.KCK...', 'KK..KCK...', 'K....KCK..', '.....KK...'];
    for (let j = 0; j < rows.length; j++) for (let i = 0; i < rows[j].length; i++) { const ch = rows[j][i]; if (ch === 'K') R(x + i, y + j, 1, 1, K); else if (ch === 'C') R(x + i, y + j, 1, 1, pressed ? CREAM2 : '#ffffff'); }
  }
  function burst(x, y, t, t0, d = 0.35, r0 = 60, r1 = 150, n = 6) {
    if (t < t0 || t > t0 + d) return; const k = lin(t0, t0 + d, t);
    for (let i = 0; i < n; i++) { const a = i * 2 * Math.PI / n + 0.5; star(x + Math.cos(a) * lerp(r0, r1, k), y + Math.sin(a) * lerp(r0, r1, k) * 0.8, 10, i % 2 ? CREAM : RED); }
  }
  function checkBadge(x, y, s) { // visto num círculo terracota
    pdisk(x + 6, y + 8, 40 * s, 'rgba(0,0,0,0.5)', 4); pdisk(x, y, 40 * s, K, 4); pdisk(x, y, 34 * s, RED, 4);
    const pts = [[3, -2], [2, -1], [1, 0], [0, 1], [-1, 2], [-2, 1], [-3, 0]];
    for (const [px, py] of pts) R(x + px * 6 * s - 4 * s, y + py * 6 * s - 4 * s, 9 * s, 9 * s, CREAM);
  }
  // Reposição do fundo e da poeira no início de cada quadro.
  function frame(t) {
    if (!BG) buildStatic();
    g.setTransform(1, 0, 0, 1, 0, 0); g.imageSmoothingEnabled = false; G = g; g.globalAlpha = 1;
    g.drawImage(BG, 0, 0); dust(t);
  }
  // Card final do perfil: o @ vem do config, nunca digite à mão.
  function profileCard(t, t0, key, o = {}) {
    const handle = window.PIXEL_PROFILE || '', s = popScale(t, t0, Infinity);
    if (s <= 0) return;
    withScale(540, 300, s, 0, () => creamTitle(o.title || 'SEGUE O PERFIL', 540, 300, 64));
    withScale(540, 430, popScale(t, t0 + 0.25, Infinity), 0, () => banner(handle.toUpperCase(), 540, 430, 54));
    if (key) drawPerson(key, 540, 1320, 18, { armL: 'n', armR: 'wave', wave: Math.floor(t * 4) % 2, mouth: 'grin' });
  }
  window.PX = { W, H, g, K, CREAM, CREAM2, CREAM3, RED, REDD, REDL, INKP, WHITE, MUTE, clamp, lin, eo, bo, ei, io, stp, lerp, rnd, q, fr, R, nrect, nrect2, txt, tw, font, wrap, boxText, bubble, creamTitle, banner, popScale, withScale, card, star, pdisk, dust, drawPerson, drawRobot, paper, winFrame, cursorAt, burst, checkBadge, frame, profileCard };
})();
