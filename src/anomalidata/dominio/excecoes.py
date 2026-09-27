"""Exceções do domínio do AnomaliData."""


class ErroDominio(ValueError):
    """Representa uma violação de regra do domínio."""


class DadoInvalidoError(ErroDominio):
    """Indica que um valor não satisfaz uma invariante."""


class TransicaoInvalidaError(ErroDominio):
    """Indica uma mudança de estado não permitida."""

