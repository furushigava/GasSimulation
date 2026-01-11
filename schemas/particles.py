"""
Схемы для параметров частиц.
"""
from pydantic import Field
from .base import ConfigSection


class ParticlesConfig(ConfigSection):
    """Параметры частиц."""
    
    count: int = Field(
        default=200,
        ge=1,
        le=1000,
        title="Количество частиц",
        description="Общее количество частиц в симуляции"
    )
    radius: int = Field(
        default=5,
        ge=1,
        le=50,
        title="Радиус",
        description="Радиус частицы в пикселях"
    )
    mass: int = Field(
        default=1,
        ge=1,
        le=100,
        title="Масса",
        description="Масса частицы (условные единицы)"
    )
    initial_speed: int = Field(
        default=5,
        ge=1,
        le=50,
        title="Начальная скорость",
        description="Начальная скорость частиц"
    )
    trajectory_max_length: int = Field(
        default=100,
        ge=0,
        le=1000,
        title="Макс. длина траектории",
        description="Максимальная длина траектории для отслеживания (0 = отключено)"
    )
