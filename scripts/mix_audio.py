#!/usr/bin/env python3
"""Mixa voz e efeitos com ducking e calibra o volume por medição.

Uso: mix_audio.py <projeto> [--target 20]
     mix_audio.py <projeto> --check   só mede o work/efeitos.wav existente, sem gerar nada
Grava work/mix.wav e work/efeitos.wav. Duas metas, medidas:
  média: efeitos sozinhos 18 a 22 dB abaixo da voz. Efeitos esparsos podem ficar mais baixos que isso.
  batida: em janelas de 200 ms, efeito ao menos 6 dB abaixo da fala daquele instante e, nas pausas, 3 dB abaixo da média da voz.
Rode com o Python do .venv, que tem numpy.
"""
import argparse, glob, os, re, subprocess, sys
import numpy as np

DUCK = 'sidechaincompress=threshold=0.015:ratio=10:attack=10:release=450'


def mean(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.search(r'mean_volume: (-?[\d.]+|-inf)', r).group(1))


def windows(path, dur):
    pcm = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-t', str(dur), '-ac', '1', '-ar', '8000', '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, np.float32); n = 1600; m = len(x) // n
    return 20 * np.log10(np.sqrt((x[:m * n].reshape(m, n) ** 2).mean(1)) + 1e-6)


def worst_hit(voice, fxfile, dur, vm):
    """Pior batida: (folga em dB sobre a meta, segundo). Folga negativa significa fora da meta.

    Durante a fala, o efeito fica ao menos 6 dB abaixo da voz naquele instante.
    Na pausa não há palavra para cobrir: basta ficar 3 dB abaixo do nível médio da voz.
    """
    v, f = windows(voice, dur), windows(fxfile, dur); k = min(len(v), len(f)); v, f = v[:k], f[:k]
    margin = np.where(v > -30, v - f - 6, vm - f - 3); i = int(np.argmin(margin)); return float(margin[i]), i * 0.2


def fx(voice, bed, vol, out, dur):
    fc = f'[0:a]aresample=48000,apad,atrim=0:{dur}[v];[1:a]aresample=48000,volume={vol}[b];[b][v]{DUCK}[o]'
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', voice, '-i', bed, '-filter_complex', fc, '-map', '[o]', '-t', str(dur), out], check=True)


def main():
    a = argparse.ArgumentParser(); a.add_argument('project'); a.add_argument('--target', type=float, default=20); a.add_argument('--check', action='store_true'); o = a.parse_args()
    p = os.path.abspath(o.project); voice = glob.glob(p + '/src/narracao.*')[0]; bed = p + '/assets/bed.wav'; work = p + '/work'
    html = open(p + '/index.html', encoding='utf-8').read(); dur = float(re.search(r'data-duration="([\d.]+)"', html).group(1))
    vm = mean(voice); vol = 1.0; out = work + '/efeitos.wav'; gap = hit = at = None
    if o.check:
        gap = vm - mean(out); hit, at = worst_hit(voice, out, dur, vm)
        print(f'voz {vm:.1f} dB | efeitos sozinhos {vm - gap:.1f} dB | diferença média {gap:.1f} dB | pior batida com folga de {hit:.1f} dB em {at:.1f} s')
        problems = [m for ok, m in [(hit >= 0, f'batida forte demais em {at:.1f} s'), (gap >= 15, 'efeitos altos demais na média'), (gap <= 30, 'efeitos quase inaudíveis')] if not ok]
        sys.exit('REPROVADO: ' + '; '.join(problems) if problems else 0)
    for _ in range(10):
        fx(voice, bed, vol, out, dur); gap = vm - mean(out); hit, at = worst_hit(voice, out, dur, vm)
        if hit < 0: vol = round(vol * 10 ** ((hit - 1) / 20), 3); continue  # a batida manda: nunca por cima da fala
        if gap <= 22 and gap >= 18: break
        wanted = round(max(0.02, vol * 10 ** ((gap - o.target) / 20)), 3)
        if wanted > vol and hit < 2: break  # subir mais faria a batida passar por cima da voz
        vol = wanted
    mix = work + '/mix.wav'
    fc = f'[0:a]aresample=48000,apad,atrim=0:{dur}[v];[1:a]aresample=48000[f];[v][f]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[o]'
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', voice, '-i', out, '-filter_complex', fc, '-map', '[o]', mix], check=True)
    print(f'voz {vm:.1f} dB | efeitos sozinhos {vm - gap:.1f} dB | diferença média {gap:.1f} dB | pior batida com folga de {hit:.1f} dB em {at:.1f} s | volume da base {vol}')
    if hit < 0: sys.exit(f'Batida forte demais em {at:.1f} s: reduza o ganho desse put() em sfx_bed.py')
    if gap < 15: sys.exit('Efeitos altos demais na média')
    if gap > 30: print('Aviso: efeitos quase inaudíveis. Equilibre os ganhos dos put(): uma batida muito forte segura o volume de todas.')


if __name__ == '__main__':
    main()
