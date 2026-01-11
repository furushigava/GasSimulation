"""
Функции для обновления статистических графиков.
"""
import numpy as np

# Дефолтные значения для статистических графиков
ROLLING_WINDOW_DIVISOR = 10
EMA_ALPHA = 0.1


def update_statistical_graphs(figure, canvas, data):
    """Обновление статистических графиков"""
    figure.clear()
    
    if not data.get('time') or len(data['time']) < 2:
        canvas.draw()
        return
    
    # 1. Скользящее среднее давления
    ax1 = figure.add_subplot(231)
    if data.get('pressure'):
        pressure = data['pressure']
        window = min(20, len(pressure) // ROLLING_WINDOW_DIVISOR + 1)
        if window > 1:
            rolling_mean = np.convolve(pressure, np.ones(window)/window, mode='valid')
            ax1.plot(data['time'][:len(rolling_mean)], rolling_mean, 'b-', linewidth=2, label='Скользящее среднее')
            ax1.plot(data['time'][:len(pressure)], pressure, 'gray', alpha=0.5, linewidth=1, label='Исходные данные')
            ax1.legend()
    ax1.set_xlabel('Время')
    ax1.set_ylabel('Давление')
    ax1.set_title('Скользящее среднее давления')
    ax1.grid(True, alpha=0.3)
    
    # 2. Стандартное отклонение скоростей
    ax2 = figure.add_subplot(232)
    if data.get('velocities') and len(data['velocities']) > 10:
        # Разбиваем на группы для вычисления статистики
        velocities = data['velocities']
        group_size = max(1, len(velocities) // 20)
        groups = [velocities[i:i+group_size] for i in range(0, len(velocities), group_size)]
        stds = [np.std(group) for group in groups if len(group) > 1]
        ax2.bar(range(len(stds)), stds, alpha=0.7)
    ax2.set_xlabel('Группа')
    ax2.set_ylabel('Стандартное отклонение')
    ax2.set_title('Стандартное отклонение скоростей по группам')
    ax2.grid(True, alpha=0.3)
    
    # 3. Гистограмма давлений
    ax3 = figure.add_subplot(233)
    if data.get('pressure'):
        ax3.hist(data['pressure'], bins=20, alpha=0.7, color='green', edgecolor='black')
    ax3.set_xlabel('Давление')
    ax3.set_ylabel('Частота')
    ax3.set_title('Распределение давлений')
    ax3.grid(True, alpha=0.3)
    
    # 4. Экспоненциальное скользящее среднее
    ax4 = figure.add_subplot(234)
    if data.get('temperature'):
        temp = data['temperature']
        alpha = EMA_ALPHA
        ema = [temp[0]]
        for i in range(1, len(temp)):
            ema.append(alpha * temp[i] + (1 - alpha) * ema[-1])
        ax4.plot(data['time'], temp, 'gray', alpha=0.5, label='Исходные')
        ax4.plot(data['time'], ema, 'red', linewidth=2, label='EMA')
        ax4.legend()
    ax4.set_xlabel('Время')
    ax4.set_ylabel('Температура')
    ax4.set_title('Экспоненциальное скользящее среднее')
    ax4.grid(True, alpha=0.3)
    
    # 5. Процентное изменение объема
    ax5 = figure.add_subplot(235)
    if data.get('volume') and len(data['volume']) > 1:
        volume = data['volume']
        pct_change = [(volume[i] - volume[i-1]) / volume[i-1] * 100 
                     for i in range(1, len(volume))]
        ax5.plot(data['time'][1:], pct_change, 'orange', linewidth=2)
        ax5.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax5.set_xlabel('Время')
    ax5.set_ylabel('Изменение объема (%)')
    ax5.set_title('Процентное изменение объема')
    ax5.grid(True, alpha=0.3)
    
    # 6. Статистика столкновений
    ax6 = figure.add_subplot(236)
    if data.get('collision_count'):
        stats_text = f"""
        Общее столкновений: {data.get('collision_count', 0)}
        Текущий режим: {data.get('mode', 'N/A')}
        Количество точек: {len(data.get('time', []))}
        Последнее давление: {data.get('pressure', [0])[-1]:.3f}
        Последний объем: {data.get('volume', [0])[-1]:.3f}
        """
        ax6.text(0.1, 0.5, stats_text, transform=ax6.transAxes, fontsize=10,
                verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax6.axis('off')
        ax6.set_title('Статистика системы')
    
    figure.tight_layout()
    canvas.draw()
