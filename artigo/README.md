# Artigo — Modelagem 3D procedimental do Lotus Elise 111S em Blender mediada por MCP

Artigo científico/tecnológico em LaTeX derivado do modelo e da monografia deste repositório.

- **Autor:** William da Silva Vianna — Instituto Federal Fluminense (IFF)
- **Ano:** 2026
- **Saída:** `main.pdf` — **32 páginas**, A4, `article` 11 pt, margens de 2,5 cm
- **Compilação:** `./build.sh` → `pdflatex → bibtex → pdflatex → pdflatex`
  (ambiente **sem** `latexmk`, `biber`/`biblatex` ou `abntex2`; citações numéricas
  com `natbib [numbers,sort&compress]` + `plainnat`)

## Título escolhido e alternativas avaliadas

Escolhido (objetivo, técnico, com o resultado medido explícito):

> Modelagem 3D procedimental do Lotus Elise 111S em Blender mediada por *Model Context
> Protocol*: topologia controlada por construção e verificação visual comparativa

Alternativas consideradas e descartadas:

1. Geração procedimental de um veículo esportivo em Blender com agentes via Model Context Protocol
   — descartada por omitir o resultado verificável (topologia e envelope).
2. Restrições topológicas impostas na construção: um caso de modelagem procedimental de veículo mediada por MCP
   — descartada por colocar o método acima do objeto de estudo.
3. Modelagem procedimental auditável: Lotus Elise 111S em Blender via Model Context Protocol
   — descartada por "auditável" ser uma conclusão, e não um resultado.
4. Doze mil linhas de geometria: reprodutibilidade e verificação em modelagem 3D mediada por IA
   — descartada por tom publicitário e por não descrever o escopo.

## Estrutura

```
artigo/
├── main.tex            preâmbulo, título/autoria, resumo, abstract, agradecimentos
├── references.bib      49 referências, todas citadas (nenhuma órfã)
├── build.sh            pdflatex → bibtex → pdflatex ×2 + relatório de erros/overfull
├── .gitignore          temporários de LaTeX
├── sections/
│   ├── 1-introducao.tex              problema, lacuna, hipótese, objetivo, contribuições
│   ├── 2-fundamentacao.tex           subdivisão, topologia, PBR, cor, agentes e MCP
│   ├── 3-trabalhos-relacionados.tex  quatro linhas + posicionamento
│   ├── 4-materiais-metodos.tex       ambiente, arquitetura, corpus, critérios, ameaças
│   ├── 5-desenvolvimento.tex         implementação, tampas, arcos, relatório de malha
│   ├── 6-resultados.tex              números do build + comparação visual por vista
│   ├── 7-discussao.tex               critérios parciais, papel do MCP, limitações
│   └── 8-conclusao.tex               objetivos, conclusões, trabalhos futuros
└── figures/            diagramas (Mermaid exportado) + referências + renders
```

## Elementos gráficos

| Tipo | Qtd. | Observação |
|---|---|---|
| Figuras | 11 | 5 comparações referência × render, close de roda, vistas em *clay*, arquitetura, sequência MCP, galeria |
| Tabelas | 5 | tempos, resumo do build, dimensões, envelope, grupos de objetos |
| Quadros | 7 | ambiente, critérios, origem de artefatos, malhas, aceite, posicionamento, objetivos |
| Códigos | 3 | comandos de reprodução, `arch_bottom`, `_folded_fan_cap` |

Todos os diagramas são exportações PNG dos Mermaid de `monografia/diagrams/`
(`mermaid-cli` + navegador do sistema); as fotografias de referência e os renders
vêm de `images/` e `docs/renders/`, copiados para `figures/`.

## Verificação executada

| Item | Resultado |
|---|---|
| Erros de compilação | 0 |
| Referências/citações indefinidas | 0 |
| `Overfull \hbox` | 0 |
| Páginas | 32 |
| Referências citadas / presentes no `.bib` | 49 / 49 |
| Inspeção visual do PDF | páginas renderizadas com `pdftoppm -r 50` e conferidas |

## Rastreabilidade numérica (afirmação → fonte)

| Afirmação no artigo | Fonte |
|---|---|
| 130 objetos, 13 materiais, 4 luzes, 9 câmeras | `docs/renders/mesh_report.txt`, `STATUS.md` |
| 32.632 faces (29.272 quads, 3.360 tris, 0 n-gons) | `docs/renders/mesh_report.txt` |
| 0 arestas non-manifold; 1.776 arestas de borda | `docs/renders/mesh_report.txt` |
| Casco 750 quads / cabine 148 quads | `docs/renders/mesh_report.txt` |
| 47 estações × 16 pontos ⇒ 750 faces | `scripts/build_lotus_elise_111s.py` |
| Envelope 3,736 × 1,718 × 1,117 m (+1,0 cm em X) | `docs/renders/mesh_report.txt` |
| Tempos 45,4 s (9 vistas) e ~37 s (galeria) | `STATUS.md`, `docs/renders/` |
| Build idempotente ~0,6 s | `STATUS.md` |
| CA-004 e CA-007 parciais | `STATUS.md` (limitações conhecidas), `monografia/MONOGRAFIA_EVIDENCIAS.md` |
| ~1.200 linhas de geometria | `wc -l scripts/*.py` (build + common = 1.830 linhas, das quais ~1.257 no build) |

## Pendências declaradas no próprio artigo

- **E-mail do autor:** marcador `[E-MAIL A INSERIR]` na folha de título.
- **Veículo/veículo de publicação:** nenhum template de periódico ou congresso foi
  fornecido; o artigo usa a estrutura padrão da skill (introdução → fundamentação →
  relacionados → materiais e métodos → desenvolvimento → resultados → discussão →
  conclusão).
- **Avaliação independente, cadeia colorimétrica e mapas de zebra:** declarados como
  limitações/ameaças à validade na Seção 7, não como resultados.

## Integridade

Nenhum dado, número, resultado ou referência foi inventado. Todos os valores
numéricos vêm do relatório de malha, do `STATUS.md` ou da monografia deste
repositório; todas as referências foram herdadas da bibliografia já verificada em
`monografia/references.bib`.
