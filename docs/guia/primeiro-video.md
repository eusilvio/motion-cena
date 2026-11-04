---
title: Primeiro vídeo
description: Como pedir o primeiro vídeo ao agente, o que ele mostra antes de gastar crédito, o que sai no fim e como iterar.
---

# Primeiro vídeo

Com o agente aberto na raiz do repositório, fale com ele como falaria com um editor. Um pedido curto já dispara o fluxo inteiro:

```text
Faz um reels de 30 s explicando juros compostos. Pesquisa os fatos.
```

Escreva em qualquer idioma: o agente entende o pedido e entrega no idioma em que você escreveu, inclusive a locução.

## Exemplos de pedido

| Você pede | Sai |
|---|---|
| *"Faz um reels de 30 s explicando juros compostos. Pesquisa os fatos."* | pesquisa com fonte, roteiro com 3 hooks, locução, animação e o MP4 de Reels e TikTok |
| *"Transforma esse PDF num vídeo de dados no estilo do meu site."* | os melhores números do relatório, com a página de origem, nas cores e fontes do site |
| *"Analisa o app em ../loja e faz um vídeo de 40 s do produto."* | fatos, telas e marca tirados do próprio código, sem ler `.env` nem dado de produção |
| *"Anima em cima desse vídeo em que eu falo, com legenda palavra por palavra."* | a sua gravação como base, com legenda, palavra-chave e cards no ritmo da fala |
| *"Narra esse texto num vídeo para Story. Usa o texto exatamente como está."* | narração palavra por palavra, sem adaptar o texto |
| *"Faz em carrossel de 7 slides."* | capa com gancho, um slide por ideia, PNG por slide, legenda e texto alternativo |

Diga a plataforma ("story", "reels", "TikTok", "YouTube") e, se quiser, a duração. Sem duração, o agente usa o padrão do preset: 30 s para Reels e TikTok, 15 s para Stories, 40 s para Shorts, 90 s para YouTube e 45 s para LinkedIn. Reels, TikTok ou Shorts sem plataforma definida viram o preset `vertical`, que serve aos três.

## Direção de movimento

Se você já sabe como quer o movimento, use a fórmula **efeito + duração + ease + alvo**. O agente traduz cada termo pelo dicionário, sem reinterpretar:

```text
Título entra com slide in em 0,4 s ease out, benefícios com stagger de 0,15 s.
Troca "ideia" por "vídeo" com text swap. Termina com punch zoom no produto.
```

Os nomes dos efeitos estão no [explorador de efeitos](/efeitos).

## Antes de gastar crédito, o plano

O agente não sai gravando voz. Primeiro ele escreve o `plan.md`: o formato narrativo escolhido, o roteiro com 3 hooks, a ideia central (e as duas descartadas) e o storyboard cena a cena. Então para e pede a sua aprovação antes de gastar crédito de voz e tempo de render.

Leia, peça mudança no que não gostou e aprove. Se você pediu *"faz tudo direto"*, ele pula a revisão e anota isso no plano.

## O que sai no fim

- O MP4 em `creatives/reels/<slug>-<preset>.mp4`. Num vídeo vertical, o mesmo arquivo sai como `-ig-reels.mp4` e `-tiktok.mp4`.
- A pasta `projects/<slug>/` com cada etapa: brief, plano, storyboard, marca, locução, timeline, composição e mixagem.
- Um relatório no chat com o caminho de cada MP4, a duração pedida e a real, o que mudou no seu roteiro e por quê, a ideia central, o hook usado e as alternativas, o provedor de voz, o que ficou de fora e sugestões de próxima versão.

Nada disso vai para o git: `projects/` e `creatives/` ficam na sua máquina.

## Iterar

Cada etapa grava um arquivo, então um ajuste refaz só o que mudou:

| Você pede | O agente refaz |
|---|---|
| *"Gera a versão com o hook B"* | a voz da cena 1, a timeline e o render |
| *"Adiciona efeitos sonoros"* ou *"tira a música"* | só o som e o render |
| *"Troca a entrada do título por blur in 0,5 s"* | só a linha do efeito e o render |
| *"Deixa mais rápido"* | voz 5 % mais rápida, cenas mais curtas e mais cortes |
| *"Faz a versão 16:9 para YouTube"* | o layout em 1920×1080, com a mesma narração e a mesma timeline |
| *"Divide em 3 stories"* | três partes cortadas no fim de frase |

::: tip Uma peça por sessão
A cada pedido o agente relê a conversa inteira. Nas sessões medidas, a segunda peça na mesma conversa custou de 35 % a 41 % da sessão. Terminou um vídeo? Abra uma sessão nova (`/clear` no Claude Code). Tudo fica gravado em `projects/<slug>/`, e o agente retoma de onde parou. Ajustes na mesma peça podem ficar na mesma sessão. Mais em [Quanto leva e quanto custa](/guia/custo-e-tempo).
:::

## Ver a edição ao vivo (opcional)

Peça *"quero ver ao vivo"* e, na etapa de animação, o agente abre o HyperFrames Studio assim que existe a primeira cena. O Studio recarrega a cada arquivo salvo: você vê o vídeo se montar cena por cena, com timeline, play e edição manual. Clicou num elemento e disse "muda isso"? O agente lê a seleção do Studio e sabe o que você apontou. Sem pedir, ele trabalha quieto e entrega o MP4.

Para ter chat e vídeo na mesma tela, suba a interface do projeto:

```bash
node tools/studio/server.mjs        # abre http://127.0.0.1:4400
```

À esquerda fica o chat com Claude Code, Codex ou Antigravity, com cada comando e arquivo aparecendo na hora. À direita, o Studio do projeto em edição, com abas de roteiro, storyboard e vídeo final. No topo, as etapas do pipeline acendem conforme os arquivos aparecem.

::: warning Aprovação automática
A interface escuta só em `127.0.0.1` e exige um token por execução, mas roda o agente com aprovação automática: uma página web não tem como responder aos pedidos de permissão dele. Use na sua máquina, em repositórios em que você confia.
:::
