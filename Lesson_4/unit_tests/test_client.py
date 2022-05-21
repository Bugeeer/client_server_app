import sys
import unittest

sys.path.append('../')

from ..common.variables import TIME, RESPONSE, ERROR, ACTION, PRESENCE, USER, ACCOUNT_NAME
from ..client import create_presence, process_answer


class TestClient(unittest.TestCase):
    def test_create_presence(self):
        """ Correct request """
        test = create_presence()
        test[TIME] = 1.1

        self.assertEqual(test, {
            ACTION: PRESENCE,
            TIME: 1.1,
            USER: {
                ACCOUNT_NAME: 'Guest'
            }
        })

    def test_ok_answer(self):
        """ Correct 'OK' answer """
        self.assertEqual(process_answer({RESPONSE: 200}), '200 : OK')

    def test_bad_request_answer(self):
        """ Correct 'Bad Request' answer """
        self.assertEqual(process_answer({RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')

    def test_no_response(self):
        """ No response exception """
        self.assertRaises(ValueError, process_answer, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
