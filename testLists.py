my_list = [10, 20, 30, 40]
insert_index = 1  # После 20
elements_to_insert = [100, 200]

# Способ 1: Через срезы
my_list[insert_index + 1 : insert_index + 1] = elements_to_insert

print(my_list)  # [10, 20, 100, 200, 30, 40]

# Способ 2: Через insert() в цикле (медленнее)
for elem in reversed(elements_to_insert):
    my_list.insert(insert_index + 1, elem)