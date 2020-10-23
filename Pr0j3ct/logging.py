# logging.py
# implements Server Logger class

class Logger:
    def __init__(self, caller):
        self.caller = caller

    def info(self, message):
        """
        Log information level message
        """
        pass

    def warn(self, message):
        """
        Log warning level message
        """
        pass

    def error(self, message):
        """
        Log error level message
        """
        pass