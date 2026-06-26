---
name: pseudonimizar-pii
description: Pseudonimização defensiva de PII (nomes próprios, CPF, CNPJ, sequências longas, filenames) antes de enviar payload pra LLM ou API de terceiros. Permite desmascarar a resposta antes de salvar/exibir.
categoria: habilidades
owner: xayer-mana
versao-skill: 1.0.0
ultima-revisao: 2026-06-26
ativacao: [pseudonimizar, anonimizar, mascarar, pii, lgpd, cpf, cnpj, llm-safety, dados-pessoais, antes-do-claude]
---

# pseudonimizar-pii

> **Esta é a versão canônica do SKILL.md.** A cópia em `Sementesmana/plugin-mana-skills/_kits/skills/habilidades/pseudonimizar-pii/SKILL.md` é gerada a partir dela.

## Quando usar

Quando o agente Maná vai enviar qualquer dado que pode conter PII (nome de cliente, vendedor, diretor, CPF, CNPJ, número de processo, etc.) pra **uma LLM** (Claude/OpenAI/etc.) ou **API de terceiros** que não tem contrato de LGPD com a Maná.

Cenários típicos:

- Gerar ata de comitê de crédito a partir de transcrição de reunião (caso `agente-comite-credito`)
- Triagem de documentos via filename (caso `agente-documentos`)
- Qualquer prompt pra LLM que receba dados estruturados de cliente
- Mensagens de WhatsApp que vão pro modelo
- Análise de PDFs/documentos cujo conteúdo será mandado pro LLM

**ADR transversal:** `2026-06-19-pseudonimizacao-padrao-llm-e-terceiros`. **OBRIGATÓRIO** pra qualquer chamada LLM/3rd-party com PII.

## O que faz

Substitui dados pessoais por códigos genéricos ANTES de enviar pro LLM, e permite desmascarar a resposta ANTES de salvar/exibir. Cobre **2 famílias** de PII:

1. **Nomes próprios** (cliente, vendedor, diretores) → `CLIENTE`, `VENDEDOR`, `DIRETOR_1`, `DIRETOR_2`, ...
2. **Identificadores estruturados** (CPF, CNPJ, sequências longas) → `CPF`, `CNPJ`, `NUM`

O mapa nome↔código vive **em memória apenas**. Nunca persiste em banco, log ou disco.

## Como invocar

### Caso 1 — Conteúdo livre com nomes próprios (recursivo em dict/list/str)

```python
from mana_habilidade_pseudonimizar_pii import PIIPseudonimizador

pseudo = PIIPseudonimizador().construir_mapa_de_dict({
    "cliente": "Fazenda São João Ltda",
    "vendedor": "Carlos Pereira",
    "participantes": [
        {"nome": "Ana Diretoria"},
        {"nome": "Bruno Risco"},
    ],
})

payload_anon = pseudo.aplicar(payload_dict)
# chama LLM com payload_anon
resposta_anon = claude.messages.create(...)
resposta_real = pseudo.desmascarar(resposta_anon.content[0].text)
```

### Caso 2 — Pseudonimizar filename antes de mandar pro LLM (triagem)

```python
from mana_habilidade_pseudonimizar_pii import pseudonimizar_filename, pseudonimizar_filenames

anon = pseudonimizar_filename(
    "CNH_Joao_Silva_12345678900.pdf",
    contexto={"cliente_nome": "Joao Silva"},
)
# → "CNH_CLIENTE_CPF.pdf"

anon_list, mapa_anon_to_original = pseudonimizar_filenames(
    filenames,
    contexto={"cliente_nome": "Joao Silva"},
)
```

### Caso 3 — Combinar nomes + identificadores numa única chamada

```python
pseudo = PIIPseudonimizador(aplicar_identificadores=True)
pseudo.construir_mapa_de_dict({"cliente": "Joao Silva"})
texto = "Cliente Joao Silva, CPF 123.456.789-00, fez pedido."
print(pseudo.aplicar(texto))
# → "Cliente CLIENTE, CPF CPF, fez pedido."
```

