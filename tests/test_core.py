"""
Suíte de testes — mana-habilidade-pseudonimizar-pii.

Cobre:
  - PIIPseudonimizador (caso conteúdo livre com nomes próprios)
  - pseudonimizar_filename / pseudonimizar_filenames (caso triagem)
  - Identificadores estruturados (CPF, CNPJ, sequências longas)
  - Casos derivados dos 2 agentes Maná de origem (comite-credito + documentos)

Cobertura alvo: ≥70% (config em pyproject.toml).
"""

from mana_habilidade_pseudonimizar_pii import (
    PIIPseudonimizador,
    pseudonimizar_filename,
    pseudonimizar_filenames,
)

# ─────────────────────────────────────────────────────────────────────
# PIIPseudonimizador — caso conteúdo livre
# ─────────────────────────────────────────────────────────────────────


class TestPIIPseudonimizadorBasico:
    def test_construtor_vazio(self) -> None:
        pseudo = PIIPseudonimizador()
        assert pseudo.mapa == {}
        assert pseudo.aplicar_identificadores is False

    def test_construtor_com_mapa(self) -> None:
        pseudo = PIIPseudonimizador(mapa_nomes={"João": "CLIENTE"})
        assert pseudo.mapa == {"João": "CLIENTE"}

    def test_aplicar_substitui_nome_simples(self) -> None:
        pseudo = PIIPseudonimizador(mapa_nomes={"João Silva": "CLIENTE"})
        assert pseudo.aplicar("João Silva é cliente.") == "CLIENTE é cliente."

    def test_aplicar_case_insensitive(self) -> None:
        pseudo = PIIPseudonimizador(mapa_nomes={"João Silva": "CLIENTE"})
        assert pseudo.aplicar("joão silva é cliente.") == "CLIENTE é cliente."

    def test_aplicar_word_boundary_evita_substring(self) -> None:
        pseudo = PIIPseudonimizador(mapa_nomes={"Ana": "DIRETOR_1"})
        # "Banana" contém "ana" — não deve ser substituído
        assert pseudo.aplicar("Banana é fruta.") == "Banana é fruta."

    def test_aplicar_ordem_descendente_de_comprimento(self) -> None:
        pseudo = PIIPseudonimizador(
            mapa_nomes={"João": "JOAO", "João Silva": "CLIENTE"}
        )
        # "João Silva" (maior) deve substituir antes de "João"
        assert pseudo.aplicar("João Silva veio.") == "CLIENTE veio."

    def test_aplicar_em_dict_recursivo(self) -> None:
        pseudo = PIIPseudonimizador(mapa_nomes={"João": "CLIENTE"})
        resultado = pseudo.aplicar({"texto": "João disse", "lista": ["João", "outro"]})
        assert resultado == {"texto": "CLIENTE disse", "lista": ["CLIENTE", "outro"]}

    def test_aplicar_em_list_recursivo(self) -> None:
        pseudo = PIIPseudonimizador(mapa_nomes={"João": "CLIENTE"})
        assert pseudo.aplicar(["João foi", "Maria voltou"]) == ["CLIENTE foi", "Maria voltou"]

    def test_aplicar_em_tuple(self) -> None:
        pseudo = PIIPseudonimizador(mapa_nomes={"João": "CLIENTE"})
        resultado = pseudo.aplicar(("João", "vai"))
        assert resultado == ("CLIENTE", "vai")
        assert isinstance(resultado, tuple)

    def test_aplicar_preserva_tipos_nao_string(self) -> None:
        pseudo = PIIPseudonimizador(mapa_nomes={"João": "CLIENTE"})
        assert pseudo.aplicar(42) == 42
        assert pseudo.aplicar(None) is None
        assert pseudo.aplicar(True) is True

    def test_aplicar_nao_muta_entrada_original(self) -> None:
        pseudo = PIIPseudonimizador(mapa_nomes={"João": "CLIENTE"})
        original = {"texto": "João foi"}
        _ = pseudo.aplicar(original)
        assert original == {"texto": "João foi"}  # inalterado

    def test_mapa_vazio_retorna_string_inalterada(self) -> None:
        pseudo = PIIPseudonimizador()
        assert pseudo.aplicar("João Silva foi.") == "João Silva foi."


