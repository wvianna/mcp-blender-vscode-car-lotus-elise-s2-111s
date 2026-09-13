# design.md — Modelagem procedimental do Lotus Elise 111S

## Sistema de coordenadas

- `+X` = frente do veículo, `+Y` = lado esquerdo, `+Z` = altura. Solo em `Z = 0`, eixos de roda em `X = ±1.15`.
- Unidades: metros (`unit_settings.system = 'METRIC'`, `scale_length = 1.0`).

## Dimensões de referência (Lotus Elise Series 1 111S)

| Parâmetro | Valor |
|---|---|
| Comprimento | 3,726 m (`x ∈ [-1.863, +1.863]`) |
| Largura | 1,718 m (meia-largura máx. 0,859 m) |
| Altura | 1,117 m (topo do teto) |
| Entre-eixos | 2,300 m |
| Bitola dianteira / traseira | 1,419 m / 1,454 m |
| Pneu dianteiro | 185/55R15 → raio 0,292 m, meia-largura 0,0925 m |
| Pneu traseiro | 205/50R16 → raio 0,306 m, meia-largura 0,1025 m |
| Altura de cintura (beltline) | ≈ 0,80 m |
| Topo do deck do motor | ≈ 0,92 m |
| Altura mínima (saias/splitter) | ≈ 0,12 m |

## Estratégia de modelagem

### 1. Casco principal (loft de seções transversais)

O corpo é um **loft** ao longo de X: em cada estação define-se um perfil transversal fechado com 10 pontos
(meio-perfil espelhado), garantindo grade 100% quádrupla e continuidade suave após Sub-D.

Parâmetros por estação: `w` (meia-largura máxima), `wt` (meia-largura do topo), `zb` (altura do fundo),
`zm` (altura da largura máxima), `zs` (altura do ombro), `zte` (altura da aresta superior), `zt` (altura do centro do topo).

Pontos do meio-perfil (y, z), do centro do fundo ao centro do topo:

```text
0: (0.00 , zb)
1: (0.40w, zb)
2: (0.82w, zb + 0.35(zm - zb))
3: (0.98w, zm - 0.10(zm - zb))
4: (1.00w, zm)                 <- largura máxima
5: (0.96w, zs)                 <- ombro / cintura
6: (0.82w, zte - 0.03)
7: (0.45wt, zte)
8: (0.17wt, zte + 0.55(zt - zte))
9: (0.00 , zt)
```

O perfil é espelhado em Y e fechado por 18 segmentos por anel. As extremidades (nariz e cauda) recebem
tampas por `bmesh.ops.grid_fill` (quads); se indisponível para o contorno, usa-se leque triangular restrito a
área não visível, registrado como desvio.

### 2. Arcos de roda sem boolean

O recorte do arco é obtido **elevando `zb`** nas estações junto aos eixos (de 0,13 m na saia para ≈ 0,70 m no centro
da roda). Isso gera um "túnel" suave sobre o pneu com topologia quádrupla intacta — sem booleans, sem n-gons.
A densidade de estações é aumentada em `x ≈ 1.15` e `x ≈ -1.15` para preservar a aresta viva do lip.

### 3. Cabine

Segundo loft independente assentado sobre a cintura (`z = 0,80`), de `x = +0,80` (base do para-brisa) até `x = -0,62`
(base do buttress). Faixas de faces recebem material por índice (estação × banda do perfil):

- bandas 0–1 (para-brisa) → `MAT_Glass_Polycarbonate` (vidro);
- bandas do topo → `MAT_Blue_Metallic` (teto rígido pintado);
- bandas laterais entre para-brisa e buttress → vidro (janelas laterais), com A-pillar/C-pillar em pintura;
- banda final descendente → janela traseira em vidro.

Atribuir material por faixa evita placas de vidro flutuantes e mantém G2 entre vidro e carroceria.

### 4. Componentes independentes

Rodas (6 spokes), faróis (housing + lente + óptica interna), lanternas, grelha frontal, louvers do engine cover,
entradas de ar laterais (recesso real), espelhos, difusor, escapes, splitter, roll bar, assentos, painel, volante,
emblemas (`LOTUS`, `111S` — text objects convertidos em malha).

### 5. Materiais

