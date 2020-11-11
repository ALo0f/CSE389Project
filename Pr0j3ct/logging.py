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
        # if on Windows, enable color mode in terminal
        if (os.name == "nt"): os.system("COLOR")

    def info(self, message):
        """
        Log information level message
        """
        logMessage = "[{} {} {}] {}".format("INFO", datetime.now().strftime("%d/%m/%Y %H:%M:%S"), self.caller, message)
        print(logMessage.replace("INFO", "\033[38;5;46mINFO\033[0m", 1)) # print green INFO
        self.cache.append(logMessage)
        self._update()

    def warn(self, message):
        """
        Log warning level message
        """
        warnMessage = "[{} {} {}] {}".format("WARN", datetime.now().strftime("%d/%m/%Y %H:%M:%S"), self.caller, message)
        print(warnMessage.replace("WARN", "\033[38;5;226m\033[1mWARN\033[0m", 1)) # print yellow and underscore WARN
        self.cache.append(warnMessage)
        self._update()

    def error(self, message):
        """
        Log error level message
        """
        errorMessage = "[{} {} {}] {}".format("ERROR", datetime.now().strftime("%d/%m/%Y %H:%M:%S"), self.caller, message)
        print(errorMessage.replace("ERROR", "\033[38;5;196m\033[5mERROR\033[0m", 1)) # print red and blinking ERROR
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