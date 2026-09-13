# SUMMARY.md — entrega da modelagem do Lotus Elise 111S

Data: 2026-09-13 · Escopo SDD: **Grande** (recurso novo, múltiplos componentes, arquivo único de persistência)
· Nível de evidência: **LOCAL** (Blender 5.2.1 LTS executado localmente via MCP)

## Entregáveis

| Artefato | Caminho |
|---|---|
| Modelo Blender | `car-lotus-elise-111s.blend` |
| Build idempotente | `scripts/build_lotus_elise_111s.py` |
| Helpers de modelagem | `scripts/lotus_common.py` |
| Renders de verificação | `scripts/render_views.py` → `docs/renders/*.png` |
| Galeria de apresentação | `scripts/render_gallery.py` → `images/modelo3d-*.png` |
| Relatório de malha | `docs/renders/mesh_report.txt` |
| Especificação / design / tarefas | `.specs/features/lotus-elise-111s-model/` |
| Continuidade | `README.md`, `AGENTS.md`, `STATUS.md`, `HANDOFF.md`, `LICENSE` |

## Build e verificação

```bash
blender --background car-lotus-elise-111s.blend --python scripts/build_lotus_elise_111s.py   # ~0,6 s
blender --background car-lotus-elise-111s.blend --python scripts/render_gallery.py            # ~39 s
blender --background car-lotus-elise-111s.blend --python scripts/render_views.py              # ~52 s
```

Ou, na sessão MCP: `exec(open("scripts/build_lotus_elise_111s.py").read())`.

### Resultado do build

- 130 objetos de malha · 13 materiais · 4 luzes · 9 câmeras
- Faces na malha base: **32.632** → quads 29.272 · tris 3.360 · **n-gons 0**
- Arestas non-manifold: **0** · Arestas de borda: 1.776 (apenas glifos dos emblemas)
- Envelope: **X 3,736 m · Y 1,718 m · Z 1,117 m**, solo em Z = 0,000, centrado em Y

### Tempos de render (EEVEE, 64 amostras, 1500×1000)

frontal 6,3 s · superior 3,9 s · lateral 4,0 s · traseira 4,8 s · 3/4 5,9 s · 3/4 traseira 5,8 s ·
close de roda 6,4 s · clay lateral 3,6 s · clay 3/4 4,8 s · **total 45,4 s**

## Critérios de aceite

| ID | Critério (resumo) | Status | Evidência / observação |
|---|---|---|---|
| CA-001 | Build reconstrói o modelo sem erro | **PASS** | execução via MCP; 130 objetos `GEO_*` |
| CA-002 | Envelope dentro de ±2 cm | **PASS** | X +1,0 cm; Y e Z exatos (`mesh_report.txt`) |
| CA-003 | 0 n-gons e normais coerentes nos corpos | **PASS** | 0 n-gons global; 0 non-manifold |
| CA-004 | Silhueta lateral coerente com `lateral.jpeg` | **PARCIAL** | proporções e arcos corretos; corpo mais arredondado que a referência, falta a linha de caráter |
| CA-005 | Frente com 2 faróis ovais + grade + auxiliares | **PASS** | `01_frontal.png` × `frontal.jpeg` |
| CA-006 | Traseira com 4 lanternas, LOTUS, 111S, escapes, difusor | **PASS** | `04_traseira.png` × `traseira1.jpeg` |
| CA-007 | Pintura azul multicamada com reflexos contínuos | **PARCIAL** | `05_three_quarter.png`: reflexos contínuos, sem facetas; tom um pouco mais escuro que a referência |
| CA-008 | Vista superior com entradas de ar, louvers e roll bar | **PASS** | `02_superior.png` × `superior_branco.jpeg` |
| CA-009 | Nomenclatura e metadados por objeto | **PASS** | `cat`, `part`, `mat_swap_key` em todos os `GEO_*`/`LGT_*`/`CAM_*` |

## Rastreabilidade requisito → evidência

