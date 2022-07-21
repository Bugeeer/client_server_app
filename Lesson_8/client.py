import argparse
import json
import logging
import sys
import threading
import time
import logs.client_log_config
from socket import socket, AF_INET, SOCK_STREAM

from common.utils import send_message, get_message
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, \
    DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, SENDER, MESSAGE_TEXT, EXIT, DESTINATION
from errors import ReqFieldMissingError, ServerError, IncorrectDataReceivedError
from decorators import log

CLIENT_LOGGER = logging.getLogger('client')


@log
def create_exit_message(account_name):
    """ The function creates a dictionary with an exit message. """
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }


@log
def message_from_server(sock, clients_username):
    """ Function - handler of other users' messages coming from the server. """
    while True:
        try:
            message = get_message(sock)
            if ACTION in message \
                    and message[ACTION] == MESSAGE \
                    and SENDER in message \
                    and DESTINATION in message \
                    and MESSAGE_TEXT in message \
                    and message[DESTINATION] == clients_username:

                print(f'Получено сообщение от пользователя {message[SENDER]}:\n'
                      f'{message[MESSAGE_TEXT]}.\n')
                CLIENT_LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:\n'
                                   f'{message[MESSAGE_TEXT]}.')
            else:
                CLIENT_LOGGER.error(f'Получено некорректное сообщение от сервера: {message}.')
        except IncorrectDataReceivedError:
            CLIENT_LOGGER.error(f'Не удалось декодировать полученное сообщение.')
        except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError,
                json.JSONDecodeError):
            CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
            break


@log
def create_message(sock, account_name='Guest'):
    """
    The function requests the message text and returns it.
    It also exits when such a command is entered.
    :param sock:
    :param account_name:
    :return message_dict:
    """
    to_user = input('Введите получателя сообщения: ')
    message = input('Введите сообщение для отправки: ')
    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: to_user,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}.')
    try:
        send_message(sock, message_dict)
        CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя {to_user}.')
    except Exception as err:
        print(err)
        CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
        sys.exit(1)


def print_help():
    """ Function for displaying help on usage. """
    print('Поддерживаемые команды:')
    print('    message - отправит сообщение (Адресат и текст будут запрошены отдельно),')
    print('    help - вывести подсказки по командам,')
    print('    exit - выход из программы.')


@log
def user_interactive(sock, username):
    """ User interaction function, request commands, send messages. """
    print_help()
    while True:
        command = input('Введите команду: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_message(sock, create_exit_message(username))
            print('Завершение соединения.')
            CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
            time.sleep(0.5)
            break
        else:
            print(f'Команда "{command}" не распознана. Попробуйте снова. help - вывести доступные команды.')


@log
def create_presence(account_name):
    """
    The function generates a request for the presence of the client.
    """
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}.')
    return out


@log
def process_answer(message):
    """
    The function parses the server response
    :param message:
    :return:
    """
    CLIENT_LOGGER.debug(f'Разбор сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


@log
def arg_parser():
    """
    Create a command line argument parser and read parameters, return 3 parameters.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(
            f'Попытка запустить клиента с неподходящим номером порта: {server_port}. '
            f'Допустыми адреса с 1024 по 65535. Клиент завершается.'
        )
        sys.exit(1)

    return server_address, server_port, client_name


def main():
    """
    Load command line parameters.
    """
    server_address, server_port, client_name = arg_parser()

    # Launch message.
    print(f'Консольный мессенджер. Клиентский модуль. Имя пользователя: {client_name}.')

    if not client_name:
        client_name = input('Введите имя пользователя: ')

    CLIENT_LOGGER.info(
        f'Запущен клиент с параметрами: адрес сервера = {server_address}, '
        f'порт = {server_port}, режим работы = {client_name}.'
    )

    try:
        transport = socket(AF_INET, SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence(client_name))
        answer = process_answer(get_message(transport))
        CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print('Установлено соединение с сервером.')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать полученную JSON строку.')
        sys.exit(1)
    except ServerError as err:
        CLIENT_LOGGER.error(f'При установке соединения сервер вернул ошибку: {err.text}')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                               f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле '
                            f'{missing_error.missing_field}')
        sys.exit(1)
    else:
        # If the connection to the server is established correctly,
        # start the client process of receiving messages.
        receiver = threading.Thread(target=message_from_server, args=(transport, client_name))
        receiver.daemon = True
        receiver.start()

        # Start sending messages and interact with the user.
        user_interface = threading.Thread(target=user_interactive, args=(transport, client_name))
        user_interface.daemon = True
        user_interface.start()
        CLIENT_LOGGER.debug('Запущены процессы.')

        # Main loop.
        # If one of the threads is terminated,
        # then either the connection is lost or the user entered exit.
        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break

if __name__ == '__main__':
    main()
