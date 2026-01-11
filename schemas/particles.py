"""
Схемы для параметров частиц и молекул.
"""
from pydantic import Field
from typing import Literal
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


class MoleculeConfig(ConfigSection):
    """
    Конфигурация внутренней структуры молекул.
    
    Влияет на степени свободы и распределение энергии:
    - Моноатомные (Ar, He): только поступательные DoF (2 в 2D)
    - Двухатомные линейные (H₂, N₂, O₂): поступательные + 1 вращательный DoF (3 в 2D)
    - Многоатомные линейные (CO₂): поступательные + 1 вращательный DoF (3 в 2D)
    - Многоатомные нелинейные (H₂O, CH₄): поступательные + 1 вращательный DoF (3 в 2D)
    
    В 2D симуляции вращение происходит только вокруг оси, перпендикулярной плоскости.
    """
    
    molecule_type: Literal["monatomic", "diatomic", "polyatomic"] = Field(
        default="monatomic",
        title="Тип молекулы",
        description="monatomic: одноатомные (Ar, He); diatomic: двухатомные (H₂, N₂); polyatomic: многоатомные (H₂O, CO₂)"
    )
    
    geometry: Literal["linear", "nonlinear"] = Field(
        default="linear",
        title="Геометрия",
        description="linear: линейная (CO₂); nonlinear: нелинейная (H₂O). Влияет на момент инерции"
    )
    
    atom_count: int = Field(
        default=1,
        ge=1,
        le=10,
        title="Число атомов",
        description="Количество атомов в молекуле (1-10)"
    )
    
    bond_length: float = Field(
        default=0.5,
        ge=0.1,
        le=2.0,
        title="Длина связи",
        description="Расстояние между атомами (относительно радиуса частицы)"
    )
    
    moment_of_inertia: float = Field(
        default=1.0,
        ge=0.1,
        le=100.0,
        title="Момент инерции",
        description="Момент инерции молекулы (условные единицы). Больше = медленнее вращение"
    )
    
    enable_rotation: bool = Field(
        default=False,
        title="Включить вращение",
        description="Моделировать вращательные степени свободы"
    )
    
    show_orientation: bool = Field(
        default=True,
        title="Показывать ориентацию",
        description="Отображать линию-индикатор ориентации молекулы"
    )
    
    initial_angular_velocity: float = Field(
        default=0.0,
        ge=0.0,
        le=10.0,
        title="Начальная угл. скорость",
        description="Начальная угловая скорость (0 = случайная из распределения)"
    )
    
    # Предустановки молекул
    preset: Literal["custom", "argon", "hydrogen", "nitrogen", "oxygen", "co2", "water", "methane"] = Field(
        default="custom",
        title="Пресет молекулы",
        description="Выбор предустановленной молекулы с корректными параметрами"
    )
    
    def get_degrees_of_freedom(self) -> int:
        """
        Возвращает число степеней свободы молекулы в 2D.
        
        - Моноатомные: 2 (только поступательные x, y)
        - Двухатомные и многоатомные: 3 (поступательные + 1 вращательный)
        
        В 2D вращение возможно только вокруг оси z (перпендикулярной плоскости).
        """
        if self.molecule_type == "monatomic" or not self.enable_rotation:
            return 2  # Только поступательные степени свободы
        else:
            return 3  # Поступательные + 1 вращательная
    
    def get_rotational_dof(self) -> int:
        """Возвращает число вращательных степеней свободы в 2D."""
        if self.molecule_type == "monatomic" or not self.enable_rotation:
            return 0
        return 1  # В 2D только одна ось вращения
    
    def apply_preset(self) -> None:
        """
        Применить параметры предустановленной молекулы.
        Вызывается при изменении preset.
        """
        presets = {
            "argon": {
                "molecule_type": "monatomic",
                "geometry": "linear",
                "atom_count": 1,
                "moment_of_inertia": 1.0,
                "enable_rotation": False,
                "bond_length": 0.5
            },
            "hydrogen": {
                "molecule_type": "diatomic",
                "geometry": "linear",
                "atom_count": 2,
                "moment_of_inertia": 0.5,  # Лёгкая молекула
                "enable_rotation": True,
                "bond_length": 0.4
            },
            "nitrogen": {
                "molecule_type": "diatomic",
                "geometry": "linear",
                "atom_count": 2,
                "moment_of_inertia": 2.0,
                "enable_rotation": True,
                "bond_length": 0.5
            },
            "oxygen": {
                "molecule_type": "diatomic",
                "geometry": "linear",
                "atom_count": 2,
                "moment_of_inertia": 2.5,
                "enable_rotation": True,
                "bond_length": 0.5
            },
            "co2": {
                "molecule_type": "polyatomic",
                "geometry": "linear",
                "atom_count": 3,
                "moment_of_inertia": 7.0,  # Тяжёлая линейная молекула
                "enable_rotation": True,
                "bond_length": 0.6
            },
            "water": {
                "molecule_type": "polyatomic",
                "geometry": "nonlinear",
                "atom_count": 3,
                "moment_of_inertia": 1.5,  # Угловая молекула
                "enable_rotation": True,
                "bond_length": 0.4
            },
            "methane": {
                "molecule_type": "polyatomic",
                "geometry": "nonlinear",
                "atom_count": 5,
                "moment_of_inertia": 3.0,
                "enable_rotation": True,
                "bond_length": 0.5
            }
        }
        
        if self.preset in presets:
            for key, value in presets[self.preset].items():
                setattr(self, key, value)
