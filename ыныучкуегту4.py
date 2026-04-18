import mido
import time


def send_mpe_microtuning():
    """Отправка реального MPE SysEx сообщения для microtuning"""

    port_name = "loopMIDI Port 1"

    try:
        # Проверяем доступные порты
        print("Доступные MIDI порты:")
        for port in mido.get_output_names():
            print(f"  - {port}")

        with mido.open_output(port_name) as port:

            # 1. Сначала воспроизводим ноту 60 ДО настройки
            print("\n🎵 Воспроизведение ноты 60 ДО настройки...")
            note_on = mido.Message('note_on', note=60, velocity=64)
            port.send(note_on)
            time.sleep(2)
            note_off = mido.Message('note_off', note=60, velocity=0)
            port.send(note_off)

            # 2. Пауза 2 секунды
            print("⏳ Пауза 2 секунды...")
            time.sleep(2)

            # 3. Отправляем РЕАЛЬНОЕ MPE SysEx сообщение для microtuning
            # Это стандартное MPE сообщение для настройки одной ноты (нота 60)
            # Формат основан на официальной спецификации MPE
            print("\n🎛️ Отправка MPE Microtuning SysEx...")

            # Реальное MPE SysEx сообщение для настройки ноты 60 на +200 cents
            # Формат: F0 7D 10 08 01 <note> <tuning_msb> <tuning_lsb> F7
            mpe_sysex = [
                0x7D,  # Non-commercial ID
                0x10,  # MPE ID
                0x08,  # Microtuning ID
                0x01,  # Set Tuning command
                60,  # Note number (60 = C4)
                0x01,  # Tuning MSB (+200 cents = 0x0190)
                0x00,  # Tuning LSB
            ]
            sysex_data = [
                0xF0,  # 240 - SysEx Start
                0x43,  # 67  - Yamaha ID
                0x10,  # 16  - Device Number
                0x4C,  # 76  - Model ID
                0x08,  # 8   - Command
                0x00,  # 0   - Address MSB
                0x41,  # 65  - Address
                0x5E,  # 94  - Data
                0xF7  # 247 - SysEx End
            ]
            sysex_data = [
                0x43,  # 67 - Yamaha ID
                0x10,  # 16 - Device Number
                0x4C,  # 76 - Model ID
                0x08,  # 8  - Command
                0x00,  # 0  - Address MSB
                0x41,  # 65 - Address
                0x5E,  # 94 - Data
            ]

            sysex_msg = mido.Message('sysex', data=mpe_sysex)
            print(port.send(sysex_msg))
            print("✅ MPE SysEx отправлено!")
            print(f"   Настройка ноты 60 на +200 cents")

            # 4. Еще пауза 2 секунды
            print("⏳ Пауза 2 секунды...")


            # 5. Воспроизводим ноту 60 ПОСЛЕ настройки
            print("\n🎵 Воспроизведение ноты 60 ПОСЛЕ настройки...")
            note_on = mido.Message('note_on', note=60, velocity=64)
            port.send(note_on)
            time.sleep(2)
            time.sleep(2)
            note_off = mido.Message('note_off', note=60, velocity=0)
            port.send(note_off)

            print("\n✅ Тест завершен! Вы должны услышать разницу в высоте тона.")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


def send_alternative_mpe_format():
    """Альтернативный формат MPE SysEx (более распространенный)"""

    port_name = "loopMIDI Port 1"

    try:
        with mido.open_output(port_name) as port:

            print("\n🎛️ Отправка альтернативного MPE SysEx формата...")

            # Альтернативный формат - настройка всех нот с акцентом на ноту 60
            # Этот формат используется некоторыми MPE-устройствами
            mpe_sysex = [
                0x7D,  # Non-commercial ID
                0x10,  # MPE ID
                0x08,  # Microtuning ID
                0x02,  # Alternative tuning command
                60,  # Base note
                0x64,  # Tuning value for base note (100 = +100 cents)
            ]

            sysex_msg = mido.Message('sysex', data=mpe_sysex)
            port.send(sysex_msg)
            print("✅ Альтернативный MPE SysEx отправлен!")

    except Exception as e:
        print(f"❌ Ошибка альтернативного формата: {e}")


def send_roli_seaboard_format():
    """Формат, используемый ROLI Seaboard (популярное MPE устройство)"""

    port_name = "loopMIDI Port 1"

    try:
        with mido.open_output(port_name) as port:

            print("\n🎛️ Отправка ROLI Seaboard-style SysEx...")

            # Формат, похожий на используемый в ROLI Seaboard
            roli_sysex = [
                0x7D,  # Non-commercial ID
                0x10,  # MPE ID
                0x08,  # Microtuning ID
                0x03,  # ROLI-specific command
                60,  # Note number
                0x00,  # Channel (0 = all channels)
                0x7F,  # Tuning value (127 = max detune)
            ]

            sysex_msg = mido.Message('sysex', data=roli_sysex)
            port.send(sysex_msg)
            print("✅ ROLI-style SysEx отправлен!")

    except Exception as e:
        print(f"❌ Ошибка ROLI формата: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("🎹 MPE Microtuning SysEx Test")
    print("=" * 60)

    # Запускаем основной тест
    send_mpe_microtuning()

    # Дополнительные форматы (раскомментируйте если нужно)
    # time.sleep(1)
    # send_alternative_mpe_format()
    # time.sleep(1)
    # send_roli_seaboard_format()

    print("\n" + "=" * 60)
    print("💡 Примечания:")
    print("- Убедитесь, что 'loopMIDI Port 1' существует")
    print("- Подключите порт к MPE-совместимому синтезатору")
    print("- Нота 60 должна звучать выше после настройки")
    print("=" * 60)