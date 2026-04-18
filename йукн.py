from functools import partial
import threading
import time
import tkinter as tk
from tkinter.ttk import Progressbar
import queue


def worker(q, r):
    for i in range(10000):
        # Передаём в очередь текущее значение
        q.put(i + 1)
        # Генерируем событие
        r.event_generate('<<Updated>>', when='tail')
        # Спим для наглядности
        time.sleep(0.000001)


def on_update(event, q=None, pb=None):
    # Получаем данные из очереди
    pb['value'] = q.get()
def bt():
    print("bt")

# Создаём очередь для обмена данными между поткоами
q = queue.Queue()

# Создаём окно
root = tk.Tk()
btn=tk.Button(root,text="Click Me", command=bt)
btn.pack()
progressbar = Progressbar(root, orient=tk.HORIZONTAL, length=10000, mode='determinate')
progressbar.pack()

# "Передаём" в обработчик ссылки на очередь и progressbar
handler = partial(on_update, q=q, pb=progressbar)

# Регистрируем обработчик для события обновления progressbar'а
root.bind('<<Updated>>', handler)

# Создаём поток и передаём в него ссылки на очередь и окно
t = threading.Thread(target=worker, args=(q, root))
t.start()

root.mainloop()