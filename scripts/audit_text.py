#!/usr/bin/env python3
"""Auditoria automática de texto em cenas de canvas (window.renderScene(t) puro do tempo).

Roda a cena inteira no Chrome headless e registra cada fillText. Aponta:
  OVERFLOW  texto saindo da caixa desenhada atrás dele
  EDGE      texto saindo do quadro
  SAFE      texto fora da zona segura do Reels
  SMALL     texto abaixo do mínimo por um tempo relevante

Uso: audit_text.py <pasta do projeto> [--step 0.1] [--min-size 40]
Sai com código 1 se houver OVERFLOW ou EDGE.
"""
import argparse, http.server, json, os, subprocess, sys, tempfile, threading
from common import chrome

PATCH = r"""
<script>
window.__timelines = window.__timelines || {};
(function () {
  const P = CanvasRenderingContext2D.prototype, fr = P.fillRect, ft = P.fillText;
  let rects = new WeakMap(), cur = null;
  const box = (c, x, y, w, h) => {
    const m = c.getTransform(), xs = [], ys = [];
    for (const [a, b] of [[x, y], [x + w, y], [x, y + h], [x + w, y + h]]) { xs.push(m.a * a + m.c * b + m.e); ys.push(m.b * a + m.d * b + m.f); }
    return { l: Math.min(...xs), r: Math.max(...xs), t: Math.min(...ys), b: Math.max(...ys) };
  };
  P.fillRect = function (x, y, w, h) {
    if (cur) { let a = rects.get(this); if (!a) rects.set(this, a = []); a.push({ ...box(this, x, y, w, h), c: String(this.fillStyle) }); }
    return fr.call(this, x, y, w, h);
  };
  P.fillText = function (s, x, y, mw) {
    if (cur && String(s).trim()) {
      const m = this.measureText(s), al = this.textAlign, w = m.width;
      const asc = m.actualBoundingBoxAscent, desc = m.actualBoundingBoxDescent;
      const x0 = al === 'center' ? x - w / 2 : (al === 'right' || al === 'end') ? x - w : x;
      const b = box(this, x0, y - asc, w, asc + desc), cx = (b.l + b.r) / 2, cy = (b.t + b.b) / 2;
      const main = this.canvas.id === 'c', tr = this.getTransform();
      const px = parseFloat((this.font.match(/([\d.]+)px/) || [0, 0])[1]) * Math.hypot(tr.a, tr.b);
      const list = rects.get(this) || [], W = this.canvas.width, H = this.canvas.height;
      let host = null;
      for (let i = list.length - 1; i >= 0; i--) {
        const r = list[i];
        // a caixa precisa conter início, centro ou fim do texto e ser mais alta que ele; assim poeira e detalhes não contam
        if (cy < r.t || cy > r.b || (r.b - r.t) < (b.b - b.t)) continue;
        if (![b.l + 2, cx, b.r - 2].some(px => px >= r.l && px <= r.r)) continue;
        if ((r.r - r.l) * (r.b - r.t) > W * H * 0.8) continue;
        host = { l: r.l, r: r.r, t: r.t, b: r.b };
        for (const o of list) if (o.c === r.c && cy >= o.t && cy <= o.b && !(o.r < r.l || o.l > r.r)) { host.l = Math.min(host.l, o.l); host.r = Math.max(host.r, o.r); host.t = Math.min(host.t, o.t); host.b = Math.max(host.b, o.b); }
        break;
      }
      cur.push({ s: String(s), l: b.l, r: b.r, t: b.t, b: b.b, px, main, host });
    }
    return ft.call(this, s, x, y, mw);
  };
  window.__auditFrame = function (t) {
    cur = []; rects = new WeakMap();
    window.renderScene(t);
    const out = cur; cur = null; return out;
  };
})();
</script>
"""

