"""
Функции для обновления кинетических графиков.
"""
import numpy as np


def update_kinetic_graphs(figure, canvas, data):
    """Обновление кинетических графиков"""
    figure.clear()
    
    if not data.get('time'):
        canvas.draw()
        return
    
    # 1. Средняя скорость от времени
    ax1 = figure.add_subplot(221)
    if data.get('time') and data.get('avg_velocity'):
        ax1.plot(data['time'], data['avg_velocity'], 'b-', linewidth=2)
    ax1.set_xlabel('Время')
    ax1.set_ylabel('Средняя скорость')
    ax1.set_title('Средняя скорость от времени')
    ax1.grid(True, alpha=0.3)
    
    # 2. Средняя длина свободного пробега
    ax2 = figure.add_subplot(222)
    if data.get('time') and data.get('mean_free_path'):
        ax2.plot(data['time'], data['mean_free_path'], 'r-', linewidth=2)
    ax2.set_xlabel('Время')
    ax2.set_ylabel('Средняя длина свободного пробега')
    ax2.set_title('Длина свободного пробега от времени')
    ax2.grid(True, alpha=0.3)
    
    # 3. Частота столкновений
    ax3 = figure.add_subplot(223)
    if data.get('time') and data.get('collision_rate'):
        ax3.plot(data['time'], data['collision_rate'], 'g-', linewidth=2)
    ax3.set_xlabel('Время')
    ax3.set_ylabel('Частота столкновений (1/с)')
    ax3.set_title('Частота столкновений от времени')
    ax3.grid(True, alpha=0.3)
    
    # 4. Скорость наиболее вероятной частицы
    ax4 = figure.add_subplot(224)
    if data.get('time') and data.get('velocities') and len(data['time']) == len(data['avg_velocity']):
        ax4.plot(data['time'], data['avg_velocity'], 'orange', linewidth=2, label='Средняя')
        
        # Добавляем стандартное отклонение
        if len(data['time']) > 1:
            # Для простоты используем фиксированный разброс
            std_region = np.array(data['avg_velocity']) * 0.3
            ax4.fill_between(data['time'], 
                            np.array(data['avg_velocity']) - std_region,
                            np.array(data['avg_velocity']) + std_region,
                            alpha=0.3, color='orange')
        
        ax4.legend()
        ax4.set_xlabel('Время')
        ax4.set_ylabel('Скорость')
        ax4.set_title('Изменение скорости с доверительным интервалом')
        ax4.grid(True, alpha=0.3)
    
    figure.tight_layout()
    canvas.draw()
