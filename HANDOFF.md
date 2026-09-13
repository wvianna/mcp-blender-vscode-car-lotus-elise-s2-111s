# HANDOFF.md — Lotus Elise 111S

Data: 2026-09-13 · Sessão: modelagem inicial completa (corpo, cabine, rodas, óptica, ventilações, materiais, renders).

## Contexto

O projeto estava com um `.blend` vazio (cena limpa). Foi construído, por script procedimental, o modelo completo do
Lotus Elise 111S Series 1 em azul metálico profundo, com verificação visual contra `images/*.jpeg`.

## Estado atual

- `car-lotus-elise-111s.blend` — cena completa salva (130 malhas, 13 materiais, 4 luzes, 9 câmeras).
- Galeria publicada em `images/modelo3d-*.png` e embutida no `README.md` junto às referências do cliente.
- `scripts/build_lotus_elise_111s.py` — build idempotente (limpa a cena e reconstrói em ~0,6 s).
- `scripts/lotus_common.py` — helpers (loft, revolução, primitivas, materiais, relatório).
- `scripts/render_views.py` — 9 renders de verificação em `docs/renders/`.
- `scripts/mesh_report.py` — relatório de malha avulso (o build também emite o mesmo relatório em
  `docs/renders/mesh_report.txt`).
- `scripts/render_gallery.py` — galeria de apresentação em `images/modelo3d-{superior,traseira,lateral,isometrica,efeitoluz}.png`;
  o hero shot monta um rig dramático temporário (rim lights + emissão nos faróis + bloom no compositor) e restaura
  o rig neutro ao final. **Não salva o `.blend`**, de propósito.
- `monografia/` — monografia em LaTeX (`main.tex` + `chapters/` + `appendices/` + `diagrams/` + `references.bib`),
  compilada por `monografia/build.sh` (pdflatex → bibtex → pdflatex ×2) em `monografia/main.pdf` (94 páginas).
  Arquivos de controle: `MONOGRAFIA_STATUS.md`, `MONOGRAFIA_PLANO.md`, `MONOGRAFIA_EVIDENCIAS.md`,
  `MONOGRAFIA_RASTREABILIDADE.md`, `MONOGRAFIA_PENDENCIAS.md`.

## Alterações realizadas

1. `.specs/` criado com constituição, `spec.md` (21 FR, 4 NFR, 9 CA), `design.md` (4 ADRs) e `tasks.md`.
2. `AGENTS.md`, `README.md`, `LICENSE` (Apache 2.0) e este handoff.
3. Pipeline de modelagem procedimental:
   - corpo por loft de 47 seções transversais (16 pontos cada) com arcos de roda obtidos por modulação do fundo
     (`arch_bottom`) — sem boolean;
   - tampas de loft e de cilindros em quads via *folded fan* (`_folded_fan_cap`), eliminando n-gons;
   - cabine como segundo loft, com material de vidro atribuído por faixa de faces (sem placas flutuantes);
   - rebaixos reais (não normal map) para as entradas de ar laterais e para o alojamento dos faróis, por deslocamento
     de vértices com *falloff*;
   - rodas de 6 raios (revolução de perfil + 6 spokes + disco e pinça de freio);
   - pintura multicamada com micro-flakes (Noise → Bump/Roughness/Metallic) e clear coat (Coat IOR 1,55 /
     Coat Roughness 0,02), com profundidade de pigmento por Layer Weight.

## Decisões

- **ADR-001** modelagem 100% procedimental (sem assets externos).
- **ADR-002** arcos de roda por modulação do fundo do perfil, não por boolean.
- **ADR-003** vidro por índice de face no loft da cabine.
- **ADR-004** EEVEE como engine (única disponível) com raytracing ligado.
- Rig de estúdio do §5 da descrição tratado como **fora de escopo**; usado apenas rig neutro de verificação.
- Verificação por **comparação visual** (decisão do usuário), sem suíte de testes.

## Problemas encontrados e resolvidos

| Problema | Causa | Solução |
|---|---|---|
| `IndexError: list index out of range` no build | `lotus_common` ficava em cache no `sys.modules` da sessão do Blender, misturando versões | `importlib.reload(lc)` no início do script |
| Loft e cilindros com arestas de borda / n-gons | `bmesh.ops.grid_fill` não preenchia os laços; `create_cone` gera tampas n-gon | tampa *folded fan* própria (`_folded_fan_cap`) + `quad_caps` |
| Render gravado em outro workspace | `os.getcwd()` do Blender apontava para outro projeto | detecção de raiz exigindo `images/` + o `.blend` (ou `scripts/lotus_common.py`) |
| Lanternas traseiras ocultas pela carroça | superfície real (pós-Sub-D) recua em relação à tampa nominal do loft | lanternas deslocadas para trás do envelope nominal (≤ 1,863 m) |
| `view_settings.look` inválido | nomes de *look* do AgX mudam entre versões | tentativa em cascata com fallback |

## Pendências

1. Arestas vivas: adicionar *proximity loops* nas bordas de arco/entradas de ar (ver `STATUS.md`).
2. Emblemas de texto geram arestas de borda — trocar por glifos de contorno fechado.
3. Rig de estúdio do §5 (HDRI + light cards) se os renders de apresentação forem necessários.
4. Blender 5.2 expõe apenas `BLENDER_EEVEE`; se o build do Blender for trocado, reavaliar `render_views.py`.

## Cuidados para o próximo agente

- Sempre reexecutar o build completo; o script é idempotente e a fonte da verdade é `scripts/build_lotus_elise_111s.py`.
- `lotus_common.py` é recarregado pelo build — não é preciso reiniciar o Blender, mas scripts novos que o importem
  diretamente precisam do mesmo cuidado.
- As câmeras usam lentes longas (62–105 mm) e distâncias de 7,6–8,2 m: alterar uma sem a outra desenquadra a vista.
- O `.gitignore` já cobre `*.blend1`; não commitar automaticamente.

## Critério de conclusão

Modelo reconstruível por um comando, sem n-gons nos corpos, envelope dentro de ±2 cm das dimensões do 111S e
comparação visual registrada para as 5 vistas. **Atendido**, exceto pelos itens de fidelidade fina listados em
`STATUS.md` (limitações conhecidas).