class TestConstruirMapaDeDict:
    def test_mapa_default_cliente_vendedor_participantes(self) -> None:
        pseudo = PIIPseudonimizador()
        pseudo.construir_mapa_de_dict(
            {
                "cliente": "João Silva",
                "vendedor": "Maria Santos",
                "participantes": [{"nome": "Ana"}, {"nome": "Bruno"}],
            }
        )
        assert pseudo.mapa == {
            "João Silva": "CLIENTE",
            "Maria Santos": "VENDEDOR",
            "Ana": "DIRETOR_1",
            "Bruno": "DIRETOR_2",
        }

    def test_participantes_aceita_lista_de_strings(self) -> None:
        pseudo = PIIPseudonimizador()
        pseudo.construir_mapa_de_dict({"participantes": ["Ana", "Bruno"]})
        assert pseudo.mapa == {"Ana": "DIRETOR_1", "Bruno": "DIRETOR_2"}

    def test_campos_customizados(self) -> None:
        pseudo = PIIPseudonimizador()
        pseudo.construir_mapa_de_dict(
            {"comprador": "X", "fornecedor": "Y"},
            campos={"comprador": "BUYER", "fornecedor": "SUPPLIER"},
        )
        assert pseudo.mapa == {"X": "BUYER", "Y": "SUPPLIER"}

    def test_ignora_campos_ausentes_ou_vazios(self) -> None:
        pseudo = PIIPseudonimizador()
        pseudo.construir_mapa_de_dict({"cliente": "", "vendedor": None})
        assert pseudo.mapa == {}

    def test_nao_sobrescreve_mapa_existente(self) -> None:
        pseudo = PIIPseudonimizador(mapa_nomes={"João": "CLIENTE_ESPECIAL"})
        pseudo.construir_mapa_de_dict({"cliente": "João"})
        # Mapa preexistente prevalece
        assert pseudo.mapa["João"] == "CLIENTE_ESPECIAL"

    def test_retorna_self_encadeavel(self) -> None:
        pseudo = PIIPseudonimizador()
        resultado = pseudo.construir_mapa_de_dict({"cliente": "X"})
        assert resultado is pseudo

    def test_entrada_nao_dict_retorna_inalterado(self) -> None:
        pseudo = PIIPseudonimizador()
        pseudo.construir_mapa_de_dict("não é dict")  # type: ignore[arg-type]
        assert pseudo.mapa == {}


class TestDesmascarar:
    def test_reverte_codigo_pra_nome(self) -> None:
        pseudo = PIIPseudonimizador(mapa_nomes={"João Silva": "CLIENTE"})
        assert pseudo.desmascarar("Decisão sobre CLIENTE: aprovada.") == "Decisão sobre João Silva: aprovada."

    def test_diretor_10_nao_quebra_por_diretor_1(self) -> None:
        # DIRETOR_1 não pode substituir antes de DIRETOR_10
        pseudo = PIIPseudonimizador(mapa_nomes={"Ana": "DIRETOR_1", "Zé": "DIRETOR_10"})
        assert pseudo.desmascarar("Conversa entre DIRETOR_1 e DIRETOR_10.") == "Conversa entre Ana e Zé."

    def test_mapa_vazio_retorna_texto_inalterado(self) -> None:
        pseudo = PIIPseudonimizador()
        assert pseudo.desmascarar("CLIENTE foi.") == "CLIENTE foi."

    def test_texto_vazio_retorna_vazio(self) -> None:
        pseudo = PIIPseudonimizador(mapa_nomes={"João": "CLIENTE"})
        assert pseudo.desmascarar("") == ""


