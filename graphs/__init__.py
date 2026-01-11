"""
Модуль graphs - компоненты для отображения графиков.
"""
from .graph_window import GraphWindow
from .thermodynamic import update_thermodynamic_graphs
from .distribution import update_distribution_graphs
from .kinetic import update_kinetic_graphs
from .correlation import update_correlation_graphs
from .advanced import update_advanced_graphs
from .realtime import update_realtime_graphs

__all__ = [
    'GraphWindow',
    'update_thermodynamic_graphs',
    'update_distribution_graphs',
    'update_kinetic_graphs',
    'update_correlation_graphs',
    'update_advanced_graphs',
    'update_realtime_graphs'
]
