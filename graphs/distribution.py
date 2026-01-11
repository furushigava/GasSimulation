"""
Функции для обновления графиков распределений с верификацией распределения Максвелла.
"""
import numpy as np
from scipy import stats


def maxwell_2d_pdf(v, T, m=1.0):
    """
    2D распределение Максвелла по модулю скорости.
    f(v) = (m*v / k_B*T) * exp(-m*v^2 / (2*k_B*T))
    
    В симуляции k_B = 1, поэтому T = <E_kin> = <m*v^2/2>
    """
    if T <= 0:
        return np.zeros_like(v)
    return (m * v / T) * np.exp(-m * v**2 / (2 * T))


def fit_maxwell_temperature(velocities, mass=1.0):
    """
    Фит температуры из распределения скоростей.
    Для 2D: T = m * <v^2> / 2
    """
    if len(velocities) < 2:
        return 0.0
    v_squared_mean = np.mean(np.array(velocities)**2)
    return mass * v_squared_mean / 2


def maxwell_cdf(v, T, m=1.0):
    """Кумулятивная функция распределения Максвелла 2D."""
    if T <= 0:
        return np.zeros_like(v)
    return 1 - np.exp(-m * v**2 / (2 * T))


def chi_squared_test(velocities, T, m=1.0, n_bins=20):
    """
    Тест χ² для проверки соответствия распределению Максвелла.
    Возвращает (χ², p-value, степени свободы)
    """
    if len(velocities) < 30 or T <= 0:
        return None, None, None
    
    velocities = np.array(velocities)
    
    # Создаём гистограмму
    hist, bin_edges = np.histogram(velocities, bins=n_bins, density=False)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_width = bin_edges[1] - bin_edges[0]
    
    # Ожидаемые частоты
    expected_probs = maxwell_2d_pdf(bin_centers, T, m) * bin_width
    expected_freq = expected_probs * len(velocities)
    
    # Фильтруем бины с малым ожидаемым значением
    mask = expected_freq >= 5
    if np.sum(mask) < 3:
        return None, None, None
    
    observed = hist[mask]
    expected = expected_freq[mask]
    
    # χ² статистика
    chi2 = np.sum((observed - expected)**2 / expected)
    df = len(observed) - 1  # степени свободы
    p_value = 1 - stats.chi2.cdf(chi2, df)
    
    return chi2, p_value, df


def ks_test_maxwell(velocities, T, m=1.0):
    """
    Тест Колмогорова-Смирнова для распределения Максвелла.
    Возвращает (статистику KS, p-value)
    """
    if len(velocities) < 10 or T <= 0:
        return None, None
    
    velocities = np.array(velocities)
    
    # Эмпирическая CDF
    sorted_v = np.sort(velocities)
    empirical_cdf = np.arange(1, len(sorted_v) + 1) / len(sorted_v)
    
    # Теоретическая CDF
    theoretical_cdf = maxwell_cdf(sorted_v, T, m)
    
    # KS статистика
    ks_stat = np.max(np.abs(empirical_cdf - theoretical_cdf))
    
    # Приближённое p-value (формула Колмогорова)
    n = len(velocities)
    lambda_ks = (np.sqrt(n) + 0.12 + 0.11/np.sqrt(n)) * ks_stat
    p_value = 2 * np.exp(-2 * lambda_ks**2)
    p_value = min(1.0, max(0.0, p_value))
    
    return ks_stat, p_value


