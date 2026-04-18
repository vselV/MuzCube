from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWidgets import (QWidget, QSlider, QHBoxLayout, QVBoxLayout,
                             QPushButton, QLabel, QMenu, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

import mido
from dataclasses import dataclass
from typing import List
from src.MuzCube.Midi.midi_player import MidiPlayer  # Предполагается, что у вас есть класс MidiPlayer
import midiread


@dataclass
class MidiDuration:
    seconds: float
    ticks: int
    beats: float
    bars: float


class MidiPlayerWidget(QWidget):
    playback_position_changed = pyqtSignal(float)  # Сигнал при изменении позиции

    def __init__(self, parent=None):
        super().__init__(parent)
        self.midi_player = None
        self.events = []
        self.total_duration = MidiDuration(0, 0, 0, 0)
        self.current_position = MidiDuration(0, 0, 0, 0)
        self.is_playing = False
        self.setup_ui()

        # Таймер для обновления позиции
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self.update_position)
        try:
            self.select_port("Microsoft GS Wavetable Synth 0")
        except:
            print(":(")

    def setup_ui(self):
        """Инициализация интерфейса"""
        main_layout = QVBoxLayout(self)

        # Верхняя панель с кнопками и портом
        top_panel = QHBoxLayout()

        # Кнопка воспроизведения/паузы
        self.play_button = QPushButton("▶")
        self.play_button.setFixedSize(30, 30)
        self.play_button.clicked.connect(self.toggle_playback)
        top_panel.addWidget(self.play_button)

        # Кнопка остановки
        self.stop_button = QPushButton("■")
        self.stop_button.setFixedSize(30, 30)
        self.stop_button.clicked.connect(self.stop_playback)
        top_panel.addWidget(self.stop_button)

        # Кнопка выбора MIDI порта
        self.port_button = QPushButton("MIDI Port")
        self.port_button.setFixedSize(100, 30)
        self.port_menu = QMenu()
        self.update_port_menu()
        self.port_button.setMenu(self.port_menu)
        top_panel.addWidget(self.port_button)

        top_panel.addStretch()
        main_layout.addLayout(top_panel)

        # Ползунок проигрывания
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 1000)
        self.position_slider.sliderMoved.connect(self.on_slider_moved)
        self.position_slider.sliderPressed.connect(self.on_slider_pressed)
        self.position_slider.sliderReleased.connect(self.on_slider_released)
        main_layout.addWidget(self.position_slider)

        # Панель с временем
        time_panel = QHBoxLayout()

        self.current_time_label = QLabel("00:00.00")
        self.current_time_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        time_panel.addWidget(self.current_time_label)

        time_panel.addStretch()

        self.total_time_label = QLabel("00:00.00")
        self.total_time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        time_panel.addWidget(self.total_time_label)

        main_layout.addLayout(time_panel)

        # Настройка размеров
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(100)

    def update_port_menu(self):
        """Обновляет меню выбора MIDI портов"""
        self.port_menu.clear()
        available_ports = mido.get_output_names()

        if not available_ports:
            action = QAction("No ports available", self)
            action.setEnabled(False)
            self.port_menu.addAction(action)
        else:
            for port in available_ports:
                action = QAction(port, self)
                action.triggered.connect(lambda _, p=port: self.select_port(p))
                self.port_menu.addAction(action)

    def select_port(self, port_name: str):
        """Выбирает MIDI порт"""
        if self.midi_player:
            self.midi_player.close()

        try:
            self.midi_player = MidiPlayer(port_name=port_name)
            self.port_button.setText(port_name[:10] + "..." if len(port_name) > 10 else port_name)
        except Exception as e:
            print(f"Failed to connect to MIDI port: {e}")

    def load_midi_data(self, events: List, duration: MidiDuration):
        """Загружает MIDI данные для воспроизведения"""
        self.events = events
        self.total_duration = duration
        self.current_position = MidiDuration(0, 0, 0, 0)
        self.update_time_labels()
        self.position_slider.setValue(0)

    def toggle_playback(self):
        """Переключает воспроизведение/паузу"""
        if not self.midi_player:
            print("MIDI port not selected")
            return

        if self.is_playing:
            self.pause_playback()
        else:
            self.start_playback()

    def start_playback(self):
        """Начинает воспроизведение"""
        if not self.events:
            return

        start_time = self.current_position.ticks
        self.midi_player.play_sequence(self.events, start_time)

     #   self.midi_player.special_check(self.events, start_time)
        self.is_playing = True
        self.play_button.setText("❚❚")
        self.position_timer.start(50)  # Обновление каждые 50 мс

    def pause_playback(self):
        """Приостанавливает воспроизведение"""
        if self.midi_player:
            self.midi_player.stop()
        self.is_playing = False
        self.play_button.setText("▶")
        self.position_timer.stop()

    def stop_playback(self):
        """Полностью останавливает воспроизведение"""
        self.pause_playback()
        self.current_position = MidiDuration(0, 0, 0, 0)
        self.position_slider.setValue(0)
        self.update_time_labels()

    def on_slider_moved(self, value):
        """Обработчик перемещения ползунка"""
        if self.total_duration.seconds == 0:
            return

        ratio = value / self.position_slider.maximum()
        new_seconds = ratio * self.total_duration.seconds

        self.current_position = MidiDuration(
            new_seconds,
            int(ratio * self.total_duration.ticks),
            ratio * self.total_duration.beats,
            ratio * self.total_duration.bars
        )

        self.update_time_labels()

        # Если воспроизведение активно, обновляем позицию
        if self.is_playing:
            self.midi_player.stop()
            self.midi_player.play_sequence(self.events, new_seconds)

    def on_slider_pressed(self):
        """При нажатии на ползунок приостанавливаем воспроизведение"""
        if self.is_playing:
            self.was_playing = True
            self.pause_playback()
        else:
            self.was_playing = False

    def on_slider_released(self):
        """При отпускании ползунка возобновляем воспроизведение, если оно было активно"""
        if self.was_playing:
            self.start_playback()

    def update_position(self):
        """Обновляет текущую позицию во время воспроизведения"""
        if not self.midi_player or not self.is_playing:
            return

        # Здесь должна быть логика получения текущей позиции из плеера
        # Для примера будем просто увеличивать время
        new_seconds = self.current_position.seconds + 0.05  # 50 мс

        if new_seconds >= self.total_duration.seconds:
            self.stop_playback()
            return

        ratio = new_seconds / self.total_duration.seconds
        slider_value = int(ratio * self.position_slider.maximum())

        self.position_slider.setValue(slider_value)

        self.current_position = MidiDuration(
            new_seconds,
            int(ratio * self.total_duration.ticks),
            ratio * self.total_duration.beats,
            ratio * self.total_duration.bars
        )

        self.update_time_labels()

    def update_time_labels(self):
        """Обновляет отображение времени"""
        # Форматируем время как MM:SS.mm
        current_mm = int(self.current_position.seconds // 60)
        current_ss = int(self.current_position.seconds % 60)
        current_ff = int((self.current_position.seconds % 1) * 100)
        self.current_time_label.setText(f"{current_mm:02d}:{current_ss:02d}.{current_ff:02d}")

        total_mm = int(self.total_duration.seconds // 60)
        total_ss = int(self.total_duration.seconds % 60)
        total_ff = int((self.total_duration.seconds % 1) * 100)
        self.total_time_label.setText(f"{total_mm:02d}:{total_ss:02d}.{total_ff:02d}")

    def closeEvent(self, event):
        """Обработчик закрытия виджета"""
        if self.midi_player:
            self.midi_player.close()
        self.position_timer.stop()
        super().closeEvent(event)





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.midi_player_widget = MidiPlayerWidget()
        self.setCentralWidget(self.midi_player_widget)

        # Пример загрузки MIDI данных
     #   duration = MidiDuration(seconds=120.5, ticks=115200, beats=120, bars=30)
        duration = midiread.get_midi_duration("a.mid")
        events = midiread.midi_to_events("a.mid")
        self.midi_player_widget.load_midi_data(events, duration)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()