class TestIdentificadoresEstruturados:
    def test_cpf_substituido_quando_flag_ligada(self) -> None:
        pseudo = PIIPseudonimizador(aplicar_identificadores=True)
        assert pseudo.aplicar("CPF 123.456.789-00 do cliente.") == "CPF CPF do cliente."

    def test_cpf_sem_pontuacao(self) -> None:
        pseudo = PIIPseudonimizador(aplicar_identificadores=True)
        assert pseudo.aplicar("12345678900") == "CPF"

    def test_cnpj_substituido(self) -> None:
        pseudo = PIIPseudonimizador(aplicar_identificadores=True)
        assert pseudo.aplicar("CNPJ 12.345.678/0001-90") == "CNPJ CNPJ"

    def test_identificadores_off_por_default(self) -> None:
        pseudo = PIIPseudonimizador()
        # Sem aplicar_identificadores, CPF/CNPJ não são tocados
        assert pseudo.aplicar("123.456.789-00") == "123.456.789-00"

    def test_sequencia_longa_substituida(self) -> None:
        pseudo = PIIPseudonimizador(aplicar_identificadores=True)
        assert pseudo.aplicar("processo 1234567890") == "processo NUM"

    def test_adicionar_encadeavel(self) -> None:
        pseudo = PIIPseudonimizador().adicionar("João", "CLIENTE").adicionar("Maria", "VENDEDOR")
        assert pseudo.mapa == {"João": "CLIENTE", "Maria": "VENDEDOR"}


# ─────────────────────────────────────────────────────────────────────
# pseudonimizar_filename — caso triagem
# ─────────────────────────────────────────────────────────────────────


class TestPseudonimizarFilename:
    def test_cpf_no_filename(self) -> None:
        assert pseudonimizar_filename("CNH_12345678900.pdf") == "CNH_CPF.pdf"

    def test_cpf_com_pontuacao(self) -> None:
        assert pseudonimizar_filename("CNH_123.456.789-00.pdf") == "CNH_CPF.pdf"

    def test_cnpj_no_filename(self) -> None:
        assert pseudonimizar_filename("contrato_12.345.678_0001-90.pdf") == "contrato_CNPJ.pdf"

    def test_nome_cliente_variacao_underline(self) -> None:
        out = pseudonimizar_filename(
            "CNH_Joao_Silva_12345678900.pdf",
            contexto={"cliente_nome": "Joao Silva"},
        )
        assert out == "CNH_CLIENTE_CPF.pdf"

    def test_nome_cliente_variacao_hifen(self) -> None:
        out = pseudonimizar_filename(
            "doc-Joao-Silva.pdf",
            contexto={"cliente_nome": "Joao Silva"},
        )
        assert out == "doc-CLIENTE.pdf"

    def test_nome_cliente_variacao_sem_separador(self) -> None:
        out = pseudonimizar_filename(
            "JoaoSilva_doc.pdf",
            contexto={"cliente_nome": "Joao Silva"},
        )
        assert out == "CLIENTE_doc.pdf"

    def test_nome_cliente_case_insensitive(self) -> None:
        out = pseudonimizar_filename(
            "JOAO_SILVA.pdf",
            contexto={"cliente_nome": "Joao Silva"},
        )
        assert out == "CLIENTE.pdf"

    def test_filename_vazio_retorna_vazio(self) -> None:
        assert pseudonimizar_filename("") == ""

    def test_preserva_pistas_de_tipo_de_documento(self) -> None:
        # CNH, IRPF, IPTU devem continuar visíveis pro LLM
        out = pseudonimizar_filename("IRPF_45678901234_2025.pdf")
        # 45678901234 é 11 dígitos colado por _, vira NUM
        # 2025 é só 4 dígitos, fica
        assert "IRPF" in out
        assert "2025" in out

    def test_sequencia_longa_protocolo(self) -> None:
        # 10 dígitos = não é CPF (11) nem CNPJ (14); vira NUM longo.
        # 11 dígitos colados seriam tratados como CPF (decisão consciente —
        # mais comum em filenames Maná que número de processo judicial).
        assert pseudonimizar_filename("processo_9876543210.pdf") == "processo_NUM.pdf"

    def test_cliente_curto_demais_e_ignorado(self) -> None:
        # cliente_nome com <4 chars é ignorado pra evitar substituição falsa
        out = pseudonimizar_filename("Ana_doc.pdf", contexto={"cliente_nome": "Ana"})
        assert out == "Ana_doc.pdf"


