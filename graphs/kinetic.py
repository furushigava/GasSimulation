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
        avg_vel = np.array(data['avg_velocity'])
        ax4.plot(data['time'], avg_vel, 'orange', linewidth=2, label='Средняя')
        
        # Вычисляем реальное стандартное отклонение из скоростей частиц
        if len(data['time']) > 1 and len(data['velocities']) > 0:
            # Получаем текущее std из последнего набора скоростей
            current_velocities = np.array(data['velocities'][-1]) if isinstance(data['velocities'][-1], (list, np.ndarray)) else data['velocities']
            current_std = np.std(current_velocities) if len(current_velocities) > 0 else avg_vel[-1] * 0.3
            
            # Используем относительное std для всего графика
            std_ratio = current_std / avg_vel[-1] if avg_vel[-1] > 0 else 0.3
            std_region = avg_vel * std_ratio
            
            # Доверительный интервал (±1 std ≈ 68%)
            lower_bound = avg_vel - std_region
            upper_bound = avg_vel + std_region
            
            ax4.fill_between(data['time'], lower_bound, upper_bound,
                            alpha=0.3, color='orange', label=f'±1σ (68% ДИ)')
            
            # Добавляем подписи с информацией
            current_mean = avg_vel[-1]
            info_text = f'σ = {current_std:.3f}\nДИ: [{current_mean - current_std:.3f}, {current_mean + current_std:.3f}]\nОтн. σ = {std_ratio*100:.1f}%'
            ax4.text(0.02, 0.98, info_text, transform=ax4.transAxes, fontsize=8,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        ax4.legend(loc='upper right')
        ax4.set_xlabel('Время')
        ax4.set_ylabel('Скорость')
        ax4.set_title('Изменение скорости с доверительным интервалом')
        ax4.grid(True, alpha=0.3)
    
    figure.tight_layout()
    canvas.draw()
