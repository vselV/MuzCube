import time
import threading
import mido
from dataclasses import dataclass
from typing import List, Dict, Optional
from queue import Queue, Empty


@dataclass
class Note:
    start_time: int  # Время начала в тиках (1 четверть = 960 тиков)
    channel: int  # MIDI канал (0-15)
    pitch: int  # Высота ноты (0-127)
    duration: int  # Длительность в тиках
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
        :param output_port: Имя MIDI выходного порта (None для виртуального порта)
        """
        self.bpm = bpm
        self._ticks_per_quarter = 960
        self._running = False
        self._playback_threads = []
        self._stop_event = threading.Event()

        # Открываем MIDI выход
        try:
            
            if output_port:
                self._midi_out = mido.open_output(output_port)
            else:
                self._midi_out = mido.open_output('Virtual MIDI Player', virtual=True)
        except Exception as e:
            raise RuntimeError(f"Не удалось открыть MIDI порт: {e}")

        # Очередь для синхронизации сообщений между потоками
        self._message_queue = Queue()

    def _calculate_tick_duration(self, ticks: int) -> float:
        """Конвертирует тики в секунды с учетом текущего темпа"""
        microseconds_per_quarter = 60000000 / self.bpm
        seconds_per_tick = microseconds_per_quarter / (self._ticks_per_quarter * 1000000)
        return ticks * seconds_per_tick

    def _play_sequence(self, sequence: List, start_tick: int = 0):
        """Воспроизводит последовательность нот/событий"""
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
                        self._message_queue.put(pitch_msg)

                    # Отправляем note on
                    note_on = mido.Message('note_on',
                                           channel=item.channel,
                                           note=item.pitch,
                                           velocity=64)
                    self._message_queue.put(note_on)

                    # Запланировать note off
                    note_off_time = current_time + self._calculate_tick_duration(item.duration)
                    note_off = mido.Message('note_off',
                                            channel=item.channel,
                                            note=item.pitch)
                    self._message_queue.put((note_off_time, note_off))

                elif isinstance(item, Event):
                    # Отправляем контрольное событие
                    event_msg = mido.Message('control_change',
                                             channel=item.channel,
                                             control=item.num,
                                             value=item.value)
                    self._message_queue.put(event_msg)

        except Exception as e:
            print(f"Ошибка при воспроизведении: {e}")

    def _message_sender(self):
        """Отправляет сообщения из очереди на MIDI устройство"""
        scheduled_messages = []

        while self._running or not self._message_queue.empty() or scheduled_messages:
            current_time = time.time()

            # Проверяем запланированные сообщения
            new_scheduled = []
            for msg_time, msg in scheduled_messages:
                if msg_time <= current_time:
                    self._midi_out.send(msg)
                else:
                    new_scheduled.append((msg_time, msg))
            scheduled_messages = new_scheduled

            try:
                # Получаем сообщение из очереди
                item = self._message_queue.get(timeout=0.01)

                if isinstance(item, tuple):
                    # Это запланированное сообщение
                    scheduled_messages.append(item)
                else:
                    # Это немедленное сообщение
                    self._midi_out.send(item)

            except Empty:
                continue

    def play(self, tracks: Dict[str, List], start_time: float = 0.0):
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

        # Запускаем поток для отправки сообщений
        sender_thread = threading.Thread(target=self._message_sender, daemon=True)
        sender_thread.start()

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

        # Очищаем очередь сообщений
        while not self._message_queue.empty():
            try:
                self._message_queue.get_nowait()
            except Empty:
                break

        # Посылаем note off на все каналы
        for channel in range(16):
            for note in range(128):
                self._midi_out.send(mido.Message('note_off', channel=channel, note=note))

        # Ждем завершения потоков
        for thread in self._playback_threads:
            thread.join(timeout=0.1)
        self._playback_threads.clear()

    def close(self):
        """Закрывает MIDI соединение"""
        self.stop()
        self._midi_out.close()


# Пример использования
if __name__ == "__main__":
    # Создаем тестовые данные
    notes = [
        Note(start_time=0, channel=0, pitch=60, duration=480, pitch_wheel=0),  # До на 1/2 ноты
        Note(start_time=480, channel=0, pitch=62, duration=480, pitch_wheel=0),  # Ре на 1/2 ноты
        Note(start_time=960, channel=0, pitch=64, duration=960, pitch_wheel=2000),  # Ми на 1 ноту с pitch bend
    ]

    events = [
        Event(start_time=0, channel=0, num=7, value=100),  # Громкость канала
        Event(start_time=960, channel=0, num=10, value=64),  # Панорама
    ]

    # Создаем и запускаем проигрыватель
    player = MidiPlayer(bpm=120)

    try:
        print("Начало воспроизведения...")
        player.play({
            "melody": notes,
            "controls": events
        })

        # Ждем 5 секунд или пока пользователь не нажмет Enter
        input("Нажмите Enter для остановки...\n")

    finally:
        player.stop()
        player.close()
        print("Воспроизведение остановлено")