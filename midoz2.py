import time
import threading
import mido
from dataclasses import dataclass
from typing import List, Dict, Optional, Union
import sys


@dataclass
class Note:
    start_time: int  # Время начала в тиках (1 четверть = 960 тиков)
    channel: int  # MIDI канал (0-15)
    pitch: int  # Высота ноты (0-127)
    duration: int  # Длительность в тиках
    velocity: int  # Громкость ноты (1-127)
    pitch_wheel: int  # Значение pitch wheel (-8192 до 8191)

@dataclass
class Event:
    start_time: int    # Время начала в тиках
    channel: int       # MIDI канал (0-15)
    num: int           # Номер события (0-127)
    value: int         # Значение события (0-127)


@dataclass
class Tempo:
    start_time: int  # Время изменения темпа в тиках
    bpm: float  # Новый темп (ударов в минуту)


class MidiPlayer:
    def __init__(self, initial_bpm: int = 120, port_name: Optional[str] = None):
        self._initial_bpm = initial_bpm
        self._current_bpm = initial_bpm
        self._ticks_per_quarter = 960
        self._running = False
        self._stop_event = threading.Event()
        self._midi_out = None
        self._tempo_changes = []
        self._playback_threads = []
        self._init_midi_port(port_name)

    def _init_midi_port(self, port_name: Optional[str]):
        """Инициализирует MIDI выходной порт с обработкой ошибок"""
        try:
            available_ports = mido.get_output_names()
            if not available_ports:
                raise RuntimeError("No MIDI output ports found")

            print("Доступные MIDI порты:", available_ports)

            if port_name is None:
                port_name = available_ports[0]
                print(f"Автоматически выбран порт: {port_name}")

            if port_name not in available_ports:
                raise RuntimeError(f"Порт '{port_name}' не найден")

            try:
                self._midi_out = mido.open_output(port_name)
            except AttributeError:
                # Обход ошибки с API_UNSPECIFIED
                backend = mido.backends.backend
                self._midi_out = backend.open_output(port_name)

            print(f"Успешное подключение к порту: {port_name}")

        except Exception as e:
            error_msg = f"Ошибка инициализации MIDI: {e}\n"
            if sys.platform == 'win32':
                error_msg += (
                    "Для Applications:\n"
                    "1. Установите loopMIDI (https://www.tobias-erichsen.de/software/loopmidi.html)\n"
                    "2. Создайте виртуальный порт в loopMIDI\n"
                    "3. Укажите имя порта при создании MidiPlayer"
                )
            raise RuntimeError(error_msg)

    def add_tempo_changes(self, tempo_changes: List[Tempo]):
        """Добавляет изменения темпа (должны быть отсортированы по времени)"""
        self._tempo_changes = sorted(tempo_changes, key=lambda x: x.start_time)

    def _get_current_bpm(self, current_tick: int) -> float:
        """Возвращает текущий BPM для указанного времени"""
        current_bpm = self._initial_bpm
        for change in self._tempo_changes:
            if change.start_time <= current_tick:
                current_bpm = change.bpm
            else:
                break
        return current_bpm

    def _calculate_tick_duration(self, ticks: int, current_bpm: float) -> float:
        """Конвертирует тики в секунды с учетом текущего темпа"""
        microseconds_per_quarter = 60000000 / current_bpm
        seconds_per_tick = microseconds_per_quarter / (self._ticks_per_quarter * 1000000)
        return ticks * seconds_per_tick

    def play_notes(self, notes: List[Note], start_time: float = 0.0):
        """Воспроизводит последовательность нот в отдельном потоке"""
        if not self._running:
            self._running = True
            self._stop_event.clear()

        thread = threading.Thread(
            target=self._play_notes_sequence,
            args=(notes, start_time),
            daemon=True
        )
        thread.start()
        self._playback_threads.append(thread)

    def _play_notes_sequence(self, notes: List[Note], start_time: float):
        """Внутренний метод для воспроизведения нот"""
        try:
            start_tick = int(start_time * self._ticks_per_quarter * self._initial_bpm / 60)
            playback_start = time.time()
            current_time = 0.0

            for note in notes:
                if self._stop_event.is_set():
                    break

                if note.start_time < start_tick:
                    continue

                current_bpm = self._get_current_bpm(note.start_time)
                wait_time = self._calculate_tick_duration(note.start_time - start_tick, current_bpm) - current_time

                if wait_time > 0:
                    time.sleep(wait_time)
                    current_time += wait_time

                # Отправляем сообщения
                if note.pitch_wheel != 0:
                    self._send_midi_message(mido.Message(
                        'pitchwheel',
                        channel=note.channel,
                        pitch=note.pitch_wheel
                    ))

                self._send_midi_message(mido.Message(
                    'note_on',
                    channel=note.channel,
                    note=note.pitch,
                    velocity=note.velocity
                ))

                # Запланировать note off
                threading.Timer(
                    self._calculate_tick_duration(note.duration, current_bpm),
                    lambda: self._send_midi_message(mido.Message(
                        'note_off',
                        channel=note.channel,
                        note=note.pitch,
                        velocity=0
                    ))
                ).start()

        except Exception as e:
            print(f"Ошибка воспроизведения нот: {e}")

    def play_midi_file(self, file_path: str, start_time: float = 0.0):
        """Воспроизводит MIDI файл в отдельном потоке"""
        if not self._running:
            self._running = True
            self._stop_event.clear()

        thread = threading.Thread(
            target=self._play_midi_file_sequence,
            args=(file_path, start_time),
            daemon=True
        )
        thread.start()
        self._playback_threads.append(thread)

    def _play_midi_file_sequence(self, file_path: str, start_time: float):
        """Внутренний метод для воспроизведения MIDI файла"""
        try:
            mid = mido.MidiFile(file_path)
            start_tick = int(start_time * mid.ticks_per_beat * self._initial_bpm / 60)
            playback_start = time.time()

            for msg in mid.play(meta_messages=True):
                if self._stop_event.is_set():
                    break

                if msg.time < start_tick:
                    continue

                if not msg.is_meta:
                    self._send_midi_message(msg)
                elif msg.type == 'set_tempo':
                    # Можно обрабатывать изменения темпа из файла
                    pass

        except Exception as e:
            print(f"Ошибка воспроизведения MIDI файла: {e}")

    def _send_midi_message(self, msg):
        """Безопасная отправка MIDI сообщения"""
        if self._midi_out:
            try:
                self._midi_out.send(msg)
            except Exception as e:
                print(f"Ошибка отправки MIDI: {e}")

    def stop(self):
        """Останавливает все воспроизведение"""
        self._stop_event.set()
        self._all_notes_off()

        for thread in self._playback_threads:
            thread.join(timeout=0.1)
        self._playback_threads = []
        self._running = False

    def _all_notes_off(self):
        """Отправляет сообщения note off для всех каналов"""
        if not self._midi_out:
            return

        for channel in range(16):
            try:
                self._midi_out.send(mido.Message(
                    'control_change',
                    channel=channel,
                    control=123,  # All notes off
                    value=0
                ))
            except Exception as e:
                print(f"Ошибка all notes off: {e}")

    def close(self):
        """Закрывает соединение"""
        self.stop()
        if self._midi_out:
            self._midi_out.close()
            self._midi_out = None