class TestPseudonimizarFilenames:
    def test_lista_simples(self) -> None:
        anon, mapa = pseudonimizar_filenames(["doc.pdf", "outro.pdf"])
        assert anon == ["doc.pdf", "outro.pdf"]
        assert mapa == {"doc.pdf": "doc.pdf", "outro.pdf": "outro.pdf"}

    def test_unicidade_quando_pseudonimo_colide(self) -> None:
        # 2 CPFs diferentes viram o mesmo pseudonimo "CPF.pdf"
        anon, mapa = pseudonimizar_filenames(
            ["12345678900.pdf", "98765432109.pdf"]
        )
        assert anon == ["CPF.pdf", "CPF_1.pdf"]
        assert mapa["CPF.pdf"] == "12345678900.pdf"
        assert mapa["CPF_1.pdf"] == "98765432109.pdf"

    def test_preserva_extensao_no_sufixo(self) -> None:
        anon, _ = pseudonimizar_filenames(["doc.pdf", "doc.pdf", "doc.pdf"])
        assert anon == ["doc.pdf", "doc_1.pdf", "doc_2.pdf"]

    def test_contexto_propagado(self) -> None:
        anon, _ = pseudonimizar_filenames(
            ["Joao_Silva_doc.pdf"],
            contexto={"cliente_nome": "Joao Silva"},
        )
        assert anon == ["CLIENTE_doc.pdf"]

    def test_lista_vazia(self) -> None:
        anon, mapa = pseudonimizar_filenames([])
        assert anon == []
        assert mapa == {}


# ─────────────────────────────────────────────────────────────────────
# Cenários integrados (caso típico do comite-credito + documentos)
# ─────────────────────────────────────────────────────────────────────


class TestCenarioComite:
    """Replica fluxo do agente-comite-credito: ata de reunião pro LLM."""

    def test_pipeline_completo(self) -> None:
        dados = {
            "cliente": "Fazenda São João Ltda",
            "vendedor": "Carlos Pereira",
            "participantes": [
                {"nome": "Ana Diretoria"},
                {"nome": "Bruno Risco"},
            ],
            "discussao": [
                {"nome": "Ana Diretoria", "fala": "Aprovo o crédito da Fazenda São João Ltda."},
                {"nome": "Bruno Risco", "fala": "Carlos Pereira pode endossar."},
            ],
        }
        pseudo = PIIPseudonimizador().construir_mapa_de_dict(dados)
        anon = pseudo.aplicar(dados)
        # Nomes substituídos
        assert anon["cliente"] == "CLIENTE"
        assert anon["vendedor"] == "VENDEDOR"
        assert anon["participantes"][0]["nome"] == "DIRETOR_1"
        assert anon["discussao"][0]["fala"] == "Aprovo o crédito da CLIENTE."
        assert anon["discussao"][1]["fala"] == "VENDEDOR pode endossar."
        # Resposta do LLM (simulada) desmascarada
        resposta = "Decisão: CLIENTE recebe crédito; VENDEDOR endossa; DIRETOR_1 aprova."
        real = pseudo.desmascarar(resposta)
        assert "Fazenda São João Ltda" in real
        assert "Carlos Pereira" in real
        assert "Ana Diretoria" in real


class TestCenarioDocumentos:
    """Replica fluxo do agente-documentos: triagem de PDFs por filename."""

    def test_triagem_lista_real(self) -> None:
        filenames = [
            "CNH_Joao_Silva.pdf",
            "CPF_12345678900.pdf",
            "IRPF_2025.pdf",
            "contrato_12.345.678_0001-90.pdf",
            "CNH_Joao_Silva.pdf",  # duplicata pra testar unicidade
        ]
        anon, mapa = pseudonimizar_filenames(
            filenames, contexto={"cliente_nome": "Joao Silva"}
        )
        assert anon[0] == "CNH_CLIENTE.pdf"
        assert anon[1] == "CPF_CPF.pdf"
        assert "2025" in anon[2]  # ano preservado
        assert anon[3] == "contrato_CNPJ.pdf"
        # Duplicata ganha sufixo
        assert anon[4] == "CNH_CLIENTE_1.pdf"
        # Mapa permite reverter
        assert mapa[anon[0]] == "CNH_Joao_Silva.pdf"
        assert mapa[anon[4]] == "CNH_Joao_Silva.pdf"
