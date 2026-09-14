# STATUS.md — Lotus Elise 111S (modelo 3D)

Última atualização: 2026-09-14

## Concluído

| Item | Evidência |
|---|---|
| Levantamento visual das 6 referências em `images/` | leitura das imagens durante a sessão |
| Artefatos SDD (`spec.md`, `design.md`, `tasks.md`, constituição) | `.specs/` |
| Documentação de continuidade (`README.md`, `AGENTS.md`, `LICENSE`) | raiz do projeto |
| Biblioteca de helpers de modelagem (`scripts/lotus_common.py`) | 0 n-gons nas tampas; loft com tampas em quads |
| Corpo por loft de 47 seções, com arcos de roda modulados (sem boolean) | `GEO_Body_Hull`: 750 quads, 0 n-gons, 0 arestas de borda |
| Cabine com vidro atribuído por faixa de faces | `GEO_Cabin_Hull`: 148 quads, 0 n-gons |
| Interior simplificado (assentos, painel, volante, santo-antônio) | 7 objetos `GEO_*` |
| 4 rodas de 6 raios com pneu 185/55R15 e 205/50R16 | 4 × 11 objetos; close `docs/renders/07_wheel_closeup.png` |
| Conjuntos ópticos dianteiro e traseiro | 2 carcaças de farol + lentes; 4 lanternas com aro |
| Entradas de ar laterais com rebaixo real (sem normal map) | `_scoop_dent` em `GEO_Body_Hull`; visível em `10_clay_lateral.png` |
| Rebaixo real do alojamento dos faróis | `_headlamp_recess`; visível em `01_frontal.png` |
| Grelha frontal com aletas, difusor, escapamentos e splitter | renders frontal e traseiro |
| Emblemas `LOTUS` e `111S` como malha real | `GEO_Badge_LOTUS`, `GEO_Badge_111S` |
| Materiais PBR (pintura multicamada + 11 secundários) | 13 materiais `MAT_*` |
| Rig neutro de verificação e 7 câmeras | `LGT_*`, `CAM_*` |
| Relatório de malha automatizado | `docs/renders/mesh_report.txt` |
| 9 renders de verificação | `docs/renders/*.png` |
| Galeria de apresentação (superior, traseira, lateral, isométrica, efeito de luz) | `images/modelo3d-*.png` via `scripts/render_gallery.py` |
| Rig dramático do hero shot (rim lights + faróis acesos + bloom no compositor) | `render_gallery.py` (não persiste no `.blend`) |
| Monografia em LaTeX (94 páginas) com verificação visual e rastreabilidade por critério | `monografia/main.pdf`, `monografia/MONOGRAFIA_*.md`, `monografia/build.sh` |
| Artigo científico em LaTeX (32 páginas, 49 referências citadas, 0 erros/overfull) | `artigo/main.pdf`, `artigo/README.md`, `artigo/build.sh` |

### Números do último build

- Objetos de malha: 130 · Materiais: 13 · Luzes: 4 · Câmeras: 9
- Faces (malha base): 32.632 → quads 29.272 · tris 3.360 · **n-gons 0**
- Arestas non-manifold: **0**
- Envelope: X 3,736 m · Y 1,718 m · Z 1,117 m · solo em Z = 0,0000
- Galeria: 5 imagens em `images/modelo3d-*.png` (37 s) · verificação: 9 renders (52 s)

## Em andamento

- Nada bloqueante.

## Limitações conhecidas

1. **Fidelidade de superfície.** A silhueta e os elementos de identidade estão presentes, mas o corpo ainda é mais
   arredondado que a referência: faltam a linha de caráter lateral (waistline em crease) e a aresta viva do lip dos
   arcos. O loft com Sub-D suaviza transições abruptas.
2. **Triângulos em chanfros.** Os 3.360 triângulos vêm de cantos de `bevel` em caixas e dos glifos de texto dos
   emblemas — nunca de superfícies curvas principais. Ver `mesh_report.txt`.
3. **Cauda e bico.** Receberam anéis de retenção (`-1.852/-1.858` e `1.856/1.863`) que deixam a face mais plana e
   estável sob Sub-D; ainda assim o corte é menos seco que o da referência.
4. **Arestas de borda (1.776).** Exclusivamente das malhas de texto dos emblemas (glifos com contorno aberto).
5. **Interior simplificado** (fora de escopo por decisão do usuário).
6. **Rig de estúdio completo (§5 da descrição) não implementado** — apenas rig neutro de verificação.

## Próximo passo recomendado

1. Introduzir *proximity loops* nos contornos de arco e nas bordas das entradas de ar para preservar arestas
   vivas após a subdivisão (design.md, ADR-002) — os anéis de retenção do bico/cauda já validaram a técnica.
2. Avaliar `Crease` por aresta ou `Bevel` nos lips de para-lama em vez de aumentar a densidade de estações.
3. Substituir os emblemas de texto por glifos de contorno fechado (extrude) para eliminar arestas de borda.
4. Implementar o rig de iluminação de estúdio do §5 com HDRI neutro, se o cliente quiser os renders de apresentação.

## Ambiente verificado

- Blender 5.2.1 LTS · engine `BLENDER_EEVEE` (única disponível neste build)
- Execução via MCP `blender-mcp` na sessão local · evidência nível `LOCAL`
