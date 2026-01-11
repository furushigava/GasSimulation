"""
Схемы для параметров графиков и анализа.
"""
from pydantic import Field
from .base import ConfigSection


class GraphUpdateConfig(ConfigSection):
    """Параметры обновления графиков."""
    
    update_interval: int = Field(
        default=5,
        ge=1,
        le=100,
        title="Интервал обновления",
        description="Обновлять графики каждые N тиков симуляции"
    )
    realtime_points_limit: int = Field(
        default=100,
        ge=10,
        le=1000,
        title="Лимит точек реального времени",
        description="Количество точек для графиков реального времени"
    )
    combined_graph_points: int = Field(
        default=50,
        ge=10,
        le=500,
        title="Точки комбинированного графика",
        description="Количество точек для комбинированного графика"
    )


class StatisticalConfig(ConfigSection):
    """Параметры статистического анализа."""
    
    rolling_window_divisor: int = Field(
        default=10,
        ge=2,
        le=50,
        title="Делитель окна",
        description="Делитель для расчета размера окна скользящего среднего"
    )
    ema_alpha: float = Field(
        default=0.1,
        ge=0.01,
        le=1.0,
        title="EMA Alpha",
        description="Коэффициент для экспоненциального скользящего среднего"
    )


class SpectralConfig(ConfigSection):
    """Параметры спектрального анализа."""
    
    wavelet_scales_max: int = Field(
        default=31,
        ge=10,
        le=100,
        title="Макс. масштабы вейвлета",
        description="Максимальное количество масштабов вейвлета"
    )
    fft_min_points: int = Field(
        default=10,
        ge=4,
        le=100,
        title="Мин. точек FFT",
        description="Минимальное количество точек для FFT анализа"
    )


class FractalConfig(ConfigSection):
    """Параметры фрактального анализа."""
    
    box_sizes_num: int = Field(
        default=20,
        ge=5,
        le=100,
        title="Количество размеров боксов",
        description="Количество размеров боксов для box-counting"
    )
    hurst_min_size: int = Field(
        default=10,
        ge=5,
        le=50,
        title="Мин. размер Hurst",
        description="Минимальный размер для анализа Hurst"
    )
    hurst_sizes_num: int = Field(
        default=10,
        ge=3,
        le=50,
        title="Количество размеров Hurst",
        description="Количество размеров для анализа Hurst"
    )


class CorrelationConfig(ConfigSection):
    """Параметры анализа корреляций."""
    
    min_points: int = Field(
        default=10,
        ge=3,
        le=100,
        title="Мин. точек корреляции",
        description="Минимальное количество точек для анализа корреляций"
    )
    matrix_min_points: int = Field(
        default=5,
        ge=3,
        le=50,
        title="Мин. точек матрицы",
        description="Минимальное количество точек для матрицы корреляций"
    )
