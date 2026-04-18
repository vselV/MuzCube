import subprocess
# подключение к текущему проекту
result = subprocess.check_output(['lua', '-l', 'demo.lua', '-e', 'test("a", "b")'])