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


class MidiPlayer:
    def __init__(self, bpm: int = 120, output_port: Optional[str] = None):
        """
        Инициализация MIDI проигрывателя

        :param bpm: Темп в ударах в минуту
        :param output_port: Имя MIDI выходного порта (None для автоматического выбора)
        """
        self.bpm = bpm
        self._ticks_per_quarter = 960
        self._running = False
        self._playback_threads = []
        self._stop_event = threading.Event()
        self._midi_out = None

        # Инициализация MIDI порта
        self._init_midi_port(output_port)

    def _init_midi_port(self, port_name: Optional[str]):
        """Инициализирует MIDI выходной порт"""
        try:
            if port_name:
                self._midi_out = mido.open_output(port_name)
            else:
                # Пытаемся найти доступный порт
                available_ports = mido.get_output_names()
                if available_ports:
                    self._midi_out = mido.open_output(available_ports[0])
                else:
                    if sys.platform == 'win32':
                        raise RuntimeError(
                            "No MIDI ports available. On Applications you need to:\n"
                            "1. Install a virtual MIDI driver like loopMIDI\n"
                            "2. OR connect a physical MIDI device\n"
                            "3. OR use MIDI software that creates virtual ports"
                        )
                    else:
                        # Для других ОС пробуем создать виртуальный порт
                        try:
                            self._midi_out = mido.open_output('Python MIDI Out', virtual=True)
                        except:
                            raise RuntimeError("No MIDI ports available and cannot create virtual port")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize MIDI port: {e}")

    def _calculate_tick_duration(self, ticks: int) -> float:
        """Конвертирует тики в секунды с учетом текущего темпа"""
        microseconds_per_quarter = 60000000 / self.bpm
        seconds_per_tick = microseconds_per_quarter / (self._ticks_per_quarter * 1000000)
        return ticks * seconds_per_tick

    def _play_sequence(self, sequence: List[Union[Note, Event]], start_tick: int = 0):
        """Воспроизводит последовательность нот/событий с учётом velocity"""
        try:
            start_time = time.time()
            current_time = 0.0

            for item in sequence:
                if self._stop_event.is_set():
                    break

                # Пропускаем события, которые должны были начаться до start_tick
                if item.start_time < start_tick:
                    continue

                # Вычисляем время ожидания до этого события
                wait_time = self._calculate_tick_duration(item.start_time - start_tick) - current_time

                if wait_time > 0:
                    time.sleep(wait_time)
                    current_time += wait_time

                # Обрабатываем ноту или событие
                if isinstance(item, Note):
                    # Отправляем pitch wheel если нужно
                    if item.pitch_wheel != 0:
                        pitch_msg = mido.Message('pitchwheel',
                                                 channel=item.channel,
                                                 pitch=item.pitch_wheel)
                        self._send_midi_message(pitch_msg)

                    # Отправляем note on с учётом velocity
                    velocity = max(1, min(127, item.velocity))  # Ограничиваем диапазон
                    note_on = mido.Message('note_on',
                                           channel=item.channel,
                                           note=item.pitch,
                                           velocity=velocity)
                    self._send_midi_message(note_on)

                    # Запланировать note off (velocity=0 для некоторых синтезаторов)
                    note_off_time =  self._calculate_tick_duration(item.duration)
                     ## print(current_time,self._calculate_tick_duration(item.duration))
                    #note_off_time = 1
                    note_off = mido.Message('note_off',
                                            channel=item.channel,
                                            note=item.pitch,
                                            velocity=0)  # Явно указываем velocity=0
                    self._schedule_midi_message(note_off_time, note_off)

                elif isinstance(item, Event):
                    # Отправляем контрольное событие
                    event_msg = mido.Message('control_change',
                                             channel=item.channel,
                                             control=item.num,
                                             value=item.value)
                    self._send_midi_message(event_msg)

        except Exception as e:
            print(f"Playback error: {e}")

    def _send_midi_message(self, msg):
        """Отправляет MIDI сообщение немедленно"""
        if self._midi_out:
            try:
                self._midi_out.send(msg)
            except Exception as e:
                print(f"Failed to send MIDI message: {e}")

    def _schedule_midi_message(self, timestamp: float, msg):
        """Запланировать MIDI сообщение на определённое время"""

        delay = timestamp
         ## print(delay)
        if delay > 0:
            time.sleep(delay)
        self._send_midi_message(msg)

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

        # Конвертируем время начала в тики
        start_tick = int(start_time / self._calculate_tick_duration(1))

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

        # Посылаем note off на все каналы
        self._all_notes_off()

        # Ждем завершения потоков
        for thread in self._playback_threads:
            thread.join(timeout=0.1)
        self._playback_threads.clear()

    def _all_notes_off(self):
        """Отправляет сообщения note off для всех нот на всех каналах"""
        if not self._midi_out:
            return

        for channel in range(16):
            # Стандартное сообщение all notes off (CC 123)
            try:
                self._midi_out.send(mido.Message(
                    'control_change',
                    channel=channel,
                    control=123,
                    value=0
                ))
                # Дополнительно посылаем note off для всех нот
                for note in range(128):
                    self._midi_out.send(mido.Message(
                        'note_off',
                        channel=channel,
                        note=note,
                        velocity=0
                    ))
            except Exception as e:
                print(f"Failed to send all notes off: {e}")

    def close(self):
        """Закрывает MIDI соединение"""
        self.stop()
        if self._midi_out:
            self._midi_out.close()
            self._midi_out = None


# Пример использования с учётом velocity
if __name__ == "__main__":
    try:
        # Создаем тестовые данные с разной громкостью
        print(mido.get_output_names())
        notes = [
            Note(start_time=0, channel=0, pitch=60, duration=10000, velocity=100, pitch_wheel=0),  # Средняя громкость
            Note(start_time=480, channel=0, pitch=62, duration=480, velocity=100, pitch_wheel=0),
            Note(start_time=550, channel=0, pitch=63, duration=480, velocity=100, pitch_wheel=0),  # # Громкая нота
            Note(start_time=960, channel=0, pitch=64, duration=960, velocity=100, pitch_wheel=8000),
            Note(start_time=960, channel=0, pitch=79, duration=960, velocity=100, pitch_wheel=8000)
            # Тихая нота с pitch bend
        ]

        events = [
            Event(start_time=0, channel=0, num=7, value=127),  # Громкость канала
            Event(start_time=200, channel=0, num=10, value=120),  # Панорама
        ]

        # Пытаемся автоматически найти порт
        player = None
        try:
            player = MidiPlayer(bpm=120#,output_port="loopMIDI Port 1")
                                )
            print("Доступные MIDI порты:", mido.get_output_names())
            print("Используется порт:", player._midi_out.name if player._midi_out else "None")

            print("Начало воспроизведения с разной громкостью нот...")
            player.play({
                "melody": notes,
                "controls": events
            })

            # Ждем 5 секунд или пока пользователь не нажмет Enter
            input("Нажмите Enter для остановки...\n")

        except RuntimeError as e:
            print("Ошибка:", e)
            if sys.platform == 'win32':
                print("\nДля Applications рекомендуем:")
                print("1. Установите loopMIDI (https://www.tobias-erichsen.de/software/loopmidi.html)")
                print("2. Создайте виртуальный порт в loopMIDI")
                print("3. Укажите имя порта при создании MidiPlayer(output_port='Ваш порт')")

    finally:
        if player:
            player.close()
        print("Воспроизведение остановлено")