"""
Графики для броуновского движения и соотношения Эйнштейна.
⟨r²⟩ = 2*n*D*t, где n - размерность (2D), D - коэффициент диффузии
"""
import numpy as np
from scipy import stats


def calculate_msd(positions_history):
    """
    Расчёт среднеквадратичного смещения (MSD) из истории позиций.
    
    Args:
        positions_history: список списков позиций [(x0, y0), (x1, y1), ...]
                          для каждого временного шага
    
    Returns:
        msd_values: массив значений MSD для каждого временного лага
        time_lags: массив временных лагов
    """
    if len(positions_history) < 2:
        return np.array([]), np.array([])
    
    n_steps = len(positions_history)
    max_lag = min(n_steps // 2, 100)  # Ограничиваем максимальный лаг
    
    msd_values = []
    time_lags = []
    
    for lag in range(1, max_lag + 1):
        displacements_squared = []
        
        for t in range(n_steps - lag):
            if len(positions_history[t]) > 0 and len(positions_history[t + lag]) > 0:
                # Берём первую частицу (или среднее по всем отслеживаемым)
                x0, y0 = positions_history[t][0]
                x1, y1 = positions_history[t + lag][0]
                
                dr_squared = (x1 - x0)**2 + (y1 - y0)**2
                displacements_squared.append(dr_squared)
        
        if displacements_squared:
            msd_values.append(np.mean(displacements_squared))
            time_lags.append(lag)
    
    return np.array(msd_values), np.array(time_lags)


def fit_diffusion_coefficient(msd, time_lags, time_step=0.1):
    """
    Фит коэффициента диффузии из MSD.
    Для 2D: MSD = 4*D*t => D = MSD / (4*t)
    
    Returns:
        D: коэффициент диффузии
        r_squared: коэффициент детерминации
    """
    if len(msd) < 3 or len(time_lags) < 3:
        return None, None
    
    # Переводим лаги во время
    t = time_lags * time_step
    
    # Линейная регрессия MSD = 4*D*t (через начало координат)
    # Используем обычную линейную регрессию для лучшего фита
    slope, intercept, r_value, p_value, std_err = stats.linregress(t, msd)
    
    D = slope / 4  # Для 2D: MSD = 4*D*t
    r_squared = r_value ** 2
    
    return D, r_squared


def einstein_relation_check(D, T, radius, viscosity=1.0):
    """
    Проверка соотношения Эйнштейна: D = k_B*T / (6*π*η*r)
    Для 2D: D = k_B*T / (4*π*η*r)
    
    В наших единицах k_B = 1
    
    Returns:
        D_theoretical: теоретический коэффициент диффузии
        relative_error: относительная ошибка
    """
    if radius <= 0 or viscosity <= 0:
        return None, None
    
    # Для 2D системы
    D_theoretical = T / (4 * np.pi * viscosity * radius)
    
    if D_theoretical > 0 and D is not None:
        relative_error = abs(D - D_theoretical) / D_theoretical * 100
    else:
        relative_error = None
    
    return D_theoretical, relative_error


def update_brownian_graphs(figure, canvas, data):
    """Обновление графиков броуновского движения."""
    figure.clear()
    
    positions_history = data.get('positions_history', [])
    time_data = data.get('time', [])
    msd_data = data.get('msd', [])
    brownian_config = data.get('brownian_config', {})
    temperature = data.get('temperature', [0])[-1] if data.get('temperature') else 1.0
    
    # Параметры из конфигурации
    time_step = data.get('time_step', 0.1)
    particle_radius = brownian_config.get('large_radius', 15) if brownian_config.get('enabled', False) else data.get('particle_radius', 5)
    
    # 1. Траектория броуновской частицы
    ax1 = figure.add_subplot(231)
    
    trajectory = data.get('brownian_trajectory', [])
    if trajectory and len(trajectory) > 1:
        x_coords = [p[0] for p in trajectory]
        y_coords = [p[1] for p in trajectory]
        
        # Цветовая шкала по времени
        colors = np.linspace(0, 1, len(x_coords))
        scatter = ax1.scatter(x_coords, y_coords, c=colors, cmap='viridis', s=1, alpha=0.7)
        ax1.plot(x_coords, y_coords, 'b-', alpha=0.3, linewidth=0.5)
        
        # Начальная и конечная точки
        ax1.scatter([x_coords[0]], [y_coords[0]], c='green', s=50, marker='o', label='Старт', zorder=5)
        ax1.scatter([x_coords[-1]], [y_coords[-1]], c='red', s=50, marker='x', label='Финиш', zorder=5)
        
        ax1.legend(loc='best', fontsize=8)
        figure.colorbar(scatter, ax=ax1, label='Время')
    
    ax1.set_xlabel('x')
    ax1.set_ylabel('y')
    ax1.set_title('Траектория броуновской частицы')
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3)
    
    # 2. MSD vs время
    ax2 = figure.add_subplot(232)
    
    if len(msd_data) > 3:
        time_lags = np.arange(1, len(msd_data) + 1) * time_step
        ax2.plot(time_lags, msd_data, 'b-', linewidth=2, label='MSD(t)')
        
        # Фит линейной зависимости
        D, r_squared = fit_diffusion_coefficient(np.array(msd_data), np.arange(1, len(msd_data) + 1), time_step)
        
        if D is not None:
            msd_fit = 4 * D * time_lags
            ax2.plot(time_lags, msd_fit, 'r--', linewidth=2, 
                     label=f'Фит: 4Dt (D={D:.4f})')
            ax2.legend(loc='best', fontsize=8)
    
    ax2.set_xlabel('Время t')
    ax2.set_ylabel('⟨r²⟩')
    ax2.set_title('Среднеквадратичное смещение')
    ax2.grid(True, alpha=0.3)
    
    # 3. MSD vs √t (для проверки аномальной диффузии)
    ax3 = figure.add_subplot(233)
    
    if len(msd_data) > 3:
        time_lags = np.arange(1, len(msd_data) + 1) * time_step
        sqrt_msd = np.sqrt(msd_data)
        
        ax3.plot(time_lags, sqrt_msd, 'g-', linewidth=2, label='√⟨r²⟩')
        
        # Теоретическая зависимость √(4Dt)
        if D is not None:
            sqrt_msd_theory = np.sqrt(4 * D * time_lags)
            ax3.plot(time_lags, sqrt_msd_theory, 'r--', linewidth=2, label='√(4Dt)')
            ax3.legend(loc='best', fontsize=8)
    
    ax3.set_xlabel('Время t')
    ax3.set_ylabel('√⟨r²⟩')
    ax3.set_title('Корень из MSD')
    ax3.grid(True, alpha=0.3)
    
    # 4. log(MSD) vs log(t) - определение показателя диффузии
    ax4 = figure.add_subplot(234)
    
    if len(msd_data) > 5:
        time_lags = np.arange(1, len(msd_data) + 1) * time_step
        
        # Фильтруем нулевые значения
        mask = np.array(msd_data) > 0
        if np.sum(mask) > 3:
            log_t = np.log(time_lags[mask])
            log_msd = np.log(np.array(msd_data)[mask])
            
            ax4.plot(log_t, log_msd, 'b-', linewidth=2, label='log(MSD)')
            
            # Линейный фит для определения показателя α: MSD ∝ t^α
            slope, intercept, r_value, p_value, std_err = stats.linregress(log_t, log_msd)
            
            fit_line = slope * log_t + intercept
            ax4.plot(log_t, fit_line, 'r--', linewidth=2, 
                     label=f'Фит: α = {slope:.3f}')
            
            # Нормальная диффузия: α = 1
            if abs(slope - 1) < 0.2:
                diffusion_type = "Нормальная"
            elif slope < 1:
                diffusion_type = "Субдиффузия"
            else:
                diffusion_type = "Супердиффузия"
            
            ax4.set_title(f'log-log график ({diffusion_type})')
            ax4.legend(loc='best', fontsize=8)
    else:
        ax4.set_title('log-log график')
    
    ax4.set_xlabel('log(t)')
    ax4.set_ylabel('log(⟨r²⟩)')
    ax4.grid(True, alpha=0.3)
    
    # 5. Распределение смещений
    ax5 = figure.add_subplot(235)
    
    if trajectory and len(trajectory) > 10:
        x_coords = np.array([p[0] for p in trajectory])
        y_coords = np.array([p[1] for p in trajectory])
        
        # Смещения за 1 шаг
        dx = np.diff(x_coords)
        dy = np.diff(y_coords)
        
        # Гистограмма
        all_displacements = np.concatenate([dx, dy])
        ax5.hist(all_displacements, bins=30, density=True, alpha=0.7, 
                 color='blue', edgecolor='black', label='Эмпирическое')
        
        # Теоретическое нормальное распределение
        if len(all_displacements) > 5:
            mu, std = np.mean(all_displacements), np.std(all_displacements)
            x_range = np.linspace(min(all_displacements), max(all_displacements), 100)
            pdf = stats.norm.pdf(x_range, mu, std)
            ax5.plot(x_range, pdf, 'r-', linewidth=2, label='Нормальное')
            ax5.legend(loc='best', fontsize=8)
    
    ax5.set_xlabel('Смещение')
    ax5.set_ylabel('Плотность')
    ax5.set_title('Распределение смещений')
    ax5.grid(True, alpha=0.3)
    
    # 6. Статистика и соотношение Эйнштейна
    ax6 = figure.add_subplot(236)
    ax6.axis('off')
    
    # Расчёт коэффициента диффузии
    D_measured = None
    r_squared = None
    
    if len(msd_data) > 3:
        D_measured, r_squared = fit_diffusion_coefficient(
            np.array(msd_data), 
            np.arange(1, len(msd_data) + 1), 
            time_step
        )
    
    # Теоретический D из соотношения Эйнштейна
    D_theoretical, rel_error = einstein_relation_check(
        D_measured, temperature, particle_radius, viscosity=1.0
    )
    
    stats_text = f"""БРОУНОВСКОЕ ДВИЖЕНИЕ

Параметры:
  Радиус частицы r = {particle_radius}
  Температура T = {temperature:.4f}
  Шаг времени dt = {time_step}

Измерения:
  Точек траектории: {len(trajectory) if trajectory else 0}
  Точек MSD: {len(msd_data)}

КОЭФФИЦИЕНТ ДИФФУЗИИ:
"""
    
    if D_measured is not None:
        stats_text += f"""  D (измеренный) = {D_measured:.6f}
  R² фита = {r_squared:.4f}
"""
    else:
        stats_text += "  Недостаточно данных\n"
    
    if D_theoretical is not None:
        stats_text += f"""
СООТНОШЕНИЕ ЭЙНШТЕЙНА:
  D = k_B*T / (4πηr)
  D (теоретич.) = {D_theoretical:.6f}
"""
        if rel_error is not None:
            einstein_check = "✓" if rel_error < 50 else "✗"
            stats_text += f"""  Отн. ошибка = {rel_error:.1f}%
  {einstein_check} {'ПОДТВЕРЖДЕНО' if rel_error < 50 else 'НЕ ПОДТВЕРЖДЕНО'}
"""
    
    # Показатель диффузии
    if len(msd_data) > 5:
        time_lags = np.arange(1, len(msd_data) + 1) * time_step
        mask = np.array(msd_data) > 0
        if np.sum(mask) > 3:
            log_t = np.log(time_lags[mask])
            log_msd = np.log(np.array(msd_data)[mask])
            alpha, _, _, _, _ = stats.linregress(log_t, log_msd)
            
            stats_text += f"""
ПОКАЗАТЕЛЬ ДИФФУЗИИ:
  α = {alpha:.3f}
  ⟨r²⟩ ∝ t^α
  {"✓ Норм. диффузия" if abs(alpha - 1) < 0.2 else "⚠ Аномальная"}
"""
    # print(stats_text)
    ax6.text(0.05, 0.95, stats_text, transform=ax6.transAxes, fontsize=8,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
    
    figure.tight_layout()
    canvas.draw()
