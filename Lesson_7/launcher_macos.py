import os
import signal
import stat
import subprocess
import sys
from time import sleep

PYTHON_PATH = sys.executable
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
CLIENTS_COUNT = 1


def get_subprocess(file_name, args=''):
    sleep(0.5)
    command_file = 'start_node.command'
    file_full_path = f'{BASE_PATH}/{file_name}'

    with open(command_file, 'w', encoding='utf-8') as f:
        f.write(f'#!/bin/sh\npython3 "{file_full_path}" {args}')

    os.chmod(command_file, stat.S_IRWXU)
    return subprocess.Popen(['/usr/bin/open', '-n', '-a', 'Terminal', command_file], shell=False)


PROCESS = []

while True:
    ACTION = input(f'Запустить {CLIENTS_COUNT} клиентов (s) | Закрыть клиентов (x) | Выйти (q): ')

    if ACTION.lower() == 'q':
        break

    elif ACTION.lower() == 's':
        sleep(0.5)
        for i in range(CLIENTS_COUNT):
            PROCESS.append(get_subprocess('client.py'))
            sleep(1)
            PROCESS.append(get_subprocess('client.py', '--mode send'))
            sleep(1)

        print(f'Число запущенных пар клиентских скриптов: {CLIENTS_COUNT}.')

    elif ACTION.lower() == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            os.killpg(VICTIM.pid, signal.SIGINT)
