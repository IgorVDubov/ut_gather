class BaseException(Exception):
    """ Base exception """

    def __init__(self, string):
        """ Initialize the exception
        :param string: The message to append to the error
        """
        self.string = string

    def __str__(self):
        return self.string

    def isError(self):
        """Error"""
        return True



class DBException(BaseException):
    """ Error congurating program stucture """

    def __init__(self, string=""):
        """ Initialize the exception
        :param string: The message to append to the error
        """
        self.message = "DB error: %s" % string
        BaseException.__init__(self, self.message)

class ConfigException(BaseException):
    """ Error congurating program stucture """

    def __init__(self, string=""):
        """ Initialize the exception
        :param string: The message to append to the error
        """
        self.message = string
        BaseException.__init__(self, self.message)

class ProgrammException(BaseException):
    """ Error congurating program stucture """

    def __init__(self, string=""):
        """ Initialize the exception
        :param string: The message to append to the error
        """
        self.message = string
        BaseException.__init__(self, self.message)

class ChannelException(BaseException):
    """ Error executing channel """

    def __init__(self, string=""):
        """ Initialize the exception
        :param string: The message to append to the error
        """
        self.message = "[Channels] %s" % string
        BaseException.__init__(self, self.message)

class SourceException(BaseException):
    """ Error getting from data source """

    def __init__(self, string=""):
        """ Initialize the exception
        :param string: The message to append to the error
        """
        self.message = "[Source] %s" % string
        BaseException.__init__(self, self.message)


class ModbusException(SourceException):
    """ Error resulting from Modbus data i/o """

    def __init__(self, string="", function_code=None):
        """ Initialize the exception
        :param string: The message to append to the error
        """
        self.fcode = function_code
        self.message = "[Modbus] %s" % string
        SourceException.__init__(self, self.message)

class ExchangeServerException(BaseException):
    """ Error resulting from data source """

    def __init__(self, string=""):
        """ Initialize the exception
        :param string: The message to append to the error
        """
        self.message = "[ExchangeServer] %s" % string
        BaseException.__init__(self, self.message)

class ModbusExchangeServerException(ExchangeServerException):
    """ Error resulting from Modbus data i/o """

    def __init__(self, string="", function_code=None):
        """ Initialize the exception
        :param string: The message to append to the error
        """
        self.fcode = function_code
        self.message = "[ModbusExchangeServer] %s" % string
        SourceException.__init__(self, self.message)