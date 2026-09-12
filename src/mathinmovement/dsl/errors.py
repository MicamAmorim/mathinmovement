class DSLError(ValueError):
    """Erro de validação/execução da DSL visual."""


class DSLVersionError(DSLError):
    """Versão da DSL não suportada."""


class DSLReferenceError(DSLError):
    """Referência a objeto/tracker inexistente."""
