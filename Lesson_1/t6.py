# 6. Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет», «декоратор».
# Проверить кодировку файла по умолчанию. Принудительно открыть файл в формате Unicode и вывести его содержимое.
import locale
from chardet import detect

strings = [
    'сетевое программирование',
    'сокет',
    'декоратор'
]

with open('test_file.txt', 'w', encoding='utf-8') as f:
    for string in strings:
        print(f'{string}', file=f)

with open('test_file.txt', 'rb') as f:
    content = f.read()
encoding = detect(content)['encoding']

with open('test_file.txt', encoding=encoding) as f:
    for line in f:
        print(line, end='')