"""
Схемы для параметров пользовательского интерфейса.
"""
from pydantic import Field
from typing import Tuple
from .base import ConfigSection


class MainWindowConfig(ConfigSection):
    """Параметры главного окна."""
    
    width: int = Field(
        default=1400,
        ge=800,
        le=3840,
        title="Ширина",
        description="Ширина главного окна в пикселях"
    )
    height: int = Field(
        default=900,
        ge=600,
        le=2160,
        title="Высота",
        description="Высота главного окна в пикселях"
    )


class GraphWindowConfig(ConfigSection):
    """Параметры окна графиков."""
    
    width: int = Field(
        default=1400,
        ge=800,
        le=3840,
        title="Ширина",
        description="Ширина окна графиков в пикселях"
    )
    height: int = Field(
        default=900,
        ge=600,
        le=2160,
        title="Высота",
        description="Высота окна графиков в пикселях"
    )
    figure_width: int = Field(
        default=12,
        ge=6,
        le=24,
        title="Ширина фигуры",
        description="Ширина matplotlib фигуры"
    )
    figure_height: int = Field(
        default=8,
        ge=4,
        le=16,
        title="Высота фигуры",
        description="Высота matplotlib фигуры"
    )


class LoggingConfig(ConfigSection):
    """Параметры логирования."""
    
    buffer_size: int = Field(
        default=100,
        ge=10,
        le=1000,
        title="Размер буфера",
        description="Размер буфера для логов"
    )
