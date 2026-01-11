"""
Pydantic-схемы конфигурации для симуляции газа.

Структура:
- AppConfig - главная конфигурация, агрегирует все секции
- Каждая секция в отдельном модуле для чистоты кода
"""
from pydantic import Field
from pathlib import Path
from typing import Optional

from .base import ConfigSection, save_config_to_file, load_config_from_file
from .simulation import SimulationWindowConfig, TimeConfig, StateChangeConfig, CollisionConfig
from .particles import ParticlesConfig, MoleculeConfig
from .physics import (
    GravityConfig, 
    BrownianConfig, 
    ExperimentConfig,
    LennardJonesConfig,
    MorseConfig,
    DLVOConfig,
    InteractionPotentialsConfig
)
from .ui import MainWindowConfig, GraphWindowConfig, LoggingConfig
from .graphs import (
    GraphUpdateConfig, 
    StatisticalConfig, 
    SpectralConfig, 
    FractalConfig, 
    CorrelationConfig
)
from .colors import (
    ParticleColorsConfig,
    BorderColorsConfig,
    UIColorsConfig,
    ModeColorsConfig,
    ModeIndicatorColorsConfig
)


class AppConfig(ConfigSection):
    """
    Главная конфигурация приложения.
    Агрегирует все секции конфигурации.
    """
    
    # Симуляция
    simulation_window: SimulationWindowConfig = Field(
        default_factory=SimulationWindowConfig,
        title="Окно симуляции"
    )
    time: TimeConfig = Field(
        default_factory=TimeConfig,
        title="Время"
    )
    state_change: StateChangeConfig = Field(
        default_factory=StateChangeConfig,
        title="Изменение состояния"
    )
    collision: CollisionConfig = Field(
        default_factory=CollisionConfig,
        title="Столкновения"
    )
    
    # Физика
    gravity: GravityConfig = Field(
        default_factory=GravityConfig,
        title="Гравитация"
    )
    brownian: BrownianConfig = Field(
        default_factory=BrownianConfig,
        title="Броуновское движение"
    )
    experiment: ExperimentConfig = Field(
        default_factory=ExperimentConfig,
        title="Экспериментальные режимы"
    )
    
    # Потенциалы взаимодействия
    interaction_potentials: InteractionPotentialsConfig = Field(
        default_factory=InteractionPotentialsConfig,
        title="Потенциалы взаимодействия",
        description="Леннард-Джонс, Морзе, ДЛФО"
    )
    
    # Частицы
    particles: ParticlesConfig = Field(
        default_factory=ParticlesConfig,
        title="Частицы"
    )
    
    # Молекулярная структура
    molecule: MoleculeConfig = Field(
        default_factory=MoleculeConfig,
        title="Структура молекулы"
    )
    
    # UI
    main_window: MainWindowConfig = Field(
        default_factory=MainWindowConfig,
        title="Главное окно"
    )
    graph_window: GraphWindowConfig = Field(
        default_factory=GraphWindowConfig,
        title="Окно графиков"
    )
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig,
        title="Логирование"
    )
    
    # Графики
    graph_update: GraphUpdateConfig = Field(
        default_factory=GraphUpdateConfig,
        title="Обновление графиков"
    )
    statistical: StatisticalConfig = Field(
        default_factory=StatisticalConfig,
        title="Статистика"
    )
    spectral: SpectralConfig = Field(
        default_factory=SpectralConfig,
        title="Спектральный анализ"
    )
    fractal: FractalConfig = Field(
        default_factory=FractalConfig,
        title="Фрактальный анализ"
    )
    correlation: CorrelationConfig = Field(
        default_factory=CorrelationConfig,
        title="Корреляции"
    )
    
    # Цвета
    particle_colors: ParticleColorsConfig = Field(
        default_factory=ParticleColorsConfig,
        title="Цвета частиц"
    )
    border_colors: BorderColorsConfig = Field(
        default_factory=BorderColorsConfig,
        title="Цвета границ"
    )
    ui_colors: UIColorsConfig = Field(
        default_factory=UIColorsConfig,
        title="Цвета UI"
    )
    mode_colors: ModeColorsConfig = Field(
        default_factory=ModeColorsConfig,
        title="Цвета режимов"
    )
    mode_indicator_colors: ModeIndicatorColorsConfig = Field(
        default_factory=ModeIndicatorColorsConfig,
        title="Цвета индикаторов"
    )
    
    def save(self, filepath: Optional[Path] = None) -> None:
        """Сохранить конфигурацию в файл."""
        if filepath is None:
            filepath = Path(__file__).parent.parent / "saved_config.json"
        save_config_to_file(self, filepath)
    
    @classmethod
    def load(cls, filepath: Optional[Path] = None) -> 'AppConfig':
        """Загрузить конфигурацию из файла."""
        if filepath is None:
            filepath = Path(__file__).parent.parent / "saved_config.json"
        if not filepath.exists():
            return cls()  # Возвращаем дефолтную конфигурацию
        return load_config_from_file(cls, filepath)
    
    @classmethod
    def get_default(cls) -> 'AppConfig':
        """Получить конфигурацию с дефолтными значениями."""
        return cls()


# Экспортируем все классы
__all__ = [
    'AppConfig',
    'ConfigSection',
    'SimulationWindowConfig',
    'TimeConfig', 
    'StateChangeConfig',
    'CollisionConfig',
    'GravityConfig',
    'BrownianConfig',
    'ExperimentConfig',
    'LennardJonesConfig',
    'MorseConfig',
    'DLVOConfig',
    'InteractionPotentialsConfig',
    'ParticlesConfig',
    'MoleculeConfig',
    'MainWindowConfig',
    'GraphWindowConfig',
    'LoggingConfig',
    'GraphUpdateConfig',
    'StatisticalConfig',
    'SpectralConfig',
    'FractalConfig',
    'CorrelationConfig',
    'ParticleColorsConfig',
    'BorderColorsConfig',
    'UIColorsConfig',
    'ModeColorsConfig',
    'ModeIndicatorColorsConfig',
    'save_config_to_file',
    'load_config_from_file',
]
