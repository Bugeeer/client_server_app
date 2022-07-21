# 3. Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.

TEST_LIST = [
    'attribute',
    'класс',
    'функция',
    'type'
]

for word in TEST_LIST:
    try:
        eval(f'b"{word}"')
    except SyntaxError as err:
        print(f'"{word}" cannot be written in byte type.')