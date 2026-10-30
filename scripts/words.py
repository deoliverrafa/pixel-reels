#!/usr/bin/env python3
"""Tempos de cada palavra da narração. Uso: words.py audio saida.json [--lang pt]

Compare o texto impresso com o roteiro: a transcrição é também a conferência do que foi falado.
"""
import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

lang = sys.argv[sys.argv.index('--lang') + 1] if '--lang' in sys.argv else 'pt'
pcm = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', sys.argv[1], '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True, check=True).stdout
segs, _ = WhisperModel('medium', compute_type='int8').transcribe(np.frombuffer(pcm, np.float32), language=lang, word_timestamps=True)
out = [{'w': w.word.strip(), 'start': round(w.start, 2), 'end': round(w.end, 2)} for s in segs for w in s.words]
json.dump(out, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(' '.join(w['w'] for w in out)); print(len(out), 'palavras')
