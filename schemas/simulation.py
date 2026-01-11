"""
Схемы для параметров симуляции.
"""
from pydantic import Field
from .base import ConfigSection


class SimulationWindowConfig(ConfigSection):
    """Параметры окна симуляции."""
    
    width: int = Field(
        default=500,
        ge=100,
        le=2000,
        title="Ширина",
        description="Ширина области симуляции в пикселях"
    )
    height: int = Field(
        default=500,
        ge=100,
        le=2000,
        title="Высота",
        description="Высота области симуляции в пикселях"
    )


class TimeConfig(ConfigSection):
    """Параметры времени симуляции."""
    
    time_step: float = Field(
        default=0.01,
        ge=0.001,
        le=0.1,
        title="Шаг времени",
        description="Шаг времени для обновления симуляции"
    )
    check_interval: float = Field(
        default=0.1,
        ge=0.01,
        le=1.0,
        title="Интервал проверки",
        description="Интервал для расчета статистики"
    )


class StateChangeConfig(ConfigSection):
    """Параметры изменения состояния."""
    
    expansion_rate: float = Field(
        default=0.1,
        ge=0.01,
        le=1.0,
        title="Скорость расширения",
        description="Скорость расширения контейнера"
    )
    compression_rate: float = Field(
        default=0.1,
        ge=0.01,
        le=1.0,
        title="Скорость сжатия",
        description="Скорость сжатия контейнера"
    )
    heat_rate: float = Field(
        default=0.05,
        ge=0.01,
        le=0.5,
        title="Скорость нагрева",
        description="Прирост скорости частиц при нагреве"
    )
    freeze_rate: float = Field(
        default=0.05,
        ge=0.01,
        le=0.5,
        title="Скорость охлаждения",
        description="Уменьшение скорости частиц при охлаждении"
    )
    freeze_min_counter: int = Field(
        default=50,
        ge=1,
        le=500,
        title="Мин. итераций до охлаждения",
        description="Минимальное количество итераций перед охлаждением"
    )


class CollisionConfig(ConfigSection):
    """Параметры столкновений."""
    
    distance_multiplier: float = Field(
        default=2.5,
        ge=1.0,
        le=5.0,
        title="Множитель расстояния",
        description="Множитель для проверки близости частиц"
    )
    overlap_threshold: float = Field(
        default=0.1,
        ge=0.01,
        le=1.0,
        title="Порог перекрытия",
        description="Пороговое значение для перекрытия частиц"
    )
    prediction_step: float = Field(
        default=0.01,
        ge=0.001,
        le=0.1,
        title="Шаг предсказания",
        description="Шаг для предсказания столкновения"
    )
