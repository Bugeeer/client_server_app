# 2. Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в последовательность
# кодов (не используя методы encode и decode) и определить тип, содержимое и длину соответствующих переменных.

TEST_LIST = [
    'class',
    'function',
    'method'
]

for i, word in enumerate(TEST_LIST):
    print(f'"{word}" => \n    '
          f'type: {type(TEST_LIST[i])}\n    '
          f'value: {TEST_LIST[i]}\n    '
          f'length: {len(TEST_LIST[i])}\n')