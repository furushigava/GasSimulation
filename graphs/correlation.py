"""
Функции для обновления корреляционных графиков.
"""
import numpy as np

from config import MIN_CORRELATION_POINTS, CORRELATION_MATRIX_MIN_POINTS


def update_correlation_graphs(figure, canvas, data):
    """Обновление корреляционных графиков"""
    figure.clear()
    
    if not data.get('pressure') or len(data['pressure']) < MIN_CORRELATION_POINTS:
        canvas.draw()
        return
    
    # 1. Корреляция P и V
    ax1 = figure.add_subplot(231)
    if data.get('volume') and data.get('pressure'):
        ax1.scatter(data['volume'], data['pressure'], alpha=0.6, s=20)
        
        # Линейная регрессия
        if len(data['volume']) > 2:
            x = np.array(data['volume'])
            y = np.array(data['pressure'])
            coeffs = np.polyfit(x, y, 1)
            poly = np.poly1d(coeffs)
            ax1.plot(x, poly(x), 'r-', linewidth=2, 
                    label=f'y = {coeffs[0]:.3f}x + {coeffs[1]:.3f}')
            ax1.legend()
    
    ax1.set_xlabel('Объем')
    ax1.set_ylabel('Давление')
    ax1.set_title('Корреляция P-V')
    ax1.grid(True, alpha=0.3)
    
    # 2. Корреляция P и T
    ax2 = figure.add_subplot(232)
    if data.get('temperature') and data.get('pressure'):
        ax2.scatter(data['temperature'], data['pressure'], alpha=0.6, s=20, color='green')
    ax2.set_xlabel('Температура')
    ax2.set_ylabel('Давление')
    ax2.set_title('Корреляция P-T')
    ax2.grid(True, alpha=0.3)
    
    # 3. Корреляция V и T
    ax3 = figure.add_subplot(233)
    if data.get('temperature') and data.get('volume'):
        ax3.scatter(data['temperature'], data['volume'], alpha=0.6, s=20, color='red')
    ax3.set_xlabel('Температура')
    ax3.set_ylabel('Объем')
    ax3.set_title('Корреляция V-T')
    ax3.grid(True, alpha=0.3)
    
    # 4. Автокорреляция давления
    ax4 = figure.add_subplot(234)
    if len(data['pressure']) > MIN_CORRELATION_POINTS:
        autocorr = np.correlate(data['pressure'], data['pressure'], mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        ax4.plot(range(len(autocorr)), autocorr/autocorr[0], 'purple', linewidth=2)
    ax4.set_xlabel('Лаг')
    ax4.set_ylabel('Автокорреляция')
    ax4.set_title('Автокорреляция давления')
    ax4.grid(True, alpha=0.3)
    
    # 5. Взаимная корреляция P и V
    ax5 = figure.add_subplot(235)
    if data.get('pressure') and data.get('volume') and len(data['pressure']) == len(data['volume']):
        cross_corr = np.correlate(data['pressure'], data['volume'], mode='full')
        lags = np.arange(-len(data['pressure']) + 1, len(data['pressure']))
        ax5.plot(lags, cross_corr, 'orange', linewidth=2)
    ax5.set_xlabel('Лаг')
    ax5.set_ylabel('Кросс-корреляция')
    ax5.set_title('Взаимная корреляция P и V')
    ax5.grid(True, alpha=0.3)
    
    # 6. Корреляционная матрица
    ax6 = figure.add_subplot(236)
    if (data.get('pressure') and data.get('volume') and 
        data.get('temperature') and data.get('avg_velocity')):
        
        # Создаем мини-матрицу
        n = min(len(data['pressure']), len(data['volume']), 
               len(data['temperature']), len(data['avg_velocity']))
        
        if n > CORRELATION_MATRIX_MIN_POINTS:
            matrix = np.array([
                data['pressure'][:n],
                data['volume'][:n],
                data['temperature'][:n],
                data['avg_velocity'][:n]
            ])
            
            corr_matrix = np.corrcoef(matrix)
            im = ax6.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
            
            # Добавляем текст
            for i in range(corr_matrix.shape[0]):
                for j in range(corr_matrix.shape[1]):
                    text = ax6.text(j, i, f'{corr_matrix[i, j]:.2f}',
                                   ha="center", va="center", color="black")
            
            ax6.set_xticks(range(4))
            ax6.set_yticks(range(4))
            ax6.set_xticklabels(['P', 'V', 'T', 'v'])
            ax6.set_yticklabels(['P', 'V', 'T', 'v'])
            ax6.set_title('Корреляционная матрица')
    
    figure.tight_layout()
    canvas.draw()
