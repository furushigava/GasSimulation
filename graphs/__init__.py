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
from .energy_conservation import update_energy_conservation_graphs
from .brownian import update_brownian_graphs
from .boltzmann import update_boltzmann_graphs
from .entropy import update_entropy_graphs
from .ergodic import update_ergodic_graphs

__all__ = [
    'GraphWindow',
    'update_thermodynamic_graphs',
    'update_distribution_graphs',
    'update_kinetic_graphs',
    'update_correlation_graphs',
    'update_advanced_graphs',
    'update_realtime_graphs',
    'update_energy_conservation_graphs',
    'update_brownian_graphs',
    'update_boltzmann_graphs',
    'update_entropy_graphs',
    'update_ergodic_graphs'
]
