"""
Testes da habilidade. Substituir pelo conjunto real após implementação.
Cobertura mínima exigida: 70% (configurada em pyproject.toml).
"""

import pytest

from mana_habilidade_placeholder.core import placeholder_function


class TestPlaceholderFunction:
    """Smoke tests do template. Substituir pelos testes reais."""

    def test_processa_entrada_valida(self) -> None:
        resultado = placeholder_function("teste")
        assert resultado == "teste processado"

    def test_rejeita_entrada_vazia(self) -> None:
        with pytest.raises(ValueError, match="Entrada não pode ser vazia"):
            placeholder_function("")

    def test_processa_caractere_unico(self) -> None:
        resultado = placeholder_function("a")
        assert resultado == "a processado"
