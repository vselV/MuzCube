import tkinter as tk
from tkinter import messagebox
class FileDict:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._data = {}
        self._load_from_file()

    def _load_from_file(self):
        """Загружает данные из файла в словарь."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line and ':' in line:
                        key, value = line.split(':', 1)
                        self._data[key.strip()] = value.strip()
        except FileNotFoundError:
            # Файл не существует, создадим его при первом сохранении
            pass

    def _save_to_file(self):
        """Сохраняет текущее состояние словаря в файл."""
        with open(self.file_path, 'w', encoding='utf-8') as file:
            for key, value in self._data.items():
                file.write(f"{key}:{value}\n")

    def __setitem__(self, key, value):
        """Добавляет или изменяет элемент."""
        self._data[key] = str(value)
        self._save_to_file()

    def __getitem__(self, key):
        """Возвращает значение по ключу."""
        return self._data[key]

    def __delitem__(self, key):
        """Удаляет элемент по ключу."""
        del self._data[key]
        self._save_to_file()

    def __contains__(self, key):
        """Проверяет наличие ключа."""
        return key in self._data

    def __len__(self):
        """Возвращает количество элементов."""
        return len(self._data)

    def __str__(self):
        """Строковое представление словаря."""
        return str(self._data)

    def keys(self):
        """Возвращает ключи."""
        return self._data.keys()

    def values(self):
        """Возвращает значения."""
        return self._data.values()

    def items(self):
        """Возвращает пары ключ-значение."""
        return self._data.items()

    def get(self, key, default=None):
        """Безопасное получение значения."""
        return self._data.get(key, default)

def add_to_file_dict(file_path: str, key: str, value: str):
    """Добавляет пару ключ-значение в файловый словарь."""
    fd = FileDict(file_path)
    fd[key] = value
  #  messagebox.showinfo("Успех", f"Добавлено: {key}:{value}")

def main(**kwargs):
    file_path = kwargs.get("file","data.txt")  # Путь к файлу с данными

    # Создаем графическое окно
    root = tk.Tk()
    if kwargs.get("top"):
        root.attributes('-topmost', True)
    root.title(kwargs.get("label","Добавить в файловый словарь"))
    root.geometry("300x150")

    # Поля для ввода ключа и значения
    tk.Label(root, text="Ключ:").pack(pady=5)
    key_entry = tk.Entry(root)
    key_entry.pack(pady=5)

    tk.Label(root, text="Значение:").pack(pady=5)
    value_entry = tk.Entry(root)
    value_entry.pack(pady=5)

    keyIn = kwargs.get('key')

    # Кнопка для сохранения

    def on_save():
        key = key_entry.get().strip()
        value = value_entry.get().strip()
        if key and value:
            add_to_file_dict(file_path, key, value)
            root.destroy()  # Закрываем окно после сохранения
       # else:
         #   messagebox.showerror("Ошибка", "Ключ и значение не могут быть пустыми!")
    def on_save2(self):
        on_save()
    if keyIn is not None:
        key_entry.insert(0, keyIn)
        key_entry.config(state="readonly")
        value_entry.focus_set()
        value_entry.bind('<Return>', on_save2)
    save_btn = tk.Button(root, text="Сохранить и закрыть", command=on_save)
    save_btn.pack(pady=10)

   # root.mainloop()
    while True:
        root.update()
        if not root.winfo_exists():
            break
# Пример использования
if __name__ == "__main__":
    main(key = "reaper")
    # Создаем или загружаем словарь из файла
    fd = FileDict("data.txt")

    # Добавляем/изменяем элементы
    fd["name"] = "Alice"
    fd["age"] = "30"
    fd["city"] = "New York"

    # Чтение элементов
    print(fd["name"])  # Alice
    print("age" in fd)  # True

    # Удаление элемента
    del fd["city"]

    # Итерация по элементам
    for key, value in fd.items():
        print(f"{key}: {value}")


