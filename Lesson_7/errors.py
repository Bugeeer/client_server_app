class IncorrectDataReceivedError(Exception):
    """
    Exception - invalid data received from the socket.
    """

    def __str__(self):
        return 'An invalid message was received from the remote computer.'


class NonDictInputError(Exception):
    """
    Exception - function argument is not a dictionary.
    """

    def __str__(self):
        return 'The function argument must be a dictionary.'


class ReqFieldMissingError(Exception):
    """
    Error - a required field is missing in the received dictionary.
    """

    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'Required field {self.missing_field} is missing in the received dictionary.'


class ServerError(Exception):
    """ Exception - server error """

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text
