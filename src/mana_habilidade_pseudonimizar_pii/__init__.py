"""
mana-habilidade-pseudonimizar-pii — Pseudonimização defensiva de PII.

Habilidade canônica da Maná Builder. Substitui dados pessoais identificáveis
(nomes próprios, CPF, CNPJ, sequências longas de dígitos) por códigos genéricos
ANTES de enviar payload pra LLM ou API de terceiros, e permite desmascarar a
resposta antes de salvar/exibir.

ADR fundador: 2026-06-19-pseudonimizacao-padrao-llm-e-terceiros (vault Maná).

USO TÍPICO

  Caso 1 — Conteúdo livre com nomes próprios (ex: ata de comitê)
  -----------------------------------------------------------------
  >>> from mana_habilidade_pseudonimizar_pii import PIIPseudonimizador
  >>> pseudo = PIIPseudonimizador()
  >>> pseudo.construir_mapa_de_dict({"cliente": "João Silva", "vendedor": "Maria Santos"})
  >>> texto_anon = pseudo.aplicar("João Silva é cliente da Maria Santos.")
  >>> # "CLIENTE é cliente da VENDEDOR."
  >>> resposta_llm = "..."  # LLM responde usando CLIENTE/VENDEDOR
  >>> texto_real = pseudo.desmascarar(resposta_llm)

  Caso 2 — Filenames (ex: triagem de documentos)
  -----------------------------------------------------------------
  >>> from mana_habilidade_pseudonimizar_pii import pseudonimizar_filename
  >>> pseudonimizar_filename("CNH_Joao_Silva_12345678900.pdf",
  ...                        contexto={"cliente_nome": "João Silva"})
  'CNH_CLIENTE_CPF.pdf'
"""

__version__ = "0.1.0"

from .core import (
    PIIPseudonimizador,
    pseudonimizar_filename,
    pseudonimizar_filenames,
)

__all__ = [
    "PIIPseudonimizador",
    "pseudonimizar_filename",
    "pseudonimizar_filenames",
]
