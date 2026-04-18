import numpy as np
import matplotlib.pyplot as plt


def sethares_dissonance_vectorized(freqs1, amps1, freqs2, amps2):
    """Векторизованная функция диссонанса Сетэреса."""
    all_freqs = np.concatenate([freqs1, freqs2])
    all_amps = np.concatenate([amps1, amps2])

    f1_mat, f2_mat = np.meshgrid(all_freqs, all_freqs, indexing='ij')
    a1_mat, a2_mat = np.meshgrid(all_amps, all_amps, indexing='ij')

    mask = np.triu(np.ones_like(f1_mat, dtype=bool), k=1)

    f1 = f1_mat[mask]
    f2 = f2_mat[mask]
    a1 = a1_mat[mask]
    a2 = a2_mat[mask]

    # Параметры Сетэреса (2005)
    s1, s2 = 0.0207, 18.96
    d_star = 0.24
    a, b = 3.5, 5.75

    s = d_star / (s1 * np.minimum(f1, f2) + s2)
    diff = np.abs(f2 - f1)

    dissonance_pairs = a1 * a2 * (np.exp(-a * s * diff) - np.exp(-b * s * diff))
    return np.sum(dissonance_pairs)


def cents_to_ratio(cents):
    """Конвертирует центы в частотное отношение."""
    return 2 ** (cents / 1200)


# Параметры
fundamental = 440  # Ля 4-й октавы (440 Гц)
cents_range = np.linspace(0, 1200, 10000)  # От унисона до октавы с шагом 5 центов

# Тембр струны (амплитуды гармоник, типичные для струнных инструментов)
# Первые 10 гармоник
string_spectrum = {
    1: 1.00,  # основная частота
    2: 0.85,  # октава
    3: 0.70,  # дуодецима
    4: 0.60,  # две октавы
    5: 0.50,  # большая терция
    6: 0.40,  # квинта
    7: 0.30,  # малая септима
    8: 0.25,  # октава
    9: 0.20,  # большая нота
    10: 0.15,  # терция
    11: 0.15,  # терция
    13: 0.15,  # терция
    14: 0.15,  # терция
    15: 0.15,  # терция
}

# Преобразуем спектр в массивы для первой ноты
harmonics = np.array(list(string_spectrum.keys()))
amps_base = np.array(list(string_spectrum.values()))

# Нормируем амплитуды (сумма квадратов = 1 для стабильности)
amps_base = amps_base / np.sqrt(np.sum(amps_base ** 2))

# Вычисляем диссонанс для каждого интервала
dissonance_values = []

for cents in cents_range:
    ratio = cents_to_ratio(cents)
    freq2 = fundamental * ratio

    # Частоты гармоник для обеих нот
    freqs1 = fundamental * harmonics
    freqs2 = freq2 * harmonics

    # Используем одинаковый тембр для обеих нот
    dissonance = sethares_dissonance_vectorized(freqs1, amps_base, freqs2, amps_base)
    dissonance_values.append(dissonance)

# Находим названия и положения основных интервалов
intervals = {
    "Унисон (0)": 0,
    "М. сек. (100)": 100,
    "Б. сек. (200)": 200,
    "М. тер. (300)": 300,
    "Б. тер. (400)": 400,
    "Кварта (500)": 500,
    "Тритон (600)": 600,
    "Квинта (700)": 700,
    "М. сек. (800)": 800,
    "Б. сек. (900)": 900,
    "М. тер. (1000)": 1000,
    "Б. тер. (1100)": 1100,
    "Октава (1200)": 1200
}
natural_intervals = {
    "1/1": 0,  # унисон
    "16/15": 111.73,  # малая секунда
    "9/8": 203.91,  # большая секунда
    "6/5": 315.64,  # малая терция
    "5/4": 386.31,  # большая терция
    "4/3": 498.04,  # кварта
    "7/5": 582.51,  # тритон (примерно)
    "3/2": 701.96,  # квинта
    "8/5": 813.69,  # малая секста
    "5/3": 884.36,  # большая секста
    "7/4": 968.83,  # гармоническая септима
    "15/8": 1088.27,  # большая септима
    "2/1": 1200.00,  # октава

    # Дополнительные интересные гармоники
    "11/10": 165.00,  # ~
    "11/9": 347.41,  # ~
    "11/8": 551.32,  # именно то, что ты просил! (11-я гармоника)
    "13/8": 840.53,  # ~
    "13/10": 454.21,  # ~
    "14/9": 764.92,  # ~
}
# Строим график
plt.figure(figsize=(14, 7))
plt.plot(cents_range, dissonance_values, 'b-', linewidth=2, label='Диссонанс струнного тембра')

# Отмечаем основные интервалы
for name, cents in natural_intervals.items():
    idx = np.abs(cents_range - cents).argmin()
    plt.plot(cents, dissonance_values[idx], 'ro', markersize=6)
    # Подписи только для важных интервалов

    plt.text(cents, dissonance_values[idx] + 0.01, name,
                 ha='center', fontsize=9, rotation=45)

# Добавляем горизонтальную сетку для лучшей читаемости
plt.grid(True, alpha=0.3)
plt.minorticks_on()
plt.grid(which='minor', alpha=0.2)

# Настройки графика
plt.xlabel('Интервал (центы)', fontsize=12)
plt.ylabel('Диссонанс (отн. ед.)', fontsize=12)
plt.title('Диссонанс интервалов от унисона до октавы\nТембр: струнный инструмент', fontsize=14)
plt.xlim(0, 1200)

# Подписываем области консонанса/диссонанса
plt.axvspan(0, 100, alpha=0.1, color='green', label='Сильный консонанс')
plt.axvspan(300, 500, alpha=0.1, color='lightgreen', label='Умеренный консонанс')
plt.axvspan(600, 800, alpha=0.1, color='orange', label='Умеренный диссонанс')
plt.axvspan(100, 300, alpha=0.1, color='yellow', label='Слабый диссонанс')
plt.axvspan(800, 1100, alpha=0.1, color='yellow')

plt.legend(loc='upper right')
plt.tight_layout()
plt.show()

# Выводим таблицу значений для основных интервалов
print("\n" + "=" * 60)
print("ДИССОНАНС ОСНОВНЫХ ИНТЕРВАЛОВ (струнный тембр)")
print("=" * 60)
print(f"{'Интервал':<20} {'Центы':<10} {'Диссонанс':<10}")
print("-" * 60)

for name, cents in intervals.items():
    idx = np.abs(cents_range - cents).argmin()
    dissonance_val = dissonance_values[idx]
    print(f"{name:<20} {cents:<10} {dissonance_val:.4f}")

# Находим самые диссонансные и консонансные интервалы
max_idx = np.argmax(dissonance_values)
min_idx = np.argmin(dissonance_values[1:]) + 1  # исключаем унисон

print("\n" + "=" * 60)
print(f"МАКСИМАЛЬНЫЙ ДИССОНАНС: {dissonance_values[max_idx]:.4f} при {cents_range[max_idx]:.0f} центах")
print(f"МИНИМАЛЬНЫЙ ДИССОНАНС (кроме унисона): {dissonance_values[min_idx]:.4f} при {cents_range[min_idx]:.0f} центах")
print("=" * 60)