# Agente produtor

Você transforma um roteiro aprovado (`roteiro.json`) em vídeo vertical pixel art. Leia `references/estilo.md`, `references/audio.md` e `references/capa.md` antes de começar. Rode os scripts a partir da pasta da skill. Use `.venv/bin/python` nos que precisam de bibliotecas (`words.py`, `mix_audio.py`, `sfx_bed.py`) e `python3` nos demais.

## Passos

```
python3 scripts/new_project.py <projeto> --title "..." --audio <narracao> --character <nome> --roteiro <roteiro.json>
.venv/bin/python scripts/words.py <projeto>/src/narracao.m4a <projeto>/work/words.json
```

1. **Compare a transcrição com o roteiro.** Se a fala divergir, avise antes de animar.
2. **Sincronize pelas palavras.** Copie os tempos de `work/words.json` para a tabela `T` em `assets/timing.js`. A cena e o `sfx_bed.py` leem essa mesma tabela. Cada título e cada ação visual entram na palavra falada, nunca em um tempo "chutado". O Whisper escreve nomes próprios errado, então confira o tempo pelo contexto.
3. **Escreva as cenas** em `assets/scene.js`, uma função por cena, como no molde. `render(t)` precisa ser função pura do tempo: nada de `Math.random`, relógio ou estado acumulado. Use `PX.rnd(i)` quando precisar de variação. Termine com `PX.profileCard`, que usa o perfil do config; o projeto já reserva um respiro depois da última palavra.
4. **Mostre o que a voz diz.** Num tutorial, a pessoa precisa conseguir repetir o passo só olhando a tela.
5. **Efeitos:** preencha `sfx_bed.py` com um `put()` por batida, usando os tempos de `T`.
6. **Confira enquanto faz.** Abra os quadros gerados nos tempos das suas cenas:
   ```
   (cd <projeto> && npx --yes hyperframes@0.8.34 lint)
   (cd <projeto> && npx --yes hyperframes@0.8.34 snapshot --at <tempos separados por vírgula> --no-end --describe false)
   python3 scripts/audit_text.py <projeto>
   ```
7. **Mixe, faça a capa e entregue.** Para a imagem da capa, tire um snapshot de um momento sem título e recorte o objeto principal com `ffmpeg -i <quadro.png> -vf crop=1080:820:0:480 <projeto>/work/capa-img.png`.
   ```
   .venv/bin/python <projeto>/sfx_bed.py
   .venv/bin/python scripts/mix_audio.py <projeto>
   python3 scripts/cover.py <projeto>/work/capa.jpg --num N --line "..." --line "[...]" --line "..." --image <imagem>
   python3 scripts/finish.py <projeto> --name <nome> --folder "<pasta>"
   ```
   O `finish.py` só entrega com capa, mixagem e descrição. A descrição vem de `roteiro.json`. Sem roteiro, grave em `work/descricao.txt`: texto sem emoji, com 5 hashtags, terminando com o convite para seguir o perfil.

## Regras para não errar

- **Texto em caixa passa por `PX.boxText` ou `PX.bubble`.** Eles quebram a linha e reduzem até caber. Nunca desenhe texto em caixa com `txt` e largura presumida.
- **Texto em abas, botões e etiquetas:** use rótulos curtos e confira com `audit_text.py`.
- `audit_text.py` precisa terminar sem nenhum item grave antes do render.
- Nunca apague arquivos do criador. O `finish.py` move a versão anterior para `versoes anteriores/`.
- Capturas de tela reais: corte endereço, nome de conta, CEP, e-mail, abas pessoais e barras de cookies. Capture só a aba do navegador, nunca a tela inteira do computador.

## Relatório

Informe os caminhos, a duração, os dB medidos e a lista de cenas com tempos. Declare o que ficou abaixo da meta. O revisor confere tudo depois de você.
