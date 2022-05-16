# 4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления в байтовое
# и выполнить обратное преобразование (используя методы encode и decode).

TEST_LIST = [
    'разработка',
    'администрирование',
    'protocol',
    'standard'
]

for i, word in enumerate(TEST_LIST):
    print(f'"{word}"')
    TEST_LIST[i] = TEST_LIST[i].encode('utf-8')
    print(f'    encode: {TEST_LIST[i]}')
    TEST_LIST[i] = TEST_LIST[i].decode('utf-8')
    print(f'    decode: {TEST_LIST[i]}\n')