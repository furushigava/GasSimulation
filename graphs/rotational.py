"""
Графики для вращательных степеней свободы молекул.

Отображает:
1. Распределение угловых скоростей (сравнение с нормальным распределением)
2. Соотношение E_rot/E_total vs time
3. Проверка теоремы о равнораспределении энергии
4. Зависимость <E_rot>/DoF vs <E_trans>/DoF (должны быть равны при равновесии)
"""
import numpy as np
from scipy import stats


def angular_velocity_distribution_pdf(omega, T, I=1.0):
    """
    Распределение угловых скоростей при тепловом равновесии.
    
    В 2D для одной вращательной степени свободы:
    f(ω) = sqrt(I / (2π k_B T)) * exp(-I ω² / (2 k_B T))
    
    Это нормальное распределение с σ = sqrt(k_B T / I)
    
    Args:
        omega: Угловая скорость
        T: Температура (в единицах энергии, k_B = 1)
        I: Момент инерции
    
    Returns:
        Значение функции распределения
    """
    if T <= 0 or I <= 0:
        return np.zeros_like(omega)
    
    sigma = np.sqrt(T / I)
    return (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-omega**2 / (2 * sigma**2))


def fit_angular_temperature(angular_velocities, I=1.0):
    """
    Фит температуры из распределения угловых скоростей.
    
    При равновесии: <I*ω²/2> = k_B*T/2 для 1 вращательной DoF
    Поэтому: T = I * <ω²>
    
    Args:
        angular_velocities: Список угловых скоростей
        I: Момент инерции
    
    Returns:
        Температура (в условных единицах)
    """
    if len(angular_velocities) < 2:
        return 0.0
    omega_squared_mean = np.mean(np.array(angular_velocities)**2)
    return I * omega_squared_mean


def chi_squared_test_angular(angular_velocities, T, I=1.0, n_bins=15):
    """
    Тест χ² для проверки нормальности распределения угловых скоростей.
    
    Args:
        angular_velocities: Список угловых скоростей
        T: Температура
        I: Момент инерции
        n_bins: Число бинов
    
    Returns:
        (χ², p-value, степени свободы) или (None, None, None)
    """
    if len(angular_velocities) < 20 or T <= 0 or I <= 0:
        return None, None, None
    
    omega = np.array(angular_velocities)
    sigma = np.sqrt(T / I)
    
    # Нормализованная статистика
    chi2_stat, p_value = stats.normaltest(omega)
    
    return chi2_stat, p_value, len(omega) - 1


