"""
Configuração centralizada de logging para o sistema.

Fornece logs formatados e coloridos no terminal para
facilitar o acompanhamento em tempo real.
"""

import logging
import sys


def setup_logger(level: str = "INFO") -> logging.Logger:
    """
    Configura e retorna o logger principal do sistema.

    Args:
        level: Nível de log (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Logger configurado
    """
    # Converte string para constante do logging
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Formato do log: [HORA] NIVEL - módulo - mensagem
    log_format = (
        "[%(asctime)s] %(levelname)-8s | %(name)-25s | %(message)s"
    )
    date_format = "%H:%M:%S"

    # Configura o logger raiz
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        datefmt=date_format,
        stream=sys.stdout,
        force=True,  # Sobrescreve configurações anteriores
    )

    # Reduz verbosidade de bibliotecas externas
    logging.getLogger("ultralytics").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logger = logging.getLogger("separador_lixo")
    logger.info("Sistema de logging inicializado")

    return logger
