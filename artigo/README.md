# Artigo — Modelagem 3D procedimental do Lotus Elise 111S em Blender mediada por MCP

Artigo científico/tecnológico em LaTeX derivado do modelo e da monografia deste repositório.

- **Autor:** William da Silva Vianna — Instituto Federal Fluminense (IFF)
- **Ano:** 2026
- **Saída:** `main.pdf` — **16 páginas**, A4, `article` 10 pt, margens de 2,0 cm
- **Compilação:** `./build.sh` → `pdflatex → bibtex → pdflatex → pdflatex`
  (ambiente **sem** `latexmk`, `biber`/`biblatex` ou `abntex2`; citações numéricas
  com `natbib [numbers,sort&compress]` + `plainnat`)

## Histórico de compactação

A primeira versão compilada tinha 32 páginas. Como o objetivo era um artigo de
congresso/periódico, o documento foi compactado até **16 páginas**, sem remover
evidentes nem inventar dados, por meio de:

- layout mais denso (10 pt, margens de 2,0 cm, `\linespread{0.97}`, espaçamento de
  floats reduzido) — 32 → 26 páginas;
- fusão das sete figuras de comparação visual em três figuras de múltiplas linhas
  (pares referência × render alinhados pela altura), com as vistas em material neutro
  e o detalhe de roda na mesma figura — 26 → 22 páginas;
- fusão dos sete quadros em prosa ou em tabelas únicas (o quadro de critérios e o de
  resultado por critério viraram a `Tabela 4`), eliminação do quadro de ambiente e
  das tabelas de tempos por vista e de grupos funcionais — 22 → 18 páginas;
- corte de prosa redundante (derivação de dimensões, estratégia de materiais,
  reprodutibilidade, comparação com a literatura, limitações) e de 12 referências que
  ficaram sem citação — 18 → 16 páginas.

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
├── references.bib      37 referências, todas citadas (nenhuma órfã)
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
| Figuras | 4 | arquitetura MCP; 3 linhas de comparação referência × render (frontal/lateral/traseira); 2 linhas (superior/três-quartos); detalhe de roda + vista lateral em material neutro |
| Tabelas | 4 | dimensões de referência; resumo do build; envelope dimensional; critérios de aceitação com método, status e evidência |
| Códigos | 1 | `_folded_fan_cap` (tampa de loft que emite apenas quads) |

Todos os diagramas são exportações PNG dos Mermaid de `monografia/diagrams/`
(`mermaid-cli` + navegador do sistema); as fotografias de referência e os renders
vêm de `images/` e `docs/renders/`, copiados para `figures/`. A pasta contém
**apenas as figuras efetivamente citadas** — as seis que ficaram sem referência após a
compactação (diagrama de sequência, pipeline metodológico, galeria com rig dramático,
traseira em três-quartos, vistas em material neutro adicionais) foram removidas, e os
originais permanecem em `monografia/figures/` e `monografia/diagrams/`.

## Verificação executada

| Item | Resultado |
|---|---|
| Erros de compilação | 0 |
| Referências/citações indefinidas | 0 |
| `Overfull \hbox` | 0 |
| Páginas | 16 |
| Referências citadas / presentes no `.bib` | 37 / 37 |
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
`monografia/references.bib`. As 12 referências removidas na compactação eram apenas
as que ficaram sem citação no texto — nenhuma foi descartada por ser incômoda, e
nenhuma afirmação do texto ficou sem suporte bibliográfico.
