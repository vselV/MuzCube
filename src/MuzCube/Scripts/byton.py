import base64


def decode_midi_text_event(encoded_data: str) -> str:
    """
    Декодирует Base64 MIDI-мета-ивент и извлекает текстовые данные.
    Формат: 0xFF (мета-ивент) + длина (1 байт) + текст.
    """
    try:
        # Декодируем из Base64
        decoded_bytes = base64.b64decode(encoded_data)

        # Проверяем, что это мета-ивент (0xFF)
        if decoded_bytes[0] != 0xFF:
            raise ValueError("Не MIDI-мета-ивент (первый байт не 0xFF)")

        # Извлекаем длину текста (второй байт)
        text_length = decoded_bytes[1]

        # Извлекаем текст (пропускаем 2 служебных байта)
        text_data = decoded_bytes[2:2 + text_length]

        return text_data.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Ошибка декодирования: {e}")