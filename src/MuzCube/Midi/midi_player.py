import time
import threading
import mido
from typing import List, Optional, Union
import sys
from src.MuzCube.Scripts.rGrigDataMethods import *
from src.MuzCube.UtilClasses.dataClass import Note, NoteOff, Event, Tempo, ProgramChange, PitchWheel  # Импортируем классы из вашего файла
import midiread
class PlayerInterface():
    def __init__(self, port):
        self.port_name = "opened"
        self.closed = True
        self._midi_out = None
        if type(port) is str:
            self.port_name = port
            self._init_midi_port(port)
        else:
            self._midi_out = port
        if self._midi_out is not None:
            self.closed = False
    def _init_midi_port(self, port_name: Optional[str]):
        """Инициализирует MIDI выходной порт с обработкой ошибок"""
        try:
            available_ports = mido.get_output_names()
            print(available_ports)
            if not available_ports:
                raise RuntimeError("No MIDI output ports found")

            print("Available MIDI ports:", available_ports)

            if port_name is None:
                port_name = available_ports[0]
                print(f"Using first available port: {port_name}")

            if port_name not in available_ports:
                port_name = available_ports[0]
                self.port_name = port_name

            try:
                self._midi_out = mido.open_output(port_name)

                self.playable = True
            except AttributeError:
                # Обход ошибки с API_UNSPECIFIED
                backend = mido.backends.backend
                self._midi_out = backend.open_output(port_name)

            print(f"Successfully connected to MIDI port: {port_name}")

        except Exception as e:
            error_msg = f"Failed to initialize MIDI port: {e}\n"
            if sys.platform == 'win32':
                error_msg += (
                    "For Applications:\n"
                    "1. Install loopMIDI (https://www.tobias-erichsen.de/software/loopmidi.html)\n"
                    "2. Create virtual port in loopMIDI\n"
                    "3. Specify port name when creating MidiPlayer"
                )
            raise RuntimeError(error_msg)
    def _send_midi_message(self, msg):
        """Безопасная отправка MIDI сообщения"""
        if self._midi_out:
            try:
                self._midi_out.send(msg)
            except Exception as e:
                print(f"Failed to send MIDI message: {e}")
    def play_note(self,item):
        self._send_midi_message(mido.Message(
            'pitchwheel',
            channel=item.channel,
            pitch=item.pitch_wheel
        ))

        self._send_midi_message(mido.Message(
            'note_on',
            channel=item.channel,
            note=item.pitch,
            velocity=item.velocity
        ))
    def play_event(self,item):
        self._send_midi_message(mido.Message(
            'control_change',
            channel=item.channel,
            control=item.num,
            value=item.value
        ))
    def play_note_off(self,item):
        self._send_midi_message(mido.Message(
            'note_off',
            channel=item.channel,
            note=item.pitch,
            velocity=item.velocity
        ))
    def play_program_change(self, item):
        self._send_midi_message(mido.Message(
            'program_change',
            channel=item.channel,
            program=item.program
        ))
    def play_pitch(self,item):
        self._send_midi_message(mido.Message(
            'pitchwheel',
            channel=item.channel,
            pitch=item.value
        ))
    def play_note_with_pitch(self,note,pitch):
        pitch_wheel = max(min(pitch.value + note.pitch_wheel,8196),-8196)
        self._send_midi_message(mido.Message(
            'pitchwheel',
            channel=pitch.channel,
            pitch=pitch_wheel
        ))
        self._send_midi_message(mido.Message(
            'note_on',
            channel=note.channel,
            note=note.pitch,
            velocity=note.velocity
        ))
    def play_pitch_with_note(self,pitch,note):
        pitch_wheel = max(min(pitch.value + note.pitch_wheel, 8196), -8196)
        self._send_midi_message(mido.Message(
            'pitchwheel',
            channel=pitch.channel,
            pitch=pitch_wheel
        ))
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
                print(f"Failed to send all notes off: {e}")

    def close(self):
        self.closed = True
        if self._midi_out:
            self._midi_out.close()
            self._midi_out = None
    def open(self):
        if self.closed:
            self._init_midi_port(self.port_name)

