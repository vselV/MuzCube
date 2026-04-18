import win32api
import win32con
import time
import mido

def create_virtual_midi_ports():
    """Создание виртуальных MIDI портов"""
    ports = []

    try:
        # Попытка создать несколько виртуальных портов
        for i in range(4):  # Пробуем создать 4 порта
            try:
                port_name = f"Microsoft GS Wavetable Synth {i}"
                port = mido.open_output(port_name)
                ports.append(port)
                print(f"Создан порт: {port_name}")
            except Exception as e:
                print(f"Не удалось создать порт {i}: {e}")
                break

    except Exception as e:
        print(f"Ошибка при создании портов: {e}")

    return ports


# Использование
ports = create_virtual_midi_ports()
for port in ports:
    port.send(mido.Message('note_on', note=60, velocity=64))
    time.sleep(0.1)
    port.send(mido.Message('note_off', note=60))