"""
Módulo de predição e interpretação de resultados.

Processa as detecções brutas do YOLO e determina o tipo
de lixo predominante na imagem.
"""

import logging
from collections import Counter
from typing import Any

from config import settings

logger = logging.getLogger(__name__)


def get_predominant_trash(detections: list[dict[str, Any]]) -> str | None:
    """
    Determina o tipo de lixo predominante com base nas detecções.

    A lógica de decisão usa duas estratégias combinadas:
    1. Contagem: qual classe aparece mais vezes
    2. Confiança: em caso de empate, a classe com maior confiança média vence

    Args:
        detections: Lista de detecções do YOLO, cada uma com:
            - 'class_name': nome da classe
            - 'confidence': confiança da detecção

    Returns:
        Nome do tipo de lixo predominante ('plastico', 'papel' ou 'metal'),
        ou None se nenhuma detecção válida foi encontrada.
    """
    if not detections:
        logger.warning("Nenhuma detecção recebida")
        return None

    # Filtra apenas detecções com classes válidas
    valid_detections = [
        d for d in detections
        if d.get("class_name") in settings.VALID_TRASH_TYPES
    ]

    if not valid_detections:
        logger.warning("Nenhuma detecção com classe válida")
        return None

    # Conta quantas vezes cada tipo aparece
    class_counts = Counter(d["class_name"] for d in valid_detections)

    # Calcula a confiança média por classe
    class_confidence = {}
    for class_name in class_counts:
        confidences = [
            d["confidence"]
            for d in valid_detections
            if d["class_name"] == class_name
        ]
        class_confidence[class_name] = sum(confidences) / len(confidences)

    # Encontra a contagem máxima
    max_count = max(class_counts.values())

    # Classes empatadas na contagem máxima
    tied_classes = [
        cls for cls, count in class_counts.items()
        if count == max_count
    ]

    # Desempata pela confiança média
    predominant = max(tied_classes, key=lambda cls: class_confidence[cls])

    # Log detalhado do resultado
    logger.info(
        f"Resultado da análise: {predominant} "
        f"(contagem: {class_counts[predominant]}, "
        f"confiança média: {class_confidence[predominant]:.2f})"
    )

    for cls, count in class_counts.items():
        logger.debug(
            f"  → {cls}: {count}x detecções, "
            f"confiança média: {class_confidence[cls]:.2f}"
        )

    return predominant


def format_result(trash_type: str | None) -> str:
    """
    Formata o resultado para envio ao ESP32.

    Args:
        trash_type: Tipo de lixo detectado ou None

    Returns:
        String formatada para envio (ex: 'plastico', 'papel', 'metal', 'nenhum')
    """
    if trash_type is None:
        return "nenhum"

    # Garante que o tipo é válido
    if trash_type not in settings.VALID_TRASH_TYPES:
        logger.warning(f"Tipo de lixo inválido: {trash_type}")
        return "nenhum"

    return trash_type
