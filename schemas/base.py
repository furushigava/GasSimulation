"""
Базовые классы и утилиты для Pydantic-схем конфигурации.
"""
from pydantic import BaseModel, ConfigDict
from typing import Any, Dict, Tuple
import json
from pathlib import Path


class ConfigSection(BaseModel):
    """
    Базовый класс для секций конфигурации.
    Предоставляет общие методы для сериализации и десериализации.
    """
    model_config = ConfigDict(
        validate_assignment=True,  # Валидация при присваивании
        extra='forbid',  # Запрет дополнительных полей
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь."""
        return self.model_dump()
    
    @classmethod
    def get_field_info(cls) -> Dict[str, Dict[str, Any]]:
        """
        Получить информацию о полях для генерации UI.
        Возвращает словарь с метаданными полей.
        """
        fields_info = {}
        for field_name, field_info in cls.model_fields.items():
            metadata = {
                'type': field_info.annotation,
                'default': field_info.default,
                'title': field_info.title or field_name,
                'description': field_info.description or '',
            }
            
            # Извлекаем constraints из metadata
            if field_info.metadata:
                for constraint in field_info.metadata:
                    if hasattr(constraint, 'ge'):
                        metadata['ge'] = constraint.ge
                    if hasattr(constraint, 'le'):
                        metadata['le'] = constraint.le
                    if hasattr(constraint, 'gt'):
                        metadata['gt'] = constraint.gt
                    if hasattr(constraint, 'lt'):
                        metadata['lt'] = constraint.lt
            
            fields_info[field_name] = metadata
        
        return fields_info


class RGBColor(BaseModel):
    """RGB цвет как кортеж (r, g, b)."""
    r: int
    g: int
    b: int
    
    model_config = ConfigDict(
        validate_assignment=True,
    )
    
    @classmethod
    def from_tuple(cls, rgb: Tuple[int, int, int]) -> 'RGBColor':
        return cls(r=rgb[0], g=rgb[1], b=rgb[2])
    
    def to_tuple(self) -> Tuple[int, int, int]:
        return (self.r, self.g, self.b)
    
    def to_hex(self) -> str:
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"
    
    @classmethod
    def from_hex(cls, hex_color: str) -> 'RGBColor':
        hex_color = hex_color.lstrip('#')
        return cls(
            r=int(hex_color[0:2], 16),
            g=int(hex_color[2:4], 16),
            b=int(hex_color[4:6], 16)
        )


def save_config_to_file(config: BaseModel, filepath: Path) -> None:
    """Сохранить конфигурацию в JSON файл."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(config.model_dump(), f, indent=2, ensure_ascii=False)


def load_config_from_file(config_class: type, filepath: Path) -> BaseModel:
    """Загрузить конфигурацию из JSON файла."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return config_class(**data)
