"""
Схемы для физических параметров симуляции.
"""
from pydantic import Field
from typing import Literal
from .base import ConfigSection


class LennardJonesConfig(ConfigSection):
    """
    Параметры потенциала Леннард-Джонса.
    
    U(r) = 4ε[(σ/r)¹² - (σ/r)⁶]
    
    Где:
    - ε (epsilon) — глубина потенциальной ямы
    - σ (sigma) — расстояние, на котором потенциал равен нулю
    - r — расстояние между частицами
    """
    
    enabled: bool = Field(
        default=False,
        title="Включить потенциал Леннард-Джонса",
        description="Учитывать межмолекулярное взаимодействие по потенциалу Леннард-Джонса"
    )
    epsilon: float = Field(
        default=1.0,
        ge=0.01,
        le=100.0,
        title="ε (глубина ямы)",
        description="Глубина потенциальной ямы, определяет силу притяжения"
    )
    sigma: float = Field(
        default=10.0,
        ge=1.0,
        le=50.0,
        title="σ (характерный размер)",
        description="Расстояние, на котором потенциал равен нулю (примерно диаметр частицы)"
    )
    cutoff_multiplier: float = Field(
        default=2.5,
        ge=1.5,
        le=5.0,
        title="Радиус обрезки (в σ)",
        description="Множитель σ для радиуса обрезки потенциала (стандартно 2.5σ)"
    )


class MorseConfig(ConfigSection):
    """
    Параметры потенциала Морзе.
    
    U(r) = D_e * [1 - exp(-a*(r - r_e))]²
    
    Где:
    - D_e — глубина потенциальной ямы (энергия диссоциации)
    - a — параметр ширины ямы
    - r_e — равновесное расстояние между частицами
    """
    
    enabled: bool = Field(
        default=False,
        title="Включить потенциал Морзе",
        description="Учитывать межмолекулярное взаимодействие по потенциалу Морзе"
    )
    D_e: float = Field(
        default=1.0,
        ge=0.01,
        le=100.0,
        title="D_e (глубина ямы)",
        description="Энергия диссоциации связи / глубина потенциальной ямы"
    )
    a: float = Field(
        default=0.5,
        ge=0.01,
        le=5.0,
        title="a (ширина ямы)",
        description="Параметр, определяющий ширину потенциальной ямы"
    )
    r_e: float = Field(
        default=15.0,
        ge=1.0,
        le=50.0,
        title="r_e (равновесное расстояние)",
        description="Равновесное расстояние между частицами"
    )
    cutoff_multiplier: float = Field(
        default=3.0,
        ge=2.0,
        le=6.0,
        title="Радиус обрезки (в r_e)",
        description="Множитель r_e для радиуса обрезки потенциала"
    )


class DLVOConfig(ConfigSection):
    """
    Параметры потенциала ДЛФО (Дерягина-Ландау-Фервея-Овербека).
    
    U(r) = U_vdW(r) + U_elec(r)
    
    U_vdW = -A_H/(12) * [2R²/(r² - 4R²) + 2R²/r² + ln((r² - 4R²)/r²)]
    U_elec = 2πεε₀Rψ₀²exp(-κ(r - 2R))
    
    Где:
    - A_H — константа Гамакера (Ван-дер-Ваальсово притяжение)
    - R — радиус частицы
    - ψ₀ — поверхностный потенциал
    - κ — обратная дебаевская длина
    - ε — диэлектрическая проницаемость среды
    """
    
    enabled: bool = Field(
        default=False,
        title="Включить потенциал ДЛФО",
        description="Учитывать коллоидное взаимодействие (для заряженных частиц в растворах)"
    )
    hamaker_constant: float = Field(
        default=1.0,
        ge=0.001,
        le=100.0,
        title="A_H (константа Гамакера)",
        description="Константа Гамакера, определяющая силу Ван-дер-Ваальсова притяжения"
    )
    surface_potential: float = Field(
        default=0.025,
        ge=0.001,
        le=1.0,
        title="ψ₀ (поверхностный потенциал)",
        description="Поверхностный потенциал частиц (в В)"
    )
    debye_length: float = Field(
        default=10.0,
        ge=1.0,
        le=100.0,
        title="1/κ (дебаевская длина)",
        description="Дебаевская длина экранирования (в условных единицах)"
    )
    dielectric_constant: float = Field(
        default=80.0,
        ge=1.0,
        le=200.0,
        title="ε (диэлектрическая проницаемость)",
        description="Относительная диэлектрическая проницаемость среды (для воды ~80)"
    )
    cutoff_distance: float = Field(
        default=50.0,
        ge=10.0,
        le=200.0,
        title="Радиус обрезки",
        description="Максимальное расстояние взаимодействия"
    )


class InteractionPotentialsConfig(ConfigSection):
    """Общая конфигурация потенциалов взаимодействия."""
    
    lennard_jones: LennardJonesConfig = Field(
        default_factory=LennardJonesConfig,
        title="Потенциал Леннард-Джонса"
    )
    morse: MorseConfig = Field(
        default_factory=MorseConfig,
        title="Потенциал Морзе"
    )
    dlvo: DLVOConfig = Field(
        default_factory=DLVOConfig,
        title="Потенциал ДЛФО"
    )
    
    max_force: float = Field(
        default=10.0,
        ge=0.1,
        le=100.0,
        title="Максимальная сила",
        description="Ограничение максимальной силы для стабильности симуляции"
    )
    
    softening_distance: float = Field(
        default=0.1,
        ge=0.01,
        le=1.0,
        title="Смягчение на близких расстояниях",
        description="Минимальное расстояние для избежания сингулярностей"
    )


class GravityConfig(ConfigSection):
    """Параметры гравитационного поля."""
    
    enabled: bool = Field(
        default=False,
        title="Включить гравитацию",
        description="Включить внешнее гравитационное поле (направлено вниз)"
    )
    g: float = Field(
        default=9.8,
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
        default=10.0,
        ge=2.0,
        le=50.0,
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
