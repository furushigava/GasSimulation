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
from schemas import AppConfig


class SimulationWidget(QWidget):
    """Виджет для визуализации и управления симуляцией газа."""
    
    update_signal = pyqtSignal(float, float, float, float, str)
    data_updated = pyqtSignal(dict)  # Для передачи данных в окно графиков
    
    def __init__(self, width=500, height=500, config: AppConfig = None):
        super().__init__()
        
        # Используем конфигурацию или создаем дефолтную
        self.config = config if config is not None else AppConfig.get_default()
        
        self.width0 = width
        self.height0 = height
        self.width = width
        self.height = height
        self.setFixedSize(int(width * 1.5), height)
        
        # Параметры из конфигурации
        self.nn = self.config.particles.count
        self.particles = []
        self.r1 = self.config.particles.radius
        self.m1 = self.config.particles.mass
        self.v_start = self.config.particles.initial_speed
        
        self.mode = "OFF"
        self.running = True
        self.NOW_TIME = 0
        self.time_sleep = self.config.time.time_step
        self.time_check = self.config.time.check_interval
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
        
        self.log_buffer = deque(maxlen=self.config.logging.buffer_size)
        
        # Данные для физических законов
        self.initial_energy = None  # Начальная энергия для 1-го закона
        self.Entropy = []  # Энтропия для 2-го закона
        self.positions_history = []  # История позиций для броуновского движения
        self.MSD = []  # Среднеквадратичное смещение
        self.brownian_trajectory = []  # Траектория броуновской частицы
        self.brownian_initial_pos = None  # Начальная позиция броуновской частицы
        self.time_averages = {}  # Временные средние для эргодической гипотезы
        self.ensemble_averages = {}  # Ансамблевые средние
        self.H_function = []  # H-функция Больцмана
        self.SpatialEntropy = []  # Пространственная энтропия
        
        # Данные для эргодической гипотезы
        self.particle_velocity_histories = {}  # История скоростей каждой частицы
        self.time_averages_history = []  # История временных средних (1-я частица)
        self.ensemble_averages_history = []  # История ансамблевых средних
        self.initial_velocities = []  # Начальные скорости для "забывания"
        self.initial_positions_saved = []  # Начальные позиции
        self.correlations_history = []  # История корреляций с начальным состоянием
        
        self.init_particles()
        
        # Таймер для обновления симуляции
        self.simulation_timer = QTimer()
        self.simulation_timer.timeout.connect(self.update_simulation)
        self.simulation_timer.start(int(self.time_sleep * 1000))
        
        self.setStyleSheet(f"background-color: {self.config.ui_colors.background_color};")
        
    def init_particles(self):
        """Инициализация частиц"""
        self.particles = []
        first_particle_color = self.config.particle_colors.first_particle_color
        
        # Проверяем режим старта из угла (для демонстрации 2-го закона)
        corner_start = getattr(self.config.experiment, 'corner_start', False)
        
        for i in range(self.nn):
            if corner_start:
                # Все частицы в левом верхнем углу
                max_corner = min(self.width, self.height) * 0.3
                x = random.uniform(self.r1, max_corner - self.r1)
                y = random.uniform(self.r1, max_corner - self.r1)
            else:
                x = random.uniform(self.r1, self.width - self.r1)
                y = random.uniform(self.r1, self.height - self.r1)
            
            particle = GasParticle(x, y, self.r1, self.m1, self.v_start, self.config)
            if i == 0:
                particle.color = QColor(*first_particle_color)  # Первая частица зеленая
                
                # Если включен режим броуновского движения и режим single_large
                if (hasattr(self.config, 'brownian') and 
                    self.config.brownian.enabled and 
                    self.config.brownian.mode == "single_large"):
                    # Делаем первую частицу большой и тяжёлой
                    particle.radius = int(self.r1 * self.config.brownian.large_radius_multiplier)
                    particle.mass = self.m1 * self.config.brownian.large_mass_multiplier
                    particle.v = self.v_start / 2  # Медленнее из-за массы
                    
            self.particles.append(particle)
        
        # Сохраняем начальную позицию броуновской частицы
        if self.particles:
            self.brownian_initial_pos = (self.particles[0].x, self.particles[0].y)
            self.brownian_trajectory = [(self.particles[0].x, self.particles[0].y)]
        
        # Сохраняем начальные скорости и позиции для эргодической гипотезы
        self.initial_velocities = [p.v for p in self.particles]
        self.initial_positions_saved = [(p.x, p.y) for p in self.particles]
        self.particle_velocity_histories = {i: [] for i in range(len(self.particles))}
        self.time_averages_history = []
        self.ensemble_averages_history = []
        self.correlations_history = []
        
        # Сохраняем начальную энергию для проверки 1-го закона
        self._calculate_and_save_initial_energy()
    
    def paintEvent(self, event):
        """Отрисовка частиц и стенок"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Получаем цвета из конфигурации
        border_outer = self.config.border_colors.outer_color
        border_inner = self.config.border_colors.inner_color
        trajectory_color = self.config.particle_colors.trajectory_color
        
        # Рисуем внешнюю границу
        painter.setPen(QPen(QColor(*border_outer), 5))
        painter.drawRect(0, 0, int(self.width0), int(self.height0))
        
        # Рисуем текущую границу сосуда
        painter.setPen(QPen(QColor(*border_inner), 5))
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
                painter.setPen(QPen(QColor(*trajectory_color), 1))
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
            # Обновляем скорость под действием гравитации (если включена)
            if hasattr(self.config, 'gravity') and self.config.gravity.enabled:
                g = self.config.gravity.g
                # Гравитация направлена вниз (увеличивает y в системе координат экрана)
                # v_y += g * dt
                vy = particle.v * math.sin(particle.a) + g * self.time_sleep
                vx = particle.v * math.cos(particle.a)
                particle.v = math.sqrt(vx**2 + vy**2)
                particle.a = math.atan2(vy, vx)
            
            particle.x += particle.v * math.cos(particle.a)
            particle.y += particle.v * math.sin(particle.a)
            particle.trajectory.append((particle.x, particle.y))
        
        # Сохраняем траекторию броуновской частицы
        if self.particles:
            self.brownian_trajectory.append((self.particles[0].x, self.particles[0].y))
            
            # Расчёт MSD
            if self.brownian_initial_pos is not None:
                x0, y0 = self.brownian_initial_pos
                x, y = self.particles[0].x, self.particles[0].y
                msd = (x - x0)**2 + (y - y0)**2
                self.MSD.append(msd)
        
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
                
                if (abs(p1.x - p2.x) <= self.config.collision.distance_multiplier * p1.radius and 
                    abs(p1.y - p2.y) <= self.config.collision.distance_multiplier * p1.radius):
                    
                    dist = math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)
                    
                    if dist <= p1.radius * 2 + self.config.collision.overlap_threshold:
                        collisions_this_frame += 1
                        
                        # Рассчитываем новые положения
                        prediction_step = self.config.collision.prediction_step
                        x1_new = p1.x + p1.v * math.cos(p1.a) * prediction_step
                        y1_new = p1.y + p1.v * math.sin(p1.a) * prediction_step
                        x2_new = p2.x + p2.v * math.cos(p2.a) * prediction_step
                        y2_new = p2.y + p2.v * math.sin(p2.a) * prediction_step
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
        
        # Проверяем изолированность системы
        is_isolated = getattr(self.config.experiment, 'isolated_system', False)
        
        # Изменение объема (только если система не изолирована)
        if not is_isolated:
            if self.mode == "expansion":
                self.width += self.config.state_change.expansion_rate
            elif self.mode == "compression":
                self.width -= self.config.state_change.compression_rate
            
            # Изменение температуры
            if self.mode == "heat":
                for particle in self.particles:
                    particle.v += self.config.state_change.heat_rate
            elif self.mode == "freeze" and self.counter >= self.config.state_change.freeze_min_counter:
                for particle in self.particles:
                    if particle.v - self.config.state_change.freeze_rate > 0:
                        particle.v -= self.config.state_change.freeze_rate
        
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
            
            # Позиции частиц для распределения Больцмана и энтропии
            positions = [(p.x, p.y) for p in self.particles]
            
            # Расчёт энтропии для 2-го закона
            velocity_entropy = self._calculate_velocity_entropy(velocities)
            if velocity_entropy is not None:
                self.Entropy.append(velocity_entropy)
            
            h_func = self._calculate_h_function(velocities)
            if h_func is not None:
                self.H_function.append(h_func)
            
            spatial_entropy = self._calculate_spatial_entropy(positions)
            if spatial_entropy is not None:
                self.SpatialEntropy.append(spatial_entropy)
            
            # Расчёт данных для эргодической гипотезы
            self._update_ergodic_data(velocities)
            
            # Отправка данных в окно графиков
            is_isolated = getattr(self.config.experiment, 'isolated_system', False)
            
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
                'collision_count': self.collision_count,
                # Новые данные для физических законов
                'initial_energy': self.initial_energy,
                'isolated_system': is_isolated,
                'positions': positions,
                'entropy': self.Entropy,
                'msd': self.MSD,
                'particle_mass': self.m1,
                # Данные для броуновского движения
                'brownian_trajectory': self.brownian_trajectory,
                'brownian_config': {
                    'enabled': getattr(self.config.brownian, 'enabled', False),
                    'mode': getattr(self.config.brownian, 'mode', 'single_large'),
                    'large_radius': int(self.r1 * getattr(self.config.brownian, 'large_radius_multiplier', 3.0)),
                    'large_mass': self.m1 * getattr(self.config.brownian, 'large_mass_multiplier', 10.0)
                },
                'particle_radius': self.r1,
                'time_step': self.time_check,
                # Данные для распределения Больцмана
                'gravity_config': {
                    'enabled': getattr(self.config.gravity, 'enabled', False),
                    'g': getattr(self.config.gravity, 'g', 0.1)
                },
                'container_height': self.height,
                'container_width': self.width,
                # Данные для энтропии (2-й закон)
                'h_function': self.H_function,
                'spatial_entropy': self.SpatialEntropy,
                'corner_start': getattr(self.config.experiment, 'corner_start', False),
                'n_particles': self.nn,
                # Данные для эргодической гипотезы
                'time_averages_history': self.time_averages_history,
                'ensemble_averages_history': self.ensemble_averages_history,
                'initial_velocities': self.initial_velocities,
                'initial_positions': self.initial_positions_saved,
                'correlations_history': self.correlations_history,
                'particle_velocity_histories': self.particle_velocity_histories
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
        # Проверяем изолированность системы
        is_isolated = getattr(self.config.experiment, 'isolated_system', False)
        
        if is_isolated and mode in ["heat", "freeze", "expansion", "compression"]:
            # В изолированной системе нельзя менять энергию и объем
            return
        
        self.mode = mode
    
    def _calculate_and_save_initial_energy(self):
        """Расчёт и сохранение начальной энергии системы."""
        self.initial_energy = sum(
            particle.mass * (particle.v ** 2) / 2 
            for particle in self.particles
        )
    
    def toggle_isolated_system(self, enabled: bool):
        """Переключить режим изолированной системы."""
        self.config.experiment.isolated_system = enabled
        if enabled:
            self.mode = "OFF"
            # Пересчитываем начальную энергию при включении режима
            self._calculate_and_save_initial_energy()
    
    def toggle_brownian_mode(self, enabled: bool):
        """Переключить режим броуновского движения."""
        self.config.brownian.enabled = enabled
        # Перезапускаем симуляцию для применения изменений
        self.reset_simulation()
    
    def toggle_gravity(self, enabled: bool):
        """Переключить гравитацию."""
        self.config.gravity.enabled = enabled
    
    def toggle_corner_start(self, enabled: bool):
        """Переключить режим старта из угла."""
        self.config.experiment.corner_start = enabled
        # Перезапускаем симуляцию для применения
        self.reset_simulation()
    
    def _calculate_velocity_entropy(self, velocities, n_bins=20):
        """Расчёт энтропии по распределению скоростей."""
        if len(velocities) < 10:
            return None
        
        velocities = np.array(velocities)
        hist, bin_edges = np.histogram(velocities, bins=n_bins, density=True)
        bin_width = bin_edges[1] - bin_edges[0]
        probs = hist * bin_width
        probs = probs[probs > 0]
        
        if len(probs) == 0:
            return None
        
        return -np.sum(probs * np.log(probs))
    
    def _calculate_h_function(self, velocities, n_bins=30):
        """Расчёт H-функции Больцмана."""
        if len(velocities) < 10:
            return None
        
        velocities = np.array(velocities)
        hist, bin_edges = np.histogram(velocities, bins=n_bins, density=True)
        bin_width = bin_edges[1] - bin_edges[0]
        
        mask = hist > 0
        if np.sum(mask) == 0:
            return None
        
        f = hist[mask]
        return np.sum(f * np.log(f)) * bin_width
    
    def _calculate_spatial_entropy(self, positions, n_bins_x=10, n_bins_y=10):
        """Расчёт пространственной энтропии."""
        if len(positions) < 10:
            return None
        
        x_coords = [p[0] for p in positions]
        y_coords = [p[1] for p in positions]
        
        hist, _, _ = np.histogram2d(x_coords, y_coords, 
                                     bins=[n_bins_x, n_bins_y],
                                     range=[[0, self.width], [0, self.height]])
        
        total = np.sum(hist)
        if total == 0:
            return None
        
        probs = hist.flatten() / total
        probs = probs[probs > 0]
        
        if len(probs) == 0:
            return None
        
        return -np.sum(probs * np.log(probs))
    
    def _update_ergodic_data(self, velocities):
        """Обновление данных для эргодической гипотезы."""
        if len(velocities) == 0 or len(self.particles) == 0:
            return
        
        # Сохраняем скорости каждой частицы
        for i, v in enumerate(velocities):
            if i in self.particle_velocity_histories:
                self.particle_velocity_histories[i].append(v)
        
        # Временное среднее для первой частицы
        if 0 in self.particle_velocity_histories and len(self.particle_velocity_histories[0]) > 0:
            time_avg = np.mean(self.particle_velocity_histories[0])
            self.time_averages_history.append(time_avg)
        
        # Ансамблевое среднее (среднее по всем частицам в данный момент)
        ensemble_avg = np.mean(velocities)
        self.ensemble_averages_history.append(ensemble_avg)
        
        # Корреляция текущих скоростей с начальными (для "забывания")
        if len(self.initial_velocities) == len(velocities) and len(velocities) >= 5:
            try:
                from scipy import stats
                corr, _ = stats.pearsonr(self.initial_velocities, velocities)
                self.correlations_history.append(corr)
            except Exception:
                self.correlations_history.append(None)
        else:
            self.correlations_history.append(None)
    
    def stop_simulation(self):
        """Остановка симуляции"""
        self.running = False
        self.simulation_timer.stop()
    
    def start_simulation(self):
        """Запуск симуляции"""
        self.running = True
        self.simulation_timer.start(int(self.time_sleep * 1000))
    
    def reset_simulation(self):
        """Сброс симуляции"""
        self.width = self.width0
        self.height = self.height0
        self.mode = "OFF"
        self.NOW_TIME = 0
        self.counter = 0
        self.timer = 0  # Сброс таймера для логирования
        self.delta_px_left = 0
        self.delta_px_right = 0
        self.delta_py_up = 0
        self.delta_py_down = 0
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
        self.Entropy = []
        self.MSD = []
        self.brownian_trajectory = []
        self.brownian_initial_pos = None
        self.H_function = []
        self.SpatialEntropy = []
        self.collision_count = 0
        self.initial_energy = None
        # Сброс данных эргодичности
        self.particle_velocity_histories = {}
        self.time_averages_history = []
        self.ensemble_averages_history = []
        self.initial_velocities = []
        self.initial_positions_saved = []
        self.correlations_history = []
        self.init_particles()
        self.running = True
        # Перезапускаем таймер с актуальным интервалом
        self.simulation_timer.stop()
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
    
    def apply_config(self, config: AppConfig):
        """
        Применить новую конфигурацию и перезапустить симуляцию.
        
        Args:
            config: Новая конфигурация приложения
        """
        # Остановить текущую симуляцию
        self.simulation_timer.stop()
        
        # Обновить конфигурацию
        self.config = config
        
        # Обновить размеры окна симуляции
        self.width0 = config.simulation_window.width
        self.height0 = config.simulation_window.height
        self.setFixedSize(int(self.width0 * 1.5), self.height0)
        
        # Обновить параметры частиц
        self.nn = config.particles.count
        self.r1 = config.particles.radius
        self.m1 = config.particles.mass
        self.v_start = config.particles.initial_speed
        
        # Обновить параметры времени
        self.time_sleep = config.time.time_step
        self.time_check = config.time.check_interval
        
        # Обновить буфер логов
        self.log_buffer = deque(maxlen=config.logging.buffer_size)
        
        # Обновить стиль
        self.setStyleSheet(f"background-color: {config.ui_colors.background_color};")
        
        # Полный сброс симуляции
        self.reset_simulation()