class PlayerManger():
    def __init__(self,players):
        self.players = players
        self.def_port_name = ""
        self.type = ""
        if len(self.players) != 0:
            if type(self.players[0]) == str:
                self.type = "str"
            else:
                self.type = "play"

        self.dict = {}
        if self.type == "play":
            for i in players:
                self.dict[i.port_name] = i
        elif self.type == "str":
            for i in players:
                self.dict[i] = PlayerInterface(i)
        if len(self.dict.values())>0:
            self.def_port_name = list(self.dict.values())[-1]
    def set_def_port_name(self,name):
        self.def_port_name = name
    def open_port(self, port):
        if type(port) == str:
            if self.dict.get(port) is None:
                self.dict[port] = PlayerInterface(port)
        else:
            port.open()
            self.dict[port.port_name] = port

    def close_port(self, port):
        if type(port) == str:
            if self.dict.get(port) is not None:
                self.dict[port].close()
                del self.dict[port]
        else:
            if self.dict.get(port) is not None:
                port.close()
                del self.dict[port.port_name]

    def set_ports(self,massive):
        for port in self.dict.values():
            if port not in massive:
                port.close()
        self.dict = {}
        for port in massive:
            self.open_port(port)

    def def_port(self,port):
        if port == "":
            return self.dict[self.def_port_name]
        return self.dict[port]


    def play_note(self, item, port_name):
        self.def_port(port_name).play_note(item)

    def play_event(self, item, port_name):
        self.def_port(port_name).play_event(item)

    def play_note_off(self, item, port_name):
        self.def_port(port_name).play_note_off(item)

    def play_program_change(self, item, port_name):
        self.def_port(port_name).play_program_change(item)

    def play_pitch(self, item, port_name):
        self.def_port(port_name).play_pitch(item)

    def play_note_with_pitch(self, note, pitch, port_name):
        self.def_port(port_name).play_note_with_pitch(note, pitch)

    def play_pitch_with_note(self, pitch, note, port_name):
        self.def_port(port_name).play_pitch_with_note(pitch, note)

    def _all_notes_off(self):
        """Отправляет сообщения note off для всех каналов"""
        for port in self.dict.values():
            port._all_notes_off()

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
#class PlayerThreadChange()
class PlayerThreadBase():
    def __init__(self,player_manger):
        self._ticks_per_quarter = 960

        self.player_manger = player_manger


        self.mass_start = []
        self.event_start = {}
        self.last_program = None
        self.last_pitch_evt = {}
        self.current_notes = {}
        self.base_bmp = 120
        self._current_bpm = self.base_bmp

        self.sequence = []
        self.last_cook = []
        self.last_loop = []
        self.loop_bol = True
        self.current_time = 0

        self.mass_start = None
        self.event_start = None
        self.last_program = None
        self.col_note = True
        self.last_pitch_evt = None
        self.current_notes = None

        self.thread = None
        self._stop_event = threading.Event()
        self._sequence_event = threading.Event()
        self._restart_event = threading.Event()

        self.check_step = 10
    def set_bpm(self,bpm):
        self._base_bpm= bpm


    def _play_cook(self, sequence: List[Union[Note, NoteOff, Event]], start_tick: float):
        mass_start = []
        event_start = {}
        last_program = None
        last_pitch_evt = {}
        current_notes = {}
        for i in range(16):
            current_notes[i] = []
            last_pitch_evt[i] = PitchWheel(start_time=0, channel=i, value=0)
        for item in sequence:
            if item.start_time < start_tick:
                if isinstance(item, Note):
                    if item.duration + item.start_time > start_tick:
                        mass_start.append(item)
                        current_notes[item.channel].append(item)
                elif isinstance(item, Event):
                    event_start[str(item.num) + "/" + str(item.channel)] = item
                elif isinstance(item, PitchWheel):
                    last_pitch_evt[item.channel] = item
                elif isinstance(item, ProgramChange):
                    last_program = item
                elif isinstance(item, Tempo):
                    self._current_bpm = item.bpm
                continue
            break
        return [mass_start,event_start,last_program,last_pitch_evt,current_notes,self._current_bpm]

    def _calculate_tick_duration(self, ticks: int, current_bpm: float) -> float:
        microseconds_per_quarter = 60000000 / current_bpm
        seconds_per_tick = microseconds_per_quarter / (self._ticks_per_quarter * 1000000)
        return ticks * seconds_per_tick

    def _after_cook(self, sequence: List[Union[Note, NoteOff, Event]], start_tick: float, cook: List,loop_cook : List = None,loop_ticks : List[float] =  None):
        full_cook = cook

        loop_bol = loop_cook is not None
        current_time = 0.0
        while_bol = True
        tick_time = start_tick
        mass_start = cook[0]
        event_start = cook[1]
        last_program = cook[2]
        col_note = True
        last_pitch_evt = cook[3]
        current_notes = cook[4]
        self._current_bpm = cook[5]
        breakflag = False
        while while_bol:
            for item in sequence:
                if self._stop_event.isSet():
                    breakflag = True
                    break
                if item.start_time < start_tick:
                    continue
                if col_note:
                    col_note = False
                    if last_program is not None:
                        self.player_manger.play_program_change(last_program,last_program.port_name)
                    for item2 in mass_start:
                        self.player_manger.play_note(item2,item2.port_name)
                    for item2 in event_start.values():
                        self.player_manger.play_event(item2,item2.port_name)
                current_bpm = self._current_bpm
                wait_time = self._calculate_tick_duration(item.start_time - tick_time, current_bpm)
                current_time += wait_time
                if loop_bol:
                    if current_time > loop_ticks[1]:
                        time.sleep(loop_ticks[1] - current_time + wait_time)
                        current_time = 0
                        tick_time = loop_ticks[0]
                        mass_start = loop_cook[0]
                        event_start = loop_cook[1]
                        last_program = loop_cook[2]
                        col_note = True
                        last_pitch_evt = loop_cook[3]
                        current_notes = loop_cook[4]
                        self._current_bpm = loop_cook[5]
                        break
                if wait_time > 0:
                    time.sleep(wait_time)
                    tick_time = item.start_time
                if isinstance(item, Note):
                    current_notes[item.channel].append(item)
                    if last_pitch_evt[item.channel].value != 0:
                        self.player_manger.play_note_with_pitch(item, last_pitch_evt[item.channel],item.port_name)
                    else:
                        self.player_manger.play_note(item,item.port_name)
                elif isinstance(item, NoteOff):
                    remove_note(current_notes[item.channel],item)
                    self.player_manger.play_note_off(item,item.port_name)
                elif isinstance(item, Event):
                    self.player_manger.play_event(item,item.port_name)
                elif isinstance(item, PitchWheel):
                    if len(current_notes[item.channel]) > 0:
                        self.player_manger.play_pitch_with_note(item, current_notes[item.channel][-1],item.port_name)
                    else:
                        self.player_manger.play_pitch(item,item.port_name)
                elif isinstance(item, Tempo):
                    self._current_bpm = item.bpm
                elif isinstance(item, ProgramChange):
                    self.player_manger.play_program_change(item,item.port_name)
            if breakflag:
                break
            while_bol = loop_bol
    def simple_play(self, sequence: List[Union[Note, NoteOff, Event]], start_tick: float, cook: List,loop_cook : List = None,loop_ticks : List[float] =  None):
        full_cook = cook
        #self.
        self.loop_bol = loop_cook is not None
        current_time = 0.0
        while_bol = True
        tick_time = start_tick

        self.mass_start = cook[0]
        self.event_start = cook[1]
        self.last_program = cook[2]
        self.last_pitch_evt = cook[3]
        self.current_notes = cook[4]
        self._current_bpm = cook[5]

        col_note = True


        breakflag = False
        while while_bol:
            for item in sequence:
                if self._stop_event.isSet():
                    breakflag = True
                    break
                if item.start_time < start_tick:
                    continue
                if col_note:
                    col_note = False
                    if last_program is not None:
                        self.player_manger.play_program_change(last_program, last_program.port_name)
                    for item2 in mass_start:
                        self.player_manger.play_note(item2, item2.port_name)
                    for item2 in event_start.values():
                        self.player_manger.play_event(item2, item2.port_name)
                current_bpm = self._current_bpm
                wait_time = self._calculate_tick_duration(item.start_time - tick_time, current_bpm)
                current_time += wait_time
                loop_bol =6
                if loop_bol:
                    if current_time > loop_ticks[1]:
                        time.sleep(loop_ticks[1] - current_time + wait_time)
                        current_time = 0
                        tick_time = loop_ticks[0]
                        mass_start = loop_cook[0]
                        event_start = loop_cook[1]
                        last_program = loop_cook[2]
                        col_note = True
                        last_pitch_evt = loop_cook[3]
                        current_notes = loop_cook[4]
                        self._current_bpm = loop_cook[5]
                        break
                if wait_time > 0:
                    time.sleep(wait_time)
                    tick_time = item.start_time
                if isinstance(item, Note):
                    current_notes[item.channel].append(item)
                    if last_pitch_evt[item.channel].value != 0:
                        self.player_manger.play_note_with_pitch(item, last_pitch_evt[item.channel], item.port_name)
                    else:
                        self.player_manger.play_note(item, item.port_name)
                elif isinstance(item, NoteOff):
                    remove_note(current_notes[item.channel], item)
                    self.player_manger.play_note_off(item, item.port_name)
                elif isinstance(item, Event):
                    self.player_manger.play_event(item, item.port_name)
                elif isinstance(item, PitchWheel):
                    if len(current_notes[item.channel]) > 0:
                        self.player_manger.play_pitch_with_note(item, current_notes[item.channel][-1], item.port_name)
                    else:
                        self.player_manger.play_pitch(item, item.port_name)
                elif isinstance(item, Tempo):
                    self._current_bpm = item.bpm
                elif isinstance(item, ProgramChange):
                    self.player_manger.play_program_change(item, item.port_name)
            if breakflag:
                break
            #while_bol = loop_bol
    def set_sequence(self,sequence: List[Union[Note, NoteOff, Event, ProgramChange]]):
        self.sequence = sequence
        self._sequence_event.set()

    def fast_check_stops(self,wait_time,step):
        stop_bool = False
        n = int(wait_time/step)
        for i in range(n):
            stop_bool = stop_bool or self._stop_event.isSet()
            if self._sequence_event.isSet():
                self._sequence_event.clear()
                return stop_bool, wait_time - i * step
            elif stop_bool:
                return stop_bool, wait_time - i * step
            time.sleep(step)
        delta = wait_time-step*n
        stop_bool = stop_bool or self._stop_event.isSet()
        if self._sequence_event.isSet():
            self._sequence_event.clear()
            return stop_bool, delta
        elif stop_bool:
            return stop_bool, delta
        time.sleep(delta)
        return stop_bool or self._stop_event.isSet(), 0





