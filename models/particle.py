"""
Модель частицы газа с поддержкой молекулярной структуры.
"""
import math
import random
from collections import deque
from PyQt5.QtGui import QColor
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from schemas import AppConfig


class GasParticle:
    """
    Класс, представляющий частицу/молекулу газа.
    
    Поддерживает:
    - Поступательное движение (x, y, v, a)
    - Вращательное движение (theta, omega, I) для многоатомных молекул
    - Визуализацию ориентации молекулы
    """
    
    def __init__(self, x, y, radius=5, mass=1, speed=5, config: 'AppConfig' = None):
        # Поступательные степени свободы
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = mass
        self.v = speed  # Модуль скорости
        self.a = random.uniform(0, 2 * math.pi)  # Направление движения
        
        # Вращательные степени свободы (для многоатомных молекул)
        self.theta = random.uniform(0, 2 * math.pi)  # Ориентация молекулы
        self.omega = 0.0  # Угловая скорость (рад/с)
        self.I = 1.0  # Момент инерции
        
        # Параметры молекулярной структуры
        self.molecule_type = "monatomic"
        self.geometry = "linear"
        self.atom_count = 1
        self.bond_length = 0.5
        self.rotation_enabled = False
        self.show_orientation = True
        
        # Получаем параметры из конфигурации
        if config is not None:
            default_color = config.particle_colors.default_color
            trajectory_length = config.particles.trajectory_max_length
            
            # Загружаем параметры молекулы
            if hasattr(config, 'molecule'):
                mol = config.molecule
                self.molecule_type = mol.molecule_type
                self.geometry = mol.geometry
                self.atom_count = mol.atom_count
                self.bond_length = mol.bond_length
                self.I = mol.moment_of_inertia
                self.rotation_enabled = mol.enable_rotation
                self.show_orientation = mol.show_orientation
                
                # Инициализация угловой скорости
                if self.rotation_enabled and self.molecule_type != "monatomic":
                    if mol.initial_angular_velocity > 0:
                        # Случайное направление вращения
                        self.omega = mol.initial_angular_velocity * random.choice([-1, 1])
                    else:
                        # Случайная угловая скорость из теплового распределения
                        # При равновесии: <I*omega^2/2> = k_B*T/2 для 1 DoF
                        # Берём omega из нормального распределения с σ = sqrt(k_B*T/I)
                        # Используем скорость как меру температуры
                        sigma_omega = speed / math.sqrt(self.I) if self.I > 0 else speed
                        self.omega = random.gauss(0, sigma_omega)
        else:
            default_color = (255, 0, 0)  # Красный по умолчанию
            trajectory_length = 100
        
        self.color = QColor(*default_color)
        self.trajectory = deque(maxlen=trajectory_length)  # Для траектории
        self.trajectory.append((x, y))
    
    @property
    def vx(self) -> float:
        """Компонента скорости по X."""
        return self.v * math.cos(self.a)
    
    @property
    def vy(self) -> float:
        """Компонента скорости по Y."""
        return self.v * math.sin(self.a)
    
    def kinetic_energy(self) -> float:
        """Поступательная кинетическая энергия: E_trans = m*v²/2"""
        return 0.5 * self.mass * self.v ** 2
    
    def rotational_energy(self) -> float:
        """
        Вращательная кинетическая энергия: E_rot = I*ω²/2
        
        Возвращает 0 для моноатомных молекул или если вращение отключено.
        """
        if not self.rotation_enabled or self.molecule_type == "monatomic":
            return 0.0
        return 0.5 * self.I * self.omega ** 2
    
    def total_energy(self) -> float:
        """Полная кинетическая энергия: E = E_trans + E_rot"""
        return self.kinetic_energy() + self.rotational_energy()
    
    def angular_momentum(self) -> float:
        """Угловой момент: L = I*ω"""
        return self.I * self.omega
    
    def update_rotation(self, dt: float) -> None:
        """
        Обновление угла ориентации за шаг времени dt.
        theta += omega * dt
        """
        if self.rotation_enabled and self.molecule_type != "monatomic":
            self.theta += self.omega * dt
            # Нормализация угла в диапазон [-π, π]
            while self.theta > math.pi:
                self.theta -= 2 * math.pi
            while self.theta < -math.pi:
                self.theta += 2 * math.pi
    
    def get_atom_positions(self) -> list:
        """
        Возвращает позиции атомов в молекуле для визуализации.
        
        Returns:
            Список кортежей (x, y, radius) для каждого атома
        """
        if self.atom_count == 1:
            return [(self.x, self.y, self.radius)]
        
        positions = []
        bond_px = self.bond_length * self.radius  # Длина связи в пикселях
        
        if self.atom_count == 2:
            # Двухатомная молекула: два атома на линии
            dx = bond_px * math.cos(self.theta)
            dy = bond_px * math.sin(self.theta)
            atom_radius = self.radius * 0.6
            positions.append((self.x - dx, self.y - dy, atom_radius))
            positions.append((self.x + dx, self.y + dy, atom_radius))
            
        elif self.atom_count == 3:
            if self.geometry == "linear":
                # Линейная молекула (CO2): три атома на линии
                dx = bond_px * math.cos(self.theta)
                dy = bond_px * math.sin(self.theta)
                atom_radius = self.radius * 0.5
                positions.append((self.x - dx, self.y - dy, atom_radius))
                positions.append((self.x, self.y, atom_radius * 1.2))  # Центральный атом больше
                positions.append((self.x + dx, self.y + dy, atom_radius))
            else:
                # Нелинейная молекула (H2O): угол ~104.5°
                angle = math.radians(52.25)  # Половина угла HOH
                atom_radius = self.radius * 0.5
                # Центральный атом (O)
                positions.append((self.x, self.y, atom_radius * 1.2))
                # Боковые атомы (H)
                for sign in [-1, 1]:
                    ax = self.x + bond_px * math.cos(self.theta + sign * angle)
                    ay = self.y + bond_px * math.sin(self.theta + sign * angle)
                    positions.append((ax, ay, atom_radius * 0.8))
        else:
            # Многоатомная молекула: размещаем атомы по кругу
            atom_radius = self.radius * 0.4
            positions.append((self.x, self.y, atom_radius))  # Центральный атом
            for i in range(self.atom_count - 1):
                angle = self.theta + 2 * math.pi * i / (self.atom_count - 1)
                ax = self.x + bond_px * math.cos(angle)
                ay = self.y + bond_px * math.sin(angle)
                positions.append((ax, ay, atom_radius * 0.8))
        
        return positions
    
    def get_orientation_line(self) -> tuple:
        """
        Возвращает координаты линии-индикатора ориентации.
        
        Returns:
            ((x1, y1), (x2, y2)) - начало и конец линии
        """
        line_length = self.radius * 1.5
        dx = line_length * math.cos(self.theta)
        dy = line_length * math.sin(self.theta)
        return ((self.x - dx, self.y - dy), (self.x + dx, self.y + dy))
    
    def degrees_of_freedom(self) -> int:
        """
        Возвращает число активных степеней свободы.
        
        В 2D:
        - Моноатомные или без вращения: 2 (x, y)
        - С вращением: 3 (x, y, theta)
        """
        if self.rotation_enabled and self.molecule_type != "monatomic":
            return 3
        return 2
