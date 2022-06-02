import os
import signal
import subprocess
import sys
from time import sleep

PYTHON_PATH = sys.executable
BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def get_subprocess(file_with_args):
    sleep(0.2)
    file_full_path = f'{PYTHON_PATH} {BASE_PATH}/{file_with_args}'
    args = ['gnome-terminal', '--disable-factory', '--', 'bash', '-c', file_full_path]
    return subprocess.Popen(args, preexec_fn=os.setpgrp)


PROCESS = []
SENDERS = range(2)
LISTENERS = range(2)

while True:
    ACTION = input(f'Выберите действие: \n'
                   f'   q - выход, \n'
                   f'   s - запустить сервер и клиенты(отправка - {SENDERS[-1] + 1}, приём - {LISTENERS[-1] + 1}), \n'
                   f'   x - закрыть все окна: ')

    if ACTION.lower() == 'q':
        break

    elif ACTION.lower() == 's':
        PROCESS.append(get_subprocess('server.py'))

        for SENDER in SENDERS:
            PROCESS.append(get_subprocess('client.py -m send'))

        for LISTENER in LISTENERS:
            PROCESS.append(get_subprocess('client.py -m listen'))

    elif ACTION.lower() == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            os.killpg(VICTIM.pid, signal.SIGINT)
