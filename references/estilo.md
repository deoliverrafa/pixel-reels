# Estilo visual

Pixel art 2D de motion graphics, com fundo escuro, holofote colorido, sombra dura e poeira de pixels.

- **Formato:** 1080x1920.
- **Zona segura do Reels:** topo 220, base 450, laterais 35.
- **Paleta:** `estilo` no `config.json`. Ela é aplicada automaticamente em `assets/style.js`.
- **Fontes:** Press Start 2P para títulos, Silkscreen para o resto. A Press Start 2P não tem acentos neste recorte; `txt` desenha os acentos em pixel.
- **Tamanhos:** texto com pelo menos 40 px, objeto principal com 60 a 85% da largura, personagem com pelo menos 30% da largura quando for o foco. O boneco visível mede cerca de 18 unidades de largura: escala 18 dá 30%.
- **Sem logos:** interfaces viram maquetes genéricas e o assistente é um robô próprio (`drawRobot`). Em capturas de tela reais, o logo que já está na tela é aceitável.
- **Sem legenda corrida e sem filtro:** só títulos com palavras-chave. Legenda fica para o editor (CapCut etc.).

## Ferramentas do motor (`PX`)

| Função | Para quê |
|---|---|
| `frame(t)` | Fundo e poeira, no início de cada quadro |
| `creamTitle`, `banner` | Títulos; já reduzem para caber na largura |
| `boxText(texto, x, y, w, h, cor, {f, size, min, pad, al, sh})` | Texto em caixa; quebra a linha e reduz até caber |
| `bubble(texto, x, y, w, h, {col, light, text, size})` | Balão de chat, usa `boxText` |
| `txt(texto, x, y, tamanho, cor, {f: 'p' \| 'sb' \| 's', al, sh})` | Texto solto, sem caixa |
| `popScale(t, t0, t1)`, `withScale(cx, cy, s, rot, fn)` | Entrada e saída com salto |
| `drawPerson(chave, x, base, escala, estado)` | Personagem (ver abaixo) |
| `drawRobot(x, base, escala, {eyes: 'happy', look: 'left' \| 'right', glow, armL, armR, wave, t})` | Assistente genérico |
| `winFrame(x, y, w, h, título, {ts})`, `paper(x, y, w, h)`, `card(cx, cy, w, h, rot, escala, fn)` | Janela, folha e cartão |
| `cursorAt(x, y, escala, pressionado)`, `burst(x, y, t, t0)`, `checkBadge(x, y, s)`, `star(x, y, p, cor)`, `pdisk(cx, cy, r, cor)` | Detalhes |
| `profileCard(t, t0, chave)` | Card final com o perfil do config |

Cores: `CREAM` (texto claro), `INKP` (texto sobre papel), `RED`, `REDD`, `REDL` (destaque, escuro, claro), `K` (sombra), `MUTE` (secundário).

Estado do personagem: `mouth` (`n`, `smile`, `grin`, `o`, `wavy`), `brow` (`up`, `sorry`, `flat`), `gaze` (`n`, `side`, `left`, `down`, `up`), `armL` e `armR` (`n`, `wave`, `hold`, `up`), `wave` (0 ou 1, alterna o aceno), `walk` (tempo, anima os passos).

## Cenas com tela real

Coloque a captura numa moldura de janela pixel e dê zoom de 2x na região importante. O texto real raramente chega a 40 px: reforce com etiquetas pixel. Capture só a aba necessária e corte dados pessoais antes de copiar a imagem para o projeto.
