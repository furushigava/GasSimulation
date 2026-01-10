"""
GasSimulation - Симуляция газа с визуализацией и анализом.

Точка входа в приложение.
"""
import sys
from PyQt5.QtWidgets import QApplication
from ui import MainWindow


def main():
    """Запуск приложения."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
