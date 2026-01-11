"""
Графики для верификации эргодической гипотезы.
Эргодичность: <A>_t = <A>_ансамбль для любой физической величины A
Забывание начальных условий: корреляция начального и текущего состояний → 0
"""
import numpy as np
from scipy import stats


def calculate_time_average(history, window=None):
    """
    Расчёт временного среднего.
    
    Args:
        history: список значений величины по времени для одной частицы
        window: окно усреднения (None = все данные)
    
    Returns:
        time_average: временное среднее
    """
    if len(history) == 0:
        return None
    
    if window is not None and len(history) > window:
        history = history[-window:]
    
    return np.mean(history)


def calculate_ensemble_average(values):
    """
    Расчёт ансамблевого среднего (среднее по всем частицам в данный момент).
    
    Args:
        values: список значений величины для всех частиц в данный момент
    
    Returns:
        ensemble_average: ансамблевое среднее
    """
    if len(values) == 0:
        return None
    
    return np.mean(values)


def calculate_initial_correlation(initial_values, current_values):
    """
    Расчёт корреляции между начальным и текущим состоянием.
    Для эргодической системы корреляция должна стремиться к 0.
    
    Returns:
        correlation: коэффициент корреляции Пирсона
    """
    if len(initial_values) < 5 or len(current_values) < 5:
        return None
    
    if len(initial_values) != len(current_values):
        return None
    
    try:
        corr, p_value = stats.pearsonr(initial_values, current_values)
        return corr
    except Exception:
        return None


def mixing_time_estimate(correlations, time_data, threshold=0.1):
    """
    Оценка времени перемешивания (когда корреляция падает ниже порога).
    
    Returns:
        mixing_time: время перемешивания
    """
    if len(correlations) < 5 or len(time_data) != len(correlations):
        return None
    
    correlations = np.array(correlations)
    
    # Ищем момент, когда |корреляция| < threshold
    for i, corr in enumerate(correlations):
        if corr is not None and abs(corr) < threshold:
            return time_data[i]
    
    return None  # Ещё не достигнуто


