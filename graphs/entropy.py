"""
Графики для второго закона термодинамики (неубывание энтропии).
H-функция Больцмана: H = -∫ f(v) ln(f(v)) dv
Энтропия: S = -k_B Σ p_i ln(p_i)
"""
import numpy as np
from scipy import stats


def calculate_velocity_entropy(velocities, n_bins=20):
    """
    Расчёт энтропии по распределению скоростей.
    S = -k_B Σ p_i ln(p_i)
    
    В наших единицах k_B = 1
    """
    if len(velocities) < 10:
        return None
    
    velocities = np.array(velocities)
    
    # Гистограмма
    hist, bin_edges = np.histogram(velocities, bins=n_bins, density=True)
    bin_width = bin_edges[1] - bin_edges[0]
    
    # Вероятности (нормированные)
    probs = hist * bin_width
    
    # Фильтруем нулевые вероятности
    probs = probs[probs > 0]
    
    if len(probs) == 0:
        return None
    
    # Энтропия
    entropy = -np.sum(probs * np.log(probs))
    
    return entropy


def calculate_spatial_entropy(positions, width, height, n_bins_x=10, n_bins_y=10):
    """
    Расчёт пространственной энтропии.
    S = -Σ p_ij ln(p_ij), где p_ij - вероятность нахождения в ячейке (i,j)
    """
    if len(positions) < 10:
        return None
    
    x_coords = [p[0] for p in positions]
    y_coords = [p[1] for p in positions]
    
    # 2D гистограмма
    hist, _, _ = np.histogram2d(x_coords, y_coords, 
                                 bins=[n_bins_x, n_bins_y],
                                 range=[[0, width], [0, height]])
    
    # Вероятности
    total = np.sum(hist)
    if total == 0:
        return None
    
    probs = hist.flatten() / total
    probs = probs[probs > 0]
    
    if len(probs) == 0:
        return None
    
    entropy = -np.sum(probs * np.log(probs))
    
    return entropy


def calculate_h_function(velocities, n_bins=30):
    """
    H-функция Больцмана.
    H = ∫ f(v) ln(f(v)) dv
    
    H уменьшается со временем (теорема H Больцмана)
    """
    if len(velocities) < 10:
        return None
    
    velocities = np.array(velocities)
    
    # Гистограмма (плотность вероятности)
    hist, bin_edges = np.histogram(velocities, bins=n_bins, density=True)
    bin_width = bin_edges[1] - bin_edges[0]
    
    # Фильтруем нулевые значения
    mask = hist > 0
    if np.sum(mask) == 0:
        return None
    
    f = hist[mask]
    
    # H = ∫ f ln(f) dv ≈ Σ f_i ln(f_i) Δv
    H = np.sum(f * np.log(f)) * bin_width
    
    return H


def theoretical_max_entropy(n_particles, volume, temperature, mass=1.0):
    """
    Теоретическая максимальная энтропия для идеального газа.
    Для 2D: S = N * k_B * (1 + ln(V/N) + ln(2πmk_B T) / 2)
    """
    if n_particles <= 0 or volume <= 0 or temperature <= 0:
        return None
    
    # В наших единицах k_B = 1
    S_max = n_particles * (1 + np.log(volume / n_particles) + np.log(2 * np.pi * mass * temperature) / 2)
    
    return S_max


