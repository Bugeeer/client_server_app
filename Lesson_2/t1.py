# 1. Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку
# определенных данных из файлов info_1.txt, info_2.txt, info_3.txt и формирующий новый
# «отчетный» файл в формате CSV. Для этого:
# a. Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с
# данными, их открытие и считывание данных. В этой функции из считанных данных
# необходимо с помощью регулярных выражений извлечь значения параметров
# «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения
# каждого параметра поместить в соответствующий список. Должно получиться четыре
# списка — например, os_prod_list, os_name_list, os_code_list, os_type_list. В этой же
# функции создать главный список для хранения данных отчета — например, main_data
# — и поместить в него названия столбцов отчета в виде списка: «Изготовитель
# системы», «Название ОС», «Код продукта», «Тип системы». Значения для этих
# © geekbrains.ru 16
# столбцов также оформить в виде списка и поместить в файл main_data (также для
# каждого файла);
# b. Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой
# функции реализовать получение данных через вызов функции get_data(), а также
# сохранение подготовленных данных в соответствующий CSV-файл;
# c. Проверить работу программы через вызов функции write_to_csv().

import csv
import re

from chardet import detect


def get_data(items: list):
    headers = [
        'Изготовитель системы',
        'Название ОС',
        'Код продукта',
        'Тип системы'
    ]
    os_prod_list, os_name_list, os_code_list, os_type_list = [], [], [], []
    main_data = [headers, os_prod_list, os_name_list, os_code_list, os_type_list]
    for item in items:
        with open(item, 'rb') as f:
            content = f.read()
            encoding = detect(content)['encoding']
        with open(item, encoding=encoding) as f_enc:
            for line in f_enc:
                for i, header in enumerate(headers):
                    match = re.search(header, line)
                    if match:
                        data = re.sub(header + r'[:]\s{2,}', '', line).strip()
                        main_data[i + 1].append(data)
    data = [main_data[0], *data_to_matrix(main_data[1:])]
    return data


def data_to_matrix(data: list):
    matrix = [['' for j in range(len(data))] for i in range(len(data[1]))]
    for i in range(len(data)):
        for j in range(len(data[1])):
            matrix[j][i] = data[i][j]
    return matrix


def write_to_csv(file_link: str, items: list) -> None:
    main_data = get_data(items)
    with open(file_link, 'w', encoding='utf-8') as f:
        file_writer = csv.writer(f)
        file_writer.writerows(main_data)


if __name__ == '__main__':
    files = [
        'info_1.txt',
        'info_2.txt',
        'info_3.txt'
    ]

    write_to_csv('csa_lesson_2_t-1.csv', files)