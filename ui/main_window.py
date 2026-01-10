"""
Главное окно приложения симуляции газа.
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                             QGroupBox, QGridLayout)
from PyQt5.QtGui import QFont

from simulation import SimulationWidget
from graphs import GraphWindow
from config import (
    MAIN_WINDOW_WIDTH,
    MAIN_WINDOW_HEIGHT,
    SIMULATION_WIDTH,
    SIMULATION_HEIGHT,
    PARTICLE_COUNT,
    MODE_COLORS,
    LABEL_TEXT_COLOR,
    LABEL_BG_COLOR,
    GROUP_TEXT_COLOR
)


class MainWindow(QMainWindow):
    """Главное окно приложения симуляции газа."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GAS Simulation - PyQt5 Version")
        self.setGeometry(100, 100, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)
        
        # Центральный виджет и основной layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
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
        self.btn_reset = QPushButton("Сбросить")
        self.btn_graphs = QPushButton("Показать графики")
        self.btn_statistics = QPushButton("Статистика")
        
        # Настройка кнопок
        buttons = [
            self.btn_heat, self.btn_freeze, self.btn_expansion, 
            self.btn_compression, self.btn_off, self.btn_stop, 
            self.btn_reset, self.btn_graphs, self.btn_statistics
        ]
        
        for i, btn in enumerate(buttons):
            btn.setMinimumHeight(40)
            btn.setStyleSheet("font-weight: bold;")
            params_layout.addWidget(btn, i // 3, i % 3)
        
        # Параметры
        stats_layout = QHBoxLayout()
        
        self.lbl_particles = QLabel(f"Частиц: {PARTICLE_COUNT}")
        self.lbl_mode = QLabel("Режим: OFF")
        self.lbl_energy = QLabel("Энергия: 0.00")
        self.lbl_pressure = QLabel("Давление: 0.00")
        self.lbl_volume = QLabel("Объем: 0.00")
        self.lbl_velocity = QLabel("Ср.скорость: 0.00")
        
        for lbl in [self.lbl_particles, self.lbl_mode, self.lbl_energy, 
                   self.lbl_pressure, self.lbl_volume, self.lbl_velocity]:
            lbl.setStyleSheet(f"background-color: {LABEL_BG_COLOR}; color: {LABEL_TEXT_COLOR}; padding: 5px; border-radius: 3px;")
            stats_layout.addWidget(lbl)
        
        params_layout.addLayout(stats_layout, 3, 0, 1, 3)
        
        params_group.setLayout(params_layout)
        params_group.setStyleSheet(f"QGroupBox {{ color: {GROUP_TEXT_COLOR}; font-weight: bold; }}")
        main_layout.addWidget(params_group)
        
        # 2. Нижняя часть: логи слева, демонстрация справа
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        
        # Логи (слева)
        log_group = QGroupBox("Логи симуляции")
        log_group.setStyleSheet(f"QGroupBox {{ color: {GROUP_TEXT_COLOR}; font-weight: bold; }}")
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
        
        # Виджет симуляции
        self.simulation = SimulationWidget(SIMULATION_WIDTH, SIMULATION_HEIGHT)
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
    
    def connect_signals(self):
        """Подключение сигналов кнопок и обновлений"""
        # Кнопки управления
        self.btn_heat.clicked.connect(lambda: self.simulation.set_mode("heat"))
        self.btn_freeze.clicked.connect(lambda: self.simulation.set_mode("freeze"))
        self.btn_expansion.clicked.connect(lambda: self.simulation.set_mode("expansion"))
        self.btn_compression.clicked.connect(lambda: self.simulation.set_mode("compression"))
        self.btn_off.clicked.connect(lambda: self.simulation.set_mode("OFF"))
        self.btn_stop.clicked.connect(self.simulation.stop_simulation)
        self.btn_reset.clicked.connect(self.simulation.reset_simulation)
        self.btn_graphs.clicked.connect(self.show_graphs)
        self.btn_statistics.clicked.connect(self.show_statistics)
        
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
        color = MODE_COLORS.get(self.simulation.mode, '#f0f0f0')
        self.lbl_mode.setStyleSheet(f"background-color: {color}; padding: 5px; border-radius: 3px;")
    
    def show_graphs(self):
        """Показать окно с графиками"""
        if self.graph_window is None or not self.graph_window.isVisible():
            self.graph_window = GraphWindow(self.simulation, self)
        self.graph_window.show()
        self.graph_window.raise_()
    
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
