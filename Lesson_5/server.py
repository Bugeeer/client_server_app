import argparse
import json
import sys
from socket import socket, AF_INET, SOCK_STREAM
import logging
import logs.server_log_config
from errors import IncorrectDataReceivedError
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, \
    DEFAULT_IP_ADDRESS, DEFAULT_PORT, MAX_CONNECTIONS
from common.utils import send_message, get_message

SERVER_LOGGER = logging.getLogger('server')


def process_client_message(message):
    """
    Client message handler.
    Receives a message dictionary from the client, checks for correctness
    and returns a response dictionary to the client.
    :param message:
    :return:
    """
    SERVER_LOGGER.debug(f'Разбор сообщения от клиента: {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message \
            and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }


def create_arg_parser():
    """
    Create a command line argument parser.
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    return parser


def main():
    """
    Loading command line parameters, if there is no parameter, then the default value is set.
    First we handle the port:
    server.py -p 8888 -a 127.0.0.1
    :return:
    """
    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if not 1023 < listen_port < 65536:
        SERVER_LOGGER.critical(f'Попытка запуска сервера с указанием неподходящего порта {listen_port}. '
                               f'Допустимы адреса с 1024 по 65535.')
        sys.exit()
    SERVER_LOGGER.info(f'Запущен сервер, порт для подключения: {listen_port}, '
                       f'адрес с которого принимаются подключения: {listen_address}.'
                       f'Если адрес не указан, принимаются соединения с любых адресов.')

    ################
    # try:
    #     if '-p' in sys.argv:
    #         listen_port = int(sys.argv[sys.argv.index('-p') + 1])
    #     else:
    #         listen_port = DEFAULT_PORT
    #     if listen_port < 1024 or listen_port > 65535:
    #         raise ValueError
    # except IndexError:
    #     print("After the -'p' parameter, you must specify the port number.")
    #     sys.exit(1)
    # except ValueError:
    #     print("Only a number in the range from 1024 to 65535 can be specified as a port.")
    #     sys.exit(1)
    #
    # try:
    #     if '-a' in sys.argv:
    #         listen_address = sys.argv[sys.argv.index('-a') + 1]
    #     else:
    #         listen_address = ''
    # except IndexError:
    #     print("After the -'a' parameter, you must specify the address that the server will listen to.")
    #     sys.exit(1)
    #
    transport = socket(AF_INET, SOCK_STREAM)
    transport.bind((listen_address, listen_port))

    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        SERVER_LOGGER.info(f'Установлено соединение с компьютером {client_address}')
        try:
            message_from_client = get_message(client)
            SERVER_LOGGER.debug(f'Получено сообщение {message_from_client}')
            response = process_client_message(message_from_client)
            SERVER_LOGGER.info(f'Сформирован ответ клиенту {response}')
            send_message(client, response)
            SERVER_LOGGER.debug(f'Соединение с клиентом {client_address} закрывается')
            client.close()
        except (ValueError, json.JSONDecodeError):
            SERVER_LOGGER.error(f'Не удалось декодировать JSON строку, полученную от клиента {client_address}. '
                                f'Соединение закрывается')
            client.close()
        except IncorrectDataReceivedError:
            SERVER_LOGGER.error(f'От клиента {client_address} приняты некорректные данные. '
                                f'Соединение закрывается')
            client.close()



if __name__ == '__main__':
    main()
