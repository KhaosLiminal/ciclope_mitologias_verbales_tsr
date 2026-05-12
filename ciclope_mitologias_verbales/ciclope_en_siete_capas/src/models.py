"""
Modelos de datos para el proyecto Cíclope.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class FuenteBibliografica:
    """Representa una fuente bibliográfica."""
    numero: int
    bloque: str
    autor: str
    titulo: str
    año: int
    tipo: str  # libro, paper, pdf, video, tesis
    editorial_revista: str
    url: str
    doi: str = ""
    relevancia: str = ""

@dataclass
class MetadataGeneracion:
    """Metadatos sobre la generación de la bibliografía."""
    modelo: str
    intentos_necesarios: int
    tokens_entrada: int
    tokens_salida: int
    temperatura: float
    timestamp: str

@dataclass
class ResultadoTSR:
    """Resultado de la generación de bibliografía para un TSR."""
    tsr: str
    titulo: str
    cluster: str
    fecha_generacion: str
    fuentes: List[FuenteBibliografica]
    cobertura_conceptual: Dict[str, str]
    nota_metodologica: str = ""
    metadata_generacion: Optional[MetadataGeneracion] = None
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

@dataclass
class EstadisticasEjecucion:
    """Estadísticas de la ejecución del script."""
    total_tsr: int
    exitosos: int
    fallidos: int
    total_fuentes: int
    tiempo_ejecucion: float  # en segundos
    inicio_ejecucion: str
    fin_ejecucion: str

    @property
    def tasa_exito(self) -> float:
        """Calcula la tasa de éxito como porcentaje."""
        return (self.exitosos / self.total_tsr) * 100 if self.total_tsr > 0 else 0.0
