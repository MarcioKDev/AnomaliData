"""Modelo inicial do domínio do AnomaliData."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from .excecoes import DadoInvalidoError


def _texto_obrigatorio(valor: str, campo: str) -> str:
    texto = valor.strip()
    if not texto:
        raise DadoInvalidoError(f"{campo} deve ser informado")
    return texto


def calcular_expiracao_em_12_meses(executada_em: datetime) -> datetime:
    """Calcula a retenção anual, inclusive para execuções em 29 de fevereiro."""

    try:
        return executada_em.replace(year=executada_em.year + 1)
    except ValueError:
        return executada_em.replace(year=executada_em.year + 1, day=28)


@dataclass(frozen=True, slots=True)
class ChaveHistorica:
    """Identifica registros comparáveis pelo produto e fornecedor."""

    codigo_produto: str
    fornecedor: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "codigo_produto",
            _texto_obrigatorio(self.codigo_produto, "Código do produto"),
        )
        object.__setattr__(
            self,
            "fornecedor",
            _texto_obrigatorio(self.fornecedor, "Fornecedor"),
        )


@dataclass(frozen=True, slots=True)
class RegistroCompra:
    """Representa um item de compra válido."""

    id_registro: str
    codigo_produto: str
    fornecedor: str
    quantidade: Decimal
    preco_unitario: Decimal
    data_compra: date

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "id_registro",
            _texto_obrigatorio(self.id_registro, "Identificador"),
        )
        object.__setattr__(
            self,
            "codigo_produto",
            _texto_obrigatorio(self.codigo_produto, "Código do produto"),
        )
        object.__setattr__(
            self,
            "fornecedor",
            _texto_obrigatorio(self.fornecedor, "Fornecedor"),
        )
        if self.quantidade <= 0:
            raise DadoInvalidoError("Quantidade deve ser maior que zero")
        if self.preco_unitario <= 0:
            raise DadoInvalidoError("Preço unitário deve ser maior que zero")
        if self.data_compra > date.today():
            raise DadoInvalidoError("Data da compra não pode estar no futuro")

    def chave_historica(self) -> ChaveHistorica:
        return ChaveHistorica(self.codigo_produto, self.fornecedor)


@dataclass(frozen=True, slots=True)
class AlertaAnomalia:
    """Representa a evidência de um desvio suspeito."""

    id_alerta: str
    registro: RegistroCompra
    pontuacao: float
    fatores: tuple[str, ...]
    desvio_preco_percentual: Decimal

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "id_alerta",
            _texto_obrigatorio(self.id_alerta, "Identificador do alerta"),
        )
        if self.pontuacao < 0:
            raise DadoInvalidoError("Pontuação não pode ser negativa")
        if not self.fatores or any(not fator.strip() for fator in self.fatores):
            raise DadoInvalidoError("O alerta deve informar ao menos um fator")


class ClassificacaoAlerta(StrEnum):
    PENDENTE = "pendente"
    CONFIRMADA = "anomalia_confirmada"
    JUSTIFICADA = "situacao_justificada"


@dataclass(frozen=True, slots=True)
class RevisaoAlerta:
    """Registra a decisão humana sobre um alerta."""

    id_alerta: str
    classificacao: ClassificacaoAlerta
    observacao: str
    registrada_em: datetime

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "id_alerta",
            _texto_obrigatorio(self.id_alerta, "Identificador do alerta"),
        )
        if self.registrada_em > datetime.now(tz=self.registrada_em.tzinfo):
            raise DadoInvalidoError("Data da revisão não pode estar no futuro")


@dataclass(frozen=True, slots=True)
class ResultadoAnalise:
    """Representa o resultado consolidado de uma execução."""

    id_analise: str
    total_registros: int
    duracao_segundos: float
    alertas: tuple[AlertaAnomalia, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "id_analise",
            _texto_obrigatorio(self.id_analise, "Identificador da análise"),
        )
        if self.total_registros < 0:
            raise DadoInvalidoError("Total de registros não pode ser negativo")
        if self.duracao_segundos < 0:
            raise DadoInvalidoError("Duração não pode ser negativa")
        if len(self.alertas) > self.total_registros:
            raise DadoInvalidoError("Alertas não podem exceder o total analisado")
        pontuacoes = [alerta.pontuacao for alerta in self.alertas]
        if pontuacoes != sorted(pontuacoes, reverse=True):
            raise DadoInvalidoError("Alertas devem estar em ordem de pontuação")


@dataclass(frozen=True, slots=True)
class ParametrosAnalise:
    """Registra a configuração reproduzível de uma análise."""

    colunas_agrupamento: tuple[str, ...]
    coluna_numerica: str
    limiar_percentual: Decimal

    def __post_init__(self) -> None:
        colunas = tuple(
            _texto_obrigatorio(coluna, "Coluna de agrupamento")
            for coluna in self.colunas_agrupamento
        )
        if not colunas:
            raise DadoInvalidoError(
                "Ao menos uma coluna de agrupamento deve ser informada"
            )
        if len(set(colunas)) != len(colunas):
            raise DadoInvalidoError("Colunas de agrupamento não podem se repetir")
        object.__setattr__(self, "colunas_agrupamento", colunas)
        object.__setattr__(
            self,
            "coluna_numerica",
            _texto_obrigatorio(self.coluna_numerica, "Coluna numérica"),
        )
        if self.limiar_percentual <= 0:
            raise DadoInvalidoError("Limiar percentual deve ser maior que zero")


@dataclass(frozen=True, slots=True)
class AnaliseRegistrada:
    """Representa os metadados e o resultado mantidos no histórico local."""

    identificacao_conjunto: str
    parametros: ParametrosAnalise
    resultado: ResultadoAnalise
    executada_em: datetime
    expira_em: datetime

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "identificacao_conjunto",
            _texto_obrigatorio(
                self.identificacao_conjunto,
                "Identificação do conjunto",
            ),
        )
        agora = datetime.now(tz=self.executada_em.tzinfo)
        if self.executada_em > agora:
            raise DadoInvalidoError("Data da análise não pode estar no futuro")
        expiracao_esperada = calcular_expiracao_em_12_meses(self.executada_em)
        if self.expira_em != expiracao_esperada:
            raise DadoInvalidoError(
                "Expiração deve ocorrer 12 meses após a análise"
            )

    @property
    def id_analise(self) -> str:
        return self.resultado.id_analise
