# logging.py
# implements Server Logger class
import os
from datetime import datetime

class Logger:
    def __init__(self, caller):
        self.caller = caller.replace(".", "_").replace(":", "__")
        self.cache = []
        self.maxCacheSize = 100
        self.defaultFolder = ".log_entry"
        if not os.path.exists(self.defaultFolder):
            os.makedirs(self.defaultFolder)

    def info(self, message):
        """
        Log information level message
        """
        logMessage = "[{} {} {}] {}".format("INFO", datetime.now().strftime("%d/%m/%Y %H:%M:%S"), self.caller, message)
        print(logMessage)
        self.cache.append(logMessage)
        self._update()

    def warn(self, message):
        """
        Log warning level message
        """
        #print("[{} {} {}] {}".format("WARN", datetime.now().strftime("%d/%m/%Y %H:%M:%S"), self.caller, message))
        warnMessage = "[{} {} {}] {}".format("WARN", datetime.now().strftime("%d/%m/%Y %H:%M:%S"), self.caller, message)
        print(warnMessage)
        self.cache.append(warnMessage)
        self._update()

    def error(self, message):
        """
        Log error level message
        """
        #print("[{} {} {}] {}".format("ERROR", datetime.now().strftime("%d/%m/%Y %H:%M:%S"), self.caller, message))
        errorMessage = "[{} {} {}] {}".format("ERROR", datetime.now().strftime("%d/%m/%Y %H:%M:%S"), self.caller, message)
        print(errorMessage)
        self.cache.append(errorMessage)
        self._update()

    def close(self):
        """
        Close logger by saving cached message to log file
        """
        self._save()

    def _update(self):
        """
        Update cache, check cache if exceeds the default value, if yes save it to local space.
        """
        if len(self.cache) > self.maxCacheSize:
            self._save()
            self.cache = []

    def _save(self):
        """
        Save log message to local space
        """
        if len(self.cache) <= 0: return
        with open(os.path.join(self.defaultFolder, "{}.log".format(self.caller)), "a") as logFile:
            for message in self.cache:
                print(message, file=logFile)