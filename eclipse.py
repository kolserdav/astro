import swisseph as swe
import numpy as np

# Установите путь к файлам эфемерид
swe.set_ephe_path('./swisseph/ephe')

def check_solar_eclipse(jd):
    # Получаем положение Солнца и Луны
    sun_pos = swe.calc(jd, swe.SUN)[0]
    moon_pos = swe.calc(jd, swe.MOON)[0]
    
    # Вычисляем разницу между положениями
    angular_distance = np.abs(sun_pos[0] - moon_pos[0])
    
    # Проверяем, находится ли разница в пределах 0.5 градусов (30 минут)
    return angular_distance < 0.5

# Определяем временной интервал
start_jd = swe.julday(2025, 1, 1)  # Начало 2023 года
end_jd = swe.julday(2025, 12, 31)   # Конец 2023 года

for jd in range(int(start_jd), int(end_jd)):
    if check_solar_eclipse(jd):
        print(f"Солнечное затмение найдено на JD {jd}: {swe.revjul(jd)}")

