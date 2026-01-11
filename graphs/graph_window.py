"""
Окно с графиками симуляции газа.
"""
import datetime

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QWidget, QTabWidget,
                             QFileDialog, QMessageBox, QCheckBox,
                             QGroupBox, QLabel)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from schemas import AppConfig
from .thermodynamic import update_thermodynamic_graphs
from .distribution import update_distribution_graphs
from .kinetic import update_kinetic_graphs
from .correlation import update_correlation_graphs
from .advanced import update_advanced_graphs
from .realtime import update_realtime_graphs
from .energy_conservation import update_energy_conservation_graphs
from .brownian import update_brownian_graphs
from .boltzmann import update_boltzmann_graphs
from .entropy import update_entropy_graphs
from .ergodic import update_ergodic_graphs
from .rotational import update_rotational_graphs


class GraphWindow(QDialog):
    """Окно с графиками симуляции газа."""
    
    def __init__(self, simulation_widget, parent=None, config: AppConfig = None):
        super().__init__(parent)
        self.simulation = simulation_widget
        self.config = config if config is not None else AppConfig.get_default()
        
        self.setWindowTitle("Графики симуляции газа")
        self.setGeometry(
            100, 100, 
            self.config.graph_window.width, 
            self.config.graph_window.height
        )
        
        # Размер фигур
        self.figure_size = (
            self.config.graph_window.figure_width,
            self.config.graph_window.figure_height
        )
        
        # Флаг для отслеживания подключения сигнала
        self._connected = False
        
        # Подключение сигнала обновления данных
        self.simulation.data_updated.connect(self.on_data_updated)
        self._connected = True
        
        # Счетчик для регулировки частоты обновления графиков
        self.update_counter = 0
        self.cached_data = {}
        self.graph_update_interval = self.config.graph_update.update_interval
        
        # Создание вкладок
        self.tab_widget = QTabWidget()
        
        # Создание вкладок с графиками
        self.create_thermodynamic_tab()
        self.create_distribution_tab()
        self.create_kinetic_tab()
        self.create_correlation_tab()
        self.create_advanced_tab()
        self.create_real_time_tab()
        self.create_energy_conservation_tab()
        self.create_brownian_tab()
        self.create_boltzmann_tab()
        self.create_entropy_tab()
        self.create_ergodic_tab()
        self.create_rotational_tab()
        
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
        self.figure_thermo = Figure(figsize=self.figure_size)
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
        
        self.figure_dist = Figure(figsize=self.figure_size)
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
        
        self.figure_kinetic = Figure(figsize=self.figure_size)
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
        
        self.figure_corr = Figure(figsize=self.figure_size)
        self.canvas_corr = FigureCanvas(self.figure_corr)
        self.toolbar_corr = NavigationToolbar(self.canvas_corr, self)
        
        layout.addWidget(self.toolbar_corr)
        layout.addWidget(self.canvas_corr)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Корреляции")
    
    def create_advanced_tab(self):
        """Вкладка с продвинутыми графиками"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.figure_advanced = Figure(figsize=self.figure_size)
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
        
        self.figure_realtime = Figure(figsize=self.figure_size)
        self.canvas_realtime = FigureCanvas(self.figure_realtime)
        self.toolbar_realtime = NavigationToolbar(self.canvas_realtime, self)
        
        layout.addWidget(self.toolbar_realtime)
        layout.addWidget(self.canvas_realtime)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Реальное время")
    
    def create_energy_conservation_tab(self):
        """Вкладка с графиками сохранения энергии (1-й закон термодинамики)"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.figure_energy = Figure(figsize=self.figure_size)
        self.canvas_energy = FigureCanvas(self.figure_energy)
        self.toolbar_energy = NavigationToolbar(self.canvas_energy, self)
        
        layout.addWidget(self.toolbar_energy)
        layout.addWidget(self.canvas_energy)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "1-й закон ТД")
    
    def create_brownian_tab(self):
        """Вкладка с графиками броуновского движения"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.figure_brownian = Figure(figsize=self.figure_size)
        self.canvas_brownian = FigureCanvas(self.figure_brownian)
        self.toolbar_brownian = NavigationToolbar(self.canvas_brownian, self)
        
        layout.addWidget(self.toolbar_brownian)
        layout.addWidget(self.canvas_brownian)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Броуновское")
    
    def create_boltzmann_tab(self):
        """Вкладка с графиками распределения Больцмана"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.figure_boltzmann = Figure(figsize=self.figure_size)
        self.canvas_boltzmann = FigureCanvas(self.figure_boltzmann)
        self.toolbar_boltzmann = NavigationToolbar(self.canvas_boltzmann, self)
        
        layout.addWidget(self.toolbar_boltzmann)
        layout.addWidget(self.canvas_boltzmann)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Больцман")
    
    def create_entropy_tab(self):
        """Вкладка с графиками энтропии (2-й закон термодинамики)"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.figure_entropy = Figure(figsize=self.figure_size)
        self.canvas_entropy = FigureCanvas(self.figure_entropy)
        self.toolbar_entropy = NavigationToolbar(self.canvas_entropy, self)
        
        layout.addWidget(self.toolbar_entropy)
        layout.addWidget(self.canvas_entropy)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "2-й закон ТД")
    
    def create_ergodic_tab(self):
        """Вкладка с графиками эргодической гипотезы"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.figure_ergodic = Figure(figsize=self.figure_size)
        self.canvas_ergodic = FigureCanvas(self.figure_ergodic)
        self.toolbar_ergodic = NavigationToolbar(self.canvas_ergodic, self)
        
        layout.addWidget(self.toolbar_ergodic)
        layout.addWidget(self.canvas_ergodic)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Эргодичность")
    
    def create_rotational_tab(self):
        """Вкладка с графиками вращательных степеней свободы (молекулярная структура)"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.figure_rotational = Figure(figsize=self.figure_size)
        self.canvas_rotational = FigureCanvas(self.figure_rotational)
        self.toolbar_rotational = NavigationToolbar(self.canvas_rotational, self)
        
        layout.addWidget(self.toolbar_rotational)
        layout.addWidget(self.canvas_rotational)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Вращение")
    
    def init_graphs(self):
        """Инициализация всех графиков"""
        self.update_current_tab({})
    
    def on_data_updated(self, data):
        """Обработчик обновления данных с регулировкой частоты"""
        self.cached_data = data
        self.update_counter += 1
        
        # Обновляем графики только каждые graph_update_interval тиков
        if self.update_counter >= self.graph_update_interval:
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
                update_advanced_graphs(self.figure_advanced, self.canvas_advanced, data)
            elif current_index == 5:
                update_realtime_graphs(self.figure_realtime, self.canvas_realtime, data)
            elif current_index == 6:
                update_energy_conservation_graphs(self.figure_energy, self.canvas_energy, data)
            elif current_index == 7:
                update_brownian_graphs(self.figure_brownian, self.canvas_brownian, data)
            elif current_index == 8:
                update_boltzmann_graphs(self.figure_boltzmann, self.canvas_boltzmann, data)
            elif current_index == 9:
                update_entropy_graphs(self.figure_entropy, self.canvas_entropy, data)
            elif current_index == 10:
                update_ergodic_graphs(self.figure_ergodic, self.canvas_ergodic, data)
            elif current_index == 11:
                update_rotational_graphs(self.figure_rotational, data)
                self.canvas_rotational.draw()
        except Exception as e:
            print(f"Ошибка при обновлении графиков: {e}")
    
    def on_tab_changed(self, index):
        """Обработчик переключения вкладки - обновляем новую вкладку"""
        if self.cached_data:
            self.update_current_tab(self.cached_data)
    
    def update_all_graphs(self, data=None, force=False):
        """Обновление всех графиков (для сохранения)"""
        if data is None:
            data = self.cached_data
        if not data:
            return
        try:
            update_thermodynamic_graphs(self.figure_thermo, self.canvas_thermo, data)
            update_distribution_graphs(self.figure_dist, self.canvas_dist, data)
            update_kinetic_graphs(self.figure_kinetic, self.canvas_kinetic, data)
            update_correlation_graphs(self.figure_corr, self.canvas_corr, data)
            update_advanced_graphs(self.figure_advanced, self.canvas_advanced, data)
            update_realtime_graphs(self.figure_realtime, self.canvas_realtime, data)
            update_energy_conservation_graphs(self.figure_energy, self.canvas_energy, data)
            update_brownian_graphs(self.figure_brownian, self.canvas_brownian, data)
            update_boltzmann_graphs(self.figure_boltzmann, self.canvas_boltzmann, data)
            update_entropy_graphs(self.figure_entropy, self.canvas_entropy, data)
            update_ergodic_graphs(self.figure_ergodic, self.canvas_ergodic, data)
            update_rotational_graphs(self.figure_rotational, data)
            self.canvas_rotational.draw()
        except Exception as e:
            print(f"Ошибка при обновлении графиков: {e}")
    
    def clear_graphs(self):
        """Очистка всех графиков"""
        self.simulation.reset_simulation()
    
    def save_graphs(self):
        """Сохранение всех графиков с выбором папки и формата."""
        # Создаём диалог выбора опций сохранения
        dialog = QDialog(self)
        dialog.setWindowTitle("Сохранение графиков")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Выбор папки
        folder_layout = QHBoxLayout()
        self._save_folder = ""
        folder_label = QLabel("Папка: не выбрана")
        folder_btn = QPushButton("Выбрать папку...")
        
        def select_folder():
            folder = QFileDialog.getExistingDirectory(
                dialog, "Выберите папку для сохранения",
                "", QFileDialog.ShowDirsOnly
            )
            if folder:
                self._save_folder = folder
                folder_label.setText(f"Папка: {folder}")
        
        folder_btn.clicked.connect(select_folder)
        folder_layout.addWidget(folder_label, 1)
        folder_layout.addWidget(folder_btn)
        layout.addLayout(folder_layout)
        
        # Опции формата
        format_group = QGroupBox("Формат сохранения")
        format_layout = QVBoxLayout(format_group)
        
        png_checkbox = QCheckBox("PNG (отдельные файлы для каждого графика)")
        png_checkbox.setChecked(True)
        pdf_checkbox = QCheckBox("PDF (все графики в одном файле)")
        pdf_checkbox.setChecked(True)
        
        format_layout.addWidget(png_checkbox)
        format_layout.addWidget(pdf_checkbox)
        layout.addWidget(format_group)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        cancel_btn.clicked.connect(dialog.reject)
        
        def do_save():
            if not self._save_folder:
                QMessageBox.warning(dialog, "Ошибка", "Выберите папку для сохранения!")
                return
            if not png_checkbox.isChecked() and not pdf_checkbox.isChecked():
                QMessageBox.warning(dialog, "Ошибка", "Выберите хотя бы один формат!")
                return
            dialog.accept()
        
        save_btn.clicked.connect(do_save)
        
        if dialog.exec_() != QDialog.Accepted:
            return
        
        # Выполняем сохранение
        import os
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Список всех фигур и их canvas
        figures = [
            (self.figure_thermo, self.canvas_thermo, "thermodynamic", "Термодинамика"),
            (self.figure_dist, self.canvas_dist, "distribution", "Распределения"),
            (self.figure_kinetic, self.canvas_kinetic, "kinetic", "Кинетика"),
            (self.figure_corr, self.canvas_corr, "correlation", "Корреляции"),
            (self.figure_advanced, self.canvas_advanced, "advanced", "Расширенный анализ"),
            (self.figure_realtime, self.canvas_realtime, "realtime", "Реальное время"),
            (self.figure_energy, self.canvas_energy, "energy_conservation", "Сохранение энергии"),
            (self.figure_brownian, self.canvas_brownian, "brownian", "Броуновское движение"),
            (self.figure_boltzmann, self.canvas_boltzmann, "boltzmann", "Распределение Больцмана"),
            (self.figure_entropy, self.canvas_entropy, "entropy", "Энтропия"),
            (self.figure_ergodic, self.canvas_ergodic, "ergodic", "Эргодичность"),
            (self.figure_rotational, self.canvas_rotational, "rotational", "Вращательные степени свободы")
        ]
        
        # Принудительно обновляем все графики перед сохранением
        if self.cached_data:
            self.update_all_graphs(force=True)
        
        # Перерисовываем все canvas
        for fig, canvas, name, title in figures:
            canvas.draw()
        
        saved_files = []
        errors = []
        
        # Сохраняем PNG
        if png_checkbox.isChecked():
            for fig, canvas, name, title in figures:
                try:
                    filename = os.path.join(self._save_folder, f"gas_simulation_{name}_{timestamp}.png")
                    fig.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
                    saved_files.append(filename)
                except Exception as e:
                    errors.append(f"PNG {name}: {e}")
        
        # Сохраняем PDF
        if pdf_checkbox.isChecked():
            try:
                from matplotlib.backends.backend_pdf import PdfPages
                
                pdf_filename = os.path.join(self._save_folder, f"gas_simulation_all_{timestamp}.pdf")
                with PdfPages(pdf_filename) as pdf:
                    for fig, canvas, name, title in figures:
                        # Сохраняем без изменения фигуры
                        pdf.savefig(fig, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
                saved_files.append(pdf_filename)
            except Exception as e:
                errors.append(f"PDF: {e}")
        
        # Показываем результат
        if errors:
            error_msg = "\n".join(errors)
            QMessageBox.warning(
                self, "Ошибки при сохранении",
                f"Некоторые файлы не удалось сохранить:\n{error_msg}"
            )
        
        if saved_files:
            QMessageBox.information(
                self, "Сохранение завершено",
                f"Сохранено файлов: {len(saved_files)}\nПапка: {self._save_folder}"
            )

    def closeEvent(self, event):
        """Обработка закрытия окна - отключаем сигнал для предотвращения лагов"""
        if self._connected:
            try:
                self.simulation.data_updated.disconnect(self.on_data_updated)
                self._connected = False
            except (TypeError, RuntimeError):
                pass  # Сигнал уже отключен или объект удален
        event.accept()