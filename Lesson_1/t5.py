# 5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из байтовового в строковый тип на кириллице.

import subprocess


def main():
    sites_list = []
    sites_list.append(['ping', 'yandex.com'])
    sites_list.append(['ping', 'youtube.com'])

    for i in sites_list:
        subproc_ping = subprocess.Popen(i, stdout=subprocess.PIPE)
        for line in subproc_ping.stdout:
            print(line.decode(encoding='cp866'))


if __name__ == '__main__':
    try:
        main()
    except Exception as ans:
        print(ans)
