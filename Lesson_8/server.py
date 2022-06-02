import argparse
import logging
import sys
from select import select
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

import logs.server_log_config
from common.utils import send_message, get_message
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, ERROR, \
    DEFAULT_PORT, MAX_CONNECTIONS, MESSAGE, MESSAGE_TEXT, SENDER, RESPONSE_200, RESPONSE_400, \
    DESTINATION, EXIT
from decorators import log

SERVER_LOGGER = logging.getLogger('server')


@log
def process_client_message(message, messages_list, client, clients, names):
    """
    Message handler from clients,
    accepts a dictionary - a message from the client,
    checks the correctness,
    sends a response dictionary to the client with the result of the reception.
    :param message:
    :param messages_list:
    :param client:
    :param clients:
    :param names:
    :return:
    """

    SERVER_LOGGER.debug(f'Разбор сообщения от клиента: {message}')
    # If it is a presence message, accept and reply
    if ACTION in message \
            and message[ACTION] == PRESENCE \
            and TIME in message \
            and USER in message:
        # Register a user if there is none.
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        # Else: send a response and terminate the connection.
        else:
            response = RESPONSE_400
            response[ERROR] = 'Имя пользователя уже занято!'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    # If it is a message, then add it to the messages_list. No answer required.
    elif ACTION in message \
            and message[ACTION] == MESSAGE \
            and DESTINATION in message \
            and TIME in message \
            and SENDER in message \
            and MESSAGE_TEXT in message:
        messages_list.append(message)
        return
    # If the client exits.
    elif ACTION in message \
            and message[ACTION] == EXIT \
            and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    # Else: Bad request.
    else:
        response = RESPONSE_400
        response[ERROR] = 'Некорректный запрос.'
        send_message(client, response)
        return


@log
def process_message(message, names, listen_sockets):
    """
    The function of addressing sending a message to a specific client.
    It accepts a message dictionary, a list of registered users, and listening sockets.
    Returns nothing.
    :param message:
    :param names:
    :param listen_sockets:
    :return:
    """
    if message[DESTINATION] in names \
            and names[message[DESTINATION]] in listen_sockets:
        send_message(names[message[DESTINATION]], message)
        SERVER_LOGGER.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                           f'от пользователя {message[SENDER]}.')
    elif message[DESTINATION] in names \
            and names[message[DESTINATION]] not in listen_sockets:
        raise ConnectionError
    else:
        SERVER_LOGGER.error(f'Отпрвака сообщения невозможна: '
                            f'пользователь {message[DESTINATION]} не зарегистрирован на сервере.')


@log
def arg_parser():
    """ Create a command line argument parser. """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if not 1023 < listen_port < 65536:
        SERVER_LOGGER.critical(
            f'Попытка запуска сервера с указанием неподходящего порта {listen_port}.'
            f'Допустимые адреса: с 1024 по 65535.'
        )
        sys.exit(1)

    return listen_address, listen_port


def main():
    """
    Load command line parameters,
    if there are no parameters, then set the default values.
    """
    listen_address, listen_port = arg_parser()

    SERVER_LOGGER.info(f'Запущен сервер, порт для подключения: {listen_port}, '
                       f'адрес с которого принимаются подключения: {listen_address}.'
                       f'Если адрес не указан, принимаются соединения с любых адресов.')
    # Prepare socket.
    transport = socket(AF_INET, SOCK_STREAM)
    transport.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)
    transport.listen(MAX_CONNECTIONS)

    clients, messages = [], []

    names = dict()  # {client_name: client_socket}

    # Main loop.
    while True:
        # Waiting for the connection, if the timeout - catch the exception.
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            SERVER_LOGGER.info(f'Установлено соединение с компьютером {client_address}')
            clients.append(client)

        recv_data_lst, send_data_lst, err_lst = [], [], []

        # Check for waiting clients
        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select(clients, clients, [], 0)
        except OSError:
            pass

        # Receive messages and if an error, remove the client.
        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    process_client_message(
                        get_message(client_with_message),
                        messages,
                        client_with_message,
                        clients,
                        names
                    )
                except Exception:
                    SERVER_LOGGER.info(
                        f'Клиент {client_with_message.getpeername()} отключился от сервера.'
                    )
                    clients.remove(client_with_message)

        # If there are messages, process each one.
        for message in messages:
            try:
                process_message(message, names, send_data_lst)
            except Exception:
                SERVER_LOGGER.info(f'Связь с клиентом {message[DESTINATION]} была потеряна.')
                clients.remove(names[message[DESTINATION]])
                del names[message[DESTINATION]]
        messages.clear()


if __name__ == '__main__':
    main()
