"""
Pseudonimização defensiva de PII — Maná Builder.

Substitui dados pessoais identificáveis (nomes próprios, CPF, CNPJ, sequências
longas de dígitos) por códigos genéricos ANTES de enviar pra LLM/3rd party.
Aplica recursivamente em dict, list, str. Permite desmascarar a resposta.

Origem:
  - PIIPseudonimizador derivado de agente-comite-credito (foco: nomes próprios)
  - pseudonimizar_filename derivado de agente-documentos (foco: CPF/CNPJ/filenames)

ADR: 2026-06-19-pseudonimizacao-padrao-llm-e-terceiros (vault Maná).
"""

from __future__ import annotations

import re
from typing import Any

# ─────────────────────────────────────────────────────────────────────
# Regex de identificadores estruturados (CPF, CNPJ, sequências longas)
# ─────────────────────────────────────────────────────────────────────

# CPF: 123.456.789-00 ou 12345678900 (com ou sem pontuação).
# Usa (?<!\d)/(?!\d) em vez de \b porque filenames Maná usam `_` como
# separador (e _ conta como word char, então \b falha em "CNH_12345678900.pdf").
# Em texto livre tipo "CPF 123.456.789-00 do cliente." também funciona.
# 11 dígitos colados são considerados CPF (mais comum em PII de filename
# que processo judicial — que tem 20 dígitos no padrão NPU/CNJ).
_RE_CPF = re.compile(r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)")

# CNPJ: 12.345.678/0001-90, 12345678000190, ou variantes com _ ou espaço
# no lugar da barra (separadores comuns no Windows).
_RE_CNPJ = re.compile(r"(?<!\d)\d{2}\.?\d{3}\.?\d{3}[/\s_]?\d{4}-?\d{2}(?!\d)")

# Sequência longa de dígitos (RG, processo, NIRF, protocolo) — 8+ dígitos.
# Pega o que sobra depois de CPF/CNPJ. CPF/CNPJ têm precedência na ordem
# de aplicação em pseudonimizar_filename + PIIPseudonimizador.aplicar.
_RE_NUM_LONGO = re.compile(r"(?<!\d)\d{8,}(?!\d)")


# ─────────────────────────────────────────────────────────────────────
# PIIPseudonimizador — caso conteúdo livre + nomes próprios
# ─────────────────────────────────────────────────────────────────────


