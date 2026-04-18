import base64

# Исходное искажённое сообщение
distorted_b64 = r"\w9OT1RFIDAgNTUgdGV4dCBleGFs"
clean_distorted = distorted_b64.replace("\\", "")  # Убираем экранирование, если это строка с escape-символами

# Пытаемся декодировать искажённое сообщение
try:
    decoded = base64.b64decode(clean_distorted)
    print("Декодированное искажённое сообщение:", decoded)
except:
    print("Невозможно декодировать как Base64")

# Ожидаемое корректное Base64
correct_b64 = "Tk9URSAwIDU1IHRleHQgZXhhbA=="
decoded_correct = base64.b64decode(correct_b64)
print("Декодированное корректное сообщение:", decoded_correct)

# Возможно, искажённое сообщение — это сдвинутые биты корректного
# Попробуем сдвинуть биты в decoded и посмотреть, получится ли корректное
if True:  # Замените на True, если хотите попробовать битовые сдвиги
    for shift in range(1, 8):
        shifted_bytes = bytes((b << shift) & 0xFF for b in decoded)
        try:
            shifted_decoded = shifted_bytes.decode('utf-8')
            print(f"Сдвиг на {shift} бит влево:", shifted_decoded)
        except:
            pass

# Альтернативно: возможно, в искажённом сообщении лишние символы
# Удалим лишние символы и попробуем декодировать
if len(clean_distorted) > len(correct_b64):
    trimmed = clean_distorted[:len(correct_b64)]
    try:
        decoded_trimmed = base64.b64decode(trimmed)
        print("Декодированное обрезанное сообщение:", decoded_trimmed)
    except:
        print("Не удалось декодировать обрезанное сообщение")