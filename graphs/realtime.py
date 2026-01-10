"""
Функции для обновления графиков реального времени.
"""
import numpy as np
import matplotlib.pyplot as plt

from config import REALTIME_POINTS_LIMIT, COMBINED_GRAPH_POINTS, MODE_INDICATOR_COLORS


def update_realtime_graphs(figure, canvas, data):
    """Обновление графиков реального времени"""
    figure.clear()
    
    if not data.get('time'):
        canvas.draw()
        return
    
    # 1. График реального времени давления
    ax1 = figure.add_subplot(231)
    if data.get('time') and data.get('pressure'):
        ax1.plot(data['time'][-REALTIME_POINTS_LIMIT:], data['pressure'][-REALTIME_POINTS_LIMIT:], 'b-', linewidth=2)
        ax1.set_xlabel('Время')
        ax1.set_ylabel('Давление')
        ax1.set_title(f'Давление (последние {REALTIME_POINTS_LIMIT} точек)')
        ax1.grid(True, alpha=0.3)
    
    # 2. График реального времени температуры
    ax2 = figure.add_subplot(232)
    if data.get('time') and data.get('temperature'):
        ax2.plot(data['time'][-REALTIME_POINTS_LIMIT:], data['temperature'][-REALTIME_POINTS_LIMIT:], 'r-', linewidth=2)
        ax2.set_xlabel('Время')
        ax2.set_ylabel('Температура')
        ax2.set_title(f'Температура (последние {REALTIME_POINTS_LIMIT} точек)')
        ax2.grid(True, alpha=0.3)
    
    # 3. График реального времени объема
    ax3 = figure.add_subplot(233)
    if data.get('time') and data.get('volume'):
        ax3.plot(data['time'][-REALTIME_POINTS_LIMIT:], data['volume'][-REALTIME_POINTS_LIMIT:], 'g-', linewidth=2)
        ax3.set_xlabel('Время')
        ax3.set_ylabel('Объем')
        ax3.set_title(f'Объем (последние {REALTIME_POINTS_LIMIT} точек)')
        ax3.grid(True, alpha=0.3)
    
    # 4. График реального времени средней скорости
    ax4 = figure.add_subplot(234)
    if data.get('time') and data.get('avg_velocity'):
        ax4.plot(data['time'][-REALTIME_POINTS_LIMIT:], data['avg_velocity'][-REALTIME_POINTS_LIMIT:], 'orange', linewidth=2)
        ax4.set_xlabel('Время')
        ax4.set_ylabel('Средняя скорость')
        ax4.set_title(f'Средняя скорость (последние {REALTIME_POINTS_LIMIT} точек)')
        ax4.grid(True, alpha=0.3)
    
    # 5. Комбинированный график
    ax5 = figure.add_subplot(235)
    if (data.get('time') and data.get('pressure') and 
        data.get('temperature') and data.get('volume')):
        
        time_short = data['time'][-COMBINED_GRAPH_POINTS:]
        
        # Нормализуем данные для совмещения на одном графике
        if len(time_short) > 0:
            pressure_short = data['pressure'][-COMBINED_GRAPH_POINTS:]
            temp_short = data['temperature'][-COMBINED_GRAPH_POINTS:]
            volume_short = data['volume'][-COMBINED_GRAPH_POINTS:]
            
            # Нормализация
            pressure_norm = (pressure_short - np.min(pressure_short)) / (np.max(pressure_short) - np.min(pressure_short) + 1e-10)
            temp_norm = (temp_short - np.min(temp_short)) / (np.max(temp_short) - np.min(temp_short) + 1e-10)
            volume_norm = (volume_short - np.min(volume_short)) / (np.max(volume_short) - np.min(volume_short) + 1e-10)
            
            ax5.plot(time_short, pressure_norm, 'b-', label='Давление')
            ax5.plot(time_short, temp_norm, 'r-', label='Температура')
            ax5.plot(time_short, volume_norm, 'g-', label='Объем')
            ax5.legend()
            ax5.set_xlabel('Время')
            ax5.set_ylabel('Нормализованные значения')
            ax5.set_title('Комбинированный график (нормализованный)')
            ax5.grid(True, alpha=0.3)
    
    # 6. Индикатор текущего состояния
    ax6 = figure.add_subplot(236)
    mode = data.get('mode', 'OFF')
    
    # Простой индикатор
    color = MODE_INDICATOR_COLORS.get(mode, 'gray')
    ax6.add_patch(plt.Circle((0.5, 0.5), 0.3, color=color, alpha=0.7))
    ax6.text(0.5, 0.5, mode, ha='center', va='center', fontsize=14, fontweight='bold')
    ax6.set_xlim(0, 1)
    ax6.set_ylim(0, 1)
    ax6.axis('off')
    ax6.set_title('Текущий режим')
    
    # Добавляем текст с последними значениями
    if data.get('pressure') and data.get('temperature') and data.get('volume'):
        info_text = f"""
        Последние значения:
        Давление: {data['pressure'][-1]:.3f}
        Температура: {data['temperature'][-1]:.3f}
        Объем: {data['volume'][-1]:.3f}
        Время: {data['time'][-1]:.1f}
        """
        ax6.text(0.5, 0.2, info_text, ha='center', va='center', 
                fontsize=8, transform=ax6.transAxes,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    figure.tight_layout()
    canvas.draw()
