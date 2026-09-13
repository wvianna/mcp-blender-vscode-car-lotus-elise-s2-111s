# MONOGRAFIA — RASTREABILIDADE

## Objetivo específico → método → evidência → resultado → status

| Objetivo específico | Método | Evidência | Resultado | Status |
|---|---|---|---|---|
| 1. Extrair dimensões das referências | Derivação em três passos (envelope como restrição dura; proporções das fotos; consistência com a ficha de pneus) | Tabela 4.1 (dimensões e origem) | Dimensões com origem declarada; envelope dentro de ±2 cm | Atendido |
| 2. Gerar casco por loft sem booleanas | Loft de 47 estações × 16 pontos; `arch_bottom`; `_folded_fan_cap` | 750 quads no casco; 0 n-gons; 0 non-manifold | Malha quadrangular por construção | Atendido |
| 3. Modelar identidade do 111S | `build_wheels`, `build_headlamps`, `build_rear_lights`, `build_vents`, `build_badges` | Fig. 6.6 (roda), Fig. 6.3 (traseira), Fig. 6.4 (superior) | 6 raios, 4 lanternas, entradas reais, emblemas | Atendido |
| 4. Materiais PBR multicamada | `build_materials` com Principled BSDF, Noise→Bump, verniz, Layer Weight | Quadro 5.3; Fig. 5.1 (grafo); Fig. 6.5 | 13 materiais; reflexos contínuos | Atendido (tom parcial) |
| 5. Cadeia de automação via MCP | Servidor `blender-mcp` (stdio) + execução de script na sessão viva | `.vscode/mcp.json`; Figs. 4.1 e 5.3 | Build e renders executados por script | Atendido |
| 6. Relatório de malha a cada build | `report()` + `mesh_stats` + `world_bounds` | `docs/renders/mesh_report.txt` | Relatório com n-gons, non-manifold, normais e envelope | Atendido |
| 7. Comparação visual e aceite | Render de 9 vistas + confronto com as 6 referências | Figs. 6.1–6.7; Quadro 6.5 | 7 critérios PASS, 2 PARCIAL | Atendido |

## Problema → objetivo geral → objetivos específicos → método → resultado

| Problema | Objetivo geral | Objetivos específicos | Método | Resultado |
|---|---|---|---|---|
| É possível um modelo 3D fiel e reprodutível, automatizado por agente via MCP, com topologia controlada e envelope verificado? | Produzir o modelo do Lotus Elise 111S por código, verificado visualmente | 1–7 (ver acima) | SDD enxuto + geometria procedimental + verificação numérica e visual comparativa | Modelo de 130 objetos, 32.632 faces, 0 n-gons, envelope em ±1 cm; silhueta e tom parciais |

## Requisito → evidência → status

| Requisito | Evidência | Status |
|---|---|---|
| FR-001 escala | `mesh_report.txt` (envelope) | PASS (+1,0 cm em X) |
| FR-002 silhueta | `03_lateral.png`, `10_clay_lateral.png` | PARCIAL (falta linha de caráter) |
| FR-003 arcos sem boolean | `arch_bottom` + vista neutra | PASS |
| FR-004 rodas de 6 raios | `07_wheel_closeup.png` | PASS |
| FR-005 faróis com carcaça | `01_frontal.png` | PASS |
| FR-006 entradas de ar reais | `_scoop_dent` (62 mm) | PASS |
| FR-007 grelha, louvers, difusor, escapes | `01/02/04` renders | PASS |
| FR-008 4 lanternas + refletores | `04_traseira.png` | PASS |
| FR-009 emblemas LOTUS/111S | `04_traseira.png` | PASS |
| FR-010 cabine e vidros | `05_three_quarter.png` | PASS |
| FR-011 espelhos | `01_frontal.png` | PASS |
| FR-012 interior simplificado | `04_traseira.png` | PASS |
| FR-013 quad-dominant, sem n-gons | `mesh_report.txt` (0 n-gons) | PASS |
| FR-014 Subsurf render levels 3 | código | PASS |
| FR-015 nomenclatura | relatório | PASS |
| FR-016 metadados | código `tag` | PASS |
| FR-017 normais | `recalc_face_normals` + renders sem artefato | PASS |
| FR-018 relatório de malha | `mesh_report.txt` | PASS |
| FR-019 pintura multicamada | nós + `05_three_quarter.png` | PARCIAL (tom) |
| FR-020 materiais secundários | 13 `MAT_*` | PASS |
| FR-021 build idempotente | reexecuções | PASS |
| NFR-001 tempo/render e malha | 45,4 s para 9 vistas | PASS |
| NFR-002 persistência local | `.blend` | PASS |
| NFR-003 determinismo | sem aleatoriedade não semeada | PASS |
| NFR-004 verificação documentada | renders + Quadro 6.5 | PASS |

## Critério de aceitação → status → evidência

| ID | Status | Evidência |
|---|---|---|
| CA-001 | PASS | 130 objetos `GEO_*` criados sem erro |
| CA-002 | PASS | +1,0 cm em X; Y e Z exatos |
| CA-003 | PASS | 0 n-gons; 0 non-manifold |
| CA-004 | PARCIAL | Fig. 6.2 — falta a linha de caráter |
| CA-005 | PASS | Fig. 6.1 |
| CA-006 | PASS | Fig. 6.3 |
| CA-007 | PARCIAL | Fig. 6.5 — tom mais escuro |
| CA-008 | PASS | Fig. 6.4 |
| CA-009 | PASS | metadados em todos os objetos |