| Material | Estratégia |
|---|---|
| `MAT_Blue_Metallic` | Principled: Base Color azul profundo; Noise (escala fina) → Bump + mistura em Roughness (micro-flakes); Coat Weight 0,6 / Coat Roughness 0,02 / Coat IOR 1,55 (clear coat); Layer Weight (Facing) → ColorRamp → Mix com azul escuro (profundidade de pigmento) |
| `MAT_Glass_Polycarbonate` | Transmission Weight 1,0; Roughness 0,02; IOR 1,58; leve tonalidade |
| `MAT_Rubber_Tire` | Roughness 0,85 + Noise em Bump; preto |
| `MAT_Aluminum_Brushed` | Metallic 1,0; Roughness 0,32; Anisotropic 0,7 + Noise em Bump alongado |
| `MAT_Black_Trim` | Preto; Roughness 0,55 + Noise leve |
| `MAT_Chrome_Trim` | Metallic 1,0; Roughness 0,08 |
| `MAT_Lens_Red` / `MAT_Lens_Amber` | Transmission 1,0; Base Color vermelho/âmbar; Roughness 0,05 |
| `MAT_Headlamp_Lens` | Transmission 1,0; Roughness 0,03; IOR 1,52 |
| `MAT_Interior_Fabric` | Preto; Roughness 0,9 + Noise |

Conversão sRGB→linear aplicada a todas as cores hexadecimais definidas.

### 6. Rig neutro de verificação (não é o rig de estúdio do §5 da descrição)

Mundo cinza (0,35) + 3 luzes de área: key a 45° frontal-esquerda, fill oposta mais fraca, rim traseira superior.
Objetivo exclusivo: revelar continuidade de superfície (reflexos contínuos) e silhueta para comparação visual.

### 7. Câmeras de verificação

`CAM_Frontal`, `CAM_Lateral`, `CAM_Traseira`, `CAM_Superior`, `CAM_TresQuartos`, todas com distância focal longa
(≥ 85 mm) para minimizar distorção de perspectiva, posicionadas para reproduzir o enquadramento das imagens de referência.

## Estrutura do código

```text
scripts/
├── lotus_common.py            # helpers: srgb→linear, loft bmesh, materiais, metadados
├── build_lotus_elise_111s.py  # constrói corpo, cabine, rodas, detalhes, materiais, rig, câmeras, salva .blend
├── mesh_report.py             # relatório: n-gons, non-manifold, normais invertidas, bounding box
└── render_views.py            # render das 5 vistas de verificação em docs/renders/
```

## ADRs

- **ADR-001 — Modelagem procedimental via bpy, sem malhas externas.** Contexto: exigência de automação MCP e
  nomenclatura/metadados próprios; uso de modelo de terceiros traria licenciamento e topologia fora do padrão exigido.
  Decisão: gerar toda a geometria por script determinístico. Consequências: reprodutibilidade total; detalhamento fino
  limitado ao que o script descreve.
- **ADR-002 — Arcos de roda por variação de `zb` em vez de boolean.** Contexto: FR-013 proíbe n-gons; boolean gera
  topologia irregular e triângulos em borda visível. Decisão: modulação do fundo do perfil. Consequências: malha limpa;
  arco ligeiramente mais suave que o corte real, compensado por estações densas.
- **ADR-003 — Material de vidro atribuído por faixa de faces no loft da cabine.** Contexto: placas de vidro separadas
  criam descontinuidade e z-fighting. Decisão: material por índice de face. Consequências: continuidade preservada;
  exige mapeamento estável estação→banda.
- **ADR-004 — EEVEE como engine de verificação.** Contexto: build do Blender 5.2.1 LTS disponível expõe apenas
  `BLENDER_EEVEE`. Decisão: usar EEVEE com raytracing habilitado. Consequências: renders rápidos; reflexos menos
  precisos que Cycles, suficiente para checagem de continuidade.

## Alternativas rejeitadas

- **Boolean de arco de roda**: viola FR-013 (n-gons/triângulos em aresta visível).
- **Normal map para as entradas de ar laterais**: proibido explicitamente por FR-006.
- **Download de modelo pronto (Sketchfab/PolyHaven)**: não atende "criar o modelo" nem a convenção de nomes/metadados.
- **Escultura por metaballs**: topologia resultante não é quad-dominant nem adequada a Sub-D.
