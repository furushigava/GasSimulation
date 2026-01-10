"""
Функции для обновления продвинутых графиков.
"""
import numpy as np
import matplotlib.pyplot as plt

from config import (
    FFT_MIN_POINTS,
    WAVELET_SCALES_MAX,
    FRACTAL_BOX_SIZES_NUM,
    HURST_MIN_SIZE,
    HURST_SIZES_NUM
)


def update_advanced_graphs(figure, canvas, data):
    """Обновление продвинутых графиков"""
    figure.clear()
    
    if not data.get('time') or len(data['time']) < FFT_MIN_POINTS:
        canvas.draw()
        return
    
    # 1. Спектральный анализ давления
    ax1 = figure.add_subplot(231)
    if data.get('pressure'):
        pressure = data['pressure']
        n = len(pressure)
        
        if n > FFT_MIN_POINTS:
            # Быстрое преобразование Фурье
            fft_result = np.fft.fft(pressure)
            frequencies = np.fft.fftfreq(n, d=(data['time'][1] - data['time'][0]) if len(data['time']) > 1 else 1)
            
            # Только положительные частоты
            positive_freq = frequencies[:n//2]
            magnitude = np.abs(fft_result[:n//2])
            
            ax1.plot(positive_freq, magnitude, 'b-', linewidth=1.5)
            ax1.set_xlabel('Частота (Гц)')
            ax1.set_ylabel('Амплитуда')
            ax1.set_title('Спектр давления (Фурье)')
            ax1.grid(True, alpha=0.3)
    
    # 2. Вейвлет-преобразование (упрощенное)
    ax2 = figure.add_subplot(232)
    if data.get('pressure') and len(data['pressure']) > 20:
        pressure = data['pressure']
        n = len(pressure)
        
        # Простое вейвлет-преобразование
        scales = np.arange(1, WAVELET_SCALES_MAX)
        cwt_matrix = np.zeros((len(scales), n))
        
        for i, scale in enumerate(scales):
            wavelet = np.exp(-0.5 * (np.arange(-3*scale, 3*scale) / scale)**2) * np.cos(5 * np.arange(-3*scale, 3*scale) / scale)
            conv_result = np.convolve(pressure, wavelet, mode='same')
            cwt_matrix[i, :] = conv_result[:n]
        
        im = ax2.imshow(cwt_matrix, aspect='auto', cmap='viridis', 
                       extent=[data['time'][0], data['time'][-1], scales[-1], scales[0]])
        figure.colorbar(im, ax=ax2, label='Амплитуда')
        ax2.set_xlabel('Время')
        ax2.set_ylabel('Масштаб')
        ax2.set_title('Вейвлет-преобразование давления')
    
    # 3. График Пуанкаре
    ax3 = figure.add_subplot(233)
    if data.get('pressure') and len(data['pressure']) > 100:
        pressure = data['pressure']
        # Сечение Пуанкаре
        ax3.scatter(pressure[:-1], pressure[1:], alpha=0.5, s=10)
        ax3.plot([min(pressure), max(pressure)], [min(pressure), max(pressure)], 
                'r--', alpha=0.5, label='y=x')
        ax3.legend()
        ax3.set_xlabel('P(t)')
        ax3.set_ylabel('P(t+1)')
        ax3.set_title('Сечение Пуанкаре')
        ax3.grid(True, alpha=0.3)
    
    # 4. Фрактальная размерность (упрощенно)
    ax4 = figure.add_subplot(234)
    if data.get('pressure') and len(data['pressure']) > 50:
        # Упрощенный анализ фрактальной размерности
        pressure = data['pressure']
        n = len(pressure)
        
        # Метод подсчета ящиков
        box_sizes = np.logspace(0, 2, FRACTAL_BOX_SIZES_NUM).astype(int)
        box_sizes = box_sizes[box_sizes < n]
        
        counts = []
        for size in box_sizes:
            num_boxes = int(np.ceil(n / size))
            min_vals = [min(pressure[i*size:min((i+1)*size, n)]) for i in range(num_boxes)]
            max_vals = [max(pressure[i*size:min((i+1)*size, n)]) for i in range(num_boxes)]
            count = sum((max_vals[i] - min_vals[i]) / size for i in range(num_boxes))
            counts.append(count)
        
        if len(box_sizes) > 2 and len(counts) > 2:
            ax4.loglog(box_sizes, counts, 'bo-')
            ax4.set_xlabel('Размер ящика')
            ax4.set_ylabel('Количество ящиков')
            ax4.set_title('Фрактальная размерность (метод ящиков)')
            ax4.grid(True, alpha=0.3)
    
    # 5. Анализ Херста (R/S анализ)
    ax5 = figure.add_subplot(235)
    if data.get('pressure') and len(data['pressure']) > 100:
        pressure = data['pressure']
        n = len(pressure)
        
        # R/S анализ
        sizes = np.logspace(1, np.log10(n/2), HURST_SIZES_NUM).astype(int)
        rs_ratios = []
        
        for size in sizes:
            if size < HURST_MIN_SIZE:
                continue
                
            num_segments = n // size
            rs_values = []
            
            for i in range(num_segments):
                segment = pressure[i*size:(i+1)*size]
                if len(segment) < 2:
                    continue
                    
                # Преобразование в ряд накопленных отклонений
                mean_val = np.mean(segment)
                deviations = segment - mean_val
                cumulative = np.cumsum(deviations)
                
                r = np.max(cumulative) - np.min(cumulative)  # Размах
                s = np.std(segment)  # Стандартное отклонение
                
                if s > 0:
                    rs_values.append(r / s)
            
            if rs_values:
                rs_ratios.append(np.mean(rs_values))
            else:
                rs_ratios.append(np.nan)
        
        valid_indices = ~np.isnan(rs_ratios)
        if sum(valid_indices) > 2:
            valid_sizes = np.array(sizes)[valid_indices]
            valid_rs = np.array(rs_ratios)[valid_indices]
            
            ax5.loglog(valid_sizes, valid_rs, 'ro-')
            ax5.set_xlabel('Размер окна')
            ax5.set_ylabel('R/S отношение')
            ax5.set_title('Анализ Херста (R/S анализ)')
            ax5.grid(True, alpha=0.3)
    
    # 6. График Лоренца
    ax6 = figure.add_subplot(236)
    if data.get('velocities') and len(data['velocities']) > 20:
        velocities = sorted(data['velocities'])
        n = len(velocities)
        
        # Кривая Лоренца
        cumulative_vel = np.cumsum(velocities)
        cumulative_vel_norm = cumulative_vel / cumulative_vel[-1] if cumulative_vel[-1] > 0 else cumulative_vel
        perfect_line = np.linspace(0, 1, n)
        
        ax6.plot(np.linspace(0, 1, n), cumulative_vel_norm, 'b-', label='Фактическое')
        ax6.plot(np.linspace(0, 1, n), perfect_line, 'r--', label='Идеальное')
        ax6.fill_between(np.linspace(0, 1, n), cumulative_vel_norm, perfect_line, alpha=0.3)
        
        # Коэффициент Джини
        # Используем np.trapezoid (для NumPy 2.0+) или np.trapz (для старых версий)
        trapz_func = getattr(np, 'trapezoid', getattr(np, 'trapz', None))
        area_under_curve = trapz_func(cumulative_vel_norm, dx=1/n) if trapz_func else 0.5
        gini = 1 - 2 * area_under_curve
        
        ax6.text(0.6, 0.2, f'Коэфф. Джини: {gini:.3f}', 
                transform=ax6.transAxes, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax6.set_xlabel('Доля частиц')
        ax6.set_ylabel('Доля суммарной скорости')
        ax6.set_title('Кривая Лоренца распределения скоростей')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
    
    figure.tight_layout()
    canvas.draw()
