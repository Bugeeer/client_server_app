import json
from socket import socket, AF_INET, SOCK_STREAM
import sys

from common.utils import get_message, send_message
from common.variables import *


def process_client_message(message):
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message \
            and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONSE_DEFAULT_IP_ADDRESS: 400,
        ERROR: 'Bad Request'
    }


def main():
    """
    Loading command line parameters, if there is no parameter, then the default value is set.
    First we handle the port:
    server.py -p 8888 -a 127.0.0.1
    :return:
    """

    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        print("After the -'p' parameter, you must specify the port number.")
        sys.exit(1)
    except ValueError:
        print("Only a number in the range from 1024 to 65535 can be specified as a port.")
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''
    except IndexError:
        print("After the -'a' parameter, you must specify the address that the server will listen to.")
        sys.exit(1)

    transport = socket(AF_INET, SOCK_STREAM)
    transport.bind((listen_address, listen_port))

    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        try:
            message_from_client = get_message(client)
            print(message_from_client)
            response = process_client_message(message_from_client)
            send_message(client, response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            print("Incorrect message received from the client.")
            client.close()


if __name__ == '__main__':
    main()