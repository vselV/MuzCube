import mido
import time
import threading


class MPEMicrotuningTest:
    def __init__(self, port_name="loopMIDI Port 1"):
        self.port_name = port_name
        self.running = False

    def list_ports(self):
        """Показать все доступные MIDI порты"""
        print("Доступные MIDI порты:")
        for i, port in enumerate(mido.get_output_names()):
            print(f"  {i}: {port}")

    def play_test_note(self, note=60, velocity=64, duration=1.0):
        """Воспроизвести тестовую ноту"""
        try:
            with mido.open_output(self.port_name) as port:
                # Включаем ноту
                note_on = mido.Message('note_on', note=note, velocity=velocity)
                port.send(note_on)
                print(f"🎵 Включена нота {note}")

                # Ждем
                time.sleep(duration)

                # Выключаем ноту
                note_off = mido.Message('note_off', note=note, velocity=0)
                port.send(note_off)
                print(f"🔇 Выключена нота {note}")

        except Exception as e:
            print(f"Ошибка воспроизведения ноты: {e}")

    def send_mpe_microtuning(self, tuning_name="Default"):
        """Отправить MPE microtuning сообщение"""
        try:
            with mido.open_output(self.port_name) as port:
                # Создаем данные для настройки (128 значений)
                tuning_data = [64] * 128  # Все ноты настроены стандартно

                # Меняем настройку для ноты 60 (До)
                # Увеличиваем тон на полтона (примерно +100 центов)
                tuning_data[60] = 73  # Значение от 0 до 127

                # Формируем SysEx сообщение для MPE microtuning
                # Формат: F0 7D 10 08 01 <данные> F7
                sysex_header = [0x7D, 0x10, 0x08, 0x01]
                sysex_data = sysex_header + tuning_data

                sysex_msg = mido.Message('sysex', data=sysex_data)
                port.send(sysex_msg)

                print(f"✅ Отправлена настройка: {tuning_name}")
                print(f"   Нота 60 настроена на значение: {tuning_data[60]}")

        except Exception as e:
            print(f"❌ Ошибка отправки настройки: {e}")

    def run_test(self):
        """Запустить полный тест"""
        print("=" * 50)
        print("🎹 MPE Microtuning Test")
        print("=" * 50)

        # Показываем доступные порты
        self.list_ports()
        print(f"\nИспользуемый порт: {self.port_name}")
        print("-" * 50)

        try:
            # Тест 1: Воспроизводим ноту до настройки
            print("\n1. Воспроизведение ноты ДО настройки:")
            self.play_test_note(note=60, duration=2.0)

            # Пауза перед настройкой
            print("\n⏳ Пауза 2 секунды перед настройкой...")
            time.sleep(2)

            # Отправляем настройку MPE
            print("\n2. Отправка MPE microtuning настройки:")
            self.send_mpe_microtuning("Test Tuning")

            # Пауза после настройки
            print("\n⏳ Пауза 2 секунды после настройки...")
            self.play_test_note(note=60, duration=2.0)
            time.sleep(2)
            """
            # Тест 2: Воспроизводим ноту после настройки
            print("\n3. Воспроизведение ноты ПОСЛЕ настройки:")
            self.play_test_note(note=60, duration=2.0)

            # Дополнительный тест: воспроизводим соседние ноты для сравнения
            print("\n4. Сравнение с соседними нотами:")
            self.play_test_note(note=59, duration=1.0)
            time.sleep(0.5)
            self.play_test_note(note=60, duration=1.0)
            time.sleep(0.5)
            self.play_test_note(note=61, duration=1.0)

            print("\n✅ Тест завершен!")
            """
        except KeyboardInterrupt:
            print("\n⏹️ Тест прерван пользователем")
        except Exception as e:
            print(f"\n❌ Ошибка во время теста: {e}")

    def create_virtual_port_test(self):
        """Альтернативный тест с созданием виртуального порта"""
        print("\n🔧 Альтернативный тест с виртуальным портом:")

        try:
            # Пытаемся создать виртуальный порт
            with mido.open_output('MPE Test Port', virtual=True) as port:
                print("Создан виртуальный порт: MPE Test Port")

                # Простая нота для теста
                note_on = mido.Message('note_on', note=60, velocity=64)
                port.send(note_on)
                print("Отправлена нота на виртуальный порт")

                time.sleep(1)

                note_off = mido.Message('note_off', note=60, velocity=0)
                port.send(note_off)

        except Exception as e:
            print(f"Не удалось создать виртуальный порт: {e}")


def main():
    """Основная функция"""
    # Создаем экземпляр тестера
    tester = MPEMicrotuningTest("loopMIDI Port 1")

    # Запускаем тест
    tester.run_test()

    # Дополнительная информация
    print("\n" + "=" * 50)
    print("💡 Примечания:")
    print("- Убедитесь, что 'loopMIDI Port 1' доступен")
    print("- Если порт недоступен, проверьте список портов выше")
    print("- Для создания виртуального MIDI порта используйте loopMIDI или аналоги")
    print("=" * 50)


if __name__ == "__main__":
    main()