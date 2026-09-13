# Constituição do Projeto — Modelagem Lotus Elise 111S

## Identidade do sistema

- Produto: modelo 3D do Lotus Elise 111S (Series 1)
- Stack: Blender 5.2.1 LTS + `bpy`/`bmesh` (Python embutido)
- Persistência: `car-lotus-elise-111s.blend` (arquivo único, sem banco de dados)
- Integração: MCP `blender` (`blender-mcp`)
- Ambientes de validação: `LOCAL` (Blender + MCP). Não há CI/staging/produção.

## Princípios obrigatórios

### 1. Fidelidade à referência

- As imagens em `images/` são o ground truth. Em divergência entre texto e imagem, prevalece a imagem.
- Se uma feição não estiver clara nas referências, registrar como `A CONFIRMAR` em vez de inventar.

### 2. Fidelidade dimensional

- O modelo usa metros reais; qualquer desvio acima de 2 cm nas dimensões de envelope é defeito.

### 3. Qualidade de malha

- Quad-dominant, zero n-gons. Sub-D com render levels 3 nos corpos principais.
- Normais consistentes e externas; nenhuma aresta non-manifold visível.

### 4. Reprodutibilidade

- Toda a geometria é gerada por script determinístico em `scripts/`. Nenhum ajuste manual não versionado é aceito
  como estado final: se não está no script, não existe.

### 5. Materiais fisicamente plausíveis

- PBR via Principled BSDF, com clear coat e rugosidade coerentes com pintura automotiva.
- Cores definidas em sRGB convertidas para linear.

### 6. Verificação

- A evidência de conclusão é a comparação visual render × referência, com registro de PASS/FAIL/PENDENTE.
- O relatório de malha é obrigatório em todo build.

### 7. Processo de mudança

- Alterações estruturais exigem atualização de `spec.md`/`design.md`, não apenas de código.
- Não adicionar dependências, assets externos ou camadas sem benefício verificável.

## Gates padrão

- [ ] Requisitos com ID e critério de aceite observável
- [ ] Build determinístico executado sem erro
- [ ] Relatório de malha emitido (n-gons = 0, non-manifold = 0, normais ok)
- [ ] Renders das 5 vistas gerados e comparados com as referências
- [ ] `README.md`, `AGENTS.md`, `STATUS.md`, `HANDOFF.md` consistentes com o código