# Пример синхронного воспроизведения MIDI файла и массива нот
if __name__ == "__main__":
    try:
        # 1. Создаем тестовые ноты
        custom_notes = [
            Note(0, 0, 72, 480, 100, 0),  # До (высокая октава)
            Note(480, 0, 74, 480, 90, 0),  # Ре
            Note(960, 0, 76, 960, 80, 0),  # Ми
            Note(1920, 0, 77, 480, 70, 0)  # Фа
        ]
        events = [
            Event(0, 0, 7, 100),  # Громкость
            Event(960, 0, 10, 120)  # Панорама
        ]
        # 2. Изменения темпа
        tempo_changes = [
            Tempo(0, 120),  # Начальный темп
            Tempo(960, 200),  # Ускорение
            Tempo(1920, 80)  # Замедление
        ]

        # 3. Инициализируем проигрыватель
        player = MidiPlayer(initial_bpm=120)
        player.add_tempo_changes(tempo_changes)

        print("Синхронное воспроизведение MIDI файла и пользовательских нот...")

        # 4. Запускаем MIDI файл (укажите путь к вашему файлу)
       # player.play_midi_file("a.mid")  # Замените на ваш MIDI файл

        # 5. Запускаем пользовательские ноты
        player.play_notes(custom_notes,events)

        # 6. Ждем завершения или прерываем по Enter
        input("Нажмите Enter для остановки...\n")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if 'player' in locals():
            player.close()
        print("Воспроизведение завершено")