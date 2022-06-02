from subprocess import Popen, CREATE_NEW_CONSOLE

PROCESS = []

SENDERS = range(2)
LISTENERS = range(5)

while True:
    ACTION = input(f'Выберите действие: \n'
                   f'   q - выход, \n'
                   f'   s - запустить сервер и клиенты(отправка - {SENDERS[-1] + 1}, приём - {LISTENERS[-1] + 1}), \n'
                   f'   x - закрыть все окна: ')

    if ACTION.lower() == 'q':
        break

    elif ACTION.lower() == 's':
        PROCESS.append(Popen('python server.py', creationflags=CREATE_NEW_CONSOLE))

        for SENDER in SENDERS:
            PROCESS.append(Popen(
                'python client.py -m send',
                creationflags=CREATE_NEW_CONSOLE
            ))

        for LISTENER in LISTENERS:
            PROCESS.append(Popen(
                'python client.py -m listen',
                creationflags=CREATE_NEW_CONSOLE
            ))

    elif ACTION.lower() == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()
