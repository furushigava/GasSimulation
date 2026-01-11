"""
Главное окно приложения симуляции газа.
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                             QGroupBox, QGridLayout, QMenuBar, QMenu, QAction)
from PyQt5.QtGui import QFont

from simulation import SimulationWidget
from graphs import GraphWindow
from schemas import AppConfig
from ui.config_window import ConfigWindow


class MainWindow(QMainWindow):
    """Главное окно приложения симуляции газа."""
    
    def __init__(self, config: AppConfig = None):
        super().__init__()
        
        # Инициализируем конфигурацию (по умолчанию - дефолтные значения)
        self.config = config if config is not None else AppConfig.get_default()
        
        self.setWindowTitle("GAS Simulation - PyQt5 Version")
        self.setGeometry(
            100, 100, 
            self.config.main_window.width, 
            self.config.main_window.height
        )
        
        # Создаем меню
        self._create_menu()
        
        # Центральный виджет и основной layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Получаем цвета из конфигурации
        label_bg_color = self.config.ui_colors.label_bg_color
        label_text_color = self.config.ui_colors.label_text_color
        group_text_color = self.config.ui_colors.group_text_color
        
        # 1. Панель параметров (сверху)
        params_group = QGroupBox("Параметры симуляции")
        params_layout = QGridLayout()
        
        # Кнопки управления
        self.btn_heat = QPushButton("Нагрев (Shift)")
        self.btn_freeze = QPushButton("Охлаждение (Alt)")
        self.btn_expansion = QPushButton("Расширение (E)")
        self.btn_compression = QPushButton("Сжатие (C)")
        self.btn_off = QPushButton("Стоп процесс (Ctrl)")
        self.btn_stop = QPushButton("Остановить симуляцию (Esc)")
        self.btn_start = QPushButton("Запустить симуляцию")
        self.btn_reset = QPushButton("Сбросить")
        self.btn_graphs = QPushButton("Показать графики")
        self.btn_statistics = QPushButton("Статистика")
        self.btn_settings = QPushButton("Настройки")
        self.btn_exit = QPushButton("Выход")
        
        # Кнопки экспериментальных режимов
        self.btn_isolated = QPushButton("Изолированная система")
        self.btn_isolated.setCheckable(True)
        self.btn_isolated.setChecked(self.config.experiment.isolated_system)
        
        self.btn_brownian = QPushButton("Броуновское движение")
        self.btn_brownian.setCheckable(True)
        self.btn_brownian.setChecked(self.config.brownian.enabled)
        
        self.btn_gravity = QPushButton("Гравитация")
        self.btn_gravity.setCheckable(True)
        self.btn_gravity.setChecked(self.config.gravity.enabled)
        
        self.btn_corner_start = QPushButton("Старт из угла")
        self.btn_corner_start.setCheckable(True)
        self.btn_corner_start.setChecked(self.config.experiment.corner_start)
        
        # Настройка кнопок - размещаем по 4 кнопки в ряд
        buttons = [
            self.btn_heat, self.btn_freeze, self.btn_expansion, self.btn_compression,
            self.btn_off, self.btn_stop, self.btn_start, self.btn_reset,
            self.btn_statistics, self.btn_graphs, self.btn_settings, self.btn_exit,
            self.btn_isolated, self.btn_brownian, self.btn_gravity, self.btn_corner_start
        ]
        
        for i, btn in enumerate(buttons):
            btn.setMinimumHeight(40)
            btn.setStyleSheet("font-weight: bold;")
            row = i // 4
            col = i % 4
            params_layout.addWidget(btn, row, col)
        
        # Параметры - добавляем в строку 4 (после 4 рядов кнопок: 0, 1, 2, 3)
        stats_layout = QHBoxLayout()
        
        self.lbl_particles = QLabel(f"Частиц: {self.config.particles.count}")
        self.lbl_mode = QLabel("Режим: OFF")
        self.lbl_energy = QLabel("Энергия: 0.00")
        self.lbl_pressure = QLabel("Давление: 0.00")
        self.lbl_volume = QLabel("Объем: 0.00")
        self.lbl_velocity = QLabel("Ср.скорость: 0.00")
        
        for lbl in [self.lbl_particles, self.lbl_mode, self.lbl_energy, 
                   self.lbl_pressure, self.lbl_volume, self.lbl_velocity]:
            lbl.setStyleSheet(f"background-color: {label_bg_color}; color: {label_text_color}; padding: 5px; border-radius: 3px;")
            stats_layout.addWidget(lbl)
        
        # Строка 4 - после кнопок в строках 0, 1, 2, 3
        params_layout.addLayout(stats_layout, 4, 0, 1, 4)
        
        params_group.setLayout(params_layout)
        params_group.setStyleSheet(f"QGroupBox {{ color: {group_text_color}; font-weight: bold; }}")
        main_layout.addWidget(params_group)
        
        # 2. Нижняя часть: логи слева, демонстрация справа
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        
        # Логи (слева)
        log_group = QGroupBox("Логи симуляции")
        log_group.setStyleSheet(f"QGroupBox {{ color: {group_text_color}; font-weight: bold; }}")
        log_layout = QVBoxLayout()
        
        # Заголовок логов
        log_header = QLabel("Volume    Energy(Temp)   Pressure   Avg.Velocity  Time     Mode")
        log_header.setStyleSheet(f"font-weight: bold; color: #64b5f6;")
        log_layout.addWidget(log_header)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Courier", 9))
        self.log_display.setMaximumWidth(450)
        self.log_display.setStyleSheet("background-color: #1e1e1e; color: #00ff00;")
        
        log_layout.addWidget(self.log_display)
        log_group.setLayout(log_layout)
        bottom_layout.addWidget(log_group)
        
        # Демонстрация (справа)
        demo_widget = QWidget()
        demo_layout = QVBoxLayout(demo_widget)
        
        # Виджет симуляции с конфигурацией
        self.simulation = SimulationWidget(
            self.config.simulation_window.width, 
            self.config.simulation_window.height,
            self.config
        )
        demo_layout.addWidget(self.simulation)
        
        bottom_layout.addWidget(demo_widget)
        main_layout.addWidget(bottom_widget)
        
        # Описание
        self.log_display.append("="*70)
        self.log_display.append("УПРАВЛЕНИЕ СИМУЛЯЦИЕЙ:")
        self.log_display.append("="*70)
        self.log_display.append("• Нагрев: увеличение кинетической энергии частиц")
        self.log_display.append("• Охлаждение: уменьшение кинетической энергии")
        self.log_display.append("• Расширение: увеличение объема сосуда")
        self.log_display.append("• Сжатие: уменьшение объема сосуда")
        self.log_display.append("• Стоп процесс: прекращение текущего процесса")
        self.log_display.append("• Остановить симуляцию: полная остановка")
        self.log_display.append("• Сбросить: перезапуск симуляции")
        self.log_display.append("• Графики: открыть окно с графиками")
        self.log_display.append("="*70)
        
        # Подключение сигналов
        self.connect_signals()
        
        # Окно графиков (будет создано при необходимости)
        self.graph_window = None
        
        # Окно настроек
        self.config_window = None
    
    def _create_menu(self):
        """Создать меню приложения."""
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu("Файл")
        
        settings_action = QAction("⚙️ Настройки...", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def connect_signals(self):
        """Подключение сигналов кнопок и обновлений"""
        # Кнопки управления
        self.btn_heat.clicked.connect(lambda: self.simulation.set_mode("heat"))
        self.btn_freeze.clicked.connect(lambda: self.simulation.set_mode("freeze"))
        self.btn_expansion.clicked.connect(lambda: self.simulation.set_mode("expansion"))
        self.btn_compression.clicked.connect(lambda: self.simulation.set_mode("compression"))
        self.btn_off.clicked.connect(lambda: self.simulation.set_mode("OFF"))
        self.btn_stop.clicked.connect(self.simulation.stop_simulation)
        self.btn_start.clicked.connect(self.simulation.start_simulation)
        self.btn_reset.clicked.connect(self.simulation.reset_simulation)
        self.btn_graphs.clicked.connect(self.show_graphs)
        self.btn_statistics.clicked.connect(self.show_statistics)
        self.btn_settings.clicked.connect(self.show_settings)
        self.btn_exit.clicked.connect(self.close)
        
        # Экспериментальные режимы
        self.btn_isolated.clicked.connect(self.toggle_isolated_system)
        self.btn_brownian.clicked.connect(self.toggle_brownian_mode)
        self.btn_gravity.clicked.connect(self.toggle_gravity)
        self.btn_corner_start.clicked.connect(self.toggle_corner_start)
        
        # Обновление данных из симуляции
        self.simulation.update_signal.connect(self.update_display)
    
    def update_display(self, volume, energy, pressure, avg_velocity, log_entry):
        """Обновление отображения данных"""
        # Проверяем, был ли пользователь внизу списка перед добавлением
        scrollbar = self.log_display.verticalScrollBar()
        was_at_bottom = scrollbar.value() >= scrollbar.maximum() - 20
        
        # Обновление логов
        self.log_display.append(log_entry)
        
        # Прокрутка вниз только если пользователь был внизу
        if was_at_bottom:
            scrollbar.setValue(scrollbar.maximum())
        
        # Обновление параметров
        self.lbl_mode.setText(f"Режим: {self.simulation.mode}")
        self.lbl_energy.setText(f"Энергия: {energy:.2f}")
        self.lbl_pressure.setText(f"Давление: {pressure:.3f}")
        self.lbl_volume.setText(f"Объем: {volume:.1f}")
        self.lbl_velocity.setText(f"Ср.скорость: {avg_velocity:.3f}")
        
        # Цветовая индикация режима
        mode_colors = self.config.mode_colors.to_dict_by_mode()
        color = mode_colors.get(self.simulation.mode, '#f0f0f0')
        self.lbl_mode.setStyleSheet(f"background-color: {color}; padding: 5px; border-radius: 3px;")
        
        # Обновляем стиль кнопки изолированной системы
        if self.btn_isolated.isChecked():
            self.btn_isolated.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        else:
            self.btn_isolated.setStyleSheet("font-weight: bold;")
    
    def toggle_isolated_system(self, checked: bool):
        """Переключить режим изолированной системы."""
        self.simulation.toggle_isolated_system(checked)
        self.config.experiment.isolated_system = checked
        
        # Обновляем визуальное состояние кнопки
        if checked:
            self.btn_isolated.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
            self.log_display.append("🔒 Режим изолированной системы ВКЛЮЧЕН")
            self.log_display.append("   → Нагрев/охлаждение и расширение/сжатие заблокированы")
        else:
            self.btn_isolated.setStyleSheet("font-weight: bold;")
            self.log_display.append("🔓 Режим изолированной системы ВЫКЛЮЧЕН")
    
    def toggle_brownian_mode(self, checked: bool):
        """Переключить режим броуновского движения."""
        self.simulation.toggle_brownian_mode(checked)
        self.config.brownian.enabled = checked
        
        # Обновляем визуальное состояние кнопки
        if checked:
            self.btn_brownian.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
            self.log_display.append("🔬 Режим броуновского движения ВКЛЮЧЕН")
            self.log_display.append("   → Первая частица увеличена (масса и радиус)")
            self.log_display.append("   → Отслеживание MSD активно")
        else:
            self.btn_brownian.setStyleSheet("font-weight: bold;")
            self.log_display.append("🔬 Режим броуновского движения ВЫКЛЮЧЕН")
    
    def toggle_gravity(self, checked: bool):
        """Переключить гравитацию."""
        self.simulation.toggle_gravity(checked)
        self.config.gravity.enabled = checked
        
        # Обновляем визуальное состояние кнопки
        if checked:
            self.btn_gravity.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold;")
            self.log_display.append("🌍 Гравитация ВКЛЮЧЕНА")
            self.log_display.append(f"   → g = {self.config.gravity.g}")
            self.log_display.append("   → Частицы будут падать вниз")
        else:
            self.btn_gravity.setStyleSheet("font-weight: bold;")
            self.log_display.append("🌍 Гравитация ВЫКЛЮЧЕНА")
    
    def toggle_corner_start(self, checked: bool):
        """Переключить режим старта из угла."""
        self.simulation.toggle_corner_start(checked)
        self.config.experiment.corner_start = checked
        
        # Обновляем визуальное состояние кнопки
        if checked:
            self.btn_corner_start.setStyleSheet("background-color: #9C27B0; color: white; font-weight: bold;")
            self.log_display.append("📐 Режим СТАРТ ИЗ УГЛА ВКЛЮЧЕН")
            self.log_display.append("   → Частицы начинают в левом верхнем углу")
            self.log_display.append("   → Для демонстрации 2-го закона термодинамики")
        else:
            self.btn_corner_start.setStyleSheet("font-weight: bold;")
            self.log_display.append("📐 Режим старт из угла ВЫКЛЮЧЕН")
    
    def show_graphs(self):
        """Показать окно с графиками"""
        # Всегда создаем новое окно, чтобы переподключить сигнал
        if self.graph_window is not None:
            self.graph_window.close()
            self.graph_window = None
        self.graph_window = GraphWindow(self.simulation, self, self.config)
        self.graph_window.show()
        self.graph_window.raise_()
    
    def show_settings(self):
        """Показать окно настроек."""
        self.config_window = ConfigWindow(self.config, self)
        self.config_window.config_applied.connect(self._apply_new_config)
        self.config_window.exec_()
    
    def _apply_new_config(self, new_config: AppConfig):
        """Применить новую конфигурацию."""
        self.config = new_config
        
        # Обновляем лейбл количества частиц
        self.lbl_particles.setText(f"Частиц: {self.config.particles.count}")
        
        # Применяем конфигурацию к симуляции и перезапускаем
        self.simulation.apply_config(self.config)
        
        # Закрываем окно графиков (будет пересоздано с новым конфигом)
        if self.graph_window is not None:
            self.graph_window.close()
            self.graph_window = None
    
    def show_statistics(self):
        """Показать статистику"""
        stats = self.simulation.get_statistics()
        
        stats_text = f"""
        СТАТИСТИКА СИМУЛЯЦИИ:
        ======================
        Количество частиц: {stats['particle_count']}
        Текущий объем: {stats['current_volume']:.1f}
        Текущее давление: {stats['current_pressure']:.3f}
        Общая энергия: {stats['total_energy']:.2f}
        
        СКОРОСТИ:
        ----------
        Средняя скорость: {stats['mean_velocity']:.3f}
        Стандартное отклонение: {stats['std_velocity']:.3f}
        Максимальная скорость: {stats['max_velocity']:.3f}
        Минимальная скорость: {stats['min_velocity']:.3f}
        
        РЕЖИМ: {self.simulation.mode}
        ВРЕМЯ: {self.simulation.NOW_TIME:.1f}
        """
        
        self.log_display.append("\n" + "="*70)
        self.log_display.append("СТАТИСТИКА:")
        self.log_display.append("="*70)
        for line in stats_text.strip().split('\n'):
            self.log_display.append(line)
        self.log_display.append("="*70)
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        self.simulation.stop_simulation()
        
        if self.graph_window and self.graph_window.isVisible():
            self.graph_window.close()
        
        event.accept()
