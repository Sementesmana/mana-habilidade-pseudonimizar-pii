---
name: PLACEHOLDER-slug-kebab-case
description: PLACEHOLDER — 1-3 frases descrevendo quando e por que usar essa habilidade.
categoria: habilidades
owner: PLACEHOLDER
versao-skill: 1.0.0
ultima-revisao: 2026-MM-DD
ativacao: [PLACEHOLDER-keyword-1, PLACEHOLDER-keyword-2]
---

# PLACEHOLDER (Nome da Habilidade)

> **Esta é a versão canônica do SKILL.md.** A cópia em `Sementesmana/plugin-mana-skills/_kits/skills/habilidades/<nome>/SKILL.md` é gerada a partir dela via PR automático no merge.

## Quando usar

[Contexto/problema que essa habilidade resolve. Claro o suficiente pra IA decidir sozinha se essa skill é relevante pro pedido do usuário.]

Exemplo de gatilhos:
- "Quero pseudonimizar dados antes de mandar pro Claude"
- "Preciso extrair texto de PDF escaneado"
- "Quero detectar anomalia em série temporal de vendas"

## O que faz

[Descrição funcional do que a habilidade entrega. Não detalhar implementação — só capacidade.]

## Input

```python
[tipo de entrada esperada]
```

Detalhes:
- [parâmetros obrigatórios]
- [parâmetros opcionais e seus defaults]

## Output

```python
[tipo de saída]
```

Detalhes:
- [estrutura do retorno]
- [possíveis estados/erros]

## Exemplo de uso

```python
from mana_habilidade_placeholder import [SuaClasse|sua_funcao]

# Cenário típico
resultado = sua_funcao(
    parametro_obrigatorio="exemplo",
    parametro_opcional=42,
)
print(resultado)
# >>> [output esperado]
```

## Pré-requisitos

- Python >=3.10
- [outras habilidades/SDKs que precisa]
- [credenciais/env vars necessárias, se aplicável]

## Limitações conhecidas

- [edge cases que não cobre]
- [restrições de performance/escala]
- [dependências externas que podem falhar]

## Como NÃO usar

- [anti-padrão: cenário onde a habilidade não foi feita pra atender]
- [combinação que dá errado]

## Integrações comuns

| Habilidade/SDK | Como combina |
|---|---|
| `mana-habilidade-XXX` | [por que e como usa junto] |
| `mana-softexpert` | [se aplicável] |

## Pseudonimização e LGPD

[Se a habilidade toca PII, descrever:
- O que considera PII
- Em que momento pseudoniza
- Se delega pra `mana-habilidade-pseudonimizar-pii`]

[Se NÃO toca PII, escrever: "Não toca PII direto. Consumidor responsável por pseudonimizar input se precisar."]

## Histórico

- **0.1.0** (2026-MM-DD): criação inicial. [Outros marcos relevantes.]

## Suporte

- Dono: @PLACEHOLDER
- Repo: https://github.com/Sementesmana/mana-habilidade-placeholder
- Issues: usar a aba Issues do repo

## ADRs aplicáveis

- [[2026-06-26-mana-builder-matriz-cobertura]]
- [[2026-06-26-fluxo-criacao-habilidade-mana-builder]]
- [[2026-06-26-versionamento-distribuicao-mana-builder]]
- [[2026-06-26-plugin-mana-skills-cowork]]
