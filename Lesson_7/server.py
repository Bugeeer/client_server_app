import argparse
import json
import logging
import sys
import time
from select import select

import logs.server_log_config
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

from common.utils import send_message, get_message
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, \
    DEFAULT_PORT, MAX_CONNECTIONS, MESSAGE, MESSAGE_TEXT, SENDER
from errors import IncorrectDataReceivedError
from decorators import log

SERVER_LOGGER = logging.getLogger('server')


@log
def process_client_message(message, messages_list, client):
    """
    Message handler from clients,
    accepts a dictionary - a message from the client,
    checks the correctness,
    sends a response dictionary to the client with the result of the reception.
    :param message:
    :param messages_list:
    :param client:
    :return:
    """

    SERVER_LOGGER.debug(f'Разбор сообщения от клиента: {message}')
    if ACTION in message \
            and message[ACTION] == PRESENCE \
            and TIME in message \
            and USER in message \
            and message[USER][ACCOUNT_NAME] == 'Guest':
        send_message(client, {RESPONSE: 200})
        return
    elif ACTION in message \
            and message[ACTION] == MESSAGE \
            and TIME in message \
            and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return
    else:
        send_message(client, {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        })
        return


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
    """ Load command line parameters, if there are no parameters, then set the default values. """
    listen_address, listen_port = arg_parser()

    SERVER_LOGGER.info(f'Запущен сервер, порт для подключения: {listen_port}, '
                       f'адрес с которого принимаются подключения: {listen_address}.'
                       f'Если адрес не указан, принимаются соединения с любых адресов.')

    transport = socket(AF_INET, SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.listen(MAX_CONNECTIONS)
    transport.settimeout(0.5)

    clients, messages = [], []

    while True:
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            SERVER_LOGGER.info(f'Установлено соединение с компьютером {client_address}')
            clients.append(client)

        recv_data_lst, send_data_lst, err_lst = [], [], []

        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select(clients, clients, [], 0)
        except OSError:
            pass

        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    process_client_message(
                        get_message(client_with_message),
                        messages,
                        client_with_message
                    )
                except:
                    SERVER_LOGGER.info(
                        f'Клиент {client_with_message.getpeername()} отключился от сервера.'
                    )
                    clients.remove(client_with_message)

        if messages and send_data_lst:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            for waiting_client in send_data_lst:
                try:
                    send_message(waiting_client, message)
                except:
                    SERVER_LOGGER.info(
                        f'Клиент {waiting_client.getpeername()} отключился от сервера.'
                    )
                    waiting_client.close()
                    clients.remove(waiting_client)


if __name__ == '__main__':
    main()
