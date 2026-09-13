# spec.md — Modelagem 3D do Lotus Elise 111S (Series 1)

- Origem da intenção: `docs/descricao.txt` (Especificação Técnica: Modelagem e Refino Estrutural do Lotus Elise 111S).
- Ground truth visual: `images/` (frontal.jpeg, lateral.jpeg, traseira1.jpeg, traseira2.jpeg, superior_branco.jpeg, car.jpeg).
- Entregável principal: `car-lotus-elise-111s.blend` (Blender 5.2.1 LTS), reconstruível por `scripts/build_lotus_elise_111s.py`.

## Objetivo

Produzir a geometria PBR do Lotus Elise 111S Series 1 em azul metálico profundo, com topologia quad-dominant apta a Sub-D,
nomenclatura por categoria, metadados para troca automatizada de material e evidência de verificação **visual comparativa**
contra as imagens de referência.

## Fora de escopo (decidido com o usuário)

- Suíte de testes automatizados (unitário/integração/contrato) — a verificação é visual comparativa.
- Rig de iluminação de estúdio completo (§5 da descrição original: softboxes, light cards, HDRI). Usa-se apenas um
  **rig neutro mínimo** (key/fill/rim + mundo cinza) para viabilizar os renders de comparação.
- Validação automatizada de Zebra Stripes / Isophotes (a checagem de continuidade é feita por inspeção visual dos
  reflexos nos renders).
- Interior completo: apenas versão simplificada (assentos, painel, volante, santo-antônio) para leitura através dos vidros.
- Decais/adesivos, sombreamento de interior detalhado, animação, exportação FBX/GLTF, impressão 3D.

## Requisitos funcionais

| ID | Requisito | Verificação |
|---|---|---|
| FR-001 | Escala real: comprimento 3,726 m; largura 1,718 m; altura 1,117 m; entre-eixos 2,300 m; bitola dianteira 1,419 m; bitola traseira 1,454 m; veículo centrado em X=Y=0 com solo em Z=0 (tolerância ±2 cm) | medição por bounding box (relatório de build) |
| FR-002 | Silhueta do 111S: nariz baixo, arcos de roda proeminentes, waistline ascendente para a traseira, deck do motor elevado e cauda truncada | render lateral × lateral.jpeg |
| FR-003 | Abertura de arco de roda real (sem boolean), com lip de para-lama; pneu posicionado dentro do arco sem interseção com a carroceria | render lateral/3-4 × referências |
| FR-004 | Rodas de 6 raios: dianteira 15" com 185/55R15 (raio 0,292 m), traseira 16" com 205/50R16 (raio 0,306 m); 6 spokes por roda + tampa central | render de detalhe da roda |
| FR-005 | Faróis: carcaça interna (housing) com design interno específico + lente de policarbonato + elemento óptico interno; seção de indicador âmbar | render frontal × frontal.jpeg |
| FR-006 | Entradas de ar laterais atrás das portas modeladas como abertura real (recesso com profundidade ≥ 3 cm), nunca via normal map | render 3/4 e superior × car.jpeg / superior_branco.jpeg |
| FR-007 | Ventilações funcionais: grelha frontal oval com grade, louvers do engine cover, difusor traseiro com duas saídas de escape centrais | renders frontal e traseiro |
| FR-008 | Conjunto óptico traseiro: 4 lanternas redondas (2 por lado) com lente vermelha e aro metálico; 2 refletores vermelhos no difusor | render traseiro × traseira1/traseira2.jpeg |
| FR-009 | Emblemas com geometria real: palavra "LOTUS" na traseira e emblema "111S" na traseira direita | render traseiro em close |
| FR-010 | Cabine: para-brisa, teto rígido, janelas laterais, janela traseira e buttresses; base do para-brisa na linha de cintura | render 3/4 × car.jpeg |
| FR-011 | Espelhos retrovisores laterais em haste, na cor da carroceria | render 3/4 e frontal |
| FR-012 | Interior simplificado: 2 assentos, painel, volante e santo-antônio, visíveis através dos vidros | render traseiro (vidro) × traseira1.jpeg |
| FR-013 | Malha quad-dominant: zero n-gons (faces com >4 vértices); triângulos somente em superfícies planas não visíveis | relatório de malha do build |
| FR-014 | Modifier Subdivision Surface com render levels = 3 nos corpos principais | inspeção do .blend |
| FR-015 | Nomenclatura por categoria: `GEO_` (geometria), `LGT_` (luz), `CAM_` (câmera), `MAT_` (material) | relatório de build (lista de objetos) |
| FR-016 | Metadados por objeto (custom properties `cat`, `part`, `mat_swap_key`) para material swap automatizado via MCP | relatório de build |
| FR-017 | Orientação de normais consistente e externa em todas as malhas | relatório de malha do build |
| FR-018 | Relatório de malha: contagem de n-gons, arestas non-manifold e faces invertidas, emitido pelo script de build | log de execução |
| FR-019 | Pintura azul multicamada: base coat azul profundo + micro-flakes metálicos (Noise → Bump fino) + clear coat com Coat IOR 1,5–1,6 e Coat Roughness 0,02; profundidade de pigmento via Layer Weight/Fresnel escurecendo bordas | render 3/4 × car.jpeg |
| FR-020 | Materiais secundários com rugosidades distintas: borracha 0,75–0,90; policarbonato 0,02–0,05 com transmissão; alumínio escovado 0,25–0,40; plástico preto texturizado; cromado; lentes vermelha e âmbar | renders de close |
| FR-021 | Build reprodutível e idempotente: limpa a cena e reconstrói todo o modelo a partir de `scripts/build_lotus_elise_111s.py` | reexecução do script |

