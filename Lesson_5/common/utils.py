import json
import os
import sys

sys.path.append(os.path.join(os.getcwd(), '../'))
from variables import MAX_PACKAGE_LENGTH, ENCODING


def get_message(client):
    """
    Message reception and decoding utility.
    Receives bytes - outputs a dictionary. If something else - it raises a ValueError.
    :param client:
    :return:
    """
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


def send_message(sock, message):
    """
    Utility to encode and send a message.
    Receives a dictionary and sends it.
    :param sock:
    :param message:
    :return:
    """
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