| Requisito | Evidência | Status |
|---|---|---|
| FR-001 escala | `mesh_report.txt` (envelope) | PASS |
| FR-002 silhueta | `03_lateral.png`, `10_clay_lateral.png` | PARCIAL |
| FR-003 arcos sem boolean | código `arch_bottom` + `10_clay_lateral.png` | PASS |
| FR-004 rodas 6 raios | `07_wheel_closeup.png` | PASS |
| FR-005 faróis com carcaça | `01_frontal.png` | PASS |
| FR-006 entradas de ar com geometria real | `_scoop_dent` + `10_clay_lateral.png` | PASS |
| FR-007 grelha, louvers, difusor e escapes | `01_frontal.png`, `02_superior.png`, `04_traseira.png` | PASS |
| FR-008 4 lanternas + refletores | `04_traseira.png` | PASS |
| FR-009 emblemas LOTUS/111S | `04_traseira.png` | PASS |
| FR-010 cabine e vidros | `05_three_quarter.png` | PASS |
| FR-011 espelhos | `01_frontal.png` | PASS |
| FR-012 interior simplificado | `04_traseira.png` (roll bar e volante visíveis) | PASS |
| FR-013 quad-dominant, sem n-gons | `mesh_report.txt` (n-gons 0) | PASS |
| FR-014 Subsurf render levels 3 | `GEO_Body_Hull`, `GEO_Cabin_Hull` | PASS |
| FR-015 nomenclatura | nomes dos objetos no relatório | PASS |
| FR-016 metadados | `tag()` em todos os builders | PASS |
| FR-017 normais | `recalc_face_normals` + ausência de artefatos nos renders | PASS |
| FR-018 relatório de malha | `docs/renders/mesh_report.txt` | PASS |
| FR-019 pintura multicamada | nós de `MAT_Blue_Metallic` + `05_three_quarter.png` | PARCIAL (tom) |
| FR-020 materiais secundários | `MAT_Rubber_Tire`, `MAT_Glass_Polycarbonate`, `MAT_Aluminum_Brushed` etc. | PASS |
| FR-021 build idempotente | reexecuções sucessivas via MCP | PASS |
| NFR-001 tempo de render/malha | 45,4 s para 9 vistas; 32.600 faces base | PASS |
| NFR-002 persistência local | `car-lotus-elise-111s.blend` | PASS |
| NFR-003 determinismo | sem aleatoriedade não semeada | PASS |
| NFR-004 comparação visual documentada | `docs/renders/*` nesta tabela | PASS |

## Desvios da especificação

| ID | Desvio | Justificativa |
|---|---|---|
| SPEC_DEVIATION-01 | Interior simplificado (sem tapetes, portas internas, cintos) | fora de escopo por decisão do usuário |
| SPEC_DEVIATION-02 | Rig de estúdio do §5 substituído por rig neutro de 4 luzes de área | necessário apenas para viabilizar a verificação visual |
| SPEC_DEVIATION-03 | Grelha frontal e inserções ópticas são objetos assentados sobre a superfície, não recortes perfurados | a tampa de loft não possui vértices internos para escavar; a alternativa (boolean) viola FR-013 via geração de n-gons |
| SPEC_DEVIATION-04 | Triângulos presentes em cantos de chanfro e glifos de emblema | FR-013 admite triângulos em superfícies planas; nenhum triângulo em superfície curva principal |
| SPEC_DEVIATION-05 | Envelope X 3,736 m (alvo 3,726 m) | +1,0 cm, dentro da tolerância de ±2 cm do CA-002 |
| SPEC_DEVIATION-06 | Validação Zebra/Isophotes por inspeção visual dos reflexos, sem ferramenta dedicada | decisão do usuário de verificação apenas visual |

## Riscos residuais

- Fidelidade de superfície (arestas vivas, linha de caráter) — requer nova iteração de topologia.
- Arestas de borda nos emblemas de texto podem gerar artefatos em close-ups extremos.
- Renders dependem de `BLENDER_EEVEE`; outro build do Blender pode mudar o resultado fotométrico.

## Responsável pela validação

Usuário (validação visual final contra `images/`).