def update_rotational_graphs(fig, data):
    """
    Обновление графиков вращательных степеней свободы.
    
    Args:
        fig: Matplotlib Figure
        data: Словарь с данными симуляции
    """
    fig.clear()
    
    # Получаем данные о молекулярной конфигурации
    mol_config = data.get('molecule_config', {})
    enable_rotation = mol_config.get('enable_rotation', False)
    molecule_type = mol_config.get('molecule_type', 'monatomic')
    dof = mol_config.get('degrees_of_freedom', 2)
    I = mol_config.get('moment_of_inertia', 1.0)
    
    # Получаем энергетические данные
    angular_velocities = data.get('angular_velocities', [])
    e_trans = data.get('energy_translational', 0)
    e_rot = data.get('energy_rotational', 0)
    e_total = data.get('energy_total', 0)
    
    time_data = data.get('time', [])
    kinetic_energy = data.get('kinetic_energy', [])
    velocities = data.get('velocities', [])
    particle_mass = data.get('particle_mass', 1.0)
    
    # Создаём сетку графиков 2x2
    axes = fig.subplots(2, 2)
    
    # --- График 1: Распределение угловых скоростей ---
    ax1 = axes[0, 0]
    if enable_rotation and molecule_type != "monatomic" and len(angular_velocities) > 5:
        omega = np.array(angular_velocities)
        
        # Гистограмма угловых скоростей
        n, bins, patches = ax1.hist(omega, bins=20, density=True, alpha=0.7, 
                                      color='steelblue', label='Симуляция')
        
        # Теоретическое распределение
        T_rot = fit_angular_temperature(angular_velocities, I)
        if T_rot > 0:
            omega_range = np.linspace(omega.min() - 0.5, omega.max() + 0.5, 100)
            pdf_theory = angular_velocity_distribution_pdf(omega_range, T_rot, I)
            ax1.plot(omega_range, pdf_theory, 'r-', linewidth=2, 
                    label=f'Теория (T={T_rot:.2f})')
        
        ax1.set_xlabel('Угловая скорость ω')
        ax1.set_ylabel('Плотность вероятности')
        ax1.set_title('Распределение угловых скоростей')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Статистика
        mean_omega = np.mean(omega)
        std_omega = np.std(omega)
        ax1.text(0.02, 0.98, f'⟨ω⟩ = {mean_omega:.3f}\nσ = {std_omega:.3f}',
                transform=ax1.transAxes, verticalalignment='top',
                fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    else:
        ax1.text(0.5, 0.5, 'Вращение отключено\nили моноатомный газ',
                transform=ax1.transAxes, ha='center', va='center', fontsize=12)
        ax1.set_title('Распределение угловых скоростей')
    
    # --- График 2: Соотношение энергий ---
    ax2 = axes[0, 1]
    if enable_rotation and e_total > 0:
        rot_fraction = e_rot / e_total if e_total > 0 else 0
        trans_fraction = e_trans / e_total if e_total > 0 else 0
        
        # Теоретическое соотношение из теоремы о равнораспределении
        # В 2D: 2 поступательных DoF + 1 вращательная DoF = 3 DoF
        # E_rot/E_total = 1/3 при равновесии
        rot_dof = 1 if (molecule_type != "monatomic" and enable_rotation) else 0
        trans_dof = 2
        total_dof = trans_dof + rot_dof
        theory_rot_fraction = rot_dof / total_dof if total_dof > 0 else 0
        
        categories = ['Поступательная', 'Вращательная']
        values = [trans_fraction * 100, rot_fraction * 100]
        theory_values = [(1 - theory_rot_fraction) * 100, theory_rot_fraction * 100]
        
        x = np.arange(len(categories))
        width = 0.35
        
        bars1 = ax2.bar(x - width/2, values, width, label='Симуляция', color='steelblue')
        bars2 = ax2.bar(x + width/2, theory_values, width, label='Теория (равнорас.)', 
                       color='coral', alpha=0.7)
        
        ax2.set_ylabel('Доля энергии (%)')
        ax2.set_title('Распределение энергии по DoF')
        ax2.set_xticks(x)
        ax2.set_xticklabels(categories)
        ax2.legend()
        ax2.set_ylim(0, 100)
        
        # Добавляем значения на столбцы
        for bar, val in zip(bars1, values):
            height = bar.get_height()
            ax2.annotate(f'{val:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)
    else:
        ax2.text(0.5, 0.5, 'Только поступательная энергия\n(моноатомный газ или\nвращение отключено)',
                transform=ax2.transAxes, ha='center', va='center', fontsize=11)
        ax2.set_title('Распределение энергии по DoF')
    
    # --- График 3: Проверка теоремы о равнораспределении ---
    ax3 = axes[1, 0]
    if enable_rotation and len(angular_velocities) > 0 and len(velocities) > 0:
        # Средняя энергия на степень свободы
        # Для поступательного движения: <E_trans> / 2 (2 DoF в 2D)
        # Для вращательного: <E_rot> / 1 (1 DoF в 2D)
        
        n_particles = len(velocities)
        
        # Поступательная энергия на DoF
        if n_particles > 0:
            v_array = np.array(velocities)
            e_trans_per_particle = particle_mass * np.mean(v_array**2) / 2
            e_trans_per_dof = e_trans_per_particle / 2  # 2 поступательных DoF
            
            omega_array = np.array(angular_velocities)
            e_rot_per_particle = I * np.mean(omega_array**2) / 2
            e_rot_per_dof = e_rot_per_particle / 1  # 1 вращательная DoF
            
            categories = ['E_trans/DoF', 'E_rot/DoF']
            values = [e_trans_per_dof, e_rot_per_dof]
            colors = ['steelblue', 'coral']
            
            bars = ax3.bar(categories, values, color=colors, alpha=0.8)
            
            # Теоретическое значение (должно быть одинаковым)
            mean_e_per_dof = (e_trans_per_dof * 2 + e_rot_per_dof) / 3
            ax3.axhline(y=mean_e_per_dof, color='green', linestyle='--', 
                       label=f'⟨E⟩/DoF = {mean_e_per_dof:.3f}')
            
            ax3.set_ylabel('Энергия на DoF')
            ax3.set_title('Теорема о равнораспределении')
            ax3.legend()
            
            # Относительная разница
            if e_trans_per_dof > 0:
                rel_diff = abs(e_rot_per_dof - e_trans_per_dof) / e_trans_per_dof * 100
                ax3.text(0.02, 0.98, f'Отклонение: {rel_diff:.1f}%',
                        transform=ax3.transAxes, verticalalignment='top',
                        fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    else:
        ax3.text(0.5, 0.5, 'Недостаточно данных',
                transform=ax3.transAxes, ha='center', va='center', fontsize=12)
        ax3.set_title('Теорема о равнораспределении')
    
    # --- График 4: Q-Q plot для угловых скоростей ---
    ax4 = axes[1, 1]
    if enable_rotation and molecule_type != "monatomic" and len(angular_velocities) > 10:
        omega = np.array(angular_velocities)
        
        # Q-Q plot против нормального распределения
        stats.probplot(omega, dist="norm", plot=ax4)
        ax4.set_title('Q-Q график (угловые скорости vs норм. распр.)')
        ax4.grid(True, alpha=0.3)
        
        # Тест на нормальность
        if len(omega) >= 20:
            stat, p_value = stats.shapiro(omega[:min(len(omega), 5000)])
            ax4.text(0.02, 0.98, f'Shapiro-Wilk:\np = {p_value:.4f}',
                    transform=ax4.transAxes, verticalalignment='top',
                    fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    else:
        ax4.text(0.5, 0.5, 'Недостаточно данных\nдля Q-Q анализа',
                transform=ax4.transAxes, ha='center', va='center', fontsize=12)
        ax4.set_title('Q-Q график угловых скоростей')
    
    fig.tight_layout()


def get_rotational_statistics(angular_velocities, I=1.0):
    """
    Расчёт статистик вращательного движения.
    
    Args:
        angular_velocities: Список угловых скоростей
        I: Момент инерции
    
    Returns:
        Словарь со статистиками
    """
    if len(angular_velocities) < 2:
        return {
            'mean_omega': 0,
            'std_omega': 0,
            'temperature_rot': 0,
            'mean_energy_rot': 0
        }
    
    omega = np.array(angular_velocities)
    
    return {
        'mean_omega': np.mean(omega),
        'std_omega': np.std(omega),
        'temperature_rot': fit_angular_temperature(angular_velocities, I),
        'mean_energy_rot': I * np.mean(omega**2) / 2
    }
