"""
Графики для верификации первого закона термодинамики (сохранение энергии).
"""
import numpy as np


def update_energy_conservation_graphs(figure, canvas, data):
    """Обновление графиков сохранения энергии."""
    figure.clear()
    
    kinetic_energy = data.get('kinetic_energy', [])
    potential_energy_history = data.get('potential_energy_history', [])
    energy_potential = data.get('energy_potential', 0.0)
    time = data.get('time', [])
    initial_energy = data.get('initial_energy', None)
    is_isolated = data.get('isolated_system', False)
    
    # Конфигурация потенциалов
    potentials_config = data.get('potentials_config', {})
    any_potential_enabled = (
        potentials_config.get('lennard_jones', {}).get('enabled', False) or
        potentials_config.get('morse', {}).get('enabled', False) or
        potentials_config.get('dlvo', {}).get('enabled', False)
    )
    
    if not kinetic_energy or not time:
        canvas.draw()
        return
    
    kinetic_energy = np.array(kinetic_energy)
    time = np.array(time)
    
    # Обработка потенциальной энергии
    if potential_energy_history and len(potential_energy_history) == len(kinetic_energy):
        potential_energy = np.array(potential_energy_history)
        total_energy = kinetic_energy + potential_energy
    else:
        potential_energy = np.zeros_like(kinetic_energy)
        total_energy = kinetic_energy
    
    # Если начальная энергия не задана, берем первое значение полной энергии
    if initial_energy is None or initial_energy == 0:
        initial_energy = total_energy[0] if len(total_energy) > 0 else 1.0
    
    # 1. Полная энергия от времени (кинетическая + потенциальная)
    ax1 = figure.add_subplot(231)
    ax1.plot(time, kinetic_energy, 'b-', linewidth=1.5, label='E_кин', alpha=0.8)
    if any_potential_enabled:
        ax1.plot(time, potential_energy, 'r-', linewidth=1.5, label='E_пот', alpha=0.8)
        ax1.plot(time, total_energy, 'g-', linewidth=2, label='E_полн')
        ax1.axhline(y=initial_energy, color='k', linestyle='--', linewidth=1, label=f'E₀ = {initial_energy:.2f}')
    else:
        ax1.axhline(y=initial_energy, color='r', linestyle='--', linewidth=1.5, label=f'E₀ = {initial_energy:.2f}')
    ax1.set_xlabel('Время')
    ax1.set_ylabel('Энергия')
    ax1.set_title('Энергия системы')
    ax1.legend(loc='best', fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    # 2. Относительная ошибка энергии
    ax2 = figure.add_subplot(232)
    reference_energy = total_energy if any_potential_enabled else kinetic_energy
    if initial_energy != 0:
        relative_error = (reference_energy - initial_energy) / initial_energy * 100
        ax2.plot(time, relative_error, 'g-', linewidth=1.5)
        ax2.axhline(y=0, color='r', linestyle='--', linewidth=1)
        
        # Среднее и стандартное отклонение
        mean_error = np.mean(relative_error)
        std_error = np.std(relative_error)
        ax2.axhline(y=mean_error, color='orange', linestyle=':', linewidth=1.5, 
                    label=f'Среднее: {mean_error:.4f}%')
        ax2.fill_between(time, mean_error - std_error, mean_error + std_error, 
                         alpha=0.2, color='orange')
        ax2.legend(loc='best')
    ax2.set_xlabel('Время')
    ax2.set_ylabel('ΔE/E₀ (%)')
    ax2.set_title('Относительная ошибка энергии')
    ax2.grid(True, alpha=0.3)
    
    # 3. Абсолютное изменение энергии или соотношение энергий
    ax3 = figure.add_subplot(233)
    if any_potential_enabled:
        # Показываем соотношение кинетической и потенциальной энергии
        ax3.stackplot(time, kinetic_energy, np.abs(potential_energy), 
                      labels=['E_кин', '|E_пот|'], colors=['blue', 'red'], alpha=0.7)
        ax3.set_ylabel('Энергия')
        ax3.set_title('Кинетическая vs Потенциальная')
        ax3.legend(loc='best')
    else:
        delta_E = kinetic_energy - initial_energy
        ax3.plot(time, delta_E, 'm-', linewidth=1.5)
        ax3.axhline(y=0, color='r', linestyle='--', linewidth=1)
        ax3.set_ylabel('ΔE = E(t) - E₀')
        ax3.set_title('Абсолютное изменение энергии')
    ax3.set_xlabel('Время')
    ax3.grid(True, alpha=0.3)
    
    # 4. Гистограмма отклонений энергии
    ax4 = figure.add_subplot(234)
    if len(reference_energy) > 10:
        deviations = reference_energy - initial_energy
        ax4.hist(deviations, bins=30, density=True, alpha=0.7, color='purple', edgecolor='black')
        
        # Фит нормального распределения
        from scipy import stats
        if np.std(deviations) > 0:
            mu, std = np.mean(deviations), np.std(deviations)
            x = np.linspace(min(deviations), max(deviations), 100)
            ax4.plot(x, stats.norm.pdf(x, mu, std), 'r-', linewidth=2, label='Норм. распр.')
            ax4.legend()
    ax4.set_xlabel('ΔE')
    ax4.set_ylabel('Плотность вероятности')
    ax4.set_title('Распределение отклонений энергии')
    ax4.grid(True, alpha=0.3)
    
    # 5. Скользящее среднее энергии
    ax5 = figure.add_subplot(235)
    if len(reference_energy) > 10:
        window_size = min(20, len(reference_energy) // 5)
        if window_size > 0:
            moving_avg = np.convolve(reference_energy, np.ones(window_size)/window_size, mode='valid')
            time_avg = time[:len(moving_avg)]
            ax5.plot(time, reference_energy, 'b-', alpha=0.3, linewidth=1, label='E(t)')
            ax5.plot(time_avg, moving_avg, 'r-', linewidth=2, label=f'Скольз. среднее (n={window_size})')
            ax5.axhline(y=initial_energy, color='green', linestyle='--', linewidth=1.5, label='E₀')
            ax5.legend(loc='best')
    ax5.set_xlabel('Время')
    ax5.set_ylabel('Энергия')
    ax5.set_title('Энергия со скользящим средним')
    ax5.grid(True, alpha=0.3)
    
    # 6. Статистическая информация (текстовый блок)
    ax6 = figure.add_subplot(236)
    ax6.axis('off')
    
    if len(reference_energy) > 0:
        current_energy = reference_energy[-1]
        mean_energy = np.mean(reference_energy)
        std_energy = np.std(reference_energy)
        max_deviation = np.max(np.abs(reference_energy - initial_energy))
        
        if initial_energy != 0:
            rel_error = (current_energy - initial_energy) / initial_energy * 100
            max_rel_error = max_deviation / initial_energy * 100
        else:
            rel_error = 0
            max_rel_error = 0
        
        status_text = "✓ Изолированная система" if is_isolated else "✗ Открытая система"
        
        # Информация о потенциалах
        potentials_info = ""
        if any_potential_enabled:
            lj = potentials_config.get('lennard_jones', {})
            morse = potentials_config.get('morse', {})
            dlvo = potentials_config.get('dlvo', {})
            
            potentials_info = "\nАКТИВНЫЕ ПОТЕНЦИАЛЫ:\n"
            if lj.get('enabled', False):
                potentials_info += f"  • Леннард-Джонс (ε={lj.get('epsilon', 0):.2f}, σ={lj.get('sigma', 0):.1f})\n"
            if morse.get('enabled', False):
                potentials_info += f"  • Морзе (D_e={morse.get('D_e', 0):.2f}, r_e={morse.get('r_e', 0):.1f})\n"
            if dlvo.get('enabled', False):
                potentials_info += f"  • ДЛФО (A_H={dlvo.get('hamaker_constant', 0):.2f})\n"
            
            current_kinetic = kinetic_energy[-1] if len(kinetic_energy) > 0 else 0
            current_potential = potential_energy[-1] if len(potential_energy) > 0 else 0
            potentials_info += f"\nТекущая E_кин: {current_kinetic:.4f}\n"
            potentials_info += f"Текущая E_пот: {current_potential:.4f}\n"
        
        stats_text = f"""
СТАТИСТИКА СОХРАНЕНИЯ ЭНЕРГИИ

Режим: {status_text}
{potentials_info}
Начальная энергия E₀: {initial_energy:.4f}
Текущая полная E(t): {current_energy:.4f}

Средняя энергия ⟨E⟩: {mean_energy:.4f}
Станд. отклонение σ(E): {std_energy:.4f}

Текущая относит. ошибка: {rel_error:.4f}%
Макс. относит. ошибка: {max_rel_error:.4f}%
Макс. абс. отклонение: {max_deviation:.4f}

Время симуляции: {time[-1]:.2f}
Измерений: {len(reference_energy)}

ПЕРВЫЙ ЗАКОН ТЕРМОДИНАМИКИ:
{"✓ ВЫПОЛНЯЕТСЯ" if abs(rel_error) < 5 else "✗ НАРУШЕН"}
(допуск: 5% относит. ошибки)
"""
        ax6.text(0.05, 0.95, stats_text, transform=ax6.transAxes, fontsize=8,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    figure.tight_layout()
    canvas.draw()
