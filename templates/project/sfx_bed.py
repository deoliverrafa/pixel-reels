#!/usr/bin/env python3
"""Efeitos chiptune sintetizados (assets/bed.wav). Determinístico. Coloque um put() para cada batida da cena."""
import json, os, re, wave
import numpy as np
os.chdir(os.path.dirname(os.path.abspath(__file__)))
T = json.loads(re.search(r'=\s*(\{.*?\})', open('assets/timing.js', encoding='utf-8').read(), re.S).group(1))  # mesma tabela da cena
SR, DUR = 48000, __DURATION__
N = int(SR * DUR); L = np.zeros(N); Rr = np.zeros(N)
rng = np.random.default_rng(5)
def put(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N: return
    sig = sig[:N - i] * gain
    L[i:i+len(sig)] += sig * np.sqrt((1-pan)/2) * 1.414; Rr[i:i+len(sig)] += sig * np.sqrt((1+pan)/2) * 1.414
def env(n, a=0.003, r=0.03):
    e = np.ones(n); ai, ri = max(1, int(a*SR)), max(1, int(r*SR)); e[:ai] = np.linspace(0, 1, ai); e[-ri:] *= np.linspace(1, 0, ri); return e
def sq(f, d, duty=0.5):
    t = np.arange(int(d*SR))/SR
    ph = np.cumsum(np.broadcast_to(f, t.shape) if np.ndim(f) else np.full(t.shape, f))/SR
    return np.where((ph % 1) < duty, 1.0, -1.0)
def blip(f, d=0.06, duty=0.25): return sq(f, d, duty) * env(int(d*SR), 0.002, d*0.6)
def arp(fs, step=0.06, d=0.08, duty=0.25):
    out = np.zeros(int((step*len(fs)+d)*SR))
    for i, f in enumerate(fs):
        b = blip(f, d, duty); j = int(i*step*SR); out[j:j+len(b)] += b
    return out
def noise(d): return rng.standard_normal(int(d*SR))
def lp(x, a):
    y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)): acc += a*(x[i]-acc); y[i] = acc
    return y
def sweep(f0, f1, d, duty=0.25): n = int(d*SR); return sq(np.linspace(f0, f1, n), d, duty) * env(n, 0.01, d*0.3)
def thud():
    d = 0.45; t = np.arange(int(d*SR))/SR
    return np.sin(2*np.pi*np.cumsum(np.linspace(140, 45, len(t)))/SR) * np.exp(-t*9) + lp(noise(d), 0.35) * np.exp(-t*40) * 0.8
def click(d=0.03): t = np.arange(int(d*SR))/SR; return lp(noise(d), 0.6) * np.exp(-t*120)
C5, E5, G5, A5, C6, E6, G6 = 523.25, 659.25, 783.99, 880.0, 1046.5, 1318.5, 1568.0

# ---- batidas do vídeo, nos tempos de T. O ganho é relativo: tudo é normalizado pela batida mais forte.
# Faixa que funciona: blips e arpejos 0.08 a 0.13, thud até 0.5 e só fora de palavra importante.
put(arp([C5, E5, G5], 0.05), T['gancho'], 0.12)  # título entra
put(blip(A5), T['cena2'], 0.12)                  # troca de cena
put(arp([G5, C6, E6], 0.06), T['perfil'], 0.12)  # card final

pk = max(np.abs(L).max(), np.abs(Rr).max(), 1e-6); L /= pk; Rr /= pk
pcm = (np.stack([L, Rr], 1) * 0.89 * 32767).astype('<i2')
with wave.open('assets/bed.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('assets/bed.wav', DUR, 's')
