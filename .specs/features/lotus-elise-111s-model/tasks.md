# tasks.md — Modelagem do Lotus Elise 111S

Estados: `[ ]` pendente · `[-]` em andamento · `[x]` concluída · `[!]` bloqueada

## Lista

- [x] T-001 Helpers de build (`scripts/lotus_common.py`)
- [x] T-002 Casco principal por loft com arcos de roda modulados (FR-001, FR-002, FR-003, FR-013)
- [x] T-003 Cabine, vidros e interior simplificado (FR-010, FR-012)
- [x] T-004 Rodas de 6 raios e pneus (FR-004)
- [x] T-005 Conjuntos ópticos dianteiro e traseiro (FR-005, FR-008)
- [x] T-006 Entradas de ar, grelhas, louvers, difusor e escapes (FR-006, FR-007)
- [x] T-007 Espelhos, splitter, emblemas `LOTUS`/`111S` (FR-009, FR-011)
- [x] T-008 Biblioteca de materiais PBR multicamada (FR-019, FR-020)
- [x] T-009 Nomenclatura, metadados, Subsurf e relatório de malha (FR-014 a FR-018)
- [x] T-010 Rig neutro + câmeras + renders de verificação (NFR-001, NFR-004)
- [x] T-011 Comparação visual com as referências e iteração corretiva (CA-004 a CA-008)
- [x] T-012 Salvar `.blend` e finalizar documentação (NFR-002)

## Detalhamento

### T-001 — Helpers de build

- Requisitos: FR-021
- Onde: `scripts/lotus_common.py`
- Depende de: nenhum
- Feito quando: existem helpers de `srgb_to_linear`, criação de material PBR, montagem de loft bmesh com grade
  quádrupla, aplicação de metadados e limpeza idempotente da cena.
- Gate: import do módulo sem erro dentro do Blender.

### T-002 — Casco principal

- Requisitos: FR-001, FR-002, FR-003, FR-013
- Onde: `scripts/build_lotus_elise_111s.py`
- Depende de: T-001
- Feito quando: existe `GEO_Body_Hull` com ≥ 30 estações, fundo modulado (arcos), tampas por `grid_fill`, 0 n-gons.
- Gate: relatório de malha sem n-gons e bounding box dentro de ±2 cm.

### T-003 — Cabine e interior

- Requisitos: FR-010, FR-012
- Onde: `scripts/build_lotus_elise_111s.py`
- Depende de: T-002
- Feito quando: `GEO_Cabin_Hull` tem vidro por faixa de faces, headliner/teto pintado e interior simplificado
  (`GEO_Seat_L/R`, `GEO_Dashboard`, `GEO_Steering_Wheel`, `GEO_RollBar`).
- Gate: render 3/4 mostra para-brisa e janelas contínuos com a carroceria.

### T-004 — Rodas

- Requisitos: FR-004
- Onde: `scripts/build_lotus_elise_111s.py`
- Depende de: T-001
- Feito quando: 4 rodas nomeadas `GEO_Wheel_*` com 6 spokes, tampa central, pneu com perfil próprio e raios
  0,292 m (frente) / 0,306 m (trás) nos eixos `x = ±1.15` e bitolas corretas.
- Gate: close-up da roda evidencia 6 spokes.

### T-005 — Conjuntos ópticos

- Requisitos: FR-005, FR-008
- Onde: `scripts/build_lotus_elise_111s.py`
- Depende de: T-002
- Feito quando: cada farol tem housing, óptica interna e lente; a traseira tem 4 lanternas com aro metálico e
  2 refletores vermelhos no difusor.
- Gate: renders frontal e traseiro comparáveis às referências.

### T-006 — Ventilações

- Requisitos: FR-006, FR-007
- Onde: `scripts/build_lotus_elise_111s.py`
- Depende de: T-002
- Feito quando: entradas laterais são recessos com profundidade real; grelha frontal e louvers do engine cover
  têm aletas modeladas; difusor tem 2 saídas de escape centrais.
- Gate: render superior mostra os recortes e louvers.

### T-007 — Espelhos e emblemas

- Requisitos: FR-009, FR-011
- Onde: `scripts/build_lotus_elise_111s.py`
- Depende de: T-002
- Feito quando: espelhos em haste na cor da carroceria e textos `LOTUS` / `111S` convertidos em malha na traseira.
- Gate: render traseiro legível.

### T-008 — Materiais

- Requisitos: FR-019, FR-020
- Onde: `scripts/lotus_common.py`, `scripts/build_lotus_elise_111s.py`
- Depende de: T-001
- Feito quando: todos os `MAT_*` existem com os parâmetros especificados (Coat IOR 1,55 / Coat Roughness 0,02;
  borracha 0,85; policarbonato 0,02; alumínio escovado 0,32).
- Gate: inspeção dos valores dos nós no build.

### T-009 — Nomenclatura, metadados e relatório

- Requisitos: FR-014 a FR-018
- Onde: `scripts/mesh_report.py`, `scripts/build_lotus_elise_111s.py`
- Depende de: T-002..T-008
- Feito quando: todo objeto possui prefixo de categoria e custom properties; Subsurf com render levels = 3 nos
  corpos; relatório lista n-gons, non-manifold e normais invertidas = 0.
- Gate: saída do relatório anexada ao `SUMMARY.md`.

### T-010 — Renders

- Requisitos: NFR-001, NFR-004
- Onde: `scripts/render_views.py`
- Depende de: T-002..T-009
- Feito quando: 5 PNGs (frontal, lateral, traseira, superior, 3/4) + 1 close de roda em `docs/renders/`.
- Gate: todos os arquivos existem e renderizam em ≤ 90 s por vista.

### T-011 — Comparação visual

- Requisitos: CA-004, CA-005, CA-006, CA-007, CA-008
- Onde: `docs/renders/`
- Depende de: T-010
- Feito quando: cada render foi confrontado com a imagem de referência correspondente e os desvios foram
  corrigidos ou registrados.
- Gate: tabela de comparação em `SUMMARY.md` com PASS/FAIL/PENDENTE por critério.

### T-012 — Fechamento

- Requisitos: NFR-002
- Onde: `car-lotus-elise-111s.blend`, `README.md`, `AGENTS.md`, `STATUS.md`, `HANDOFF.md`
- Depende de: T-011
- Feito quando: cena salva, documentação refletindo o estado real e pendências registradas.
- Gate: `.blend` reaberto sem erros.

## Entregáveis e aceite

- **Código**: `scripts/lotus_common.py`, `scripts/build_lotus_elise_111s.py`, `scripts/mesh_report.py`, `scripts/render_views.py`
- **Modelo**: `car-lotus-elise-111s.blend`
- **Evidência visual**: `docs/renders/*.png` comparados com `images/*.jpeg`
- **Documentação**: `README.md`, `AGENTS.md`, `STATUS.md`, `HANDOFF.md`, `.specs/features/lotus-elise-111s-model/*`
- **Build/execução**: `blender --background --python scripts/build_lotus_elise_111s.py` (ou execução via MCP)
- **Testes**: não aplicável por decisão do usuário — evidência é a comparação visual (nível `LOCAL`)
- **Resultado**: ver `.specs/features/lotus-elise-111s-model/SUMMARY.md` (CA-004 e CA-007 ficaram como PARCIAL)
- **Critérios**: CA-001 a CA-009 rastreados em `SUMMARY.md`
- **Pendências e riscos residuais**: rig de estúdio completo (§5 da descrição) e validação Zebra/Isophotes automatizada
  permanecem fora de escopo; responsável pela validação final: usuário.
