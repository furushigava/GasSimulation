"""
Модель частицы газа.
"""
import math
import random
from collections import deque
from PyQt5.QtGui import QColor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas import AppConfig


class GasParticle:
    """Класс, представляющий частицу газа."""
    
    def __init__(self, x, y, radius=5, mass=1, speed=5, config: 'AppConfig' = None):
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = mass
        self.v = speed
        self.a = random.uniform(0, 2 * math.pi)
        
        # Получаем параметры из конфигурации или используем дефолтные
        if config is not None:
            default_color = config.particle_colors.default_color
            trajectory_length = config.particles.trajectory_max_length
        else:
            default_color = (255, 0, 0)  # Красный по умолчанию
            trajectory_length = 100
        
        self.color = QColor(*default_color)
        self.trajectory = deque(maxlen=trajectory_length)  # Для траектории
        self.trajectory.append((x, y))
