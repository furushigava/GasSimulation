"""
Функции для обновления кинетических графиков.
"""
import numpy as np
import math


def update_kinetic_graphs(figure, canvas, data):
    """Обновление кинетических графиков"""
    figure.clear()
    
    if not data.get('time'):
        canvas.draw()
        return
    
    # 1. Средняя скорость от времени
    ax1 = figure.add_subplot(221)
    if data.get('time') and data.get('avg_velocity'):
        try:
            t = data['time']
            v = data['avg_velocity']
            m = min(len(t), len(v))
            if m > 0:
                ax1.plot(t[-m:], v[-m:], 'b-', linewidth=2)
        except Exception:
            pass
    ax1.set_xlabel('Время')
    ax1.set_ylabel('Средняя скорость')
    ax1.set_title('Средняя скорость от времени')
    ax1.grid(True, alpha=0.3)
    
    # 2. Средняя длина свободного пробега
    ax2 = figure.add_subplot(222)
    if data.get('time'):
        has_plotted = False
        times = data['time']
        # helper to safely plot series matching the time axis length
        def safe_plot(x, y, *args, **kwargs):
            if not x or not y:
                return False
            lx = len(x)
            ly = len(y)
            if lx == 0 or ly == 0:
                return False
            m = min(lx, ly)
            try:
                ax2.plot(x[-m:], y[-m:], *args, **kwargs)
                return True
            except Exception:
                return False

        # plot available series (use safe_plot to avoid shape mismatches)
        if data.get('mean_free_path'):
            series = data['mean_free_path']
            if safe_plot(times, series, 'r-', linewidth=2, label='Эмпирическое'):
                has_plotted = True
        if data.get('mean_free_path_theoretical'):
            series_t = data['mean_free_path_theoretical']
            if safe_plot(times, series_t, 'k--', linewidth=1.5, label='Теоретическое'):
                has_plotted = True
        # По умолчанию не рисуем эффект. линию — рисуем только если ошибка эмпирич. vs теор. > 10%
        draw_eff = False
        try:
            last_emp = data['mean_free_path'][-1] if data.get('mean_free_path') else None
            last_pp = data['mean_free_path_theoretical'][-1] if data.get('mean_free_path_theoretical') else None
            if last_emp is not None and last_pp and last_pp != 0 and math.isfinite(last_emp) and math.isfinite(last_pp):
                rel_pp = abs(last_emp - last_pp) / last_pp
                if rel_pp > 0.10:
                    draw_eff = True
        except Exception:
            draw_eff = False

        if draw_eff and data.get('mean_free_path_eff'):
            series_eff = data['mean_free_path_eff']
            if safe_plot(times, series_eff, color='tab:green', linewidth=1.8, linestyle='-.', label='Эфф. mfp'):
                has_plotted = True
        if data.get('mean_free_path_roll100'):
            series_r = data['mean_free_path_roll100']
            if safe_plot(times, series_r, color='tab:blue', linewidth=1.8, label='Скольз.100'):
                has_plotted = True

        # Собираем строку с последними значениями и отображаем в желтой рамке слева
        info_lines = []
        # Собираем последние значения для таблички: эмпирич., формула (λ_pp), L/2 и эффективная длина
        emp = None
        pp = None
        wall = None
        eff = None
        try:
            if data.get('mean_free_path'):
                emp = data['mean_free_path'][-1]
                info_lines.append(f"Эмпирич.: {emp:.3g}")
        except Exception:
            pass
        try:
            if data.get('mean_free_path_theoretical'):
                pp = data['mean_free_path_theoretical'][-1]
                info_lines.append(f"По формуле: {pp:.3g}")
        except Exception:
            pass
        try:
            if data.get('mean_free_path_wall'):
                wall = data['mean_free_path_wall'][-1]
        except Exception:
            wall = None
        try:
            if data.get('mean_free_path_eff'):
                eff = data['mean_free_path_eff'][-1]
        except Exception:
            eff = None

        # Относительная ошибка эмпирической оценки по отношению к значению по формуле (λ_pp)
        rel = None
        rel_eff = None
        try:
            if emp is not None and pp and pp != 0 and math.isfinite(emp) and math.isfinite(pp):
                rel = abs(emp - pp) / pp
                info_lines.append(f"Отн. ош. (формула): {rel*100:.1f}%")
        except Exception:
            rel = None

        # Если относительная ошибка больше 10% — показываем L/2 и эффективную оценку и вторую ошибку
        if rel is not None and rel > 0.10:
            if wall is not None:
                try:
                    info_lines.append(f"L/2: {wall:.3g}")
                except Exception:
                    pass
            if eff is not None:
                try:
                    info_lines.append(f"Эфф.: {eff:.3g}")
                except Exception:
                    pass
            try:
                if emp is not None and eff and eff != 0 and math.isfinite(emp) and math.isfinite(eff):
                    rel_eff = abs(emp - eff) / eff
                    info_lines.append(f"Отн. ош. (эфф.): {rel_eff*100:.1f}%")
            except Exception:
                pass

        if info_lines:
            info_text = "\n".join(info_lines)
            ax2.text(0.02, 0.98, info_text, transform=ax2.transAxes, fontsize=8,
                     verticalalignment='top', bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.9))

        if has_plotted:
            ax2.legend(loc='upper right')
    ax2.set_xlabel('Время')
    ax2.set_ylabel('Средняя длина свободного пробега')
    ax2.set_title('Длина свободного пробега от времени')
    ax2.grid(True, alpha=0.3)
    
    # 3. Частота столкновений
    ax3 = figure.add_subplot(223)
    if data.get('time') and data.get('collision_rate'):
        try:
            t = data['time']
            s = data['collision_rate']
            m = min(len(t), len(s))
            if m > 0:
                ax3.plot(t[-m:], s[-m:], 'g-', linewidth=2)
        except Exception:
            pass
    ax3.set_xlabel('Время')
    ax3.set_ylabel('Частота столкновений (1/с)')
    ax3.set_title('Частота столкновений от времени')
    ax3.grid(True, alpha=0.3)
    
    # 4. Скорость наиболее вероятной частицы
    ax4 = figure.add_subplot(224)
    if data.get('time') and data.get('avg_velocity'):
        try:
            t = data['time']
            avg_arr = np.array(data['avg_velocity'])
            m = min(len(t), len(avg_arr))
            if m > 0:
                ax4.plot(t[-m:], avg_arr[-m:], 'orange', linewidth=2, label='Средняя')
        except Exception:
            pass
        
        # Вычисляем реальное стандартное отклонение из скоростей частиц
        if len(data.get('time', [])) > 1 and len(data.get('velocities', [])) > 0:
            try:
                # используем последний сегмент времени/средних скоростей, чтобы совпадали размеры
                t = data['time']
                avg_arr = np.array(data['avg_velocity'])
                m = min(len(t), len(avg_arr))
                if m == 0:
                    raise ValueError

                avg_vel = avg_arr[-m:]
                t_seg = t[-m:]

                # Получаем текущее std из последнего набора скоростей
                current_velocities = np.array(data['velocities'][-1]) if isinstance(data['velocities'][-1], (list, np.ndarray)) else np.array(data['velocities'])
                current_std = np.std(current_velocities) if len(current_velocities) > 0 else float(avg_vel[-1]) * 0.3

                # Используем относительное std для всего графика
                std_ratio = current_std / float(avg_vel[-1]) if float(avg_vel[-1]) > 0 else 0.3
                std_region = avg_vel * std_ratio

                # Доверительный интервал (±1 std ≈ 68%)
                lower_bound = avg_vel - std_region
                upper_bound = avg_vel + std_region

                ax4.fill_between(t_seg, lower_bound, upper_bound,
                                alpha=0.3, color='orange', label=f'±1σ (68% ДИ)')

                # Добавляем подписи с информацией
                current_mean = float(avg_vel[-1])
                info_text = f'σ = {current_std:.3f}\nДИ: [{current_mean - current_std:.3f}, {current_mean + current_std:.3f}]\nОтн. σ = {std_ratio*100:.1f}%'
                ax4.text(0.02, 0.98, info_text, transform=ax4.transAxes, fontsize=8,
                        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            except Exception:
                pass
        
        ax4.legend(loc='upper right')
        ax4.set_xlabel('Время')
        ax4.set_ylabel('Скорость')
        ax4.set_title('Изменение скорости с доверительным интервалом')
        ax4.grid(True, alpha=0.3)
    
    figure.tight_layout()
    canvas.draw()
