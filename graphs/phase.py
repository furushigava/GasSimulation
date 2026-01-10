"""
Функции для обновления фазовых диаграмм.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata


def update_phase_graphs(figure, canvas, data):
    """Обновление фазовых диаграмм"""
    figure.clear()
    
    if not data.get('pressure') or len(data['pressure']) < 3:
        canvas.draw()
        return
    
    # 1. 3D фазовая диаграмма P-V-T
    ax1 = figure.add_subplot(231, projection='3d')
    if (data.get('pressure') and data.get('volume') and 
        data.get('temperature') and len(data['pressure']) == len(data['volume']) == len(data['temperature'])):
        
        n = min(len(data['pressure']), len(data['volume']), len(data['temperature']))
        ax1.plot(data['pressure'][:n], data['volume'][:n], data['temperature'][:n], 
                'b-', alpha=0.6, linewidth=1)
        ax1.scatter(data['pressure'][-1:], data['volume'][-1:], data['temperature'][-1:], 
                   color='red', s=50)
        
        ax1.set_xlabel('Давление')
        ax1.set_ylabel('Объем')
        ax1.set_zlabel('Температура')
        ax1.set_title('3D фазовая диаграмма P-V-T')
    
    # 2. Фазовая плоскость P-V
    ax2 = figure.add_subplot(232)
    if data.get('pressure') and data.get('volume'):
        ax2.plot(data['volume'], data['pressure'], 'g-', linewidth=1.5)
        ax2.scatter(data['volume'][-1:], data['pressure'][-1:], color='red', s=30)
        
        # Добавляем векторы скорости в фазовом пространстве
        if len(data['volume']) > 2:
            for i in range(0, len(data['volume'])-1, max(1, len(data['volume'])//20)):
                dx = data['volume'][i+1] - data['volume'][i]
                dy = data['pressure'][i+1] - data['pressure'][i]
                ax2.arrow(data['volume'][i], data['pressure'][i], 
                         dx*0.8, dy*0.8, head_width=0.02, head_length=0.02, 
                         fc='blue', ec='blue', alpha=0.5)
        
        ax2.set_xlabel('Объем')
        ax2.set_ylabel('Давление')
        ax2.set_title('Фазовая плоскость P-V')
        ax2.grid(True, alpha=0.3)
    
    # 3. Фазовая плоскость V-T
    ax3 = figure.add_subplot(233)
    if data.get('volume') and data.get('temperature'):
        ax3.plot(data['temperature'], data['volume'], 'r-', linewidth=1.5)
        ax3.scatter(data['temperature'][-1:], data['volume'][-1:], color='red', s=30)
        ax3.set_xlabel('Температура')
        ax3.set_ylabel('Объем')
        ax3.set_title('Фазовая плоскость V-T')
        ax3.grid(True, alpha=0.3)
    
    # 4. Параметрический график
    ax4 = figure.add_subplot(234)
    if data.get('time') and data.get('pressure') and data.get('volume'):
        # Цвет меняется со временем
        n = min(len(data['time']), len(data['pressure']), len(data['volume']))
        scatter = ax4.scatter(data['volume'][:n], data['pressure'][:n], 
                            c=data['time'][:n], cmap='viridis', alpha=0.6, s=20)
        figure.colorbar(scatter, ax=ax4, label='Время')
        ax4.set_xlabel('Объем')
        ax4.set_ylabel('Давление')
        ax4.set_title('Параметрический график (цвет = время)')
        ax4.grid(True, alpha=0.3)
    
    # 5. Изокванты (линии уровня)
    ax5 = figure.add_subplot(235)
    if data.get('volume') and data.get('pressure') and len(data['volume']) > 10:
        try:
            # Создаем сетку для изоквант
            points = np.array([data['volume'], data['pressure']]).T
            values = np.array(data['temperature'][:len(points)])
            
            # Проверяем, что данные не вырождены (имеют достаточный разброс)
            vol_range = max(data['volume']) - min(data['volume'])
            pres_range = max(data['pressure']) - min(data['pressure'])
            
            if vol_range > 1e-10 and pres_range > 1e-10:
                # Сетка для интерполяции
                xi = np.linspace(min(data['volume']), max(data['volume']), 50)
                yi = np.linspace(min(data['pressure']), max(data['pressure']), 50)
                xi, yi = np.meshgrid(xi, yi)
                
                # Интерполяция - используем 'linear' как запасной вариант при ошибках
                try:
                    zi = griddata(points, values, (xi, yi), method='cubic')
                except Exception:
                    zi = griddata(points, values, (xi, yi), method='linear')
                
                if zi is not None and not np.isnan(zi).all():
                    contour = ax5.contour(xi, yi, zi, levels=10, cmap='coolwarm')
                    ax5.clabel(contour, inline=True, fontsize=8)
                    ax5.scatter(data['volume'], data['pressure'], alpha=0.5, s=10)
        except Exception:
            # При любой ошибке просто рисуем точки без интерполяции
            ax5.scatter(data['volume'], data['pressure'], alpha=0.5, s=10)
        
        ax5.set_xlabel('Объем')
        ax5.set_ylabel('Давление')
        ax5.set_title('Изокванты (линии уровня температуры)')
        ax5.grid(True, alpha=0.3)
    
    # 6. График в полярных координатах
    ax6 = figure.add_subplot(236, projection='polar')
    if data.get('pressure') and data.get('volume') and len(data['pressure']) > 10:
        # Преобразуем в полярные координаты
        r = np.array(data['pressure'][-100:]) / max(data['pressure'][-100:]) if max(data['pressure'][-100:]) > 0 else np.array(data['pressure'][-100:])
        theta = np.array(data['volume'][-100:]) * 2 * np.pi / max(data['volume'][-100:]) if max(data['volume'][-100:]) > 0 else np.array(data['volume'][-100:])
        
        ax6.scatter(theta, r, alpha=0.6, s=20)
        ax6.set_title('Полярный график P-V')
        ax6.grid(True, alpha=0.3)
    
    figure.tight_layout()
    canvas.draw()
