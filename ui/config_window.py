"""
Окно редактирования конфигурации.
Автоматически генерирует UI на основе Pydantic-схем.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QFormLayout, QSpinBox, QDoubleSpinBox, QLineEdit, QPushButton,
    QLabel, QGroupBox, QScrollArea, QColorDialog, QMessageBox,
    QFileDialog, QFrame, QCheckBox, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPalette
from pydantic import ValidationError
from typing import Any, Dict, Tuple, get_origin, get_args, Literal
from pathlib import Path

from schemas import AppConfig, ConfigSection


class ColorButton(QPushButton):
    """Кнопка выбора цвета."""
    
    color_changed = pyqtSignal(tuple)
    
    def __init__(self, color: Tuple[int, int, int], parent=None):
        super().__init__(parent)
        self._color = color
        self._update_style()
        self.clicked.connect(self._pick_color)
        self.setFixedSize(60, 25)
    
    def _update_style(self):
        """Обновить стиль кнопки под цвет."""
        r, g, b = self._color
        # Определяем контрастный цвет текста
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        text_color = "black" if luminance > 0.5 else "white"
        self.setStyleSheet(
            f"background-color: rgb({r}, {g}, {b}); "
            f"color: {text_color}; "
            f"border: 1px solid #555;"
        )
        self.setText(f"#{r:02x}{g:02x}{b:02x}")
    
    def _pick_color(self):
        """Открыть диалог выбора цвета."""
        initial = QColor(*self._color)
        color = QColorDialog.getColor(initial, self, "Выберите цвет")
        if color.isValid():
            self._color = (color.red(), color.green(), color.blue())
            self._update_style()
            self.color_changed.emit(self._color)
    
    def get_color(self) -> Tuple[int, int, int]:
        return self._color
    
    def set_color(self, color: Tuple[int, int, int]):
        self._color = color
        self._update_style()


class HexColorEdit(QWidget):
    """Виджет для редактирования HEX цвета."""
    
    def __init__(self, color: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.line_edit = QLineEdit(color)
        self.line_edit.setMaximumWidth(100)
        layout.addWidget(self.line_edit)
        
        self.preview = QFrame()
        self.preview.setFixedSize(25, 25)
        self.preview.setFrameStyle(QFrame.Box)
        layout.addWidget(self.preview)
        
        self.line_edit.textChanged.connect(self._update_preview)
        self._update_preview(color)
    
    def _update_preview(self, color: str):
        """Обновить превью цвета."""
        try:
            self.preview.setStyleSheet(f"background-color: {color}; border: 1px solid #555;")
        except:
            self.preview.setStyleSheet("background-color: gray; border: 1px solid red;")
    
    def get_value(self) -> str:
        return self.line_edit.text()
    
    def set_value(self, value: str):
        self.line_edit.setText(value)


class ConfigSectionWidget(QWidget):
    """Виджет для отображения секции конфигурации."""
    
    def __init__(self, section: ConfigSection, section_name: str, parent=None):
        super().__init__(parent)
        self.section = section
        self.section_name = section_name
        self.widgets: Dict[str, Any] = {}
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(10)
        
        fields_info = self.section.get_field_info()
        
        for field_name, info in fields_info.items():
            widget = self._create_widget_for_field(field_name, info)
            if widget:
                label = QLabel(f"{info['title']}:")
                label.setToolTip(info['description'])
                layout.addRow(label, widget)
                self.widgets[field_name] = widget
    
    def _create_widget_for_field(self, field_name: str, info: Dict) -> Any:
        """Создать виджет для поля на основе его типа."""
        field_type = info['type']
        default = info['default']
        current_value = getattr(self.section, field_name)
        
        # Обработка Tuple[int, int, int] как RGB цвета
        origin = get_origin(field_type)
        if origin is tuple:
            args = get_args(field_type)
            if len(args) == 3 and all(arg == int for arg in args):
                widget = ColorButton(current_value)
                return widget
        
        # Обработка Literal (выпадающий список)
        if origin is Literal:
            args = get_args(field_type)
            widget = QComboBox()
            widget.addItems([str(arg) for arg in args])
            widget.setCurrentText(str(current_value))
            widget.setToolTip(info['description'])
            return widget
        
        # bool (чекбокс)
        if field_type == bool:
            widget = QCheckBox()
            widget.setChecked(current_value)
            widget.setToolTip(info['description'])
            return widget
        
        # int
        if field_type == int:
            widget = QSpinBox()
            widget.setRange(
                info.get('ge', info.get('gt', 0) + 1 if 'gt' in info else 0),
                info.get('le', info.get('lt', 10000) - 1 if 'lt' in info else 10000)
            )
            widget.setValue(current_value)
            widget.setToolTip(info['description'])
            return widget
        
        # float
        if field_type == float:
            widget = QDoubleSpinBox()
            widget.setDecimals(4)
            widget.setSingleStep(0.01)
            widget.setRange(
                info.get('ge', info.get('gt', 0.0) + 0.001 if 'gt' in info else 0.0),
                info.get('le', info.get('lt', 1000.0) - 0.001 if 'lt' in info else 1000.0)
            )
            widget.setValue(current_value)
            widget.setToolTip(info['description'])
            return widget
        
        # str (возможно HEX цвет)
        if field_type == str:
            if current_value.startswith('#') or current_value in ('black', 'white', 'gray', 'red', 'green', 'blue', 'orange'):
                widget = HexColorEdit(current_value)
            else:
                widget = QLineEdit(current_value)
            return widget
        
        # Fallback: строка
        widget = QLineEdit(str(current_value))
        return widget
    
    def get_values(self) -> Dict[str, Any]:
        """Получить все значения из виджетов."""
        values = {}
        for field_name, widget in self.widgets.items():
            if isinstance(widget, QSpinBox):
                values[field_name] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                values[field_name] = widget.value()
            elif isinstance(widget, QLineEdit):
                values[field_name] = widget.text()
            elif isinstance(widget, ColorButton):
                values[field_name] = widget.get_color()
            elif isinstance(widget, HexColorEdit):
                values[field_name] = widget.get_value()
            elif isinstance(widget, QCheckBox):
                values[field_name] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                values[field_name] = widget.currentText()
        return values
    
    def set_values(self, section: ConfigSection):
        """Установить значения из секции конфигурации."""
        self.section = section
        for field_name, widget in self.widgets.items():
            value = getattr(section, field_name)
            if isinstance(widget, QSpinBox):
                widget.setValue(value)
            elif isinstance(widget, QDoubleSpinBox):
                widget.setValue(value)
            elif isinstance(widget, QLineEdit):
                widget.setText(str(value))
            elif isinstance(widget, ColorButton):
                widget.set_color(value)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(value)
            elif isinstance(widget, QComboBox):
                widget.setCurrentText(str(value))
            elif isinstance(widget, HexColorEdit):
                widget.set_value(value)


class ConfigWindow(QDialog):
    """
    Окно редактирования конфигурации.
    Генерирует табы и виджеты на основе Pydantic-схем.
    """
    
    config_applied = pyqtSignal(object)  # Сигнал при применении конфига
    restart_requested = pyqtSignal()  # Сигнал для перезапуска симуляции
    
    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.section_widgets: Dict[str, ConfigSectionWidget] = {}
        
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self):
        self.setWindowTitle("Настройки симуляции")
        self.setMinimumSize(600, 700)
        self.resize(700, 800)
        
        layout = QVBoxLayout(self)
        
        # Табы для категорий
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Создаем табы по категориям
        self._create_simulation_tab()
        self._create_physics_tab()
        self._create_particles_tab()
        self._create_ui_tab()
        self._create_graphs_tab()
        self._create_colors_tab()
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.reset_defaults_btn = QPushButton("Сбросить к дефолтным")
        self.reset_defaults_btn.setToolTip("Сбросить все параметры к значениям по умолчанию")
        buttons_layout.addWidget(self.reset_defaults_btn)
        
        buttons_layout.addStretch()
        
        self.load_btn = QPushButton("Загрузить из файла...")
        self.load_btn.setToolTip("Загрузить конфигурацию из JSON файла")
        buttons_layout.addWidget(self.load_btn)
        
        self.save_btn = QPushButton("Сохранить в файл...")
        self.save_btn.setToolTip("Сохранить конфигурацию в JSON файл")
        buttons_layout.addWidget(self.save_btn)
        
        buttons_layout.addStretch()
        
        self.apply_btn = QPushButton("Применить и перезапустить")
        self.apply_btn.setStyleSheet("background-color: #2d5a2d; font-weight: bold;")
        self.apply_btn.setToolTip("Применить изменения и перезапустить симуляцию")
        buttons_layout.addWidget(self.apply_btn)
        
        self.cancel_btn = QPushButton("Отмена")
        buttons_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def _create_tab_with_scroll(self, sections: list) -> QWidget:
        """Создать таб со скроллом и несколькими секциями."""
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        for section_attr, title in sections:
            section = getattr(self.config, section_attr)
            group = QGroupBox(title)
            group_layout = QVBoxLayout(group)
            
            section_widget = ConfigSectionWidget(section, section_attr)
            self.section_widgets[section_attr] = section_widget
            group_layout.addWidget(section_widget)
            
            content_layout.addWidget(group)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        tab_layout.addWidget(scroll)
        
        return tab
    
    def _create_simulation_tab(self):
        """Создать таб с параметрами симуляции."""
        sections = [
            ('simulation_window', 'Окно симуляции'),
            ('time', 'Время'),
            ('state_change', 'Изменение состояния'),
            ('collision', 'Столкновения'),
        ]
        tab = self._create_tab_with_scroll(sections)
        self.tab_widget.addTab(tab, "Симуляция")
    
    def _create_physics_tab(self):
        """Создать таб с физическими параметрами."""
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Основные физические секции
        basic_sections = [
            ('gravity', 'Гравитация'),
            ('brownian', 'Броуновское движение'),
            ('experiment', 'Экспериментальные режимы'),
        ]
        
        for section_attr, title in basic_sections:
            section = getattr(self.config, section_attr)
            group = QGroupBox(title)
            group_layout = QVBoxLayout(group)
            
            section_widget = ConfigSectionWidget(section, section_attr)
            self.section_widgets[section_attr] = section_widget
            group_layout.addWidget(section_widget)
            
            content_layout.addWidget(group)
        
        # Секция потенциалов взаимодействия
        potentials_group = QGroupBox("Потенциалы взаимодействия")
        potentials_layout = QVBoxLayout(potentials_group)
        
        # Общие параметры потенциалов
        ip = self.config.interaction_potentials
        general_widget = ConfigSectionWidget(ip, 'interaction_potentials_general')
        # Создаём виджеты только для max_force и softening_distance
        self._create_potentials_general_widget(potentials_layout, ip)
        
        # Потенциал Леннард-Джонса
        lj_group = QGroupBox("Потенциал Леннард-Джонса")
        lj_layout = QVBoxLayout(lj_group)
        lj_widget = ConfigSectionWidget(ip.lennard_jones, 'lennard_jones')
        self.section_widgets['lennard_jones'] = lj_widget
        lj_layout.addWidget(lj_widget)
        potentials_layout.addWidget(lj_group)
        
        # Потенциал Морзе
        morse_group = QGroupBox("Потенциал Морзе")
        morse_layout = QVBoxLayout(morse_group)
        morse_widget = ConfigSectionWidget(ip.morse, 'morse')
        self.section_widgets['morse'] = morse_widget
        morse_layout.addWidget(morse_widget)
        potentials_layout.addWidget(morse_group)
        
        # Потенциал ДЛФО
        dlvo_group = QGroupBox("Потенциал ДЛФО (Дерягина-Ландау-Фервея-Овербека)")
        dlvo_layout = QVBoxLayout(dlvo_group)
        dlvo_widget = ConfigSectionWidget(ip.dlvo, 'dlvo')
        self.section_widgets['dlvo'] = dlvo_widget
        dlvo_layout.addWidget(dlvo_widget)
        potentials_layout.addWidget(dlvo_group)
        
        content_layout.addWidget(potentials_group)
        content_layout.addStretch()
        scroll.setWidget(content)
        tab_layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "Физика")
    
    def _create_potentials_general_widget(self, parent_layout, ip):
        """Создать виджеты для общих параметров потенциалов."""
        form_layout = QFormLayout()
        
        # Максимальная сила
        self.max_force_spin = QDoubleSpinBox()
        self.max_force_spin.setDecimals(2)
        self.max_force_spin.setRange(0.1, 100.0)
        self.max_force_spin.setValue(ip.max_force)
        self.max_force_spin.setToolTip("Ограничение максимальной силы для стабильности симуляции")
        form_layout.addRow("Максимальная сила:", self.max_force_spin)
        
        # Смягчение
        self.softening_spin = QDoubleSpinBox()
        self.softening_spin.setDecimals(3)
        self.softening_spin.setRange(0.01, 1.0)
        self.softening_spin.setValue(ip.softening_distance)
        self.softening_spin.setToolTip("Минимальное расстояние для избежания сингулярностей")
        form_layout.addRow("Смягчение на близких расстояниях:", self.softening_spin)
        
        parent_layout.addLayout(form_layout)
    
    def _create_particles_tab(self):
        """Создать таб с параметрами частиц."""
        sections = [
            ('particles', 'Параметры частиц'),
            ('molecule', 'Структура молекулы'),
        ]
        tab = self._create_tab_with_scroll(sections)
        self.tab_widget.addTab(tab, "Частицы")
    
    def _create_ui_tab(self):
        """Создать таб с параметрами UI."""
        sections = [
            ('main_window', 'Главное окно'),
            ('graph_window', 'Окно графиков'),
            ('logging', 'Логирование'),
        ]
        tab = self._create_tab_with_scroll(sections)
        self.tab_widget.addTab(tab, "Интерфейс")
    
    def _create_graphs_tab(self):
        """Создать таб с параметрами графиков."""
        sections = [
            ('graph_update', 'Обновление графиков'),
            ('statistical', 'Статистический анализ'),
            ('spectral', 'Спектральный анализ'),
            ('fractal', 'Фрактальный анализ'),
            ('correlation', 'Корреляции'),
        ]
        tab = self._create_tab_with_scroll(sections)
        self.tab_widget.addTab(tab, "Графики")
    
    def _create_colors_tab(self):
        """Создать таб с цветовыми настройками."""
        sections = [
            ('particle_colors', 'Цвета частиц'),
            ('border_colors', 'Цвета границ'),
            ('ui_colors', 'Цвета UI'),
            ('mode_colors', 'Цвета режимов'),
            ('mode_indicator_colors', 'Цвета индикаторов графиков'),
        ]
        tab = self._create_tab_with_scroll(sections)
        self.tab_widget.addTab(tab, "Цвета")
    
    def _setup_connections(self):
        """Настроить сигналы."""
        self.apply_btn.clicked.connect(self._apply_config)
        self.cancel_btn.clicked.connect(self.reject)
        self.reset_defaults_btn.clicked.connect(self._reset_to_defaults)
        self.save_btn.clicked.connect(self._save_to_file)
        self.load_btn.clicked.connect(self._load_from_file)
    
    def _collect_config(self) -> AppConfig:
        """Собрать конфигурацию из всех виджетов."""
        config_dict = {}
        
        # Секции потенциалов (вложенные)
        potential_sections = {'lennard_jones', 'morse', 'dlvo'}
        
        for section_attr, widget in self.section_widgets.items():
            if section_attr in potential_sections:
                continue  # Обрабатываем отдельно
            config_dict[section_attr] = widget.get_values()
        
        # Собираем потенциалы взаимодействия
        interaction_potentials = {
            'max_force': self.max_force_spin.value(),
            'softening_distance': self.softening_spin.value(),
        }
        
        for pot_name in potential_sections:
            if pot_name in self.section_widgets:
                interaction_potentials[pot_name] = self.section_widgets[pot_name].get_values()
        
        config_dict['interaction_potentials'] = interaction_potentials
        
        return AppConfig(**config_dict)
    
    def _apply_config(self):
        """Применить конфигурацию."""
        try:
            new_config = self._collect_config()
            self.config = new_config
            self.config_applied.emit(new_config)
            self.restart_requested.emit()
            self.accept()
        except ValidationError as e:
            QMessageBox.critical(
                self, 
                "Ошибка валидации",
                f"Некорректные значения:\n{e}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось применить конфигурацию:\n{e}"
            )
    
    def _reset_to_defaults(self):
        """Сбросить все значения к дефолтным."""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Сбросить все параметры к значениям по умолчанию?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            default_config = AppConfig.get_default()
            self._update_widgets_from_config(default_config)
    
    def _update_widgets_from_config(self, config: AppConfig):
        """Обновить все виджеты из конфигурации."""
        self.config = config
        
        # Секции потенциалов (вложенные)
        potential_sections = {'lennard_jones', 'morse', 'dlvo'}
        
        for section_attr, widget in self.section_widgets.items():
            if section_attr in potential_sections:
                # Вложенные секции потенциалов
                section = getattr(config.interaction_potentials, section_attr)
            else:
                section = getattr(config, section_attr)
            widget.set_values(section)
        
        # Обновляем общие параметры потенциалов
        ip = config.interaction_potentials
        self.max_force_spin.setValue(ip.max_force)
        self.softening_spin.setValue(ip.softening_distance)
    
    def _save_to_file(self):
        """Сохранить конфигурацию в файл."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить конфигурацию",
            "saved_config.json",
            "JSON файлы (*.json)"
        )
        
        if filepath:
            try:
                config = self._collect_config()
                config.save(Path(filepath))
                QMessageBox.information(
                    self,
                    "Успешно",
                    f"Конфигурация сохранена в:\n{filepath}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось сохранить конфигурацию:\n{e}"
                )
    
    def _load_from_file(self):
        """Загрузить конфигурацию из файла."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить конфигурацию",
            "",
            "JSON файлы (*.json)"
        )
        
        if filepath:
            try:
                loaded_config = AppConfig.load(Path(filepath))
                self._update_widgets_from_config(loaded_config)
                QMessageBox.information(
                    self,
                    "Успешно",
                    "Конфигурация загружена. Нажмите 'Применить' для использования."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось загрузить конфигурацию:\n{e}"
                )
    
    def get_config(self) -> AppConfig:
        """Получить текущую конфигурацию."""
        return self.config
