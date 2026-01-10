"""
Виджет симуляции газа.
Содержит всю физику симуляции и визуализацию частиц.
"""
import math
import random
from statistics import mean
from collections import deque

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen
import numpy as np

from models import GasParticle
from config import (
    SIMULATION_WIDTH,
    SIMULATION_HEIGHT,
    PARTICLE_COUNT,
    PARTICLE_RADIUS,
    PARTICLE_MASS,
    PARTICLE_INITIAL_SPEED,
    TIME_STEP,
    TIME_CHECK_INTERVAL,
    EXPANSION_RATE,
    COMPRESSION_RATE,
    HEAT_RATE,
    FREEZE_RATE,
    FREEZE_MIN_COUNTER,
    COLLISION_DISTANCE_MULTIPLIER,
    COLLISION_OVERLAP_THRESHOLD,
    COLLISION_PREDICTION_STEP,
    LOG_BUFFER_SIZE,
    PARTICLE_COLOR_FIRST,
    BORDER_COLOR_OUTER,
    BORDER_COLOR_INNER,
    TRAJECTORY_COLOR,
    BACKGROUND_COLOR
)


class SimulationWidget(QWidget):
    """Виджет для визуализации и управления симуляцией газа."""
    
    update_signal = pyqtSignal(float, float, float, float, str)
    data_updated = pyqtSignal(dict)  # Для передачи данных в окно графиков
    
    def __init__(self, width=SIMULATION_WIDTH, height=SIMULATION_HEIGHT):
        super().__init__()
        self.width0 = width
        self.height0 = height
        self.width = width
        self.height = height
        self.setFixedSize(int(width * 1.5), height)
        
        self.nn = PARTICLE_COUNT  # количество частиц
        self.particles = []
        self.r1 = PARTICLE_RADIUS
        self.m1 = PARTICLE_MASS
        self.v_start = PARTICLE_INITIAL_SPEED
        
        self.mode = "OFF"
        self.running = True
        self.NOW_TIME = 0
        self.time_sleep = TIME_STEP
        self.time_check = TIME_CHECK_INTERVAL
        self.timer = 0
        self.counter = 0
        
        self.delta_px_left = 0
        self.delta_px_right = 0
        self.delta_py_up = 0
        self.delta_py_down = 0
        
        # Данные для графиков
        self.Energy_check = 0
        self.Pressure = []
        self.Temperature = []
        self.Volume = []
        self.Time_meas = []
        self.AvgVelocity = []
        self.KineticEnergy = []
        self.Density = []
        self.VelocityDistribution = []
        self.MeanFreePath = []
        self.CollisionRate = []
        
        self.collision_count = 0
        self.last_collision_time = 0
        
        self.log_buffer = deque(maxlen=LOG_BUFFER_SIZE)
        
        self.init_particles()
        
        # Таймер для обновления симуляции
        self.simulation_timer = QTimer()
        self.simulation_timer.timeout.connect(self.update_simulation)
        self.simulation_timer.start(int(self.time_sleep * 1000))
        
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")
        
    def init_particles(self):
        """Инициализация частиц"""
        self.particles = []
        for i in range(self.nn):
            x = random.uniform(self.r1, self.width - self.r1)
            y = random.uniform(self.r1, self.height - self.r1)
            particle = GasParticle(x, y, self.r1, self.m1, self.v_start)
            if i == 0:
                particle.color = QColor(*PARTICLE_COLOR_FIRST)  # Первая частица зеленая
            self.particles.append(particle)
    
    def paintEvent(self, event):
        """Отрисовка частиц и стенок"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Рисуем внешнюю границу
        painter.setPen(QPen(QColor(*BORDER_COLOR_OUTER), 5))
        painter.drawRect(0, 0, int(self.width0), int(self.height0))
        
        # Рисуем текущую границу сосуда
        painter.setPen(QPen(QColor(*BORDER_COLOR_INNER), 5))
        painter.drawRect(0, 0, int(self.width), int(self.height))
        
        # Рисуем частицы
        for particle in self.particles:
            painter.setBrush(particle.color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(
                int(particle.x - particle.radius),
                int(particle.y - particle.radius),
                particle.radius * 2,
                particle.radius * 2
            )
            
            # Рисуем траекторию для первых 5 частиц
            if particle == self.particles[0] and len(particle.trajectory) > 1:
                painter.setPen(QPen(QColor(*TRAJECTORY_COLOR), 1))
                for i in range(len(particle.trajectory) - 1):
                    x1, y1 = particle.trajectory[i]
                    x2, y2 = particle.trajectory[i + 1]
                    painter.drawLine(int(x1), int(y1), int(x2), int(y2))
    
    def calculate_mean_free_path(self):
        """Расчет средней длины свободного пробега"""
        if self.nn == 0 or self.width * self.height == 0:
            return 0
        
        particle_density = self.nn / (self.width * self.height)
        cross_section = math.pi * (2 * self.r1) ** 2
        
        if particle_density * cross_section == 0:
            return float('inf')
        
        return 1 / (math.sqrt(2) * particle_density * cross_section)
    
    def calculate_collision_rate(self):
        """Расчет частоты столкновений"""
        avg_velocity = mean([p.v for p in self.particles]) if self.particles else 0
        mean_free_path = self.calculate_mean_free_path()
        
        if mean_free_path == 0 or mean_free_path == float('inf'):
            return 0
        
        return avg_velocity / mean_free_path
    
    def update_simulation(self):
        """Основной цикл симуляции"""
        if not self.running:
            self.simulation_timer.stop()
            return
        
        self.NOW_TIME += self.time_sleep
        
        # Обновление позиций частиц
        for particle in self.particles:
            particle.x += particle.v * math.cos(particle.a)
            particle.y += particle.v * math.sin(particle.a)
            particle.trajectory.append((particle.x, particle.y))
        
        # Проверка столкновений со стенками
        for particle in self.particles:
            # Левая стенка
            if particle.x <= particle.radius and (particle.a > math.pi/2 or particle.a < -math.pi/2):
                particle.a = math.pi - particle.a
                self.delta_px_left += abs(2 * particle.mass * particle.v * math.cos(particle.a))
            
            # Правая стенка
            if particle.x >= self.width - particle.radius and (-math.pi/2 < particle.a < math.pi/2):
                particle.a = math.pi - particle.a
                self.delta_px_right += abs(2 * particle.mass * particle.v * math.cos(particle.a))
            
            # Верхняя стенка
            if particle.y <= particle.radius and (-math.pi < particle.a < 0):
                particle.a = -particle.a
                self.delta_py_up += abs(2 * particle.mass * particle.v * math.sin(particle.a))
            
            # Нижняя стенка
            if particle.y >= self.height - particle.radius and (0 < particle.a < math.pi):
                particle.a = -particle.a
                self.delta_py_down += abs(2 * particle.mass * particle.v * math.sin(particle.a))
            
            # Нормализация угла
            while particle.a > math.pi:
                particle.a -= 2 * math.pi
            while particle.a < -math.pi:
                particle.a += 2 * math.pi
        
        # Проверка столкновений между частицами
        collisions_this_frame = 0
        for i in range(len(self.particles)):
            for j in range(i + 1, len(self.particles)):
                p1 = self.particles[i]
                p2 = self.particles[j]
                
                if (abs(p1.x - p2.x) <= COLLISION_DISTANCE_MULTIPLIER * p1.radius and 
                    abs(p1.y - p2.y) <= COLLISION_DISTANCE_MULTIPLIER * p1.radius):
                    
                    dist = math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)
                    
                    if dist <= p1.radius * 2 + COLLISION_OVERLAP_THRESHOLD:
                        collisions_this_frame += 1
                        
                        # Рассчитываем новые положения
                        x1_new = p1.x + p1.v * math.cos(p1.a) * COLLISION_PREDICTION_STEP
                        y1_new = p1.y + p1.v * math.sin(p1.a) * COLLISION_PREDICTION_STEP
                        x2_new = p2.x + p2.v * math.cos(p2.a) * COLLISION_PREDICTION_STEP
                        y2_new = p2.y + p2.v * math.sin(p2.a) * COLLISION_PREDICTION_STEP
                        dist_new = math.sqrt((x1_new - x2_new)**2 + (y1_new - y2_new)**2)
                        
                        if dist > dist_new:
                            # Расчет столкновения
                            collision_angle = math.atan2(p2.y - p1.y, p2.x - p1.x)
                            
                            # Скорости в системе координат столкновения
                            velocity_angle1 = p1.a - collision_angle
                            velocity_angle2 = p2.a - collision_angle
                            
                            # Компоненты скоростей
                            normal_velocity1 = p1.v * math.cos(velocity_angle1)
                            normal_velocity2 = p2.v * math.cos(velocity_angle2)
                            
                            tangential_velocity1 = p1.v * math.sin(velocity_angle1)
                            tangential_velocity2 = p2.v * math.sin(velocity_angle2)
                            
                            # Обмен нормальными компонентами
                            normal_velocity1_new = (2 * p1.mass * p2.v * math.cos(velocity_angle2)) / (2 * p1.mass)
                            normal_velocity2_new = (2 * p1.mass * p1.v * math.cos(velocity_angle1)) / (2 * p1.mass)
                            
                            # Новые скорости
                            p1.v = math.sqrt(normal_velocity1_new**2 + tangential_velocity1**2)
                            p2.v = math.sqrt(normal_velocity2_new**2 + tangential_velocity2**2)
                            
                            # Новые углы
                            new_angle1 = math.atan2(tangential_velocity1, normal_velocity1_new)
                            new_angle2 = math.atan2(tangential_velocity2, normal_velocity2_new)
                            
                            p1.a = collision_angle + new_angle1
                            p2.a = collision_angle + new_angle2
                            
                            # Нормализация углов
                            while p1.a > math.pi:
                                p1.a -= 2 * math.pi
                            while p1.a < -math.pi:
                                p1.a += 2 * math.pi
                            while p2.a > math.pi:
                                p2.a -= 2 * math.pi
                            while p2.a < -math.pi:
                                p2.a += 2 * math.pi
        
        self.collision_count += collisions_this_frame
        
        # Изменение объема
        if self.mode == "expansion":
            self.width += EXPANSION_RATE
        elif self.mode == "compression":
            self.width -= COMPRESSION_RATE
        
        # Изменение температуры
        if self.mode == "heat":
            for particle in self.particles:
                particle.v += HEAT_RATE
        elif self.mode == "freeze" and self.counter >= FREEZE_MIN_COUNTER:
            for particle in self.particles:
                if particle.v - FREEZE_RATE > 0:
                    particle.v -= FREEZE_RATE
        
        # Расчет энергии системы
        self.Energy_check = 0
        velocities = []
        for particle in self.particles:
            self.Energy_check += particle.mass * (particle.v**2) / 2
            velocities.append(particle.v)
        
        # Логирование и обновление графиков
        self.counter += 1
        if self.time_check <= -self.timer + self.NOW_TIME:
            # Расчет среднего давления
            avg_pressure = ((self.delta_px_left + self.delta_px_right) / 
                          (self.time_check * self.height) + 
                          (self.delta_py_up + self.delta_py_down) / 
                          (self.time_check * self.width)) / 4
            
            volume = self.width * self.height - self.nn * math.pi * (self.r1**2)
            avg_velocity = mean(velocities) if velocities else 0
            density = self.nn / (self.width * self.height) if self.width * self.height > 0 else 0
            mean_free_path = self.calculate_mean_free_path()
            collision_rate = self.calculate_collision_rate()
            
            # Формирование строки лога
            log_entry = (f"{volume:.1f}       "
                        f"{self.Energy_check:.3f}         "
                        f"{avg_pressure:.3f}         "
                        f"{avg_velocity:.3f}        "
                        f"{self.NOW_TIME:.3f}     "
                        f"{self.mode}")
            
            self.log_buffer.append(log_entry)
            self.update_signal.emit(volume, self.Energy_check, avg_pressure, avg_velocity, log_entry)
            
            # Сохранение данных для графиков
            self.Pressure.append(avg_pressure)
            self.Temperature.append(self.Energy_check / 100)
            self.Volume.append(volume / 1000)
            self.Time_meas.append(self.NOW_TIME)
            self.AvgVelocity.append(avg_velocity)
            self.KineticEnergy.append(self.Energy_check)
            self.Density.append(density)
            self.VelocityDistribution.extend(velocities)
            self.MeanFreePath.append(mean_free_path)
            self.CollisionRate.append(collision_rate)
            
            # Отправка данных в окно графиков
            data_dict = {
                'time': self.Time_meas,
                'pressure': self.Pressure,
                'temperature': self.Temperature,
                'volume': self.Volume,
                'avg_velocity': self.AvgVelocity,
                'kinetic_energy': self.KineticEnergy,
                'density': self.Density,
                'velocities': velocities,
                'mean_free_path': self.MeanFreePath,
                'collision_rate': self.CollisionRate,
                'mode': self.mode,
                'collision_count': self.collision_count
            }
            self.data_updated.emit(data_dict)
            
            # Сброс счетчиков импульса
            self.delta_px_left = 0
            self.delta_px_right = 0
            self.delta_py_up = 0
            self.delta_py_down = 0
            
            self.timer = self.NOW_TIME
        
        self.update()
    
    def set_mode(self, mode):
        """Установка режима работы"""
        self.mode = mode
    
    def stop_simulation(self):
        """Остановка симуляции"""
        self.running = False
        self.simulation_timer.stop()
    
    def reset_simulation(self):
        """Сброс симуляции"""
        self.width = self.width0
        self.height = self.height0
        self.mode = "OFF"
        self.NOW_TIME = 0
        self.counter = 0
        self.Pressure = []
        self.Temperature = []
        self.Volume = []
        self.Time_meas = []
        self.AvgVelocity = []
        self.KineticEnergy = []
        self.Density = []
        self.VelocityDistribution = []
        self.MeanFreePath = []
        self.CollisionRate = []
        self.collision_count = 0
        self.init_particles()
        self.running = True
        if not self.simulation_timer.isActive():
            self.simulation_timer.start(int(self.time_sleep * 1000))
    
    def get_statistics(self):
        """Получение статистики"""
        velocities = [p.v for p in self.particles]
        return {
            'mean_velocity': mean(velocities) if velocities else 0,
            'std_velocity': np.std(velocities) if velocities else 0,
            'max_velocity': max(velocities) if velocities else 0,
            'min_velocity': min(velocities) if velocities else 0,
            'total_energy': self.Energy_check,
            'current_volume': self.width * self.height,
            'particle_count': self.nn,
            'current_pressure': self.Pressure[-1] if self.Pressure else 0
        }