def update_entropy_graphs(figure, canvas, data):
    """Обновление графиков энтропии."""
    figure.clear()
    
    entropy_history = data.get('entropy', [])
    time_data = data.get('time', [])
    velocities = data.get('velocities', [])
    positions = data.get('positions', [])
    temperature = data.get('temperature', [0])
    kinetic_energy = data.get('kinetic_energy', [])
    container_width = data.get('container_width', 500)
    container_height = data.get('container_height', 500)
    n_particles = len(positions) if positions else data.get('n_particles', 100)
    mass = data.get('particle_mass', 1.0)
    corner_start = data.get('corner_start', False)
    
    T = temperature[-1] * 100 if temperature else 1.0
    volume = container_width * container_height
    
    # Текущая энтропия
    current_velocity_entropy = calculate_velocity_entropy(velocities)
    current_spatial_entropy = calculate_spatial_entropy(positions, container_width, container_height)
    current_H = calculate_h_function(velocities)
    
    # 1. Энтропия скоростей от времени
    ax1 = figure.add_subplot(231)
    
    if len(entropy_history) > 1 and len(time_data) == len(entropy_history):
        ax1.plot(time_data, entropy_history, 'b-', linewidth=2, label='S(t)')
        
        # Теоретическая максимальная энтропия
        S_max = theoretical_max_entropy(n_particles, volume, T, mass)
        if S_max is not None:
            ax1.axhline(y=S_max, color='r', linestyle='--', linewidth=1.5, 
                       label=f'S_max ≈ {S_max:.2f}')
        
        ax1.legend(loc='best', fontsize=8)
    
    ax1.set_xlabel('Время t')
    ax1.set_ylabel('Энтропия S')
    ax1.set_title('Энтропия скоростей')
    ax1.grid(True, alpha=0.3)
    
    # 2. H-функция Больцмана
    ax2 = figure.add_subplot(232)
    
    h_history = data.get('h_function', [])
    if len(h_history) > 1 and len(time_data) == len(h_history):
        ax2.plot(time_data, h_history, 'g-', linewidth=2, label='H(t)')
        ax2.legend(loc='best', fontsize=8)
    
    ax2.set_xlabel('Время t')
    ax2.set_ylabel('H-функция')
    ax2.set_title('H-функция Больцмана (должна убывать)')
    ax2.grid(True, alpha=0.3)
    
    # 3. Пространственная энтропия
    ax3 = figure.add_subplot(233)
    
    spatial_entropy_history = data.get('spatial_entropy', [])
    if len(spatial_entropy_history) > 1 and len(time_data) == len(spatial_entropy_history):
        ax3.plot(time_data, spatial_entropy_history, 'm-', linewidth=2, label='S_пространств(t)')
        
        # Максимальная пространственная энтропия (равномерное распределение)
        S_spatial_max = np.log(100)  # для сетки 10x10
        ax3.axhline(y=S_spatial_max, color='r', linestyle='--', linewidth=1.5,
                   label=f'S_max = {S_spatial_max:.2f}')
        
        ax3.legend(loc='best', fontsize=8)
    
    ax3.set_xlabel('Время t')
    ax3.set_ylabel('Пространственная энтропия')
    ax3.set_title('Пространственная энтропия')
    ax3.grid(True, alpha=0.3)
    
    # 4. Изменение энтропии (dS/dt)
    ax4 = figure.add_subplot(234)
    
    if len(entropy_history) > 5 and len(time_data) == len(entropy_history):
        entropy_arr = np.array(entropy_history)
        time_arr = np.array(time_data)
        
        # Численная производная
        dS = np.diff(entropy_arr)
        dt = np.diff(time_arr)
        dS_dt = dS / dt
        
        ax4.plot(time_arr[1:], dS_dt, 'b-', linewidth=1, alpha=0.5)
        
        # Скользящее среднее
        if len(dS_dt) > 10:
            window = min(10, len(dS_dt) // 3)
            if window > 0:
                moving_avg = np.convolve(dS_dt, np.ones(window)/window, mode='valid')
                ax4.plot(time_arr[window:len(moving_avg)+window], moving_avg, 
                        'r-', linewidth=2, label=f'Скольз. среднее (n={window})')
        
        ax4.axhline(y=0, color='k', linestyle='--', linewidth=1)
        ax4.legend(loc='best', fontsize=8)
    
    ax4.set_xlabel('Время t')
    ax4.set_ylabel('dS/dt')
    ax4.set_title('Скорость изменения энтропии')
    ax4.grid(True, alpha=0.3)
    
    # 5. Текущее распределение по пространству (тепловая карта)
    ax5 = figure.add_subplot(235)
    
    if len(positions) > 0:
        x_coords = [p[0] for p in positions]
        y_coords = [p[1] for p in positions]
        
        heatmap, xedges, yedges = np.histogram2d(x_coords, y_coords, bins=10,
                                                  range=[[0, container_width], [0, container_height]])
        
        im = ax5.imshow(heatmap.T, extent=[0, container_width, 0, container_height],
                        origin='lower', cmap='YlOrRd', aspect='auto')
        figure.colorbar(im, ax=ax5, label='Количество частиц')
        
        if corner_start:
            ax5.set_title('Распределение (старт из угла)')
        else:
            ax5.set_title('Пространственное распределение')
    else:
        ax5.set_title('Пространственное распределение')
    
    ax5.set_xlabel('x')
    ax5.set_ylabel('y')
    ax5.grid(True, alpha=0.3)
    
    # 6. Статистика
    ax6 = figure.add_subplot(236)
    ax6.axis('off')
    
    # Проверка второго закона
    entropy_increasing = False
    if len(entropy_history) > 10:
        # Проверяем тренд энтропии
        recent_entropy = np.array(entropy_history[-20:])
        if len(recent_entropy) > 5:
            slope, _, r_value, _, _ = stats.linregress(range(len(recent_entropy)), recent_entropy)
            entropy_increasing = slope >= -0.01  # Допускаем небольшие флуктуации
    
    corner_status = "✓ ВКЛ" if corner_start else "✗ ВЫКЛ"
    
    stats_text = f"""ВТОРОЙ ЗАКОН ТЕРМОДИНАМИКИ

Параметры:
  Частиц N = {n_particles}
  Температура T = {T:.4f}
  Объём V = {volume}
  
Старт из угла: {corner_status}

ТЕКУЩИЕ ЗНАЧЕНИЯ:
"""
    
    if current_velocity_entropy is not None:
        stats_text += f"  S_скоростей = {current_velocity_entropy:.4f}\n"
    else:
        stats_text += "  S_скоростей: мало данных\n"
    
    if current_spatial_entropy is not None:
        stats_text += f"  S_пространств = {current_spatial_entropy:.4f}\n"
    else:
        stats_text += "  S_пространств: мало данных\n"
    
    if current_H is not None:
        stats_text += f"  H-функция = {current_H:.4f}\n"
    else:
        stats_text += "  H-функция: мало данных\n"
    
    S_max = theoretical_max_entropy(n_particles, volume, T, mass)
    if S_max is not None:
        stats_text += f"\n  S_теор_max ≈ {S_max:.4f}\n"
    
    # Вывод по второму закону
    stats_text += "\n"
    if len(entropy_history) > 10:
        if entropy_increasing:
            stats_text += """ВТОРОЙ ЗАКОН:
  ✓ dS/dt ≥ 0
  ✓ ВЫПОЛНЯЕТСЯ"""
        else:
            stats_text += """ВТОРОЙ ЗАКОН:
  ⚠ dS/dt < 0
  (флуктуации)"""
    else:
        stats_text += "⏳ Накопление данных..."
    
    ax6.text(0.05, 0.95, stats_text, transform=ax6.transAxes, fontsize=8,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    figure.tight_layout()
    canvas.draw()
