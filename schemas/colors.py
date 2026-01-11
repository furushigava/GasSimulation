"""
Схемы для цветовых настроек.
"""
from pydantic import Field, field_validator
from typing import Dict, Tuple
from .base import ConfigSection


class ParticleColorsConfig(ConfigSection):
    """Цвета частиц."""
    
    default_color: Tuple[int, int, int] = Field(
        default=(255, 0, 0),
        title="Цвет по умолчанию",
        description="RGB цвет обычных частиц"
    )
    first_particle_color: Tuple[int, int, int] = Field(
        default=(0, 255, 0),
        title="Цвет первой частицы",
        description="RGB цвет первой (отслеживаемой) частицы"
    )
    trajectory_color: Tuple[int, int, int] = Field(
        default=(255, 255, 0),
        title="Цвет траектории",
        description="RGB цвет линии траектории"
    )
    
    @field_validator('default_color', 'first_particle_color', 'trajectory_color', mode='before')
    @classmethod
    def validate_rgb(cls, v):
        if isinstance(v, (list, tuple)) and len(v) == 3:
            for val in v:
                if not (0 <= val <= 255):
                    raise ValueError(f"RGB значение должно быть от 0 до 255, получено: {val}")
            return tuple(v)
        raise ValueError(f"Ожидается RGB кортеж из 3 значений, получено: {v}")


class BorderColorsConfig(ConfigSection):
    """Цвета границ."""
    
    outer_color: Tuple[int, int, int] = Field(
        default=(0, 0, 255),
        title="Внешний цвет",
        description="RGB цвет внешней границы"
    )
    inner_color: Tuple[int, int, int] = Field(
        default=(255, 255, 255),
        title="Внутренний цвет",
        description="RGB цвет внутренней границы"
    )
    
    @field_validator('outer_color', 'inner_color', mode='before')
    @classmethod
    def validate_rgb(cls, v):
        if isinstance(v, (list, tuple)) and len(v) == 3:
            for val in v:
                if not (0 <= val <= 255):
                    raise ValueError(f"RGB значение должно быть от 0 до 255, получено: {val}")
            return tuple(v)
        raise ValueError(f"Ожидается RGB кортеж из 3 значений, получено: {v}")


class UIColorsConfig(ConfigSection):
    """Цвета UI элементов."""
    
    background_color: str = Field(
        default="black",
        title="Цвет фона",
        description="Цвет фона симуляции"
    )
    label_text_color: str = Field(
        default="#ffffff",
        title="Цвет текста",
        description="Цвет текста лейблов"
    )
    label_bg_color: str = Field(
        default="#2d2d2d",
        title="Цвет фона лейблов",
        description="Цвет фона лейблов"
    )
    group_text_color: str = Field(
        default="#e0e0e0",
        title="Цвет заголовков групп",
        description="Цвет текста заголовков групп"
    )


class ModeColorsConfig(ConfigSection):
    """Цвета индикаторов режима."""
    
    off: str = Field(default='#3d3d3d', title="Выключен")
    heat: str = Field(default='#5c2020', title="Нагрев")
    freeze: str = Field(default='#203d5c', title="Охлаждение")
    expansion: str = Field(default='#205c20', title="Расширение")
    compression: str = Field(default='#5c5c20', title="Сжатие")
    heat_expansion: str = Field(default='#5c4020', title="Нагрев+Расширение")
    heat_compression: str = Field(default='#5c3030', title="Нагрев+Сжатие")
    cool_expansion: str = Field(default='#205c5c', title="Охлаждение+Расширение")
    cool_compression: str = Field(default='#404060', title="Охлаждение+Сжатие")
    
    def to_dict_by_mode(self) -> Dict[str, str]:
        """Вернуть словарь mode -> color для UI."""
        return {
            'OFF': self.off,
            'heat': self.heat,
            'freeze': self.freeze,
            'expansion': self.expansion,
            'compression': self.compression,
            'heat_expansion': self.heat_expansion,
            'heat_compression': self.heat_compression,
            'cool_expansion': self.cool_expansion,
            'cool_compression': self.cool_compression
        }


class ModeIndicatorColorsConfig(ConfigSection):
    """Цвета индикаторов режима для графиков."""
    
    off: str = Field(default='gray', title="Выключен")
    heat: str = Field(default='red', title="Нагрев")
    freeze: str = Field(default='blue', title="Охлаждение")
    expansion: str = Field(default='green', title="Расширение")
    compression: str = Field(default='orange', title="Сжатие")
    heat_expansion: str = Field(default='#FF8800', title="Нагрев+Расширение")
    heat_compression: str = Field(default='#FF4400', title="Нагрев+Сжатие")
    cool_expansion: str = Field(default='#00CCCC', title="Охлаждение+Расширение")
    cool_compression: str = Field(default='#6666AA', title="Охлаждение+Сжатие")
    
    def to_dict_by_mode(self) -> Dict[str, str]:
        """Вернуть словарь mode -> color для графиков."""
        return {
            'OFF': self.off,
            'heat': self.heat,
            'freeze': self.freeze,
            'expansion': self.expansion,
            'compression': self.compression,
            'heat_expansion': self.heat_expansion,
            'heat_compression': self.heat_compression,
            'cool_expansion': self.cool_expansion,
            'cool_compression': self.cool_compression
        }
