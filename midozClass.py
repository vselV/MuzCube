import time
import random
print(time.time())
h = 100000
d = []
for i in range(h):
    d.append(random.random())
d = sorted(d)
print(time.time())
print("ura")
print(d)