RUN = r"""
<script>
window.addEventListener('load', async () => {
  const cfg = %s; await Promise.all([document.fonts.ready, (window.__hf && __hf.buildReady && __hf.buildReady.fonts) || 0]);
  await new Promise(r => setTimeout(r, 1500));
  const dur = +document.getElementById('root').dataset.duration, seen = {};
  const add = (k, o, t) => { const e = seen[k] || (seen[k] = { ...o, first: t, n: 0, worst: 0 }); e.n++; e.worst = Math.max(e.worst, o.by || 0); };
  let prev = {};
  for (let t = 0; t <= dur; t += cfg.step) {
    let frame = [];
    try { frame = window.__auditFrame(t); } catch (e) { add('X|' + e.message, { type: 'ERROR', text: e.message, by: 0 }, +t.toFixed(2)); }
    const now = {};
    for (const x of frame) (now[x.s] = now[x.s] || []).push(x);
    for (const x of frame) {
      const T = +t.toFixed(2);
      // texto em movimento (entrada, saída, transição) não conta: só o que fica parado na tela
      if (!(prev[x.s] || []).some(p => Math.abs(p.l - x.l) < 4 && Math.abs(p.r - x.r) < 4 && Math.abs(p.t - x.t) < 4)) continue;
      if (x.host) {
        const by = Math.max(x.host.l - x.l, x.r - x.host.r);
        if (by > cfg.tol) add('O|' + x.s, { type: 'OVERFLOW', text: x.s, by: Math.round(by) }, T);
      }
      if (x.main && x.r > 0 && x.l < 1080 && x.b > 0 && x.t < 1920) {
        const by = Math.max(-x.l, x.r - 1080, -x.t, x.b - 1920);
        if (by > 1) add('E|' + x.s, { type: 'EDGE', text: x.s, by: Math.round(by) }, T);
        const sf = Math.max(35 - x.l, x.r - 1045, 220 - x.t, x.b - 1470);
        if (sf > 1) add('S|' + x.s, { type: 'SAFE', text: x.s, by: Math.round(sf) }, T);
        if (x.px > 4 && x.px < cfg.min) add('M|' + x.s, { type: 'SMALL', text: x.s, by: Math.round(x.px) }, T);
      }
    }
    prev = now;
  }
  for (const w of new Set(window.__pixelWarnings || [])) seen['W|' + w] = { type: 'OVERFLOW', text: w, by: 0, first: 0, n: 99, worst: 0 };
  await fetch('/__result', { method: 'POST', body: JSON.stringify(Object.values(seen)) });
});
</script>
"""


def run_in_chrome(root, page, timeout=420):
    """Serve o projeto num endereço local, abre o Chrome e espera a página devolver o resultado."""
    result = {}; done = threading.Event()

    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k): super().__init__(*a, directory=root, **k)
        def log_message(self, *a): pass
        def do_GET(self):
            if self.path.startswith('/__audit.html'):
                body = page.encode(); self.send_response(200); self.send_header('Content-Type', 'text/html; charset=utf-8'); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
            else: super().do_GET()
        def do_POST(self):
            result['data'] = self.rfile.read(int(self.headers['Content-Length'])).decode(); self.send_response(204); self.end_headers(); done.set()

    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
    with tempfile.TemporaryDirectory() as prof:
        c = subprocess.Popen([chrome(), '--headless=new', '--disable-gpu', '--no-first-run', f'--user-data-dir={prof}', f'http://127.0.0.1:{srv.server_address[1]}/__audit.html'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try: done.wait(timeout)
        finally:
            c.terminate(); c.wait(); srv.shutdown()
    return result.get('data')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project'); ap.add_argument('--step', type=float, default=0.1); ap.add_argument('--min-size', type=float, default=40)
    ap.add_argument('--tol', type=float, default=4); ap.add_argument('--min-dur', type=float, default=0.5)
    a = ap.parse_args()
    root = os.path.abspath(a.project); src = open(os.path.join(root, 'index.html'), encoding='utf-8').read()
    cfg = json.dumps({'step': a.step, 'min': a.min_size, 'tol': a.tol})
    page = src.replace('<head>', '<head>' + PATCH, 1).replace('</body>', (RUN % cfg) + '</body>', 1)
    out = run_in_chrome(root, page)
    if out is None: sys.exit('A auditoria não terminou: confira se a cena expõe window.renderScene e #root[data-duration]')
    res = json.loads(out); order = {'ERROR': 0, 'OVERFLOW': 1, 'EDGE': 2, 'SAFE': 3, 'SMALL': 4}; shown = hard = 0
    for r in sorted(res, key=lambda r: (order[r['type']], r['first'])):
        dur = r['n'] * a.step
        if r['type'] in ('SAFE', 'SMALL') and dur < a.min_dur: continue
        if r['type'] in ('OVERFLOW', 'EDGE') and dur < 0.3: continue
        unit = 'px de corpo' if r['type'] == 'SMALL' else 'px para fora'
        print(f"{r['type']:9} t={r['first']:6.2f}s  {dur:4.1f}s  {r['worst'] if r['type'] != 'SMALL' else r['by']:>4} {unit}  {r['text']!r}")
        shown += 1; hard += r['type'] in ('ERROR', 'OVERFLOW', 'EDGE')
    print(f'{shown} apontamento(s), {hard} grave(s).')
    sys.exit(1 if hard else 0)


if __name__ == '__main__':
    main()
