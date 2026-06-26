# mana-habilidade-pseudonimizar-pii

> **Habilidade canônica da Maná Builder.** Pseudonimização defensiva de PII (nomes próprios, CPF, CNPJ, sequências longas, filenames) antes de enviar payload pra LLM ou API de terceiros. Permite desmascarar a resposta antes de salvar/exibir.

**Status:** alpha · **Versão:** 0.1.0 · **Owner:** @xayer-mana

## Por que existe

ADR transversal [`2026-06-19-pseudonimizacao-padrao-llm-e-terceiros`](https://github.com/Sementesmana/mana-vault) tornou **OBRIGATÓRIO** pseudonimizar PII antes de qualquer chamada pra LLM/3rd-party na Maná. Esta habilidade é a implementação canônica unificada — substitui as 2 cópias divergentes existentes:

- `agente-comite-credito/app/integrations/_pseudonimizador.py` (113 linhas)
- `agente-documentos/agente_documentos.py:296-354` (~60 linhas inline)

Primeira habilidade real do portfólio Maná Builder (piloto do fluxo do ADR `2026-06-26-fluxo-criacao-habilidade-mana-builder`).

## Instalação

Distribuído via Git tag (não há PyPI — GitHub Packages PyPI foi descontinuado em 2024).

**No `requirements.txt`:**

```
mana-habilidade-pseudonimizar-pii @ git+https://github.com/Sementesmana/mana-habilidade-pseudonimizar-pii.git@v0.1.0
```

**Ou via pip diretamente:**

```bash
pip install "git+https://github.com/Sementesmana/mana-habilidade-pseudonimizar-pii.git@v0.1.0"
```

Em ambientes (Railway, GitHub Actions) auth via `GITHUB_TOKEN` no header — repo privado da Org `Sementesmana` exige token. Padrão recomendado em `requirements.txt`:

```
mana-habilidade-pseudonimizar-pii @ git+https://${GITHUB_TOKEN}@github.com/Sementesmana/mana-habilidade-pseudonimizar-pii.git@v0.1.0
```

Versão: substituir `v0.1.0` pela tag desejada (semver — ver seção "Versionamento" abaixo).

## Uso rápido

### Caso 1 — Conteúdo livre com nomes próprios

```python
from mana_habilidade_pseudonimizar_pii import PIIPseudonimizador

pseudo = PIIPseudonimizador().construir_mapa_de_dict({
    "cliente": "Fazenda São João Ltda",
    "vendedor": "Carlos Pereira",
    "participantes": [{"nome": "Ana Diretoria"}, {"nome": "Bruno Risco"}],
})

# Pseudonimiza payload completo (recursivo em dict/list/str)
payload_anon = pseudo.aplicar(payload_dict)

# Chama LLM
resposta_anon = claude.messages.create(payload_anon)

# Desmascara resposta antes de salvar
resposta_real = pseudo.desmascarar(resposta_anon)
```

### Caso 2 — Filenames (triagem)

```python
from mana_habilidade_pseudonimizar_pii import pseudonimizar_filename

pseudonimizar_filename(
    "CNH_Joao_Silva_12345678900.pdf",
    contexto={"cliente_nome": "Joao Silva"},
)
# → "CNH_CLIENTE_CPF.pdf"
```

### Caso 3 — Combinar nomes + identificadores

```python
pseudo = PIIPseudonimizador(aplicar_identificadores=True)
pseudo.construir_mapa_de_dict({"cliente": "Joao Silva"})
pseudo.aplicar("Cliente Joao Silva, CPF 123.456.789-00, fez pedido.")
# → "Cliente CLIENTE, CPF CPF, fez pedido."
```

## API pública

| Símbolo | Função |
|---|---|
| `PIIPseudonimizador` | Classe principal. Pseudonimiza conteúdo livre com nomes próprios + (opcional) identificadores estruturados. |
| `PIIPseudonimizador.construir_mapa_de_dict(dados, campos=...)` | Builder: popula mapa a partir de dict estruturado. Encadeável. |
| `PIIPseudonimizador.adicionar(nome, codigo)` | Adiciona par manual. Encadeável. |
| `PIIPseudonimizador.aplicar(obj)` | Aplica recursivo em dict/list/str/tuple. Não muta entrada. |
| `PIIPseudonimizador.desmascarar(texto)` | Reverte código → nome real. |
| `pseudonimizar_filename(fn, contexto=None)` | Pseudonimiza 1 filename (CPF, CNPJ, cliente_nome, NUM). |
| `pseudonimizar_filenames(lista, contexto=None)` | Idem em lista, retorna `(lista_anon, mapa_anon_to_original)`. Garante unicidade. |

Detalhes em [`SKILL.md`](./SKILL.md) e docstrings dos métodos.

## Limitações conhecidas

- Não cobre representantes/sócios/cônjuge automaticamente — usar `mapa_nomes` manual ou `adicionar()`.
- Identificadores estruturados não são desmascarados (não há mapeamento reverso).
- Não detecta nomes próprios genéricos (sem mapa). Pra detectar PII não-mapeada, usar NER (outra habilidade).
- Não pseudoniza endereço, telefone, email — escopo intencionalmente focado. Estender quando 2º consumidor precisar.

## ADRs aplicáveis

- `2026-06-19-pseudonimizacao-padrao-llm-e-terceiros` — princípio transversal OBRIGATÓRIO
- `2026-06-24-plataforma-agentica-mana-5-camadas` — Camada 2C
- `2026-06-26-mana-builder-matriz-cobertura` — Maná Builder
- `2026-06-26-fluxo-criacao-habilidade-mana-builder` — ciclo de vida (este repo é piloto)
- `2026-06-26-versionamento-distribuicao-mana-builder` — semver + GH Packages
- `2026-06-26-plugin-mana-skills-cowork` — distribuição via Cowork

## Desenvolvimento

```bash
git clone https://github.com/Sementesmana/mana-habilidade-pseudonimizar-pii.git
cd mana-habilidade-pseudonimizar-pii

pip install -e ".[dev]"

ruff check src/ tests/
pytest
```

CI roda lint + test em Python 3.10, 3.11 e 3.12. Cobertura mínima: 70%.

## Versionamento

Semver estrito ([`2026-06-26-versionamento-distribuicao-mana-builder`](https://github.com/Sementesmana/mana-vault)):

- **PATCH** (`0.1.0 → 0.1.1`): bug fix sem mudança de interface
- **MINOR** (`0.1.0 → 0.2.0`): nova função/método, retrocompatível
- **MAJOR** (`0.1.0 → 1.0.0`): breaking change — exige ADR específico

## Licença

Proprietary — Sementes Maná LTDA. Ver `LICENSE`.

---

*Habilidade canônica da Maná Builder · Sementes Maná LTDA · 2026*
