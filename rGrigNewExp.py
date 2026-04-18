# Упрощенная версия для быстрой проверки
import numpy as np
import sounddevice as sd


def play_interval(f1, f2, wave_type='sine', duration=1.5):
    """Воспроизвести интервал из двух одновременных тонов."""
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration))

    if wave_type == 'sine':
        tone1 = 0.5 * np.sin(2 * np.pi * f1 * t)
        tone2 = 0.5 * np.sin(2 * np.pi * f2 * t)
    elif wave_type == 'square':
        tone1 = np.zeros_like(t)
        tone2 = np.zeros_like(t)
        for n in range(1, 16, 2):
            tone1 += (0.5 / n) * np.sin(2 * np.pi * n * f1 * t)
            tone2 += (0.5 / n) * np.sin(2 * np.pi * n * f2 * t)

    signal = tone1 + tone2

    # Плавное начало/конец
    fade = 0.05
    n_fade = int(sr * fade)
    envelope = np.ones_like(t)
    envelope[:n_fade] = np.linspace(0, 1, n_fade)
    envelope[-n_fade:] = np.linspace(1, 0, n_fade)

    sd.play(signal * envelope, sr)
    sd.wait()


# Быстрая проверка:
print("Слушайте биения и шероховатость:")
play_interval(440, 444, 'sine')  # Биения 4 Гц
play_interval(440, 460, 'sine')  # Шероховатость
play_interval(440, 444, 'square')  # Сложные биения!