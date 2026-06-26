<!-- Checklist do PR de habilidade Maná -->

## O que muda

<!-- Descreva em 1-2 frases. -->

## Tipo de mudança

- [ ] PATCH (bug fix, sem mudança de interface)
- [ ] MINOR (nova função/método, retrocompatível)
- [ ] MAJOR (breaking change — exige ADR específico em `08-Decisoes/`)

## Checklist

- [ ] Testes adicionados/atualizados (cobertura ≥70%)
- [ ] Type hints em assinatura pública
- [ ] Docstring em toda função pública
- [ ] `SKILL.md` atualizado se a interface mudou
- [ ] `manifest.yaml` atualizado (`versao-atual`, `ultima-revisao`)
- [ ] Lint passou localmente (`ruff check src/ tests/`)
- [ ] Testes passaram localmente (`pytest`)
- [ ] Se MAJOR: ADR de breaking change criado e linkado abaixo

## ADR de breaking change (se MAJOR)

<!-- Linkar ADR em ManaVault/08-Decisoes/. Caso contrário, deletar essa seção. -->

## Migration guide (se MAJOR)

<!-- Como consumidores migram da versão anterior. Caso contrário, deletar. -->

## Pseudonimização / PII

- [ ] Não toca PII direto
- [ ] Toca PII e delega pra `mana-habilidade-pseudonimizar-pii`
- [ ] Toca PII e implementa pseudonimização internamente (justificar no SKILL.md)

## Notas pro revisor

<!-- Algo específico que merece atenção. -->