def update_distribution_graphs(figure, canvas, data):
    """Обновление графиков распределений с верификацией Максвелла"""
    figure.clear()
    
    if not data.get('velocities'):
        canvas.draw()
        return
    
    velocities = np.array(data['velocities'])
    mass = data.get('particle_mass', 1.0)
    
    # Расчёт температуры из распределения
    T_fit = fit_maxwell_temperature(velocities, mass)
    
    # 1. Гистограмма распределения скоростей с теоретическим Максвеллом
    ax1 = figure.add_subplot(231)
    
    # Гистограмма
    hist_values, bin_edges, _ = ax1.hist(velocities, bins=30, density=True, 
                                          alpha=0.7, color='blue', edgecolor='black',
                                          label='Симуляция')
    
    # Теоретическое распределение Максвелла (2D)
    if len(velocities) > 1 and T_fit > 0:
        v_range = np.linspace(0, max(velocities) * 1.3, 200)
        maxwell_pdf = maxwell_2d_pdf(v_range, T_fit, mass)
        ax1.plot(v_range, maxwell_pdf, 'r-', linewidth=2, 
                 label=f'Максвелл 2D (T={T_fit:.2f})')
    
    ax1.set_xlabel('Скорость v')
    ax1.set_ylabel('f(v)')
    ax1.set_title('Распределение Максвелла')
    ax1.legend(loc='best', fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    # 2. Q-Q plot для Максвелла
    ax2 = figure.add_subplot(232)
    if len(velocities) > 10 and T_fit > 0:
        sorted_v = np.sort(velocities)
        n = len(sorted_v)
        theoretical_quantiles = []
        
        for i in range(n):
            p = (i + 0.5) / n
            # Обратная CDF Максвелла: v = sqrt(-2*T/m * ln(1-p))
            if p < 0.999:
                v_theoretical = np.sqrt(-2 * T_fit / mass * np.log(1 - p))
                theoretical_quantiles.append(v_theoretical)
            else:
                theoretical_quantiles.append(sorted_v[-1])
        
        ax2.scatter(theoretical_quantiles, sorted_v, alpha=0.5, s=10)
        
        # Линия идеального соответствия
        max_val = max(max(theoretical_quantiles), max(sorted_v))
        ax2.plot([0, max_val], [0, max_val], 'r--', linewidth=2, label='Идеальное соответствие')
        
    ax2.set_xlabel('Теоретические квантили')
    ax2.set_ylabel('Эмпирические квантили')
    ax2.set_title('Q-Q plot (Максвелл)')
    ax2.legend(loc='best', fontsize=8)
    ax2.grid(True, alpha=0.3)
    
    # 3. Сравнение CDF
    ax3 = figure.add_subplot(233)
    if len(velocities) > 1 and T_fit > 0:
        sorted_v = np.sort(velocities)
        empirical_cdf = np.arange(1, len(sorted_v) + 1) / len(sorted_v)
        
        ax3.step(sorted_v, empirical_cdf, 'b-', linewidth=1.5, label='Эмпирическая CDF')
        
        # Теоретическая CDF
        v_range = np.linspace(0, max(sorted_v) * 1.1, 200)
        theoretical_cdf = maxwell_cdf(v_range, T_fit, mass)
        ax3.plot(v_range, theoretical_cdf, 'r--', linewidth=2, label='Теоретическая CDF')
        
    ax3.set_xlabel('Скорость v')
    ax3.set_ylabel('F(v)')
    ax3.set_title('Кумулятивные функции распределения')
    ax3.legend(loc='best', fontsize=8)
    ax3.grid(True, alpha=0.3)
    
    # 4. Распределение кинетической энергии
    ax4 = figure.add_subplot(234)
    if len(velocities) > 0:
        kinetic_energies = 0.5 * mass * velocities**2
        ax4.hist(kinetic_energies, bins=30, density=True, alpha=0.7, 
                 color='green', edgecolor='black', label='Симуляция')
        
        # Теоретическое распределение: экспоненциальное для 2D
        # P(E) = (1/T) * exp(-E/T)
        if T_fit > 0:
            E_range = np.linspace(0, max(kinetic_energies) * 1.2, 200)
            energy_pdf = (1/T_fit) * np.exp(-E_range/T_fit)
            ax4.plot(E_range, energy_pdf, 'r-', linewidth=2, label='Больцман')
            
    ax4.set_xlabel('Кинетическая энергия E')
    ax4.set_ylabel('P(E)')
    ax4.set_title('Распределение энергии')
    ax4.legend(loc='best', fontsize=8)
    ax4.grid(True, alpha=0.3)
    
    # 5. Невязка (разность эмпирического и теоретического)
    ax5 = figure.add_subplot(235)
    if len(velocities) > 20 and T_fit > 0:
        hist, bin_edges = np.histogram(velocities, bins=30, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        theoretical = maxwell_2d_pdf(bin_centers, T_fit, mass)
        residuals = hist - theoretical
        
        ax5.bar(bin_centers, residuals, width=bin_edges[1]-bin_edges[0], 
                alpha=0.7, color='purple', edgecolor='black')
        ax5.axhline(y=0, color='r', linestyle='--', linewidth=1)
        
    ax5.set_xlabel('Скорость v')
    ax5.set_ylabel('Невязка f_эмп - f_теор')
    ax5.set_title('Отклонение от Максвелла')
    ax5.grid(True, alpha=0.3)
    
    # 6. Статистическая информация
    ax6 = figure.add_subplot(236)
    ax6.axis('off')
    
    # Статистические тесты
    chi2, chi2_p, chi2_df = chi_squared_test(velocities, T_fit, mass)
    ks_stat, ks_p = ks_test_maxwell(velocities, T_fit, mass)
    
    # Статистика скоростей
    mean_v = np.mean(velocities)
    std_v = np.std(velocities)
    v_most_probable = np.sqrt(T_fit / mass) if T_fit > 0 else 0
    v_mean_theory = np.sqrt(np.pi * T_fit / (2 * mass)) if T_fit > 0 else 0
    
    stats_text = f"""ВЕРИФИКАЦИЯ РАСПРЕДЕЛЕНИЯ МАКСВЕЛЛА

Параметры:
  Масса m = {mass}
  Температура T = {T_fit:.4f}
  Частиц N = {len(velocities)}

Скорости:
  ⟨v⟩ = {mean_v:.4f}
  ⟨v⟩_теор = {v_mean_theory:.4f}
  v_p = {v_most_probable:.4f}
  σ = {std_v:.4f}

ТЕСТЫ:
"""
    
    if chi2 is not None:
        chi2_result = "✓" if chi2_p > 0.05 else "✗"
        stats_text += f"χ²={chi2:.1f} p={chi2_p:.3f} {chi2_result}\n"
    else:
        stats_text += "χ²: мало данных\n"
    
    if ks_stat is not None:
        ks_result = "✓" if ks_p > 0.05 else "✗"
        stats_text += f"KS={ks_stat:.3f} p={ks_p:.3f} {ks_result}\n"
    else:
        stats_text += "KS: мало данных\n"
    
    # Общий вывод
    if chi2_p is not None and ks_p is not None:
        if chi2_p > 0.05 and ks_p > 0.05:
            stats_text += "\n✓ МАКСВЕЛЛ ПОДТВЕРЖДЁН"
        else:
            stats_text += "\n⚠ НЕ ПОДТВЕРЖДЁН"
    else:
        stats_text += "\n⏳ Накопление..."
    
    ax6.text(0.05, 0.95, stats_text, transform=ax6.transAxes, fontsize=8,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    figure.tight_layout()
    canvas.draw()
