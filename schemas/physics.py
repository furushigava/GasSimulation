"""
Схемы для физических параметров симуляции.
"""
from pydantic import Field
from typing import Literal
from .base import ConfigSection


class GravityConfig(ConfigSection):
    """Параметры гравитационного поля."""
    
    enabled: bool = Field(
        default=False,
        title="Включить гравитацию",
        description="Включить внешнее гравитационное поле (направлено вниз)"
    )
    g: float = Field(
        default=0.1,
        ge=0.0,
        le=10.0,
        title="Ускорение свободного падения",
        description="Величина ускорения свободного падения"
    )


class BrownianConfig(ConfigSection):
    """Параметры броуновского движения."""
    
    enabled: bool = Field(
        default=False,
        title="Включить броуновское движение",
        description="Включить режим броуновского движения"
    )
    mode: Literal["single_large", "multi_track"] = Field(
        default="single_large",
        title="Режим",
        description="single_large: одна большая частица среди малых; multi_track: отслеживание нескольких частиц"
    )
    large_mass_multiplier: float = Field(
        default=10.0,
        ge=1.0,
        le=100.0,
        title="Множитель массы",
        description="Во сколько раз масса броуновской частицы больше обычной"
    )
    large_radius_multiplier: float = Field(
        default=3.0,
        ge=1.0,
        le=10.0,
        title="Множитель радиуса",
        description="Во сколько раз радиус броуновской частицы больше обычной"
    )
    track_count: int = Field(
        default=5,
        ge=1,
        le=20,
        title="Количество отслеживаемых",
        description="Количество частиц для отслеживания MSD в режиме multi_track"
    )


class ExperimentConfig(ConfigSection):
    """Параметры экспериментальных режимов."""
    
    isolated_system: bool = Field(
        default=False,
        title="Изолированная система",
        description="Запретить изменение энергии (нагрев/охлаждение) и объема (расширение/сжатие)"
    )
    corner_start: bool = Field(
        default=False,
        title="Старт из угла",
        description="Начальное расположение частиц в углу (для демонстрации 2-го закона)"
    )
