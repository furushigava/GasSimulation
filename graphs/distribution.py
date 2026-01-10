"""
Функции для обновления графиков распределений.
"""
import numpy as np
from scipy import stats


def update_distribution_graphs(figure, canvas, data):
    """Обновление графиков распределений"""
    figure.clear()
    
    if not data.get('velocities'):
        canvas.draw()
        return
    
    velocities = data['velocities']
    
    # 1. Гистограмма распределения скоростей
    ax1 = figure.add_subplot(231)
    ax1.hist(velocities, bins=30, density=True, alpha=0.7, color='blue', edgecolor='black')
    
    # Теоретическое распределение Максвелла-Больцмана
    if len(velocities) > 1:
        mean_v = np.mean(velocities)
        std_v = np.std(velocities)
        x = np.linspace(0, max(velocities) * 1.5, 100)
        # Упрощенное распределение Максвелла-Больцмана
        pdf = (x / (std_v**2)) * np.exp(-x**2 / (2 * std_v**2))
        ax1.plot(x, pdf, 'r-', linewidth=2, label='Максвелл-Больцман')
        ax1.legend()
    
    ax1.set_xlabel('Скорость')
    ax1.set_ylabel('Плотность вероятности')
    ax1.set_title('Распределение скоростей')
    ax1.grid(True, alpha=0.3)
    
    # 2. Кумулятивная функция распределения
    ax2 = figure.add_subplot(232)
    if len(velocities) > 1:
        sorted_v = np.sort(velocities)
        cdf = np.arange(1, len(sorted_v) + 1) / len(sorted_v)
        ax2.plot(sorted_v, cdf, 'g-', linewidth=2)
    ax2.set_xlabel('Скорость')
    ax2.set_ylabel('Вероятность')
    ax2.set_title('Кумулятивная функция распределения')
    ax2.grid(True, alpha=0.3)
    
    # 3. Box plot скоростей
    ax3 = figure.add_subplot(233)
    if velocities:
        bp = ax3.boxplot([velocities], patch_artist=True)
        bp['boxes'][0].set_facecolor('lightblue')
        bp['medians'][0].set_color('red')
    ax3.set_ylabel('Скорость')
    ax3.set_title('Box plot скоростей')
    ax3.grid(True, alpha=0.3)
    
    # 4. Распределение кинетической энергии
    ax4 = figure.add_subplot(234)
    if velocities:
        kinetic_energies = [0.5 * v**2 for v in velocities]
        ax4.hist(kinetic_energies, bins=30, alpha=0.7, color='green', edgecolor='black')
    ax4.set_xlabel('Кинетическая энергия')
    ax4.set_ylabel('Частота')
    ax4.set_title('Распределение кинетической энергии')
    ax4.grid(True, alpha=0.3)
    
    # 5. Q-Q plot
    ax5 = figure.add_subplot(235)
    if len(velocities) > 10:
        stats.probplot(velocities, dist="norm", plot=ax5)
    ax5.set_title('Q-Q plot (нормальное распределение)')
    ax5.grid(True, alpha=0.3)
    
    # 6. Плотность распределения (KDE)
    ax6 = figure.add_subplot(236)
    if len(velocities) > 5:
        from scipy.stats import gaussian_kde
        kde = gaussian_kde(velocities)
        x_range = np.linspace(0, max(velocities) * 1.2, 200)
        ax6.plot(x_range, kde(x_range), 'purple', linewidth=2)
        ax6.fill_between(x_range, kde(x_range), alpha=0.3, color='purple')
    ax6.set_xlabel('Скорость')
    ax6.set_ylabel('Плотность')
    ax6.set_title('Плотность распределения (KDE)')
    ax6.grid(True, alpha=0.3)
    
    figure.tight_layout()
    canvas.draw()
