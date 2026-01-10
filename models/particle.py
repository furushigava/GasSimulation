"""
Модель частицы газа.
"""
import math
import random
from collections import deque
from PyQt5.QtGui import QColor

from config import (
    PARTICLE_RADIUS,
    PARTICLE_MASS,
    PARTICLE_INITIAL_SPEED,
    TRAJECTORY_MAX_LENGTH,
    PARTICLE_COLOR_DEFAULT
)


class GasParticle:
    """Класс, представляющий частицу газа."""
    
    def __init__(self, x, y, radius=PARTICLE_RADIUS, mass=PARTICLE_MASS, speed=PARTICLE_INITIAL_SPEED):
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = mass
        self.v = speed
        self.a = random.uniform(0, 2 * math.pi)
        self.color = QColor(*PARTICLE_COLOR_DEFAULT)
        self.trajectory = deque(maxlen=TRAJECTORY_MAX_LENGTH)  # Для траектории
        self.trajectory.append((x, y))
