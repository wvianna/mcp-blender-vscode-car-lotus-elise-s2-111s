# AGENTS.md — Regras permanentes do projeto

Projeto: **Modelagem 3D do Lotus Elise 111S (Series 1)** em Blender, conduzida via VS Code Copilot + MCP (`blender-mcp`).

## Leitura obrigatória antes de alterar qualquer coisa

1. `AGENTS.md` (este arquivo)
2. `STATUS.md` — estado real do desenvolvimento
3. `HANDOFF.md` — continuidade entre agentes
4. `.specs/features/lotus-elise-111s-model/spec.md` — requisitos e critérios de aceite
5. `docs/descricao.txt` — especificação técnica original do cliente

## Stack e versões

- Blender **5.2.1 LTS**, unidade métrica (`scale_length = 1.0`), engine de render disponível: **`BLENDER_EEVEE`** apenas.
- API: `bpy` / `bmesh` (Python 3.x embutido no Blender).
- Integração: MCP `blender` (servidor `blender-mcp` via `uvx`), configurado em `.vscode/mcp.json`.
- Não há dependências Python externas. Não baixar assets de terceiros (modelos, HDRI, texturas) sem decisão registrada.

## Convenções obrigatórias

- **Nomenclatura**: todo objeto recebe prefixo de categoria — `GEO_` (geometria), `LGT_` (luz), `CAM_` (câmera),
  `MAT_` (material), `EMP_` (empty de controle). Sufixo descritivo em `PascalCase_Snake` conforme exemplos da descrição
  (`GEO_Body_111S`, `LGT_Softbox_Front`, `MAT_Blue_Metallic`).
- **Metadados**: todo objeto de geometria recebe custom properties `cat`, `part` e `mat_swap_key` para permitir troca de
  material automatizada via MCP.
- **Unidades**: metros reais. O modelo fica centrado em `X = Y = 0` com o solo em `Z = 0`.
- **Topologia**: quad-dominant; **proibido n-gon** (face com > 4 vértices). Triângulos só em superfícies planas não visíveis.
- **Subdivisão**: `Subdivision Surface` com `render_levels = 3` nos corpos principais; `levels` (viewport) baixo (1–2)
  para manter o MCP responsivo.
- **Materiais**: sempre via `ShaderNodeBsdfPrincipled`, com cores convertidas de sRGB para linear. Ajustes de pintura
  automotiva usam `Coat Weight` / `Coat Roughness` / `Coat IOR`.
- **Scripts**: a construção do modelo vive em `scripts/` e deve ser **idempotente**: limpa a cena antes de reconstruir.

## Armadilhas conhecidas do Blender MCP (verificadas)

- A interface em PT-BR localiza nomes de nós. **Nunca** buscar o BSDF por nome exibido; usar sempre `bl_idname`
  (`ShaderNodeBsdfPrincipled`).
- `object.scale` exige tupla de 3 elementos; `(x,)*3` é tupla e quebra a atribuição.
- Blender 5.x: `scene.node_tree` não existe mais — compositor usa `bpy.data.node_groups.new(..., 'CompositorNodeTree')`
  com `scene.compositing_node_group`; `Composite` foi substituído por `NodeGroupOutput`.
- `use_bloom` do EEVEE não existe mais; bloom é feito com nó `Glare` no compositor.
- Antes de rodar código destrutivo no MCP, confirmar que o `.blend` salvo corresponde ao estado desejado.

## Fluxo de trabalho

1. Ler os artefatos listados acima.
2. Alterar o menor conjunto possível: preferir editar `scripts/*.py` e reexecutar o build em vez de ajustar a cena à mão.
3. Reexecutar o build completo (não fazer patches manuais que o script não reproduza).
4. Gerar os renders de verificação e **comparar visualmente** com `images/*.jpeg`.
5. Atualizar `STATUS.md`, `HANDOFF.md` e a matriz de rastreabilidade em `SUMMARY.md` quando aplicável.

## Verificação

- A evidência deste projeto é **visual comparativa** (determinação do usuário): renders em `docs/renders/`
  confrontados com as imagens de referência em `images/`. Não criar suíte de testes automatizados.
- O script de build emite um relatório de malha obrigatório (n-gons, non-manifold, normais invertidas, bounding box).
- Nível de evidência: `LOCAL` (Blender local via MCP). Não há CI/staging.

## Restrições

- Não usar boolean operator para arcos de roda (gera n-gons/triângulos em aresta visível).
- Não simular furos estruturais (entradas de ar) com normal map.
- Não apagar/regravar o `.blend` sem que o build tenha rodado por completo.
- Não fazer commit automaticamente.

## Licença

Apache License 2.0 — ver `LICENSE`.
