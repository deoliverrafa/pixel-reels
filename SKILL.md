---
name: pixel-reels
description: Cria Reels verticais animados em pixel art, do roteiro à entrega, com um agente roteirista, um produtor e um revisor independente. Inclui criação de personagem, narração opcional com ElevenLabs, efeitos sonoros sincronizados e capa. Use quando pedirem para criar um vídeo, Reel, Short ou TikTok animado em pixel art, escrever e produzir um roteiro de vídeo, criar um personagem pixel art para vídeos, ou com /pixel-reels.
---

# Pixel Reels

Você coordena uma equipe de agentes para produzir um Reel. Você não escreve as cenas: delega, revisa os relatórios e fala com o criador.

## Antes de tudo

1. Se `.venv` não existir na pasta da skill, rode `scripts/setup.sh`.
2. Leia `~/.config/pixel-reels/config.json`. Se ainda tiver os valores de exemplo, peça o perfil, a chamada falada e, se for usar narração sintética, o ID da voz.
3. Nunca peça para o criador colar uma chave de API no chat. Oriente a salvar no arquivo indicado em `voz.arquivo_chave`.

## Fluxo

Cada etapa é um agente separado, e cada um recebe só o arquivo de instruções dele e os caminhos de que precisa. Vários vídeos rodam em paralelo, um produtor por vídeo.

| Etapa | Agente | Instruções | Resultado |
|---|---|---|---|
| 1 | Roteirista | `references/agents/roteirista.md` | `roteiro.json`, `narracao.txt` |
| 2 | Personagem (só se ainda não existir) | `references/agents/personagem.md` | `characters/<nome>.json` e a folha de aprovação |
| 3 | Narração (você mesmo) | `references/audio.md` | Áudio do criador ou `scripts/tts.py` |
| 4 | Produtor | `references/agents/produtor.md` | Vídeo, capa, pasta de entrega |
| 5 | Revisor | `references/agents/revisor.md` | Veredito com tempos e correções |
| 6 | Correção | Mesmo produtor | Nova versão |

## Pontos de aprovação do criador

Pare e mostre antes de seguir:

- **Depois do roteiro:** o gancho e a fala completa, com as pendências de dados reais.
- **Depois do personagem:** a folha de expressões.
- **Depois da narração sintética:** o áudio, que é o que custa créditos para refazer.

Se o criador pediu para ir direto, siga e avise o que não foi aprovado.

## Ciclo de revisão

1. Depois de cada render, inicie um revisor **novo**, sem contexto do produtor. Passe só o caminho do projeto, do vídeo e do `roteiro.json`.
2. Se vier REPROVADO, envie os bloqueantes ao produtor, peça a correção e rode outro revisor novo.
3. Repita até APROVADO, em no máximo 3 rodadas. Depois disso, mostre ao criador o que ainda falta, sem esconder nada.
4. Só entregue com o `audit_text.py` sem itens graves, ou com cada item confirmado como falso positivo.

## Entrega ao criador

Informe a pasta, a duração, o que foi aprovado e o que ficou abaixo da meta. Lembre de ativar o rótulo de conteúdo de IA se a voz for sintética.
