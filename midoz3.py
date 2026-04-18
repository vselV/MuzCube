import time
import threading
import mido
from dataclasses import dataclass
from typing import List, Dict, Optional, Union
from queue import Queue, Empty
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
    start_time: int  # Время начала в тиках
    channel: int  # MIDI канал (0-15)
    num: int  # Номер события (0-127)
    value: int  # Значение события (0-127)


@dataclass
class Tempo:
    start_time: int  # Время изменения темпа в тиках
    bpm: float  # Новый темп (ударов в минуту)


class MidiPlayer:
    def __init__(self, initial_bpm: int = 120, output_port: Optional[str] = None):
        """
        Инициализация MIDI проигрывателя

        :param initial_bpm: Начальный темп в ударах в минуту
        :param output_port: Имя MIDI выходного порта
        """
        self._initial_bpm = initial_bpm
        self._current_bpm = initial_bpm
        self._ticks_per_quarter = 960
        self._running = False
        self._stop_event = threading.Event()
        self._midi_out = self._init_midi_port(output_port)
        self._tempo_changes = []
        self._playback_start_time = 0
        self._playback_offset = 0

    def _init_midi_port(self, port_name: Optional[str]):
        """Инициализирует MIDI выходной порт"""
        try:
            if port_name:
                return mido.open_output(port_name)

            # Пытаемся найти доступный порт
            available_ports = mido.get_output_names()
            if available_ports:
                print(f"Using MIDI port: {available_ports[0]}")
                return mido.open_output(available_ports[0])

            raise RuntimeError("No MIDI ports available")

        except Exception as e:
            error_msg = f"Failed to initialize MIDI port: {e}\n"
            if sys.platform == 'win32':
                error_msg += (
                    "\nДля Applications:\n"
                    "1. Установите loopMIDI (https://www.tobias-erichsen.de/software/loopmidi.html)\n"
                    "2. Запустите loopMIDI и создайте виртуальный порт\n"
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

    def _play_sequence(self, sequence: List[Union[Note, Event]], start_tick: int = 0):
        """Воспроизводит последовательность с учетом изменений темпа"""
        try:
            self._playback_start_time = time.time()
            current_time = 0.0
            last_bpm = self._initial_bpm

            for item in sequence:
                if self._stop_event.is_set():
                    break

                # Пропускаем события до start_tick
                if item.start_time < start_tick:
                    continue

                # Получаем текущий BPM
                current_bpm = self._get_current_bpm(item.start_time)
                if current_bpm != last_bpm:
                    print(f"Tempo change at tick {item.start_time}: {current_bpm} BPM")
                    last_bpm = current_bpm

                # Вычисляем время ожидания
                wait_time = self._calculate_tick_duration(item.start_time - start_tick, current_bpm) - current_time

                if wait_time > 0:
                    time.sleep(wait_time)
                    current_time += wait_time

                # Обрабатываем ноту или событие
                if isinstance(item, Note):
                    # Pitch wheel
                    if item.pitch_wheel != 0:
                        self._midi_out.send(mido.Message(
                            'pitchwheel',
                            channel=item.channel,
                            pitch=item.pitch_wheel
                        ))

                    # Note on
                    self._midi_out.send(mido.Message(
                        'note_on',
                        channel=item.channel,
                        note=item.pitch,
                        velocity=item.velocity
                    ))

                    # Запланировать note off
                    note_off_time = current_time + self._calculate_tick_duration(item.duration, current_bpm)
                    threading.Timer(
                        note_off_time - current_time,
                        lambda: self._midi_out.send(mido.Message(
                            'note_off',
                            channel=item.channel,
                            note=item.pitch,
                            velocity=0
                        ))
                    ).start()

                elif isinstance(item, Event):
                    self._midi_out.send(mido.Message(
                        'control_change',
                        channel=item.channel,
                        control=item.num,
                        value=item.value
                    ))

        except Exception as e:
            print(f"Playback error: {e}")

    def play_from_file(self, midi_file: str, start_time: float = 0.0):
        """Воспроизводит MIDI файл с возможностью начала с определенного времени"""
        try:
            mid = mido.MidiFile(midi_file)
            start_tick = int(start_time * mid.ticks_per_beat * self._initial_bpm / 60)

            # Создаем поток для воспроизведения
            thread = threading.Thread(
                target=self._play_midi_file,
                args=(mid, start_tick),
                daemon=True
            )
            thread.start()
            self._playback_threads.append(thread)

        except Exception as e:
            raise RuntimeError(f"Failed to play MIDI file: {e}")

    def _play_midi_file(self, midi_file: mido.MidiFile, start_tick: int = 0):
        """Внутренний метод для воспроизведения MIDI файла"""
        try:
            for msg in midi_file.play(meta_messages=True):
                if self._stop_event.is_set():
                    break

                # Пропускаем сообщения до start_tick
                if msg.time < start_tick:
                    continue

                # Отправляем только MIDI сообщения (не мета-сообщения)
                if not msg.is_meta:
                    self._midi_out.send(msg)
                elif msg.type == 'set_tempo':
                    # Обрабатываем изменения темпа из MIDI файла
                    bpm = mido.tempo2bpm(msg.tempo)
                    print(f"MIDI file tempo change: {bpm} BPM")

        except Exception as e:
            print(f"MIDI file playback error: {e}")

    def play(self, tracks: Dict[str, List[Union[Note, Event]]], start_time: float = 0.0):
        """
        Воспроизводит несколько треков синхронно

        :param tracks: Словарь {имя_трека: последовательность_нот_и_событий}
        :param start_time: Время начала в секундах от начала композиции
        """
        if self._running:
            self.stop()

        self._running = True
        self._stop_event.clear()
        self._playback_threads = []

        # Конвертируем время начала в тики
        start_tick = int(start_time * self._ticks_per_quarter * self._initial_bpm / 60)

        # Запускаем потоки для каждого трека
        for name, sequence in tracks.items():
            thread = threading.Thread(
                target=self._play_sequence,
                args=(sequence, start_tick),
                daemon=True,
                name=f"MidiTrack-{name}"
            )
            thread.start()
            self._playback_threads.append(thread)

    def stop(self):
        """Останавливает воспроизведение"""
        self._stop_event.set()
        self._running = False

        # Посылаем all notes off
        self._all_notes_off()

        # Ждем завершения потоков
        for thread in self._playback_threads:
            thread.join(timeout=0.1)
        self._playback_threads = []

    def _all_notes_off(self):
        """Отправляет сообщения note off для всех нот"""
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
                print(f"Failed to send all notes off: {e}")

    def close(self):
        """Закрывает MIDI соединение"""
        self.stop()
        if self._midi_out:
            self._midi_out.close()


# Пример использования
if __name__ == "__main__":
    try:
        # Создаем тестовые данные
        notes = [
            Note(0, 0, 60, 480, 64, 0),  # До
            Note(480, 0, 62, 480, 80, 0),  # Ре
            Note(960, 0, 64, 960, 100, 0),  # Ми
            Note(960, 0, 66, 960, 100, 0)  # Ми
        ]

        events = [
            Event(0, 0, 7, 100),  # Громкость
            Event(960, 0, 10, 120)  # Панорама
        ]

        # Изменения темпа
        tempo_changes = [
            Tempo(0, 120),  # Начальный темп
            Tempo(200, 150),  # Ускорение
            Tempo(1920, 100)  # Замедление
        ]

        # Инициализируем проигрыватель
        player = MidiPlayer(initial_bpm=120)
      #  player.add_tempo_changes(tempo_changes)

        print("Начало воспроизведения с изменениями темпа...")
     #   player.play({
    #        "melody": notes,
    #        "controls": events
     #   })

        # Можно одновременно воспроизводить MIDI файл
        player.play_from_file("example.mid")

        input("Нажмите Enter для остановки...\n")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if 'player' in locals():
            player.close()
        print("Воспроизведение завершено")