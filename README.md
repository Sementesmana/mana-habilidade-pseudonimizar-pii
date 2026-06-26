# template-habilidade-mana

> Template **GitHub Repository** pra criar habilidades novas da **Maná Builder**.

Este repo é um **GitHub Template Repository**. Quando você precisar criar uma habilidade nova, clica em **"Use this template"** no GitHub e o repo é clonado pra você com toda a estrutura pronta.

## Quando usar

Quando você está construindo um agente Maná e identifica uma **capacidade reusável** que não existe ainda como habilidade da Maná Builder, e que vai ser usada por **2+ agentes** (regra da 2ª cópia — ver [[ADR 2026-06-26 fluxo criação habilidade]]).

Exceções à regra da 2ª cópia (extrair direto, mesmo com 1 consumidor):
- Capacidade transversal de segurança (ex: pseudonimização)
- Capacidade que toca PII / LGPD
- Decisão explícita do Xayer ou ADR específico

## Como usar

### Passo 1 — Criar repo a partir do template

1. Vá em https://github.com/Sementesmana/template-habilidade-mana
2. Clique em **"Use this template" → "Create a new repository"**
3. Nome do repo: `mana-habilidade-<verbo-substantivo>` (ex: `mana-habilidade-pseudonimizar-pii`, `mana-habilidade-extrair-pdf`)
4. Owner: `Sementesmana`
5. Visibilidade: **Private**
6. Clique **Create repository**

### Passo 2 — Clone local e renomeie placeholders

```bash
git clone https://github.com/Sementesmana/mana-habilidade-<nome>.git
cd mana-habilidade-<nome>

# Renomear pasta do pacote
mv src/mana_habilidade_placeholder src/mana_habilidade_<nome_sem_hifen_lowercase>

# Substituir placeholders em pyproject.toml, manifest.yaml, SKILL.md
# (manual ou via sed — ver Passo 3)
```

### Passo 3 — Substituir placeholders

Procure por `<HABILIDADE>` em todos os arquivos e substitua pelo nome real da habilidade. Locais:
- `pyproject.toml` → `name`, `description`
- `manifest.yaml` → `nome`, `descricao`, `owner`
- `SKILL.md` → todo o conteúdo
- `README.md` → criar/atualizar com descrição real
- `src/mana_habilidades_<nome>/__init__.py` → ajustar exports

### Passo 4 — Implementar a habilidade

1. Código em `src/mana_habilidades_<nome>/`
2. Testes em `tests/` (cobertura mínima >70%)
3. Type hints + docstrings obrigatórios em API pública
4. Exemplo de uso em `docs/EXEMPLO_USO.md`

### Passo 5 — Preencher SKILL.md

O `SKILL.md` vai pro plugin Maná de Skills no Cowork (`Sementesmana/plugin-mana-skills`) — é como a IA (Claude/Cowork) descobre que essa habilidade existe e quando usar.

Critérios mínimos:
- "Quando usar" claro (1-3 frases)
- "Input" e "Output" tipados
- Exemplo de código real
- Limitações conhecidas

### Passo 6 — Push e publish

```bash
git add .
git commit -m "feat: implementação inicial da habilidade <nome>"
git push origin main
```

GitHub Actions roda automaticamente:
1. CI (`ci.yml`) — lint + test
2. Publish (`publish.yml`) — publica `mana-habilidade-<nome>==0.1.0` no GitHub Packages

### Passo 7 — Documentar no vault

Crie nota em `ManaVault/06-Agentes-e-Skills/habilidades/<nome>.md` (template em `_Templates/nota-habilidade.md` do vault).

### Passo 8 — Distribuir via plugin Maná

Abra PR em `Sementesmana/plugin-mana-skills`:
- Adicione `_kits/skills/habilidades/<nome>/SKILL.md` (cópia do SKILL.md deste repo)
- Atualize `CHANGELOG.md` central

CODEOWNERS revisa, merge, Cowork de todos os devs pega na próxima atualização.

## Consumo por outros agentes

Agente que quer usar essa habilidade adiciona ao `requirements.txt`:

```
mana-habilidade-<nome>>=0.1,<1.0
```

E importa:

```python
from mana_habilidades.<nome> import ...
```

## Versionamento

Semver estrito ([[ADR 2026-06-26 versionamento distribuição]]):
- **PATCH** (`0.1.0 → 0.1.1`): bug fix sem mudança de interface
- **MINOR** (`0.1.0 → 0.2.0`): nova função/método, retrocompatível
- **MAJOR** (`0.1.0 → 1.0.0`): breaking change — exige ADR específico de breaking change

## ADRs aplicáveis

- [Fluxo criação habilidade](https://github.com/Sementesmana/mana-vault/blob/main/08-Decisoes/2026-06-26-fluxo-criacao-habilidade-mana-builder.md)
- [Versionamento + distribuição](https://github.com/Sementesmana/mana-vault/blob/main/08-Decisoes/2026-06-26-versionamento-distribuicao-mana-builder.md)
- [Plugin Maná Skills](https://github.com/Sementesmana/mana-vault/blob/main/08-Decisoes/2026-06-26-plugin-mana-skills-cowork.md)
- [Maná Builder + Matriz](https://github.com/Sementesmana/mana-vault/blob/main/08-Decisoes/2026-06-26-mana-builder-matriz-cobertura.md)

## Suporte

- Skill `nova-habilidade-mana` no Cowork orienta cada etapa
- Dono da habilidade = quem criou (registrado em `CODEOWNERS` + `manifest.yaml`)
- Dúvidas estruturais: Xayer

---

*Sementes Maná LTDA · 2026*
