import json
import sys
import unittest

sys.path.append('../')

from ..common.variables import ENCODING, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR
from ..common.utils import send_message, get_message


class TestSocket:
    """
    Class for testing sending and receiving.
    Requires a dictionary when creating.
    """

    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message = None

    def send(self, message_to_send):
        """
        Test send function. Correctly encodes the message.
        Stores what is to be sent to the socket (message_to_send).
        :param message_to_send:
        :return:
        """
        json_test_message = json.dumps(self.test_dict)
        self.encoded_message = json_test_message.encode(ENCODING)
        self.received_message = message_to_send

    def receive(self, max_len):
        """
        Getting data from a socket.
        :param max_len:
        :return:
        """
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(ENCODING)


class TestUtils(unittest.TestCase):
    """
    The test class that actually performs the test.
    """
    test_dict_to_send = {
        ACTION: PRESENCE,
        TIME: 1.1,
        USER: {
            ACCOUNT_NAME: 'test_name'
        }
    }
    test_dict_receive_ok = {RESPONSE: 200}
    test_dict_receive_err = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }

    def test_send_message_correct(self):
        """
        Testing correct sending message.
        :return:
        """
        test_socket = TestSocket(self.test_dict_to_send)
        send_message(test_socket, self.test_dict_to_send)
        self.assertEqual(test_socket.encoded_message, test_socket.received_message)

    def test_send_message_incorrect(self):
        """
        Testing incorrect sending message.
        :return:
        """
        test_socket = TestSocket(self.test_dict_to_send)
        send_message(test_socket, self.test_dict_to_send)
        self.assertRaises(TypeError, send_message, test_socket)

    def test_get_message_correct(self):
        """
        Testing correct getting message.
        :return:
        """
        test_socket_ok = TestSocket(self.test_dict_receive_ok)
        self.assertEqual(get_message(test_socket_ok), self.test_dict_receive_ok)

    def test_get_message_incorrect(self):
        """
        Testing incorrect getting message.
        :return:
        """
        test_socket_err = TestSocket(self.test_dict_receive_err)
        self.assertEqual(get_message(test_socket_err), self.test_dict_receive_err)


if __name__ == '__main__':
    unittest.main()