def update_ergodic_graphs(figure, canvas, data):
    """Обновление графиков для верификации эргодической гипотезы."""
    figure.clear()
    
    time_data = data.get('time', [])
    velocities = data.get('velocities', [])
    
    # Данные для эргодичности
    time_averages_history = data.get('time_averages_history', [])
    ensemble_averages_history = data.get('ensemble_averages_history', [])
    initial_velocities = data.get('initial_velocities', [])
    correlations_history = data.get('correlations_history', [])
    particle_velocity_histories = data.get('particle_velocity_histories', {})
    
    n_particles = data.get('n_particles', len(velocities) if velocities else 100)
    
    # 1. Сходимость временного и ансамблевого средних
    ax1 = figure.add_subplot(231)
    
    if len(time_averages_history) > 1 and len(ensemble_averages_history) > 1:
        time_plot = time_data[:len(time_averages_history)]
        
        ax1.plot(time_plot, time_averages_history, 'b-', linewidth=2, 
                 label='⟨v⟩_время (1 частица)')
        ax1.plot(time_plot, ensemble_averages_history, 'r--', linewidth=2,
                 label='⟨v⟩_ансамбль')
        
        # Разность
        if len(time_averages_history) == len(ensemble_averages_history):
            diff = np.abs(np.array(time_averages_history) - np.array(ensemble_averages_history))
            ax1_twin = ax1.twinx()
            ax1_twin.fill_between(time_plot, 0, diff, alpha=0.2, color='green', label='|Δ|')
            ax1_twin.set_ylabel('|Разность|', color='green')
            ax1_twin.tick_params(axis='y', labelcolor='green')
        
        ax1.legend(loc='upper left', fontsize=8)
    
    ax1.set_xlabel('Время t')
    ax1.set_ylabel('⟨v⟩')
    ax1.set_title('Сходимость средних (эргодичность)')
    ax1.grid(True, alpha=0.3)
    
    # 2. Корреляция с начальным состоянием ("забывание")
    ax2 = figure.add_subplot(232)
    
    if len(correlations_history) > 1:
        time_plot = time_data[:len(correlations_history)]
        
        # Фильтруем None
        valid_mask = [c is not None for c in correlations_history]
        valid_time = [t for t, v in zip(time_plot, valid_mask) if v]
        valid_corr = [c for c in correlations_history if c is not None]
        
        if valid_corr:
            ax2.plot(valid_time, valid_corr, 'b-', linewidth=2, label='Корреляция')
            ax2.axhline(y=0, color='r', linestyle='--', linewidth=1.5, alpha=0.7)
            ax2.axhline(y=0.1, color='g', linestyle=':', linewidth=1, label='Порог (0.1)')
            ax2.axhline(y=-0.1, color='g', linestyle=':', linewidth=1)
            
            # Экспоненциальный фит для оценки времени релаксации
            if len(valid_corr) > 10:
                try:
                    # Берём абсолютные значения для фита exp(-t/τ)
                    abs_corr = np.abs(valid_corr)
                    log_corr = np.log(abs_corr + 1e-10)
                    slope, intercept, _, _, _ = stats.linregress(valid_time, log_corr)
                    if slope < 0:
                        tau = -1 / slope
                        fit_corr = np.exp(intercept) * np.exp(-np.array(valid_time) / tau)
                        ax2.plot(valid_time, fit_corr, 'm--', linewidth=1.5, 
                                label=f'Фит: τ={tau:.2f}')
                except Exception:
                    pass
            
            ax2.legend(loc='best', fontsize=8)
    
    ax2.set_xlabel('Время t')
    ax2.set_ylabel('Корреляция ρ(v₀, v(t))')
    ax2.set_title('Забывание начальных условий')
    ax2.set_ylim([-1.1, 1.1])
    ax2.grid(True, alpha=0.3)
    
    # 3. Распределение временных средних по частицам
    ax3 = figure.add_subplot(233)
    
    if particle_velocity_histories:
        # Вычисляем временное среднее для каждой частицы
        time_avgs = []
        for particle_id, history in particle_velocity_histories.items():
            if len(history) > 10:
                time_avgs.append(np.mean(history))
        
        if time_avgs:
            ax3.hist(time_avgs, bins=20, density=True, alpha=0.7, 
                     color='blue', edgecolor='black', label='⟨v⟩_t по частицам')
            
            # Ансамблевое среднее
            if velocities:
                ensemble_avg = np.mean(velocities)
                ax3.axvline(x=ensemble_avg, color='r', linestyle='--', linewidth=2,
                           label=f'⟨v⟩_ансамбль = {ensemble_avg:.3f}')
            
            ax3.legend(loc='best', fontsize=8)
    
    ax3.set_xlabel('Временное среднее ⟨v⟩_t')
    ax3.set_ylabel('Плотность')
    ax3.set_title('Распределение временных средних')
    ax3.grid(True, alpha=0.3)
    
    # 4. Относительная ошибка сходимости
    ax4 = figure.add_subplot(234)
    
    if len(time_averages_history) > 5 and len(ensemble_averages_history) > 5:
        time_plot = time_data[:len(time_averages_history)]
        
        time_arr = np.array(time_averages_history)
        ens_arr = np.array(ensemble_averages_history)
        
        # Относительная ошибка
        rel_error = np.abs(time_arr - ens_arr) / (ens_arr + 1e-10) * 100
        
        ax4.semilogy(time_plot, rel_error, 'b-', linewidth=1.5)
        ax4.axhline(y=5, color='r', linestyle='--', linewidth=1, label='5% порог')
        ax4.legend(loc='best', fontsize=8)
    
    ax4.set_xlabel('Время t')
    ax4.set_ylabel('Относительная ошибка (%)')
    ax4.set_title('Сходимость ⟨v⟩_t → ⟨v⟩_ансамбль')
    ax4.grid(True, alpha=0.3)
    
    # 5. Траектории нескольких частиц в фазовом пространстве (v vs x)
    ax5 = figure.add_subplot(235)
    
    positions = data.get('positions', [])
    if velocities and positions and len(velocities) == len(positions):
        x_coords = [p[0] for p in positions]
        
        # Scatter plot текущего состояния
        scatter = ax5.scatter(x_coords, velocities, c=range(len(velocities)), 
                             cmap='viridis', s=10, alpha=0.7)
        
        # Начальные позиции если есть
        initial_positions = data.get('initial_positions', [])
        if initial_velocities and initial_positions:
            init_x = [p[0] for p in initial_positions]
            ax5.scatter(init_x, initial_velocities, c='red', s=30, marker='x', 
                       label='Нач. состояние', zorder=5)
            ax5.legend(loc='best', fontsize=8)
    
    ax5.set_xlabel('Координата x')
    ax5.set_ylabel('Скорость v')
    ax5.set_title('Фазовое пространство')
    ax5.grid(True, alpha=0.3)
    
    # 6. Статистика
    ax6 = figure.add_subplot(236)
    ax6.axis('off')
    
    # Расчёт метрик эргодичности
    convergence_achieved = False
    mixing_time = None
    
    if len(time_averages_history) > 10 and len(ensemble_averages_history) > 10:
        # Проверяем сходимость (последние 10 точек)
        recent_time = np.array(time_averages_history[-10:])
        recent_ens = np.array(ensemble_averages_history[-10:])
        rel_diff = np.abs(recent_time - recent_ens) / (recent_ens + 1e-10)
        convergence_achieved = np.mean(rel_diff) < 0.1  # 10% точность
    
    if correlations_history:
        mixing_time = mixing_time_estimate(correlations_history, time_data[:len(correlations_history)])
    
    current_time_avg = time_averages_history[-1] if time_averages_history else None
    current_ens_avg = ensemble_averages_history[-1] if ensemble_averages_history else None
    current_corr = correlations_history[-1] if correlations_history else None
    
    stats_text = f"""ЭРГОДИЧЕСКАЯ ГИПОТЕЗА

Частиц N = {n_particles}
Измерений = {len(time_data)}

ТЕКУЩИЕ ЗНАЧЕНИЯ:
"""
    
    if current_time_avg is not None:
        stats_text += f"  ⟨v⟩_время = {current_time_avg:.4f}\n"
    if current_ens_avg is not None:
        stats_text += f"  ⟨v⟩_ансамбль = {current_ens_avg:.4f}\n"
    
    if current_time_avg is not None and current_ens_avg is not None:
        diff = abs(current_time_avg - current_ens_avg)
        rel_diff = diff / (current_ens_avg + 1e-10) * 100
        stats_text += f"  |Δ| = {diff:.4f} ({rel_diff:.1f}%)\n"
    
    stats_text += "\nЗАБЫВАНИЕ:\n"
    if current_corr is not None:
        stats_text += f"  ρ(v₀, v(t)) = {current_corr:.4f}\n"
        if abs(current_corr) < 0.1:
            stats_text += "  ✓ Забывание достигнуто\n"
        else:
            stats_text += "  ⏳ Идёт релаксация\n"
    else:
        stats_text += "  Мало данных\n"
    
    if mixing_time is not None:
        stats_text += f"\n  Время перемеш. ≈ {mixing_time:.2f}\n"
    
    stats_text += "\nЭРГОДИЧНОСТЬ:\n"
    if convergence_achieved:
        stats_text += "  ✓ ⟨A⟩_t ≈ ⟨A⟩_ансамбль\n"
        stats_text += "  ✓ ПОДТВЕРЖДЕНА"
    elif len(time_averages_history) > 10:
        stats_text += "  ⚠ Сходимость не достигнута\n"
        stats_text += "  ⏳ Накопление..."
    else:
        stats_text += "  ⏳ Мало данных..."
    
    ax6.text(0.05, 0.95, stats_text, transform=ax6.transAxes, fontsize=8,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    figure.tight_layout()
    canvas.draw()
