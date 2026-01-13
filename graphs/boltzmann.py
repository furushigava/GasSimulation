"""
Графики для распределения Больцмана в гравитационном поле.
Барометрическая формула: ρ(h) = ρ₀ * exp(-m*g*h / k_B*T)
"""
import numpy as np
from scipy import stats
from scipy.optimize import curve_fit


def boltzmann_height_distribution(h, T, m, g, rho_0=1.0):
    """
    Распределение Больцмана по высоте (барометрическая формула).
    ρ(h) = ρ₀ * exp(-m*g*h / k_B*T)
    
    В наших единицах k_B = 1
    """
    if T <= 0:
        return np.zeros_like(h)
    return rho_0 * np.exp(-m * g * h / T)


def fit_temperature_from_height(heights, m, g, n_bins=20):
    """
    Фит температуры из распределения по высоте.
    
    Returns:
        T_fit: температура из фита
        rho_0_fit: плотность при h=0
        r_squared: коэффициент детерминации
    """
    if len(heights) < 30 or g <= 0:
        return None, None, None
    
    heights = np.array(heights)
    
    # Создаём гистограмму плотности по высоте
    hist, bin_edges = np.histogram(heights, bins=n_bins, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    # Фильтруем нулевые значения
    mask = hist > 0
    if np.sum(mask) < 5:
        return None, None, None
    
    h_fit = bin_centers[mask]
    rho_fit = hist[mask]
    
    try:
        # Логарифмический фит: ln(ρ) = ln(ρ₀) - (m*g/T)*h
        log_rho = np.log(rho_fit)
        slope, intercept, r_value, p_value, std_err = stats.linregress(h_fit, log_rho)
        
        # slope = -m*g/T => T = -m*g/slope
        if slope < 0:
            T_fit = -m * g / slope
            rho_0_fit = np.exp(intercept)
            r_squared = r_value ** 2
            return T_fit, rho_0_fit, r_squared
        else:
            return None, None, None
            
    except Exception:
        return None, None, None


def chi_squared_boltzmann(heights, T, m, g, n_bins=20):
    """
    Тест χ² для проверки соответствия распределению Больцмана.
    """
    if len(heights) < 30 or T <= 0 or g <= 0:
        return None, None, None
    
    heights = np.array(heights)
    max_h = np.max(heights)
    
    # Гистограмма
    hist, bin_edges = np.histogram(heights, bins=n_bins, density=False)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_width = bin_edges[1] - bin_edges[0]
    
    # Нормировочный коэффициент для теоретического распределения
    # ∫₀^H ρ₀*exp(-m*g*h/T) dh = ρ₀*T/(m*g) * (1 - exp(-m*g*H/T))
    norm_factor = T / (m * g) * (1 - np.exp(-m * g * max_h / T))
    if norm_factor <= 0:
        return None, None, None
    
    # Ожидаемые частоты
    expected_probs = (1/norm_factor) * np.exp(-m * g * bin_centers / T) * bin_width
    expected_freq = expected_probs * len(heights)
    
    # Фильтруем бины с малым ожидаемым значением
    mask = expected_freq >= 5
    if np.sum(mask) < 3:
        return None, None, None
    
    observed = hist[mask]
    expected = expected_freq[mask]
    
    # χ² статистика
    chi2 = np.sum((observed - expected)**2 / expected)
    df = len(observed) - 1
    p_value = 1 - stats.chi2.cdf(chi2, df)
    
    return chi2, p_value, df


def update_boltzmann_graphs(figure, canvas, data):
    """Обновление графиков распределения Больцмана."""
    figure.clear()
    
    positions = data.get('positions', [])
    gravity_config = data.get('gravity_config', {})
    temperature_data = data.get('temperature', [0])
    mass = data.get('particle_mass', 1.0)
    container_height = data.get('container_height', 500)
    
    g = gravity_config.get('g', 0.1)
    gravity_enabled = gravity_config.get('enabled', False)
    
    # Температура из симуляции (значение уже передаётся из симуляции)
    T_sim = temperature_data[-1] if temperature_data else 1.0
    
    # Извлекаем высоты (y координата, но инвертируем: h = max_y - y)
    heights = []
    if positions:
        max_y = container_height
        heights = [max_y - p[1] for p in positions]  # h = 0 внизу
    
    heights = np.array(heights) if heights else np.array([])
    
    # 1. Гистограмма распределения по высоте
    ax1 = figure.add_subplot(231)
    
    if len(heights) > 0 and gravity_enabled:
        hist_values, bin_edges, _ = ax1.hist(heights, bins=25, density=True, 
                                              alpha=0.7, color='blue', edgecolor='black',
                                              orientation='horizontal', label='Симуляция')
        
        # Теоретическое распределение Больцмана
        h_range = np.linspace(0, max(heights), 200)
        
        # Нормировка
        max_h = max(heights)
        if T_sim > 0 and g > 0:
            norm = T_sim / (mass * g) * (1 - np.exp(-mass * g * max_h / T_sim))
            if norm > 0:
                boltzmann_pdf = (1/norm) * np.exp(-mass * g * h_range / T_sim)
                ax1.plot(boltzmann_pdf, h_range, 'r-', linewidth=2, 
                         label=f'Больцман (T={T_sim:.1f})')
        
        ax1.legend(loc='best', fontsize=8)
    elif len(heights) > 0:
        ax1.hist(heights, bins=25, density=True, alpha=0.7, color='blue', 
                 edgecolor='black', orientation='horizontal')
        ax1.text(0.5, 0.5, 'Гравитация\nвыключена', transform=ax1.transAxes,
                ha='center', va='center', fontsize=12, color='red')
    
    ax1.set_ylabel('Высота h')
    ax1.set_xlabel('Плотность ρ(h)')
    ax1.set_title('Распределение по высоте')
    ax1.grid(True, alpha=0.3)
    
    # 2. Плотность vs высота (обычный график)
    ax2 = figure.add_subplot(232)
    
    if len(heights) > 10 and gravity_enabled:
        # Бинирование по высоте
        n_bins = 20
        hist, bin_edges = np.histogram(heights, bins=n_bins, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        ax2.scatter(bin_centers, hist, c='blue', s=50, label='Симуляция')
        
        # Теоретическая кривая
        max_h = max(heights)
        if T_sim > 0 and g > 0:
            norm = T_sim / (mass * g) * (1 - np.exp(-mass * g * max_h / T_sim))
            if norm > 0:
                h_range = np.linspace(0, max_h, 100)
                rho_theory = (1/norm) * np.exp(-mass * g * h_range / T_sim)
                ax2.plot(h_range, rho_theory, 'r-', linewidth=2, label='Теория')
        
        ax2.legend(loc='best', fontsize=8)
    
    ax2.set_xlabel('Высота h')
    ax2.set_ylabel('Плотность ρ(h)')
    ax2.set_title('Распределение Больцмана по высоте')
    ax2.grid(True, alpha=0.3)
    
    # 3. log(ρ) vs h (линеаризация)
    ax3 = figure.add_subplot(233)
    
    T_fit = None
    r_squared = None
    
    if len(heights) > 20 and gravity_enabled and g > 0:
        n_bins = 20
        hist, bin_edges = np.histogram(heights, bins=n_bins, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        # Фильтруем нулевые значения
        mask = hist > 0
        if np.sum(mask) >= 5:
            h_valid = bin_centers[mask]
            rho_valid = hist[mask]
            log_rho = np.log(rho_valid)
            
            ax3.scatter(h_valid, log_rho, c='blue', s=50, label='ln(ρ) измеренное')
            
            # Линейный фит
            slope, intercept, r_value, p_value, std_err = stats.linregress(h_valid, log_rho)
            fit_line = slope * h_valid + intercept
            ax3.plot(h_valid, fit_line, 'r-', linewidth=2, 
                     label=f'Линейный фит (R²={r_value**2:.3f})')
            
            # T из фита: slope = -m*g/T
            if slope < 0:
                T_fit = -mass * g / slope
                r_squared = r_value ** 2
                ax3.set_title(f'Линеаризация (T_fit={T_fit:.2f})')
            else:
                ax3.set_title('Линеаризация')
            
            ax3.legend(loc='best', fontsize=8)
    else:
        ax3.set_title('Линеаризация')
    
    ax3.set_xlabel('Высота h')
    ax3.set_ylabel('ln(ρ)')
    ax3.grid(True, alpha=0.3)
    
    # 4. Сравнение T_sim и T_fit
    ax4 = figure.add_subplot(234)
    
    T_history = data.get('boltzmann_T_history', [])
    time_data = data.get('time', [])
    
    if T_history and time_data and len(T_history) == len(time_data):
        ax4.plot(time_data, data.get('temperature', []), 
                 'b-', linewidth=2, label='T (симуляция)')
        ax4.plot(time_data, T_history, 'r--', linewidth=2, label='T (из Больцмана)')
        ax4.legend(loc='best', fontsize=8)
    elif T_fit is not None:
        ax4.bar(['T_сим', 'T_фит'], [T_sim, T_fit], color=['blue', 'red'], alpha=0.7)
        ax4.axhline(y=T_sim, color='blue', linestyle='--', alpha=0.5)
    
    ax4.set_ylabel('Температура T')
    ax4.set_title('Сравнение температур')
    ax4.grid(True, alpha=0.3)
    
    # 5. 2D карта плотности
    ax5 = figure.add_subplot(235)
    
    if len(positions) > 10:
        x_coords = [p[0] for p in positions]
        y_coords = [container_height - p[1] for p in positions]  # инвертируем Y
        
        # Тепловая карта
        heatmap, xedges, yedges = np.histogram2d(x_coords, y_coords, bins=20)
        extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
        
        im = ax5.imshow(heatmap.T, extent=extent, origin='lower', 
                        cmap='hot', aspect='auto')
        figure.colorbar(im, ax=ax5, label='Плотность')
        
        if gravity_enabled:
            ax5.set_title('Карта плотности (гравитация вкл.)')
        else:
            ax5.set_title('Карта плотности (гравитация выкл.)')
    
    ax5.set_xlabel('x')
    ax5.set_ylabel('Высота h')
    ax5.grid(True, alpha=0.3)
    
    # 6. Статистика
    ax6 = figure.add_subplot(236)
    ax6.axis('off')
    
    # Тест χ²
    chi2, chi2_p, chi2_df = chi_squared_boltzmann(heights, T_sim, mass, g) if gravity_enabled else (None, None, None)
    
    status = "✓ ВКЛ" if gravity_enabled else "✗ ВЫКЛ"
    
    stats_text = f"""РАСПРЕДЕЛЕНИЕ БОЛЬЦМАНА

Гравитация: {status}
  g = {g:.3f}
  
Параметры:
  Масса m = {mass}
  T (симуляция) = {T_sim:.4f}
  Частиц = {len(heights)}
  
"""
    
    if gravity_enabled and T_fit is not None:
        rel_error = abs(T_fit - T_sim) / T_sim * 100 if T_sim > 0 else 0
        stats_text += f"""ФИТИРОВАНИЕ:
  T (из Больцмана) = {T_fit:.4f}
  R² = {r_squared:.4f}
  Отн. ошибка T = {rel_error:.1f}%
  
"""
    
    if chi2 is not None:
        chi2_result = "✓ ПРОЙДЕН" if chi2_p > 0.05 else "✗ ОТКЛОНЁН"
        stats_text += f"""χ²-ТЕСТ:
  χ² = {chi2:.2f}
  p-value = {chi2_p:.4f}
  {chi2_result}
  
"""
    
    # Вывод
    if gravity_enabled:
        if chi2_p is not None and chi2_p > 0.05:
            stats_text += "\n✓ БОЛЬЦМАН ПОДТВЕРЖДЁН"
        elif chi2_p is not None:
            stats_text += "\n⚠ БОЛЬЦМАН НЕ ПОДТВЕРЖДЁН"
        else:
            stats_text += "\n⏳ Накопление данных..."
    else:
        stats_text += "\nВключите гравитацию\nдля проверки"
    
    ax6.text(0.05, 0.95, stats_text, transform=ax6.transAxes, fontsize=8,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    figure.tight_layout()
    canvas.draw()
