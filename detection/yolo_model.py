"""
Carregamento e gerenciamento do modelo YOLO.

Este módulo encapsula toda a interação com a biblioteca ultralytics,
permitindo trocar facilmente entre o modelo real e uma versão simulada (mock).
"""

import logging
import random
from typing import Any

import numpy as np

from config import settings

logger = logging.getLogger(__name__)


class YOLOModel:
    """
    Wrapper para o modelo YOLO da ultralytics.
    
    Carrega o modelo a partir de um arquivo .pt e executa inferência
    em imagens (numpy arrays).
    """

    def __init__(self, model_path: str = None, confidence: float = None):
        """
        Inicializa o modelo YOLO.

        Args:
            model_path: Caminho para o arquivo de pesos (.pt).
                        Se None, usa o caminho definido em settings.
            confidence: Limiar de confiança mínima (0.0 a 1.0).
                        Se None, usa o valor definido em settings.
        """
        self.model_path = model_path or settings.YOLO_MODEL_PATH
        self.confidence = confidence or settings.YOLO_CONFIDENCE_THRESHOLD
        self.model = None

    def load(self) -> bool:
        """
        Carrega o modelo YOLO na memória.

        Returns:
            True se carregou com sucesso, False caso contrário.
        """
        try:
            from ultralytics import YOLO

            logger.info(f"Carregando modelo YOLO: {self.model_path}")
            self.model = YOLO(self.model_path)
            logger.info("Modelo YOLO carregado com sucesso!")
            return True

        except ImportError:
            logger.error(
                "Biblioteca 'ultralytics' não instalada. "
                "Execute: pip install ultralytics"
            )
            return False

        except Exception as e:
            logger.error(f"Erro ao carregar modelo YOLO: {e}")
            return False

    def predict(self, image: np.ndarray) -> list[dict[str, Any]]:
        """
        Executa inferência em uma imagem.

        Args:
            image: Imagem como numpy array (BGR, formato OpenCV)

        Returns:
            Lista de detecções, cada uma contendo:
            - 'class_id': ID numérico da classe
            - 'class_name': Nome da classe (ex: 'plastico')
            - 'confidence': Confiança da detecção (0.0 a 1.0)
            - 'bbox': Bounding box [x1, y1, x2, y2]
        """
        if self.model is None:
            logger.error("Modelo não carregado. Chame load() primeiro.")
            return []

        try:
            # Executa inferência
            results = self.model(image, conf=self.confidence, verbose=False)

            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is None:
                    continue

                for box in boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    bbox = box.xyxy[0].tolist()

                    # Mapeia ID da classe para nome
                    class_name = settings.CLASSES.get(class_id, f"desconhecido_{class_id}")

                    detections.append({
                        "class_id": class_id,
                        "class_name": class_name,
                        "confidence": confidence,
                        "bbox": bbox,
                    })

            logger.debug(f"Detectados {len(detections)} objetos")
            return detections

        except Exception as e:
            logger.error(f"Erro durante inferência YOLO: {e}")
            return []


class MockYOLOModel:
    """
    Modelo YOLO simulado para testes.
    
    Gera detecções aleatórias sem precisar do modelo real.
    Útil para desenvolvimento e testes de integração.
    """

    def __init__(self):
        """Inicializa o modelo mock."""
        self.classes = settings.VALID_TRASH_TYPES

    def load(self) -> bool:
        """Simula o carregamento do modelo."""
        logger.info("Modelo MOCK carregado (simulação)")
        return True

    def predict(self, image: np.ndarray) -> list[dict[str, Any]]:
        """
        Gera detecções simuladas aleatórias.

        Args:
            image: Imagem (ignorada no mock, mas mantém a mesma interface)

        Returns:
            Lista com 1 a 3 detecções simuladas
        """
        num_detections = random.randint(1, 3)
        detections = []

        for _ in range(num_detections):
            class_name = random.choice(self.classes)
            class_id = self.classes.index(class_name)

            detections.append({
                "class_id": class_id,
                "class_name": class_name,
                "confidence": round(random.uniform(0.6, 0.99), 2),
                "bbox": [
                    random.randint(0, 300),
                    random.randint(0, 200),
                    random.randint(300, 600),
                    random.randint(200, 400),
                ],
            })

        logger.debug(f"Mock: geradas {len(detections)} detecções simuladas")
        return detections


def create_model(use_mock: bool = None):
    """
    Factory function para criar a instância correta do modelo.

    Args:
        use_mock: Se True, retorna MockYOLOModel. Se None, usa settings.

    Returns:
        Instância de YOLOModel ou MockYOLOModel
    """
    if use_mock is None:
        use_mock = settings.USE_MOCK_DETECTION

    if use_mock:
        logger.info("Usando modelo MOCK (simulação)")
        return MockYOLOModel()
    else:
        logger.info("Usando modelo YOLO real")
        return YOLOModel()
