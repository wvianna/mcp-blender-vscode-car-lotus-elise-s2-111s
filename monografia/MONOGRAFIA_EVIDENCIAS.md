# MONOGRAFIA — EVIDÊNCIAS

| Afirmação | Evidência | Arquivo/Fonte | Seção |
|---|---|---|---|
| Envelope: 3,736 × 1,718 × 1,117 m | medição por bounding box no build | `docs/renders/mesh_report.txt` | 6.4 / Tabela 6.3 |
| Solo em Z = 0,0000 e centro em Y = 0,0000 | medição por bounding box | `docs/renders/mesh_report.txt` | 6.4 |
| 130 objetos de malha, 13 materiais, 4 luzes, 9 câmeras | relatório de build | `docs/renders/mesh_report.txt`, `scripts/build_lotus_elise_111s.py` | 6.2 / Tabela 6.2 |
| 32.632 faces: 29.272 quads, 3.360 tris, 0 n-gons | relatório de malha | `docs/renders/mesh_report.txt` | 6.2 |
| 0 arestas non-manifold | relatório de malha | `docs/renders/mesh_report.txt` | 6.2 |
| 1.776 arestas de borda, só em glifos de emblema | relatório de malha (por objeto) | `docs/renders/mesh_report.txt` | 6.2 / Quadro 6.1 |
| Casco com 750 faces, todas quads | relatório de malha | `docs/renders/mesh_report.txt` | 6.3 |
| Casco definido por 47 estações × 16 pontos/anel | código-fonte + aritmética de faces | `scripts/build_lotus_elise_111s.py`, `scripts/lotus_common.py` | 5.4 / Apêndice A e D |
| Cabine com 148 faces, todas quads | relatório de malha | `docs/renders/mesh_report.txt` | 6.3 |
| Rodas com 6 raios, 185/55R15 e 205/50R16 | código + render de detalhe | `scripts/build_lotus_elise_111s.py`, `docs/renders/07_wheel_closeup.png` | 5.7 / Fig. 6.6 |
| Arco de roda sem operação booleana | código `arch_bottom` + vista neutra | `scripts/lotus_common.py`, `docs/renders/10_clay_lateral.png` | 5.4.3 / Fig. 6.7 |
| Entradas de ar com rebaixo real (62 mm) | código `_scoop_dent` + vista neutra | `scripts/build_lotus_elise_111s.py` | 5.4.5 |
| Rebaixo real do alojamento dos faróis (30 mm) | código `_headlamp_recess` | `scripts/build_lotus_elise_111s.py` | 5.4.5 |
| Tampas de loft produzem apenas quads | código `_folded_fan_cap` + 0 n-gons no relatório | `scripts/lotus_common.py` | 5.4.4 |
| Pintura multicamada com verniz IOR 1,55 / rug. 0,02 | código de `build_materials` + render 3/4 | `scripts/build_lotus_elise_111s.py` | 5.3.1 / Fig. 6.5 |
| Cores convertidas de sRGB para linear | código `srgb_to_linear` | `scripts/lotus_common.py` | 5.2.1 |
| Refração habilitada em vidros e lentes | código de habilitação | `scripts/build_lotus_elise_111s.py` | 5.3.2 |
| Render: EEVEE, 1500×1000 | configuração de render | `scripts/render_views.py`, `scripts/render_gallery.py` | 6.1 |
| Tempos: 45,4 s (9 vistas, 64 amostras); ~37 s (galeria, 96 amostras) | registro de sessão | `SUMMARY.md`, `STATUS.md` | 6.1 / Tabela 6.1 |
| Build idempotente em ~0,6 s | execução do script | `scripts/build_lotus_elise_111s.py` | 6.1 |
| Automação via MCP em transporte stdio | configuração do servidor | `.vscode/mcp.json` | 4.3 / 5.11 |
| Metadados `cat`, `part`, `mat_swap_key` | código `tag` + inspeção da cena | `scripts/lotus_common.py` | 5.9 |
| Subdivisão com render levels = 3 nos corpos | código `finalize`/`add_subsurf` | `scripts/lotus_common.py` | 5.9 |
| Ausência da linha de caráter lateral (CA-004 parcial) | inspeção comparativa da vista lateral | `docs/renders/03_lateral.png` × `images/lateral.jpeg` | 6.5.2 / 7.2.1 |
| Tom de pintura mais escuro que a referência (CA-007 parcial) | inspeção comparativa 3/4 | `docs/renders/05_three_quarter.png` × `images/car.jpeg` | 6.5.5 / 7.2.2 |
| 49 referências bibliográficas reais | `references.bib` | `references.bib` | Referências |
| Divergência 45 × 47 estações na documentação | confronto código × documentação | `STATUS.md` vs `scripts/build_lotus_elise_111s.py` | Apêndice D.5 |
