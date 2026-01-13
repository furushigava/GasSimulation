"""
Функции для обновления термодинамических графиков.
"""

import numpy as np
from scipy import stats


def update_thermodynamic_graphs(figure, canvas, data):
    """Обновление термодинамических графиков"""
    figure.clear()
    
    if not data.get('time'):
        canvas.draw()
        return
    
    # 1. P-T диаграмма
    ax1 = figure.add_subplot(331)
    if data.get('temperature') and data.get('pressure'):
        ax1.plot(data['temperature'], data['pressure'], 'b-', linewidth=2)
        ax1.scatter(data['temperature'][-1:], data['pressure'][-1:], color='red', s=50)
    ax1.set_xlabel('Температура (E)')
    ax1.set_ylabel('Давление')
    ax1.set_title('P-T диаграмма')
    ax1.grid(True, alpha=0.3)
    
    # 2. P-V диаграмма
    ax2 = figure.add_subplot(332)
    if data.get('volume') and data.get('pressure'):
        ax2.plot(data['volume'], data['pressure'], 'g-', linewidth=2)
        ax2.scatter(data['volume'][-1:], data['pressure'][-1:], color='red', s=50)
    ax2.set_xlabel('Объем')
    ax2.set_ylabel('Давление')
    ax2.set_title('P-V диаграмма')
    ax2.grid(True, alpha=0.3)
    
    # 3. V-T диаграмма
    ax3 = figure.add_subplot(333)
    if data.get('temperature') and data.get('volume'):
        ax3.plot(data['temperature'], data['volume'], 'r-', linewidth=2)
        ax3.scatter(data['temperature'][-1:], data['volume'][-1:], color='red', s=50)
    ax3.set_xlabel('Температура (E)')
    ax3.set_ylabel('Объем')
    ax3.set_title('V-T диаграмма')
    ax3.grid(True, alpha=0.3)
    
    # 4. P(t)
    ax4 = figure.add_subplot(334)
    if data.get('time') and data.get('pressure'):
        ax4.plot(data['time'], data['pressure'], 'purple', linewidth=2)
    ax4.set_xlabel('Время')
    ax4.set_ylabel('Давление')
    ax4.set_title('Давление от времени')
    ax4.grid(True, alpha=0.3)
    
    # 5. V(t)
    ax5 = figure.add_subplot(335)
    if data.get('time') and data.get('volume'):
        ax5.plot(data['time'], data['volume'], 'orange', linewidth=2)
    ax5.set_xlabel('Время')
    ax5.set_ylabel('Объем')
    ax5.set_title('Объем от времени')
    ax5.grid(True, alpha=0.3)
    
    # 6. T(t)
    ax6 = figure.add_subplot(336)
    if data.get('time') and data.get('temperature'):
        ax6.plot(data['time'], data['temperature'], 'brown', linewidth=2)
    ax6.set_xlabel('Время')
    ax6.set_ylabel('Температура (E)')
    ax6.set_title('Температура от времени')
    ax6.grid(True, alpha=0.3)
    
    # 7. Параметрический график (цвет = время)
    ax7 = figure.add_subplot(337)
    if data.get('time') and data.get('pressure') and data.get('volume'):
        n = min(len(data['time']), len(data['pressure']), len(data['volume']))
        scatter = ax7.scatter(data['volume'][:n], data['pressure'][:n], 
                            c=data['time'][:n], cmap='viridis', alpha=0.6, s=20)
        figure.colorbar(scatter, ax=ax7, label='Время')
    ax7.set_xlabel('Объем')
    ax7.set_ylabel('Давление')
    ax7.set_title('Параметрический график (цвет = время)')
    ax7.grid(True, alpha=0.3)
    
    # 8. Энергия от времени
    ax8 = figure.add_subplot(338)
    if data.get('time') and data.get('kinetic_energy'):
        ax8.plot(data['time'], data['kinetic_energy'], 'magenta', linewidth=2)
    ax8.set_xlabel('Время')
    ax8.set_ylabel('Кинетическая энергия')
    ax8.set_title('Энергия системы от времени')
    ax8.grid(True, alpha=0.3)
    
    # 9. Проверка уравнения состояния PV = NkT (для 2D: PV = E_kin)
    ax9 = figure.add_subplot(339)
    if data.get('time') and data.get('pressure') and data.get('volume') and data.get('kinetic_energy'):
        # В 2D идеальном газе: PV = NkT (т.к. 2 степени свободы)
        # Давление и объём уже в согласованных единицах симуляции
        
        pv_values = []
        ratio_values = []
        
        for i in range(len(data['time'])):
            if i < len(data['pressure']) and i < len(data['volume']):
                P = data['pressure'][i]
                V = data['volume'][i]  # Восстанавливаем исходный объём
                # E_kin = data['kinetic_energy'][i]
                
                pv = P * V
                pv_values.append(pv)
                
                N = data.get('n_particles', 1)
                k = 1
                T = data['temperature'][i] if i < len(data['temperature']) else 1
                
                if N > 0 and T > 0:
                    E_kin = N * k * T  # В 2D: E_кин = NkT
                    ratio = pv / E_kin
                    ratio_values.append(ratio)
                #if E_kin > 0:
                #    ratio_values.append(pv / E_kin)
                #else:
                #     ratio_values.append(0)
        
        if ratio_values:
            time_data = data['time'][:len(ratio_values)]
            ax9.plot(time_data, ratio_values, 'teal', linewidth=2, label='PV / E')
            ax9.axhline(y=1.0, color='red', linestyle='--', linewidth=1.5, label='Идеальный газ')
            
            # Среднее значение (по последним 100 точкам)
            stable_ratios = ratio_values[-100:] if len(ratio_values) >= 100 else ratio_values
            avg_ratio = sum(stable_ratios) / len(stable_ratios) if stable_ratios else 0
            ax9.axhline(y=avg_ratio, color='green', linestyle=':', linewidth=1.5, 
                       label=f'Среднее: {avg_ratio:.3f}')
            
            # Статистический тест
            if len(stable_ratios) > 1:
                t_stat, p_value = stats.ttest_1samp(stable_ratios, 1.0)
                is_equal = "Да" if p_value > 0.05 else "Нет"
                std_ratio = np.std(stable_ratios)
                
                # Добавляем аннотацию с статистиками
                ax9.annotate(f'Среднее: {avg_ratio:.3f}\nSTD: {std_ratio:.3f}\nT-test (last 100, a=0.05) p: {p_value:.3f}\nРавенство: {is_equal}', 
                             xy=(0.02, 0.98), xycoords='axes fraction', fontsize=8,
                             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            ax9.legend(loc='upper right', fontsize=7)
    
    ax9.set_xlabel('Время')
    ax9.set_ylabel('PV / NkT')
    ax9.set_title('Проверка PV = NkT')
    ax9.grid(True, alpha=0.3)
    
    figure.tight_layout()
    canvas.draw()
