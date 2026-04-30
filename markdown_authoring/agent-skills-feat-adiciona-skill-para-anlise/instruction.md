# feat: Adiciona skill para análise de acoplamento

Source: [tech-leads-club/agent-skills#43](https://github.com/tech-leads-club/agent-skills/pull/43)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `packages/skills-catalog/skills/(architecture)/coupling-analysis/SKILL.md`

## What to add / change

# Adiciona skill de Análise de Acoplamento (Coupling Analysis)

## Resumo

Esta PR adiciona uma nova skill de arquitetura que permite aos agentes de IA analisar acoplamento em codebases seguindo o modelo tridimensional do livro "Balancing Coupling in Software Design" de Vlad Khononov.

## O que esta skill faz?

A skill **Coupling Analysis** fornece uma metodologia estruturada para avaliar a qualidade arquitetural de um código através da análise de três dimensões:

### 1. **Força de Integração (Integration Strength)**
Analisa *o que* é compartilhado entre componentes, classificando o acoplamento em níveis:
- **Intrusivo** (mais forte) — acesso a detalhes de implementação não projetados para integração
- **Funcional** — módulos com lógica de negócio inter-relacionada (sequencial, transacional ou simétrica)
- **Modelo** — uso direto do modelo de domínio interno do componente upstream
- **Contrato** (mais fraco/ideal) — uso de DTOs/contratos específicos para integração

### 2. **Distância (Distance)**
Avalia *onde* o acoplamento vive fisicamente na hierarquia de encapsulamento:
- Mesmo método → Mesmo objeto → Mesmo namespace → Mesmo módulo → Serviços diferentes → Sistemas diferentes

### 3. **Volatilidade (Volatility)**
Mede *com que frequência* os componentes mudam, classificando subdomínios:
- **Core** (alta volatilidade) — lógica proprietária, vantagem competitiva
- **Supporting** (baixa volatilidade) — CRUD simples, suporte básico
- **Generic** (mínim

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
