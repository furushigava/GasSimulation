"""
Окно с графиками симуляции газа.
"""
import datetime

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QWidget, QTabWidget)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from config import GRAPH_WINDOW_WIDTH, GRAPH_WINDOW_HEIGHT, FIGURE_SIZE, GRAPH_UPDATE_INTERVAL
from .thermodynamic import update_thermodynamic_graphs
from .distribution import update_distribution_graphs
from .kinetic import update_kinetic_graphs
from .correlation import update_correlation_graphs
from .statistical import update_statistical_graphs
from .phase import update_phase_graphs
from .advanced import update_advanced_graphs
from .realtime import update_realtime_graphs


class GraphWindow(QDialog):
    """Окно с графиками симуляции газа."""
    
    def __init__(self, simulation_widget, parent=None):
        super().__init__(parent)
        self.simulation = simulation_widget
        self.setWindowTitle("Графики симуляции газа")
        self.setGeometry(100, 100, GRAPH_WINDOW_WIDTH, GRAPH_WINDOW_HEIGHT)
        
        # Подключение сигнала обновления данных
        self.simulation.data_updated.connect(self.on_data_updated)
        
        # Счетчик для регулировки частоты обновления графиков
        self.update_counter = 0
        self.cached_data = {}
        
        # Создание вкладок
        self.tab_widget = QTabWidget()
        
        # Создание вкладок с графиками
        self.create_thermodynamic_tab()
        self.create_distribution_tab()
        self.create_kinetic_tab()
        self.create_correlation_tab()
        self.create_statistical_tab()
        self.create_phase_tab()
        self.create_advanced_tab()
        self.create_real_time_tab()
        
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        self.btn_save = QPushButton("Сохранить графики")
        self.btn_clear = QPushButton("Очистить данные")
        self.btn_close = QPushButton("Закрыть")
        
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_clear)
        button_layout.addWidget(self.btn_close)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Подключение кнопок
        self.btn_close.clicked.connect(self.close)
        self.btn_clear.clicked.connect(self.clear_graphs)
        self.btn_save.clicked.connect(self.save_graphs)
        
        # Обновление графика при переключении вкладки
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Инициализация графиков
        self.init_graphs()
    
    def create_thermodynamic_tab(self):
        """Вкладка с термодинамическими графиками"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Создание фигур с графиками
        self.figure_thermo = Figure(figsize=FIGURE_SIZE)
        self.canvas_thermo = FigureCanvas(self.figure_thermo)
        self.toolbar_thermo = NavigationToolbar(self.canvas_thermo, self)
        
        layout.addWidget(self.toolbar_thermo)
        layout.addWidget(self.canvas_thermo)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Термодинамика")
    
    def create_distribution_tab(self):
        """Вкладка с распределениями"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.figure_dist = Figure(figsize=FIGURE_SIZE)
        self.canvas_dist = FigureCanvas(self.figure_dist)
        self.toolbar_dist = NavigationToolbar(self.canvas_dist, self)
        
        layout.addWidget(self.toolbar_dist)
        layout.addWidget(self.canvas_dist)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Распределения")
    
    def create_kinetic_tab(self):
        """Вкладка с кинетическими графиками"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.figure_kinetic = Figure(figsize=FIGURE_SIZE)
        self.canvas_kinetic = FigureCanvas(self.figure_kinetic)
        self.toolbar_kinetic = NavigationToolbar(self.canvas_kinetic, self)
        
        layout.addWidget(self.toolbar_kinetic)
        layout.addWidget(self.canvas_kinetic)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Кинетика")
    
    def create_correlation_tab(self):
        """Вкладка с корреляционными графиками"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.figure_corr = Figure(figsize=FIGURE_SIZE)
        self.canvas_corr = FigureCanvas(self.figure_corr)
        self.toolbar_corr = NavigationToolbar(self.canvas_corr, self)
        
        layout.addWidget(self.toolbar_corr)
        layout.addWidget(self.canvas_corr)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Корреляции")
    
    def create_statistical_tab(self):
        """Вкладка со статистическими графиками"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.figure_stat = Figure(figsize=FIGURE_SIZE)
        self.canvas_stat = FigureCanvas(self.figure_stat)
        self.toolbar_stat = NavigationToolbar(self.canvas_stat, self)
        
        layout.addWidget(self.toolbar_stat)
        layout.addWidget(self.canvas_stat)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Статистика")
    
    def create_phase_tab(self):
        """Вкладка с фазовыми диаграммами"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.figure_phase = Figure(figsize=FIGURE_SIZE)
        self.canvas_phase = FigureCanvas(self.figure_phase)
        self.toolbar_phase = NavigationToolbar(self.canvas_phase, self)
        
        layout.addWidget(self.toolbar_phase)
        layout.addWidget(self.canvas_phase)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Фазовые диаграммы")
    
    def create_advanced_tab(self):
        """Вкладка с продвинутыми графиками"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.figure_advanced = Figure(figsize=FIGURE_SIZE)
        self.canvas_advanced = FigureCanvas(self.figure_advanced)
        self.toolbar_advanced = NavigationToolbar(self.canvas_advanced, self)
        
        layout.addWidget(self.toolbar_advanced)
        layout.addWidget(self.canvas_advanced)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Продвинутые")
    
    def create_real_time_tab(self):
        """Вкладка с графиками реального времени"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.figure_realtime = Figure(figsize=FIGURE_SIZE)
        self.canvas_realtime = FigureCanvas(self.figure_realtime)
        self.toolbar_realtime = NavigationToolbar(self.canvas_realtime, self)
        
        layout.addWidget(self.toolbar_realtime)
        layout.addWidget(self.canvas_realtime)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Реальное время")
    
    def init_graphs(self):
        """Инициализация всех графиков"""
        self.update_current_tab({})
    
    def on_data_updated(self, data):
        """Обработчик обновления данных с регулировкой частоты"""
        self.cached_data = data
        self.update_counter += 1
        
        # Обновляем графики только каждые GRAPH_UPDATE_INTERVAL тиков
        if self.update_counter >= GRAPH_UPDATE_INTERVAL:
            self.update_counter = 0
            self.update_current_tab(data)
    
    def update_current_tab(self, data):
        """Обновление только текущей активной вкладки"""
        try:
            current_index = self.tab_widget.currentIndex()
            
            if current_index == 0:
                update_thermodynamic_graphs(self.figure_thermo, self.canvas_thermo, data)
            elif current_index == 1:
                update_distribution_graphs(self.figure_dist, self.canvas_dist, data)
            elif current_index == 2:
                update_kinetic_graphs(self.figure_kinetic, self.canvas_kinetic, data)
            elif current_index == 3:
                update_correlation_graphs(self.figure_corr, self.canvas_corr, data)
            elif current_index == 4:
                update_statistical_graphs(self.figure_stat, self.canvas_stat, data)
            elif current_index == 5:
                update_phase_graphs(self.figure_phase, self.canvas_phase, data)
            elif current_index == 6:
                update_advanced_graphs(self.figure_advanced, self.canvas_advanced, data)
            elif current_index == 7:
                update_realtime_graphs(self.figure_realtime, self.canvas_realtime, data)
        except Exception as e:
            print(f"Ошибка при обновлении графиков: {e}")
    
    def on_tab_changed(self, index):
        """Обработчик переключения вкладки - обновляем новую вкладку"""
        if self.cached_data:
            self.update_current_tab(self.cached_data)
    
    def update_all_graphs(self, data):
        """Обновление всех графиков (для сохранения)"""
        try:
            update_thermodynamic_graphs(self.figure_thermo, self.canvas_thermo, data)
            update_distribution_graphs(self.figure_dist, self.canvas_dist, data)
            update_kinetic_graphs(self.figure_kinetic, self.canvas_kinetic, data)
            update_correlation_graphs(self.figure_corr, self.canvas_corr, data)
            update_statistical_graphs(self.figure_stat, self.canvas_stat, data)
            update_phase_graphs(self.figure_phase, self.canvas_phase, data)
            update_advanced_graphs(self.figure_advanced, self.canvas_advanced, data)
            update_realtime_graphs(self.figure_realtime, self.canvas_realtime, data)
        except Exception as e:
            print(f"Ошибка при обновлении графиков: {e}")
    
    def clear_graphs(self):
        """Очистка всех графиков"""
        self.simulation.reset_simulation()
    
    def save_graphs(self):
        """Сохранение всех графиков"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Сохраняем каждый график отдельно
        figures = [
            (self.figure_thermo, "thermodynamic"),
            (self.figure_dist, "distribution"),
            (self.figure_kinetic, "kinetic"),
            (self.figure_corr, "correlation"),
            (self.figure_stat, "statistical"),
            (self.figure_phase, "phase"),
            (self.figure_advanced, "advanced"),
            (self.figure_realtime, "realtime")
        ]
        
        for fig, name in figures:
            filename = f"gas_simulation_{name}_{timestamp}.png"
            fig.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"График сохранен: {filename}")
        
        # Сохраняем все графики в один PDF
        from matplotlib.backends.backend_pdf import PdfPages
        
        pdf_filename = f"gas_simulation_all_{timestamp}.pdf"
        with PdfPages(pdf_filename) as pdf:
            for fig, name in figures:
                pdf.savefig(fig, bbox_inches='tight')
        
        print(f"Все графики сохранены в PDF: {pdf_filename}")
