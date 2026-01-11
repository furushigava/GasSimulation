"""
Функции для обновления термодинамических графиков.
"""


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
    ax1.set_xlabel('Температура (E/100)')
    ax1.set_ylabel('Давление')
    ax1.set_title('P-T диаграмма')
    ax1.grid(True, alpha=0.3)
    
    # 2. P-V диаграмма
    ax2 = figure.add_subplot(332)
    if data.get('volume') and data.get('pressure'):
        ax2.plot(data['volume'], data['pressure'], 'g-', linewidth=2)
        ax2.scatter(data['volume'][-1:], data['pressure'][-1:], color='red', s=50)
    ax2.set_xlabel('Объем (x1000)')
    ax2.set_ylabel('Давление')
    ax2.set_title('P-V диаграмма')
    ax2.grid(True, alpha=0.3)
    
    # 3. V-T диаграмма
    ax3 = figure.add_subplot(333)
    if data.get('temperature') and data.get('volume'):
        ax3.plot(data['temperature'], data['volume'], 'r-', linewidth=2)
        ax3.scatter(data['temperature'][-1:], data['volume'][-1:], color='red', s=50)
    ax3.set_xlabel('Температура (E/100)')
    ax3.set_ylabel('Объем (x1000)')
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
    ax5.set_ylabel('Объем (x1000)')
    ax5.set_title('Объем от времени')
    ax5.grid(True, alpha=0.3)
    
    # 6. T(t)
    ax6 = figure.add_subplot(336)
    if data.get('time') and data.get('temperature'):
        ax6.plot(data['time'], data['temperature'], 'brown', linewidth=2)
    ax6.set_xlabel('Время')
    ax6.set_ylabel('Температура (E/100)')
    ax6.set_title('Температура от времени')
    ax6.grid(True, alpha=0.3)
    
    # 7. Параметрический график (цвет = время)
    ax7 = figure.add_subplot(337)
    if data.get('time') and data.get('pressure') and data.get('volume'):
        n = min(len(data['time']), len(data['pressure']), len(data['volume']))
        scatter = ax7.scatter(data['volume'][:n], data['pressure'][:n], 
                            c=data['time'][:n], cmap='viridis', alpha=0.6, s=20)
        figure.colorbar(scatter, ax=ax7, label='Время')
    ax7.set_xlabel('Объем (x1000)')
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
    
    # 9. Плотность от времени
    ax9 = figure.add_subplot(339)
    if data.get('time') and data.get('density'):
        ax9.plot(data['time'], data['density'], 'teal', linewidth=2)
    ax9.set_xlabel('Время')
    ax9.set_ylabel('Плотность (частиц/площадь)')
    ax9.set_title('Плотность от времени')
    ax9.grid(True, alpha=0.3)
    
    figure.tight_layout()
    canvas.draw()
