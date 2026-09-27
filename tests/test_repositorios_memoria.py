from datetime import datetime, timedelta, timezone
from decimal import Decimal
import unittest

from anomalidata.dominio import (
    AnaliseRegistrada,
    ClassificacaoAlerta,
    DadoInvalidoError,
    ParametrosAnalise,
    RepositorioAnalises,
    RepositorioRevisoes,
    ResultadoAnalise,
    RevisaoAlerta,
    calcular_expiracao_em_12_meses,
)
from anomalidata.persistencia import (
    RepositorioAnalisesMemoria,
    RepositorioRevisoesMemoria,
)


class AnaliseRegistradaTest(unittest.TestCase):
    def criar_analise(self, executada_em: datetime) -> AnaliseRegistrada:
        resultado = ResultadoAnalise(
            id_analise=f"ANA-{executada_em:%Y%m%d%H%M%S}",
            total_registros=10_000,
            duracao_segundos=2.4,
            alertas=(),
        )
        parametros = ParametrosAnalise(
            colunas_agrupamento=("codigo_produto", "fornecedor"),
            coluna_numerica="preco_unitario",
            limiar_percentual=Decimal("25"),
        )
        return AnaliseRegistrada(
            identificacao_conjunto="base-validacao.csv",
            parametros=parametros,
            resultado=resultado,
            executada_em=executada_em,
            expira_em=calcular_expiracao_em_12_meses(executada_em),
        )

    def test_calcula_expiracao_de_ano_bissexto(self) -> None:
        executada_em = datetime(2024, 2, 29, 10, tzinfo=timezone.utc)

        self.assertEqual(
            datetime(2025, 2, 28, 10, tzinfo=timezone.utc),
            calcular_expiracao_em_12_meses(executada_em),
        )

    def test_rejeita_expiracao_diferente_de_12_meses(self) -> None:
        executada_em = datetime.now(timezone.utc) - timedelta(days=1)

        with self.assertRaises(DadoInvalidoError):
            AnaliseRegistrada(
                identificacao_conjunto="base-validacao.csv",
                parametros=ParametrosAnalise(
                    colunas_agrupamento=("produto",),
                    coluna_numerica="preco",
                    limiar_percentual=Decimal("25"),
                ),
                resultado=ResultadoAnalise("ANA-001", 10_000, 1.0, ()),
                executada_em=executada_em,
                expira_em=executada_em + timedelta(days=30),
            )


class RepositorioAnalisesMemoriaTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repositorio = RepositorioAnalisesMemoria()
        self.fabrica = AnaliseRegistradaTest()

    def test_implementa_contrato_do_dominio(self) -> None:
        self.assertIsInstance(self.repositorio, RepositorioAnalises)

    def test_salva_busca_e_lista_somente_analises_ativas(self) -> None:
        referencia = datetime(2026, 9, 27, 12, tzinfo=timezone.utc)
        ativa = self.fabrica.criar_analise(referencia - timedelta(days=30))
        expirada = self.fabrica.criar_analise(referencia - timedelta(days=400))
        self.repositorio.salvar(ativa)
        self.repositorio.salvar(expirada)

        self.assertEqual(ativa, self.repositorio.buscar_por_id(ativa.id_analise))
        self.assertEqual((ativa,), self.repositorio.listar_ativas(referencia))

    def test_exclui_analises_expiradas(self) -> None:
        referencia = datetime(2026, 9, 27, 12, tzinfo=timezone.utc)
        expirada = self.fabrica.criar_analise(referencia - timedelta(days=400))
        self.repositorio.salvar(expirada)

        self.assertEqual(1, self.repositorio.excluir_expiradas(referencia))
        self.assertIsNone(self.repositorio.buscar_por_id(expirada.id_analise))


class RepositorioRevisoesMemoriaTest(unittest.TestCase):
    def test_implementa_contrato_e_substitui_revisao_anterior(self) -> None:
        repositorio = RepositorioRevisoesMemoria()
        registrada_em = datetime.now(timezone.utc) - timedelta(minutes=1)
        pendente = RevisaoAlerta(
            "ALT-001",
            ClassificacaoAlerta.PENDENTE,
            "Aguardando conferência",
            registrada_em,
        )
        confirmada = RevisaoAlerta(
            "ALT-001",
            ClassificacaoAlerta.CONFIRMADA,
            "Preço incompatível com o histórico",
            registrada_em + timedelta(seconds=1),
        )

        self.assertIsInstance(repositorio, RepositorioRevisoes)
        repositorio.salvar(pendente)
        repositorio.salvar(confirmada)

        self.assertEqual(confirmada, repositorio.buscar_por_alerta("ALT-001"))


if __name__ == "__main__":
    unittest.main()