class PIIPseudonimizador:
    """
    Pseudonimiza nomes próprios e (opcionalmente) identificadores estruturados
    em conteúdo livre antes de enviar pra LLM/3rd party.

    Uso típico:
        >>> pseudo = PIIPseudonimizador()
        >>> pseudo.construir_mapa_de_dict(
        ...     {"cliente": "João Silva", "vendedor": "Maria Santos"}
        ... )
        >>> pseudo.aplicar("João Silva é cliente.")
        'CLIENTE é cliente.'
        >>> pseudo.desmascarar("Decisão sobre CLIENTE: aprovada.")
        'Decisão sobre João Silva: aprovada.'

    O mapa nome↔código vive em memória apenas durante a vida da instância.
    Nunca persistir o mapa em banco, log ou disco.
    """

    def __init__(
        self,
        mapa_nomes: dict[str, str] | None = None,
        aplicar_identificadores: bool = False,
    ) -> None:
        """
        Args:
            mapa_nomes: dict {nome_real: codigo_anonimo}. Opcional — pode ser
                construído depois via `construir_mapa_de_dict()` ou injetado
                manualmente em `self.mapa`.
            aplicar_identificadores: se True, `aplicar()` também substitui
                CPF/CNPJ/sequências longas por placeholders ("CPF", "CNPJ",
                "NUM") em qualquer string processada. Default False — útil
                quando o input vem de campos estruturados já limpos.
        """
        self.mapa: dict[str, str] = dict(mapa_nomes) if mapa_nomes else {}
        self.aplicar_identificadores = bool(aplicar_identificadores)

    # ── Builders de mapa ────────────────────────────────────────────────

    def construir_mapa_de_dict(
        self,
        dados: dict[str, Any],
        campos: dict[str, str] | None = None,
    ) -> PIIPseudonimizador:
        """
        Popula o mapa a partir de um dict estruturado.

        Args:
            dados: dict com chaves canônicas (ex: cliente, vendedor, participantes).
            campos: mapeamento {chave_no_dict: codigo_anonimo_base}.
                Default:
                  {"cliente":"CLIENTE", "vendedor":"VENDEDOR", "participantes":"DIRETOR"}
                `participantes` é tratado como lista de dicts com chave "nome",
                gerando DIRETOR_1, DIRETOR_2, ... na ordem.

        Returns:
            self (encadeável).

        Exemplo:
            >>> pseudo = PIIPseudonimizador()
            >>> pseudo.construir_mapa_de_dict({
            ...     "cliente": "João Silva",
            ...     "vendedor": "Maria Santos",
            ...     "participantes": [{"nome": "Ana"}, {"nome": "Bruno"}],
            ... })  # doctest: +ELLIPSIS
            <...PIIPseudonimizador object at 0x...>
            >>> sorted(pseudo.mapa.items())
            [('Ana', 'DIRETOR_1'), ('Bruno', 'DIRETOR_2'), ('João Silva', 'CLIENTE'), ('Maria Santos', 'VENDEDOR')]
        """
        if not isinstance(dados, dict):
            return self
        if campos is None:
            campos = {"cliente": "CLIENTE", "vendedor": "VENDEDOR", "participantes": "DIRETOR"}

        for chave, codigo_base in campos.items():
            valor = dados.get(chave)
            if valor is None:
                continue
            if isinstance(valor, str):
                nome = valor.strip()
                if nome and nome not in self.mapa:
                    self.mapa[nome] = codigo_base
            elif isinstance(valor, list):
                # lista de dicts com chave "nome" → DIRETOR_1, DIRETOR_2, ...
                contador = 1
                for item in valor:
                    if isinstance(item, dict):
                        nome = (item.get("nome") or "").strip()
                    elif isinstance(item, str):
                        nome = item.strip()
                    else:
                        continue
                    if nome and nome not in self.mapa:
                        self.mapa[nome] = f"{codigo_base}_{contador}"
                        contador += 1
        return self

    def adicionar(self, nome_real: str, codigo: str) -> PIIPseudonimizador:
        """Adiciona um par nome→código manualmente. Idempotente. Encadeável."""
        nome = (nome_real or "").strip()
        if nome and nome not in self.mapa:
            self.mapa[nome] = codigo
        return self

    # ── Aplicação ───────────────────────────────────────────────────────

    def aplicar(self, obj: Any) -> Any:
        """
        Aplica pseudonimização recursivamente em dict, list, tuple, str.

        Estruturas mutáveis são COPIADAS — não muta entrada original.

        Se `aplicar_identificadores=True`, substitui também CPF/CNPJ/NUM
        em qualquer string processada (independente do mapa de nomes).

        Returns:
            Objeto com mesmo formato da entrada, com strings pseudonimizadas.
        """
        if isinstance(obj, str):
            return self._aplicar_em_string(obj)
        if isinstance(obj, dict):
            return {k: self.aplicar(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self.aplicar(item) for item in obj]
        if isinstance(obj, tuple):
            return tuple(self.aplicar(item) for item in obj)
        return obj

    def _aplicar_em_string(self, s: str) -> str:
        if not s:
            return s
        out = s
        # Ordena por comprimento descendente: nomes maiores primeiro
        # (evita "João" substituir antes de "João Silva")
        for original in sorted(self.mapa.keys(), key=len, reverse=True):
            codigo = self.mapa[original]
            out = re.sub(rf"\b{re.escape(original)}\b", codigo, out, flags=re.IGNORECASE)
        if self.aplicar_identificadores:
            out = _RE_CPF.sub("CPF", out)
            out = _RE_CNPJ.sub("CNPJ", out)
            out = _RE_NUM_LONGO.sub("NUM", out)
        return out

    # ── Desmascaramento (resposta do LLM → nome real) ──────────────────

    def desmascarar(self, texto: str) -> str:
        """
        Reverte códigos pra nomes reais.

        Aplica em ordem de comprimento descendente do CÓDIGO pra evitar que
        DIRETOR_1 atrapalhe a substituição de DIRETOR_10/11/.../99.

        Identificadores estruturados (CPF/CNPJ/NUM) NÃO são desmascarados
        — eles não têm correspondência original conhecida.
        """
        if not texto or not self.mapa:
            return texto
        out = texto
        pares = sorted(self.mapa.items(), key=lambda kv: len(kv[1]), reverse=True)
        for original, codigo in pares:
            out = out.replace(codigo, original)
        return out


# ─────────────────────────────────────────────────────────────────────
# pseudonimizar_filename — caso filename / triagem
# ─────────────────────────────────────────────────────────────────────


def pseudonimizar_filename(
    filename: str,
    contexto: dict[str, Any] | None = None,
) -> str:
    """
    Pseudonimiza um filename antes de mandar pro LLM (caso triagem).

    Substitui:
      - CPF (com ou sem pontuação) → "CPF"
      - CNPJ (com ou sem pontuação ou barra) → "CNPJ"
      - Nome do cliente conhecido (do contexto), em todas as variações
        comuns (com espaço, underline, hífen, sem separador) → "CLIENTE"
      - Sequências longas de dígitos (8+) → "NUM"

    Não altera a extensão. Não destrói pistas de tipo de documento
    (CNH, RG, IRPF, IPTU etc continuam visíveis pro LLM).

    Args:
        filename: nome do arquivo (com ou sem extensão).
        contexto: dict opcional. Suporta:
            - `cliente_nome` (str): nome completo do cliente real, pra
              substituir em variações no filename.

    Returns:
        Filename pseudonimizado.

    Exemplo:
        >>> pseudonimizar_filename("CNH_Joao_Silva_12345678900.pdf",
        ...                        contexto={"cliente_nome": "Joao Silva"})
        'CNH_CLIENTE_CPF.pdf'
    """
    if not filename:
        return filename
    out = filename
    # 1. CPF
    out = _RE_CPF.sub("CPF", out)
    # 2. CNPJ
    out = _RE_CNPJ.sub("CNPJ", out)
    # 3. Nome do cliente conhecido (variações comuns)
    if contexto:
        cliente = (contexto.get("cliente_nome") or "").strip()
        if cliente and len(cliente) >= 4:
            variacoes = {
                cliente,
                cliente.replace(" ", "_"),
                cliente.replace(" ", "-"),
                cliente.replace(" ", ""),
            }
            for v in sorted(variacoes, key=len, reverse=True):
                out = re.sub(re.escape(v), "CLIENTE", out, flags=re.IGNORECASE)
    # 4. Sequências longas de dígitos (RG, processo, NIRF, protocolo)
    out = _RE_NUM_LONGO.sub("NUM", out)
    return out


def pseudonimizar_filenames(
    filenames: list[str],
    contexto: dict[str, Any] | None = None,
) -> tuple[list[str], dict[str, str]]:
    """
    Pseudonimiza lista de filenames. Garante unicidade do nome pseudonimizado.

    Args:
        filenames: lista de filenames.
        contexto: vide `pseudonimizar_filename`.

    Returns:
        Tupla (lista_anon, mapa_anon_to_original).

    Se 2 filenames diferentes virarem o mesmo pseudo, o segundo ganha
    sufixo _1, _2, ... preservando a extensão.

    Exemplo:
        >>> anon, mapa = pseudonimizar_filenames(
        ...     ["doc.pdf", "doc.pdf"]
        ... )
        >>> anon
        ['doc.pdf', 'doc_1.pdf']
        >>> mapa['doc.pdf'] == 'doc.pdf' and mapa['doc_1.pdf'] == 'doc.pdf'
        True
    """
    mapa: dict[str, str] = {}
    anon_list: list[str] = []
    for fn in filenames:
        base = pseudonimizar_filename(fn, contexto)
        anon = base
        idx = 1
        while anon in mapa:
            # Preserva extensão no sufixo: "doc.pdf" → "doc_1.pdf"
            m = re.match(r"^(.*?)(\.[^.]{1,5})$", base)
            anon = f"{m.group(1)}_{idx}{m.group(2)}" if m else f"{base}_{idx}"
            idx += 1
        mapa[anon] = fn
        anon_list.append(anon)
    return anon_list, mapa