## Pré-requisitos

- Python ≥ 3.10
- Apenas stdlib (`re`, `typing`) — zero dependência externa
- Instalação: `pip install mana-habilidade-pseudonimizar-pii` (via GitHub Packages da Org Sementesmana)

## Limitações conhecidas

- **`construir_mapa_de_dict` não cobre representantes/sócios/cônjuge** ainda. Pra escopo estendido (ex: scred completo do agente-documentos Aba 2), passe um `mapa_nomes` manual no construtor com todos os nomes adicionais.
- **Identificadores estruturados não são desmascarados.** A função `desmascarar()` só reverte códigos do mapa de nomes. CPF/CNPJ/NUM nunca voltam (não há mapeamento reverso).
- **Não detecta nomes próprios genéricos.** Só substitui quem está no mapa. Pra detectar PII não-mapeada (ex: nome aleatório no meio de texto livre), use NER — outra habilidade.
- **Não pseudoniza endereço, telefone, email** — escopo intencionalmente focado. Estender quando 2º consumidor precisar (regra da 2ª cópia).

## Como NÃO usar

- ❌ **Não persistir o mapa** (`pseudo.mapa`) em banco, log, disco ou cookie. Mapa é segredo — vive em memória só durante a request.
- ❌ **Não logar o mapa** mesmo em DEBUG. Logar só códigos pseudonimizados.
- ❌ **Não passar dados sem pseudonimização pra Claude direto, OpenAI direto, ou qualquer 3rd-party sem contrato LGPD.**
- ❌ **Não usar pra anonimizar dados de pesquisa** (estatística/ML) — pseudonimização não é anonimização. Mapa permite re-identificação.

## Integrações comuns

| Outra peça | Como combina |
|---|---|
| `mana-llm-gateway` | Pseudonimiza ANTES de chamar via gateway. Gateway audita custo, esta habilidade audita PII. |
| `agente-whatsapp` (hub) | Mensagens WhatsApp que vão pro LLM passam por pseudonimização antes (idem resposta). |
| `softexpert-ws-suite` (SDK SE) | Dados de scred/comite/documentos vêm do SE com PII completa. Pseudonimizar antes do LLM. |

## Pseudonimização e LGPD

Pseudonimização ≠ anonimização. **Mantém vínculo reversível** entre código e nome original (via mapa em memória). Anonimização rompe esse vínculo definitivamente.

Esta habilidade implementa **pseudonimização defensiva** — pra atender LGPD/GDPR quando dado pessoal **precisa sair do ambiente Maná** (LLM/3rd-party) mas volta identificado dentro do ambiente. O mapa nunca atravessa a fronteira: memória do servidor Maná → LLM recebe só códigos → resposta volta com códigos → Maná desmascara internamente.

Em caso de incidente: como mapa não persiste, LLM (ou seus logs) nunca viu PII real, apenas códigos.

## Histórico

- **0.1.0** (2026-06-26): criação inicial. Primeira habilidade real do portfólio Maná Builder (piloto do fluxo). API derivada de:
  - `agente-comite-credito/app/integrations/_pseudonimizador.py` (PIIPseudonimizador)
  - `agente-documentos/agente_documentos.py:296-354` (pseudonimizar_filename)

## Suporte

- Dono: @xayer-mana
- Repo: https://github.com/Sementesmana/mana-habilidade-pseudonimizar-pii
- Issues: aba Issues do repo

## ADRs aplicáveis

- [[2026-06-19-pseudonimizacao-padrao-llm-e-terceiros]] — princípio transversal (OBRIGATÓRIO)
- [[2026-06-24-plataforma-agentica-mana-5-camadas]] — Camada 2C
- [[2026-06-26-mana-builder-matriz-cobertura]] — Maná Builder
- [[2026-06-26-fluxo-criacao-habilidade-mana-builder]] — ciclo de vida
- [[2026-06-26-versionamento-distribuicao-mana-builder]] — semver + GH Packages
- [[2026-06-26-plugin-mana-skills-cowork]] — distribuição
