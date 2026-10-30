#!/usr/bin/env python3
"""Prepara o material do revisor: uma folha 1 fps para ver o ritmo e quadros em resolução cheia para ler os detalhes.

Uso: review_frames.py video.mp4 pasta_saida [--at 1.2,5.0,9.4]
Sem --at, salva um quadro inteiro a cada 2 s, incluindo o último. A folha sozinha não basta: texto estourado não aparece nela.
"""
import argparse, math, os, subprocess
from common import duration


def main():
    a = argparse.ArgumentParser(); a.add_argument('video'); a.add_argument('out'); a.add_argument('--at', default=''); o = a.parse_args()
    os.makedirs(o.out, exist_ok=True); d = duration(o.video)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', o.video, '-vf', f'fps=1,scale=240:-1,tile=10x{math.ceil(d / 10)}', '-frames:v', '1', f'{o.out}/folha-1fps.jpg'], check=True)
    end = d - 0.2  # o último quadro nem sempre fica exatamente na duração informada
    times = [min(float(t), end) for t in o.at.split(',') if t] or [t * 2 + 0.5 for t in range(math.ceil((end - 0.5) / 2))] + [end]
    for t in times:
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(t), '-i', o.video, '-frames:v', '1', '-q:v', '2', f'{o.out}/t{t:06.2f}.jpg'], check=True)
    print(f'{o.out}: folha-1fps.jpg + {len(times)} quadros em resolução cheia')


if __name__ == '__main__':
    main()
