import numpy as np
import sounddevice as sd
import soundfile as sf
from scipy import signal
import time
import csv
import matplotlib.pyplot as plt

class PlompLeveltExperiment:
    def __init__(self):
        # Параметры из статьи
        self.sample_rate = 44100
        self.duration = 1.5  # seconds
        self.fade_duration = 0.05  # seconds
        self.pause_duration = 0.5  # seconds

        # Частотная сетка (адаптивная)
        self.base_freqs = [200, 250, 300, 350, 400, 450, 500]

        # Типы волн для сравнения
        self.wave_types = ['sine', 'square']

        # Случайный порядок презентации
        self.trials = self.generate_trials()

        # Данные
        self.responses = []

    def generate_wave(self, freq, wave_type='sine'):
        """Генерация волны заданного типа."""
        t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))

        if wave_type == 'sine':
            wave = np.sin(2 * np.pi * freq * t)
        elif wave_type == 'square':
            # Идеальная квадратная волна (бесконечные гармоники)
            # На практике ограничим 15 гармониками как в статье Сетэреса
            wave = np.zeros_like(t)
            for n in range(1, 16, 2):  # только нечетные гармоники
                wave += (1 / n) * np.sin(2 * np.pi * n * freq * t)
            # Нормировка
            wave = wave / np.max(np.abs(wave))

        # Амплитудная огибающая (плавное начало/конец)
        envelope = np.ones_like(t)
        n_fade = int(self.sample_rate * self.fade_duration)
        envelope[:n_fade] = np.linspace(0, 1, n_fade)
        envelope[-n_fade:] = np.linspace(1, 0, n_fade)

        return wave * envelope

    def generate_trials(self):
        """Генерация списка испытаний по методике статьи."""
        trials = []

        # Интервалы в пределах критической полосы (0-50% от частоты)
        for base_freq in self.base_freqs:
            # Критическая полоса ~17% от частоты
            critical_bandwidth = 0.17 * base_freq

            # 10 интервалов внутри критической полосы
            for ratio in np.linspace(0.01, 0.5, 10):
                delta_f = ratio * critical_bandwidth
                freq2 = base_freq + delta_f

                # Для каждого типа волны
                for wave_type in self.wave_types:
                    trials.append({
                        'wave_type': wave_type,
                        'f1': base_freq,
                        'f2': freq2,
                        'delta_f': delta_f,
                        'ratio': ratio  # delta_f / b
                    })

        # Перемешать порядок
        np.random.shuffle(trials)
        return trials

    def play_trial(self, trial):
        """Воспроизведение одного испытания."""
        # Генерация тонов
        tone1 = self.generate_wave(trial['f1'], trial['wave_type'])
        tone2 = self.generate_wave(trial['f2'], trial['wave_type'])

        # Пауза между тонами
        pause = np.zeros(int(self.sample_rate * self.pause_duration))

        # Объединенный сигнал
        signal = np.concatenate([tone1, pause, tone2])

        # Воспроизведение
        sd.play(signal, self.sample_rate)
        sd.wait()

    def run_experiment(self):
        """Запуск полного эксперимента."""
        print("=" * 60)
        print("ЭКСПЕРИМЕНТ ПО ВОСПРИЯТИЮ ПРИЯТНОСТИ ИНТЕРВАЛОВ")
        print("=" * 60)
        print("\nИнструкция:")
        print("Вы будете слышать пары звуков. Оцените, насколько ПРИЯТНО")
        print("звучит каждая пара по шкале от 1 до 5:")
        print("1 — Очень приятно")
        print("2 — Приятно")
        print("3 — Нейтрально")
        print("4 — Неприятно")
        print("5 — Очень неприятно")
        print("\nНажмите Enter для начала...")
        input()

        for i, trial in enumerate(self.trials):
            print(f"\nИспытание {i + 1}/{len(self.trials)}")
            print(f"Тип волны: {trial['wave_type']}")

            self.play_trial(trial)

            # Получение ответа
            while True:
                try:
                    response = int(input("Ваша оценка (1-5): "))
                    if 1 <= response <= 5:
                        break
                    else:
                        print("Пожалуйста, введите число от 1 до 5")
                except:
                    print("Пожалуйста, введите число")

            # Сохранение ответа
            trial['response'] = response
            self.responses.append(trial)

            # Пауза между испытаниями
            time.sleep(0.5)

        # Сохранение данных
        self.save_results()

    def save_results(self):
        """Сохранение результатов в CSV."""
        filename = f"plomp_experiment_{time.strftime('%Y%m%d_%H%M%S')}.csv"

        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'wave_type', 'f1', 'f2', 'delta_f', 'ratio', 'response'
            ])
            writer.writeheader()
            writer.writerows(self.responses)

        print(f"\nРезультаты сохранены в {filename}")

        # Быстрый анализ
        self.analyze_results()

    def analyze_results(self):
        """Быстрый анализ результатов."""
        import pandas as pd
        import matplotlib.pyplot as plt

        df = pd.DataFrame(self.responses)

        # Средние значения для каждого типа волны
        for wave_type in self.wave_types:
            subset = df[df['wave_type'] == wave_type]

            # Группировка по отношению delta_f/b
            grouped = subset.groupby('ratio')['response'].mean().reset_index()

            plt.plot(grouped['ratio'], grouped['response'],
                     marker='o', label=wave_type)

        plt.xlabel('Δf / b (нормированная разность частот)')


plt.ylabel('Средняя оценка неприятности')
plt.title('Кривые неприятностей для разных типов волн')
plt.legend()
plt.grid(True)
plt.savefig('results_plot.png')
plt.show()

# Запуск эксперимента
if __name__ == "__main__":
    experiment = PlompLeveltExperiment()
    experiment.run_experiment()