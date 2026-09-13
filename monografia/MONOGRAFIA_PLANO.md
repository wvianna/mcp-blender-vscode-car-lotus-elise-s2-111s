# MONOGRAFIA — PLANO

## Identificação

- Título provisório: **Modelagem 3D Procedimental do Lotus Elise 111S em Blender Automatizada
  por Model Context Protocol (MCP)**
- Curso: Engenharia [VALIDAR COM O AUTOR]
- Instituição: Instituto Federal Fluminense (IFF)
- Autor: William da Silva Vianna
- Orientador: William da Silva Vianna (o próprio autor)

## Problema

É possível produzir, de forma integralmente reprodutível e automatizada por um agente de IA
via Model Context Protocol, um modelo tridimensional de um automóvel esportivo cuja geometria e
materiais sejam fiéis a referências fotográficas, atendendo simultaneamente a restrições de
topologia de malha e a um envelope dimensional verificado?

## Justificativa

Reprodutibilidade (o artefato é reconstruível por um comando); auditabilidade do processo de IA
(cada interação é uma mensagem serializada do protocolo); formação de engenharia (derivar
requisitos de um documento informal e provar atendimento por evidência).

## Objetivo geral

Produzir, com verificação visual comparativa, um modelo 3D do Lotus Elise 111S (Series 1) em
escala real, construído apenas por código executado em Blender via agente MCP.

## Objetivos específicos

1. Extrair das referências dimensões, alturas e parâmetros de perfil, registrando a origem de cada valor.
2. Gerar o casco por loft sem booleanas, com malha quadrangular dominante e zero n-gons.
3. Modelar os elementos de identidade do 111S como geometria real.
4. Construir biblioteca de materiais PBR com pintura multicamada.
5. Estabelecer a cadeia de automação via MCP.
6. Emitir relatório de malha a cada build.
7. Comparar renders com as referências e registrar aceite por critério.

## Delimitação

Fora de escopo: suíte de testes automatizados; validação automatizada de zebra/isofotas; rig de
estúdio completo (§5 da descrição original); interior detalhado; decais; animação; exportação
FBX/GLTF. Verificação exclusivamente visual comparativa + medição numérica estrutural.

## Estrutura planejada

1. Introdução
2. Fundamentação teórica
3. Trabalhos relacionados
4. Materiais e métodos
5. Desenvolvimento
6. Resultados
7. Discussão
8. Conclusão
+ Referências, Apêndices A–D

## Meta de extensão

65–100 páginas de conteúdo acadêmico, sem preenchimento artificial.
Resultado obtido: 94 páginas totais (≈60 páginas de capítulos + pré-textuais + apêndices).

## LaTeX

- Classe/modelo: `memoir` 12 pt com formatação ABNT manual (margens 3 cm / 2 cm; espaçamento 1,5)
- Compilador: `pdflatex` (pdfTeX 3.141592653-2.6-1.40.25, TeX Live 2023/Debian)
- Ferramenta de compilação: `build.sh` (pdflatex → bibtex → pdflatex → pdflatex)
- Citações: numéricas, `unsrt.bst`, por ordem de citação
- Diagramas: Mermaid (`mmdc`) em `diagrams/`, PNG incluído em `figures/`

## Pendências

- Curso e área de concentração a confirmar com o autor.
- Membros da banca de avaliação a confirmar.
- Quantificar a contribuição de exposição × cadeia de imagem no desvio de tom (CA-007).