## Requisitos não funcionais

| ID | Requisito |
|---|---|
| NFR-001 | Render de verificação em EEVEE ≤ 90 s por vista; malha total avaliada ≤ 400k triângulos |
| NFR-002 | Persistência em `car-lotus-elise-111s.blend` (Blender 5.2.1 LTS), sem assets externos baixados |
| NFR-003 | Build determinístico (sem aleatoriedade não semeada) e executável na mesma sessão do Blender MCP |
| NFR-004 | Verificação visual documentada para 5 vistas: frontal, lateral, traseira, superior e 3/4 |

## Critérios de aceitação

- CA-001: DADO `scripts/build_lotus_elise_111s.py` e uma cena vazia, QUANDO o script é executado no Blender, ENTÃO o modelo completo existe com os objetos `GEO_*` esperados, sem erros de execução.
- CA-002: DADO o modelo construído, QUANDO o bounding box é medido, ENTÃO comprimento/largura/altura ficam dentro de ±2 cm de 3,726/1,718/1,117 m.
- CA-003: DADO o modelo construído, QUANDO o relatório de malha é emitido, ENTÃO n-gons = 0 nos corpos principais e não há faces com normais invertidas visíveis.
- CA-004: DADO o render lateral, QUANDO comparado com `images/lateral.jpeg`, ENTÃO a silhueta (nariz, waistline, arco de roda, deck traseiro) é coerente em proporção.
- CA-005: DADO o render frontal, QUANDO comparado com `images/frontal.jpeg`, ENTÃO os 2 faróis ovais, a grelha central e os 2 faróis auxiliares redondos coincidem em posição relativa.
- CA-006: DADO o render traseiro, QUANDO comparado com `images/traseira1.jpeg`, ENTÃO aparecem as 4 lanternas redondas, o lettering "LOTUS", os 2 escapes centrais e o difusor.
- CA-007: DADO o render 3/4, QUANDO comparado com `images/car.jpeg`, ENTÃO a cor azul metálica apresenta clear coat com reflexos contínuos, sem facetas ou ondulações visíveis.
- CA-008: DADO o render superior, QUANDO comparado com `images/superior_branco.jpeg`, ENTÃO a vista revela as entradas de ar laterais, os louvers do engine cover e a posição da cabine/roll bar.
- CA-009: DADO o .blend salvo, QUANDO inspecionado, ENTÃO todo objeto tem nome com prefixo de categoria e as custom properties de metadados preenchidas.

## Matriz de rastreabilidade

| Requisito | Evidência | Status |
|---|---|---|
| FR-001 | relatório de build (bounding box) PASS |
| FR-002, FR-003 | `docs/renders/03_lateral.png` × `images/lateral.jpeg` PASS (FR-002 PARCIAL) |
| FR-004 | `docs/renders/07_wheel_closeup.png` PASS |
| FR-005, FR-007 | `docs/renders/01_frontal.png` × `images/frontal.jpeg` PASS |
| FR-006, FR-010, FR-011, FR-019 | `docs/renders/05_three_quarter.png` × `images/car.jpeg` PASS (FR-019 PARCIAL) |
| FR-008, FR-009, FR-012 | `docs/renders/04_traseira.png` × `images/traseira1.jpeg` PASS |
| FR-013, FR-014, FR-021 | relatório de malha / inspeção do .blend PASS |
| FR-015, FR-016 | relatório de build (objetos + propriedades) PASS |
| FR-017, FR-018 | relatório de malha do build PASS |
| FR-020 | `docs/renders/07_wheel_closeup.png` + closes PASS |
| NFR-001 | tempos de render registrados PASS |
| NFR-002, NFR-003, NFR-004 | `STATUS.md` + `SUMMARY.md` PASS |

## Resultado da verificação

Ver `.specs/features/lotus-elise-111s-model/SUMMARY.md` para a tabela de aceite, desvios e riscos residuais.
Resumo: 21 requisitos funcionais implementados; CA-004 (silhueta fina) e CA-007 (tom da pintura) ficaram como
**PARCIAL**; os demais critérios PASS.

## Premissas

- A variante é o Elise Series 1 111S com hardtop rígido (imagens frontais/laterais/traseiras mostram teto fechado).
- A vista `superior_branco.jpeg` é usada apenas para topologia de superfície (recortes, grelhas, cabine), não para cor.
- Dimensões do 111S tomadas da ficha do Series 1 (entre-eixos 2.300 mm) — `A CONFIRMAR` se o cliente exigir ficha de outra fonte.

## Riscos

- Ausência de blueprints ortográficos: proporções são derivadas das fotos em perspectiva → desvio esperado de poucos centímetros.
- Loft procedimental pode suavizar arestas vivas (arquear o lip do para-lama); mitigado por controle de densidade de estações.
- EEVEE sem passes de raytracing completos pode reduzir a leitura de curvatura; mitigado com rig de área e raytracing ligado.
