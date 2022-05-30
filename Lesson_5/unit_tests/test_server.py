import sys
import unittest

sys.path.append('../')

from ..common.variables import RESPONSE, ERROR, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME
from ..server import process_client_message


class TestServer(unittest.TestCase):
    err_dict = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }
    ok_dict = {RESPONSE: 200}

    def test_ok_check(self):
        """ Correct request """
        self.assertEqual(process_client_message(
            {
                ACTION: PRESENCE,
                TIME: 1.1,
                USER: {
                    ACCOUNT_NAME: 'Guest'
                }
            }), self.ok_dict)

    # def test_err_check(self):
    #     """ Incorrect request """
    #     self.assertEqual(process_client_message(''), self.err_dict)

    def test_no_action(self):
        """ No action error """
        self.assertEqual(process_client_message(
            {
                TIME: 1.1,
                USER: {
                    ACCOUNT_NAME: 'Guest'
                }
            }), self.err_dict)

    def test_wrong_action(self):
        """ Wrong action error """
        self.assertEqual(process_client_message(
            {
                ACTION: 'Wrong',
                TIME: 1.1,
                USER: {
                    ACCOUNT_NAME: 'Guest'
                }
            }), self.err_dict)

    def test_no_time(self):
        """ No time error """
        self.assertEqual(process_client_message(
            {
                ACTION: PRESENCE,
                USER: {
                    ACCOUNT_NAME: 'Guest'
                }
            }), self.err_dict)

    def test_unknown_user(self):
        """ Not Guest error """
        self.assertEqual(process_client_message(
            {
                ACTION: PRESENCE,
                TIME: 1.1,
                USER: {
                    ACCOUNT_NAME: 'Not_Guest'
                }
            }), self.err_dict)

    def test_no_user(self):
        """ No user error """
        self.assertEqual(process_client_message(
            {
                ACTION: PRESENCE,
                TIME: 1.1
            }), self.err_dict)


if __name__ == '__main__':
    unittest.main()
