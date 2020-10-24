# logging.py
# implements Server Logger class
from datetime import datetime

class Logger:
    def __init__(self, caller):
        self.caller = caller
        self.cache = []
        self.maxCacheSize = 100

    def info(self, message):
        """
        Log information level message
        """
        print("[{} {} {}] {}".format("INFO", datetime.now().strftime("%d/%m/%Y %H:%M:%S"), self.caller, message))
        

    def warn(self, message):
        """
        Log warning level message
        """
        print("[{} {} {}] {}".format("WARN", datetime.now().strftime("%d/%m/%Y %H:%M:%S"), self.caller, message))

    def error(self, message):
        """
        Log error level message
        """
        print("[{} {} {}] {}".format("ERROR", datetime.now().strftime("%d/%m/%Y %H:%M:%S"), self.caller, message))

    def _update(self):
        """
        Update cache, check cache if exceeds the default value, if yes save it to local space.
        """
        pass

    def _save(self):
        """
        Save log message to local space
        """
        pass