class MidiPlayer:
    def __init__(self, initial_bpm: int = 120, port_name: Optional[str] = None):
        """
        Инициализация MIDI проигрывателя

        :param initial_bpm: Начальный темп в ударах в минуту
        :param port_name: Имя MIDI выходного порта
        """
        self.ports = {}

        self.playable = False
        self._initial_bpm = initial_bpm
        self._current_bpm = initial_bpm
        self._ticks_per_quarter = 960
        self._running = False
        self._stop_event = threading.Event()
        self._midi_out = None
        self._tempo_changes = []
        self._playback_threads = []
        self.port_name = port_name

        # Инициализация MIDI порта
        self._init_midi_port(port_name)

    def _init_midi_port(self, port_name: Optional[str]):
        """Инициализирует MIDI выходной порт с обработкой ошибок"""
        try:
            available_ports = mido.get_output_names()
            print(available_ports)
            if not available_ports:
                raise RuntimeError("No MIDI output ports found")

            print("Available MIDI ports:", available_ports)

            if port_name is None:
                port_name = available_ports[0]
                print(f"Using first available port: {port_name}")

            if port_name not in available_ports:
                port_name = available_ports[0]
                self.port_name = port_name

            try:
                self._midi_out = mido.open_output(port_name)

                self.playable = True
            except AttributeError:
                # Обход ошибки с API_UNSPECIFIED
                backend = mido.backends.backend
                self._midi_out = backend.open_output(port_name)

            print(f"Successfully connected to MIDI port: {port_name}")

        except Exception as e:
            error_msg = f"Failed to initialize MIDI port: {e}\n"
            if sys.platform == 'win32':
                error_msg += (
                    "For Applications:\n"
                    "1. Install loopMIDI (https://www.tobias-erichsen.de/software/loopmidi.html)\n"
                    "2. Create virtual port in loopMIDI\n"
                    "3. Specify port name when creating MidiPlayer"
                )
            raise RuntimeError(error_msg)
    def open_port(self,port_name):
        if self.ports.get(port_name) is not None:
            try:
                available_ports = mido.get_output_names()
                if not available_ports:
                    raise RuntimeError("No MIDI output ports found")

                print("Available MIDI ports:", available_ports)

                if port_name is None:
                    port_name = available_ports[0]
                    print(f"Using first available port: {port_name}")

                if port_name not in available_ports:
                    raise RuntimeError(f"Port '{port_name}' not found")

                try:
                    self.ports[port_name] = mido.open_output(port_name)

                    self.playable = True
                except AttributeError:
                    # Обход ошибки с API_UNSPECIFIED
                    backend = mido.backends.backend
                    self._midi_out = backend.open_output(port_name)

                print(f"Successfully connected to MIDI port: {port_name}")

            except Exception as e:
                error_msg = f"Failed to initialize MIDI port: {e}\n"
                if sys.platform == 'win32':
                    error_msg += (
                        "For Applications:\n"
                        "1. Install loopMIDI (https://www.tobias-erichsen.de/software/loopmidi.html)\n"
                        "2. Create virtual port in loopMIDI\n"
                        "3. Specify port name when creating MidiPlayer"
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
   #     print(ticks, current_bpm)
        microseconds_per_quarter = 60000000 / current_bpm
        seconds_per_tick = microseconds_per_quarter / (self._ticks_per_quarter * 1000000)
        return ticks * seconds_per_tick

    def play_sequence(self, sequence: List[Union[Note, NoteOff, Event]], start_time: float = 0.0):
        """
        Воспроизводит последовательность MIDI событий с указанного времени

        :param sequence: Отсортированный по времени массив событий
        :param start_time: Время начала в секундах от начала композиции
        """
        if self._running:
           self.stop()
        self._running = True
        self._stop_event.clear()
        thread = self.get_thread(sequence,start_time)
        thread.start()
        self._playback_threads.append(thread)
    def get_thread(self, sequence: List[Union[Note, NoteOff, Event]], start_time: float = 0.0):
        # Конвертируем время начала в тики
        start_tick = start_time

        thread = threading.Thread(
            target=self._play_sequence_thread,
            args=(sequence, start_tick),
            daemon=True
        )
        return thread
    def play_note(self,item):
        self._send_midi_message(mido.Message(
            'pitchwheel',
            channel=item.channel,
            pitch=item.pitch_wheel
        ))

        self._send_midi_message(mido.Message(
            'note_on',
            channel=item.channel,
            note=item.pitch,
            velocity=item.velocity
        ))
    def play_event(self,item):
        self._send_midi_message(mido.Message(
            'control_change',
            channel=item.channel,
            control=item.num,
            value=item.value
        ))
    def play_note_off(self,item):
        self._send_midi_message(mido.Message(
            'note_off',
            channel=item.channel,
            note=item.pitch,
            velocity=item.velocity
        ))
    def play_program_change(self, item):
        self._send_midi_message(mido.Message(
            'program_change',
            channel=item.channel,
            program=item.program
        ))
    def play_pitch(self,item):
        self._send_midi_message(mido.Message(
            'pitchwheel',
            channel=item.channel,
            pitch=item.value
        ))
    def play_note_with_pitch(self,note,pitch):
        pitch_wheel = max(min(pitch.value + note.pitch_wheel,8196),-8196)
        self._send_midi_message(mido.Message(
            'pitchwheel',
            channel=pitch.channel,
            pitch=pitch_wheel
        ))
        self._send_midi_message(mido.Message(
            'note_on',
            channel=note.channel,
            note=note.pitch,
            velocity=note.velocity
        ))
    def play_pitch_with_note(self,pitch,note):
        pitch_wheel = max(min(pitch.value + note.pitch_wheel, 8196), -8196)
        self._send_midi_message(mido.Message(
            'pitchwheel',
            channel=pitch.channel,
            pitch=pitch_wheel
        ))
    def _buck(self):
        if self._running:
           self.stop()
        self._running = True
        self._stop_event.clear()
    def _special_thread(self, sequence: List[Union[Note, NoteOff, Event]], start_time: float = 0.0):
        self._buck()
        start_tick = start_time
        mass = self._play_cook(sequence, start_tick)
        thread = StoppableThread(
            target=self._after_cook,
            args=(sequence, start_tick,mass),
            daemon=True
        )
        return thread
    def _special_thread_loop(self, sequence: List[Union[Note, NoteOff, Event]], start_time: float = 0.0,loop_time : List[float] = None):
        if loop_time is None:
            return self._special_thread(sequence, start_time)
        self._buck()
        start_tick = start_time
        mass = self._play_cook(sequence, start_tick)
        loop_tick = loop_time[0]
        loop_mass = self._play_cook(sequence, loop_tick)
        thread = StoppableThread(
            target=self._after_cook,
            args=(sequence, start_tick,mass,loop_mass,loop_time),
            daemon=True
        )
        return thread
    def special_check(self, sequence: List[Union[Note, NoteOff, Event]], start_time: float = 0.0,loop_time : List[float] = None):
        if self._running:
            self.stop()
        self._running = True
        self._stop_event.clear()
        a = self._special_thread(sequence, start_time)
        a.start()
        self._playback_threads.append(a)

    def _play_cook(self, sequence: List[Union[Note, NoteOff, Event]], start_tick: float):
        mass_start = []
        event_start = {}
        last_program = None
        last_pitch_evt = {}
        current_notes = {}
        for i in range(16):
            current_notes[i] = []
            last_pitch_evt[i] = PitchWheel(start_time=0, channel=i, value=0)
        for item in sequence:
            if item.start_time < start_tick:
                if isinstance(item, Note):
                    if item.duration + item.start_time > start_tick:
                        mass_start.append(item)
                        current_notes[item.channel].append(item)
                elif isinstance(item, Event):
                    event_start[str(item.num) + "/" + str(item.channel)] = item
                elif isinstance(item, PitchWheel):
                    last_pitch_evt[item.channel] = item
                elif isinstance(item, ProgramChange):
                    last_program = item
                elif isinstance(item, Tempo):
                    self._current_bpm = item.bpm
                continue
            break
        return [mass_start,event_start,last_program,last_pitch_evt,current_notes,self._current_bpm]
    def _after_cook(self, sequence: List[Union[Note, NoteOff, Event]], start_tick: float, cook: List,loop_cook : List = None,loop_ticks : List[float] =  None):
        loop_bol = loop_cook is not None
        while_bol = True
        current_time = 0.0
        tick_time = start_tick
        mass_start = cook[0]
        event_start = cook[1]
        last_program = cook[2]
        col_note = True
        last_pitch_evt = cook[3]
        current_notes = cook[4]
        self._current_bpm = cook[5]
        breakflag = False
        while while_bol:
            for item in sequence:
                #print(item,self._stop_event.isSet())
                if self._stop_event.isSet():
                    breakflag = True
                    break
                if item.start_time < start_tick:
                    continue
                if col_note:
                    col_note = False
                    if last_program is not None:
                        self.play_program_change(last_program)
                    for item2 in mass_start:
                        self.play_note(item2)
                    for item2 in event_start.values():
                        self.play_event(item2)
                current_bpm = self._current_bpm
                wait_time = self._calculate_tick_duration(item.start_time - tick_time, current_bpm)
                current_time += wait_time
                if loop_bol:
                    if current_time > loop_ticks[1]:
                        time.sleep(loop_ticks[1] - current_time + wait_time)
                        current_time = 0
                        tick_time = loop_ticks[0]
                        mass_start = loop_cook[0]
                        event_start = loop_cook[1]
                        last_program = loop_cook[2]
                        col_note = True
                        last_pitch_evt = loop_cook[3]
                        current_notes = loop_cook[4]
                        self._current_bpm = loop_cook[5]
                        break
                if wait_time > 0:
                    time.sleep(wait_time)
                    tick_time = item.start_time
                if isinstance(item, Note):
                    current_notes[item.channel].append(item)
                    if last_pitch_evt[item.channel].value != 0:
                        self.play_note_with_pitch(item, last_pitch_evt[item.channel])
                    else:
                        self.play_note(item)
                elif isinstance(item, NoteOff):
                  #  current_notes[item.channel].remove(item)
                    remove_note(current_notes[item.channel],item)
                    self.play_note_off(item)
                elif isinstance(item, Event):
                    self.play_event(item)
                elif isinstance(item, PitchWheel):
                    if len(current_notes[item.channel]) > 0:
                        self.play_pitch_with_note(item, current_notes[item.channel][-1])
                    else:
                        self.play_pitch(item)
                elif isinstance(item, Tempo):
                    self._current_bpm = item.bpm
                elif isinstance(item, ProgramChange):
                    self.play_program_change(item)
            if breakflag:
                break
            while_bol = loop_bol

    def _play_sequence_thread(self, sequence: List[Union[Note, NoteOff, Event]], start_tick: float):
        mass = self._play_cook(sequence, start_tick)
        self._after_cook(sequence, start_tick, mass)
    def _play_sequence_thread2(self, sequence: List[Union[Note, NoteOff, Event]], start_tick: float):
        """Поток для воспроизведения последовательности"""
        try:
            playback_start = time.time()
            current_time = 0.0
            last_bpm = self._initial_bpm
            tick_time = start_tick
            mass_start = []
            event_start = {}
            last_program = None
            col_note = True
            last_pitch_evt = {}
            current_notes = {}
            for i in range(16):
                current_notes[i] = []
                last_pitch_evt[i] = PitchWheel(start_time = 0,channel=i,value=0)
            for item in sequence:
                if self._stop_event.is_set():
                    break

                # Пропускаем события до start_tick
                if item.start_time < start_tick:
                    if isinstance(item, Note):
                        if item.duration + item.start_time > start_tick:
                            mass_start.append(item)
                            current_notes[item.channel].append(item)
                    elif isinstance(item, Event):
                        event_start[str(item.num) + "/" + str(item.channel)] = item
                    elif isinstance(item, PitchWheel):
                        last_pitch_evt[item.channel] = item
                    elif isinstance(item, ProgramChange):
                        last_program = item
                    elif isinstance(item, Tempo):
                        self._current_bpm = item.bpm
                    continue
                if col_note:
                    col_note=False
                    if last_program is not None:
                        self.play_program_change(last_program)
                    for item2 in mass_start:
                        self.play_note(item2)
                    for item2 in event_start.values():
                        self.play_event(item2)
                # Получаем текущий BPM
                current_bpm = self._current_bpm
                # Вычисляем время ожидания
                wait_time = self._calculate_tick_duration(item.start_time - tick_time, current_bpm)
                print(item,"a")
                if wait_time > 0:
                    time.sleep(wait_time)
                    current_time += wait_time
                    tick_time = item.start_time

                # Обрабатываем разные типы событий
                if isinstance(item, Note):
                    current_notes[item.channel].append(item)
                    if last_pitch_evt[item.channel].value !=0:
                        self.play_note_with_pitch(item,last_pitch_evt[item.channel])
                    else:
                        self.play_note(item)
                elif isinstance(item, NoteOff):
                    # Отправляем note off
                    remove_note(current_notes[item.channel],item)
                    self.play_note_off(item)
                elif isinstance(item, Event):
                    # Отправляем контрольное событие
                    self.play_event(item)
                elif isinstance(item, PitchWheel):
                    if len(current_notes[item.channel]) > 0:
                        self.play_pitch_with_note(item,current_notes[item.channel][-1])
                    else:
                        self.play_pitch(item)
                elif isinstance(item, Tempo):
                    # Отправляем контрольное событие
                    self._current_bpm = item.bpm
                elif isinstance(item, ProgramChange):
                    # Отправляем note off
                    self.play_program_change(item)



        except Exception as e:
            print(f"Playback error: {e}")
        finally:
            self._running = False

    def _send_midi_message(self, msg):
        """Безопасная отправка MIDI сообщения"""
        if self._midi_out:
            try:
                self._midi_out.send(msg)
            except Exception as e:
                print(f"Failed to send MIDI message: {e}")

    def stop(self):
        """Останавливает все воспроизведение"""
        self._stop_event.set()
        self._all_notes_off()

       # for thread in self._playback_threads:
         #   thread.join(timeout=0.1)
       # print("threads",self._playback_threads)
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
                print(f"Failed to send all notes off: {e}")

    def close(self):
        """Закрывает соединение"""
        self.stop()
        if self._midi_out:
            self._midi_out.close()
            self._midi_out = None

def play_sort_massive_midi(sequence,player,start_time):
    player.play_sequence(sequence, start_time=start_time)
class MidiPlaySync():
    def __init__(self):
        self.players = {}
        self.threads = []
    def open_player(self,port_name):
        if self.players.get(port_name) is None:
            player =  MidiPlayer(port_name = port_name)
            self.players[player.port_name] = player
            return player.port_name
        return port_name
    def play_all(self,lines:List[Union[str,List]],start_time:float = 0.0, loop_time = None):
        self.threads = []
        for line in lines:
            if self.players.get(line[0]):
                self.threads.append(self.players[line[0]]._special_thread_loop(line[1],start_time,loop_time))
        for thread in self.threads:
            thread.start()
    def stop_all(self):
        for thread in self.threads:
            thread.stop()
            thread.join()

            print("threads",thread)
        print("threads", self.threads)
        print("threads", self.threads)
# Пример использования
if __name__ == "__main__":
    try:
        # Создаем тестовую последовательность
        test_sequence = [
            Note(start_time=0, channel=2, pitch=60, velocity=64, pitch_wheel=0,duration = 0),
            Note(start_time=0, channel=0, pitch=64, velocity=64, pitch_wheel=0,duration = 0),
            NoteOff(start_time=480, channel=0, pitch=64, velocity=64, pitch_wheel=0),
            NoteOff(start_time=480, channel=2, pitch=60, velocity=64, pitch_wheel=0),
            Note(start_time=480, channel=0, pitch=62, velocity=80, pitch_wheel=0,duration = 0),
            NoteOff(start_time=960, channel=0, pitch=62, velocity=80, pitch_wheel=0),
            Note(start_time=960, channel=0, pitch=64, velocity=100, pitch_wheel=2000,duration = 0),
            NoteOff(start_time=1920, channel=0, pitch=64, velocity=100, pitch_wheel=2000),
         #   Event(start_time=0, channel=0, num=7, value=100),
         #   Event(start_time=200, channel=0, num=10, value=120),  # Панорама
            # Громкость
            Tempo(start_time=480, bpm=60, time_num=4, time_denum=4)  # Изменение темпа
        ]
        test_sequence = sorted(test_sequence, key= lambda x: (
        x.start_time,
        0 if x.__class__.__name__ == 'Tempo' else 1
        ))
        print(test_sequence)
        test_sequence = midiread.midi_to_events("a.mid")
        print(test_sequence)
        # Инициализируем проигрыватель
        player = MidiPlayer(initial_bpm=30,port_name="loopMIDI Port 1")
       # player.add_tempo_changes([t for t in test_sequence if isinstance(t, Tempo)])

        print("Starting playback from 1 second...")
        player.play_sequence(test_sequence, start_time=480)  # Начинаем с 1 секунды

        input("Press Enter to stop...\n")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'player' in locals():
            player.close()
        print("Playback finished")