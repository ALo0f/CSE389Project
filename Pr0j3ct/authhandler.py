# authhandler.py
# implements handler for authentication

from Pr0j3ct.logging import Logger

import os
import glob
import json
import ntpath
import threading
import subprocess

class AuthHandler:
    def __init__(self, rootDirectory):
        self._init_keys()
        self.rootDirectory = rootDirectory
        self.logger = Logger(self.__class__.__name__)
        self._init_rules()
        self.mutex = threading.Condition() # mutex for multithreading synchronization
    
    def _init_keys(self):
        """
        Init keys for rules
        """
        self.KEY_Allow = "Allow"
        self.KEY_Forbidden = "Forbidden"
        self.KEY_Exception = "Exception"
        self.KEY_Database = "Database"
        self.KEY_Username = "Username"
        self.KEY_Files = "Files"
        self.KEY_Handler = "Handler"

    def _init_rules(self):
        """
        Init pre-defined rules in root directory
        """
        rules = {}
        # database = {}
        if not os.path.exists(os.path.join(self.rootDirectory, "rules.json")):
            # if not found, generate default rules
            rules = {
                # allow paths
                self.KEY_Allow: ["*"],
                # forbidden paths, overriden by allowed path
                self.KEY_Forbidden: ["*"],
                # user-specific exception paths
                self.KEY_Exception: [],
                # database
                self.KEY_Database: "",
                # define specific handlers for web page
                self.KEY_Handler: {}
            }
        else:
            with open(os.path.join(self.rootDirectory, "rules.json")) as inFile:
                rules = json.load(inFile)
        # validate rules
        if self.KEY_Allow not in rules.keys():
            self.logger.warn("'{}' not defined in {}, setting to default".format(self.KEY_Allow, os.path.join(self.rootDirectory, "rules.json")))
            rules[self.KEY_Allow] = ["*"]
        if self.KEY_Forbidden not in rules.keys():
            self.logger.warn("'{}' not defined in {}, setting to default".format(self.KEY_Forbidden, os.path.join(self.rootDirectory, "rules.json")))
            rules[self.KEY_Forbidden] = ["*"]
        if self.KEY_Exception not in rules.keys():
            self.logger.warn("'{}' not defined in {}, setting to default".format(self.KEY_Exception, os.path.join(self.rootDirectory, "rules.json")))
            rules[self.KEY_Exception] = []
        if self.KEY_Database not in rules.keys():
            self.logger.warn("'{}' not defined in {}, setting to default".format(self.KEY_Database, os.path.join(self.rootDirectory, "rules.json")))
            rules[self.KEY_Database] = ""
        if self.KEY_Handler not in rules.keys():
            self.logger.warn("'{}' not defined in {}, setting to default".format(self.KEY_Handler, os.path.join(self.rootDirectory, "rules.json")))
            rules[self.KEY_Handler] = {}
        # remove wrong format exceptions
        rulesExceptionToRemove = []
        for item in rules[self.KEY_Exception]:
            if (not self.KEY_Username in item.keys()) or (not self.KEY_Files in item.keys()):
                self.logger.warn("Item {} has wrong format, removed in {}".format(item, os.path.join(self.rootDirectory, "rules.json")))
                rulesExceptionToRemove.append(item)
        for item in rulesExceptionToRemove:
            rules[self.KEY_Exception].remove(item)
        # check database
        if not os.path.exists(os.path.join(self.rootDirectory, rules[self.KEY_Database])):
            self.logger.warn("Database {} not found, removed in {}".format(os.path.join(self.rootDirectory, rules[self.KEY_Database]), os.path.join(self.rootDirectory, "rules.json")))
            rules[self.KEY_Database] = ""
            self.databasePath = None
        else:
            self.databasePath = os.path.join(self.rootDirectory, rules[self.KEY_Database])
        # remove not found handlers
        rulesHandlerToRemove = []
        for key, val in rules[self.KEY_Handler].items():
            if (not os.path.isfile(os.path.join(self.rootDirectory, val))) or (val.split(".")[-1] != "py"):
                self.logger.warn("Handler {} not found or not Python script, removed in {}".format(os.path.join(self.rootDirectory, val), os.path.join(self.rootDirectory, "rules.json")))
                rulesHandlerToRemove.append(key)
        for key in rulesHandlerToRemove:
            del rules[self.KEY_Handler][key]
        self.rules = rules
        self.logger.info("Rules initialized")
        self._save()
        
    def _save(self):
        """
        Save updated rules
        """
        with open(os.path.join(self.rootDirectory, "rules.json"), "w") as outFile:
            json.dump(self.rules, outFile, indent=4)
        self.logger.info("Rules saved")

    def auth(self, path, user=None):
        """
        Authenticate path, given a user
        """
        # if user is given and database is not empty, check exception
        if user and self.database:
            for item in self.rules[self.KEY_Exception]:
                if item[self.KEY_Username] == user:
                    # check if path is exception
                    for filename in item[self.KEY_Files]:
                        # user glob for path matching
                        if os.path.normpath(path) in glob.glob(os.path.join(self.rootDirectory, filename)):
                            return True # access is accepted
                    break
        # else check in allowed paths
        for item in self.rules[self.KEY_Allow]:
            if os.path.normpath(path) in glob.glob(os.path.join(self.rootDirectory, item)):
                return True
        # else check forbidden paths
        for item in self.rules[self.KEY_Forbidden]:
            if os.path.normpath(path) in glob.glob(os.path.join(self.rootDirectory, item)):
                return False
        # by default, return True
        self.logger.warn("Path {} is authenticated, but not mentioned in rules.json".format(path))
        return True

    def handle(self, path, params):
        """
        Handle parameters using specified handlers, only for html pages
        """
        if not params: return []
        pathHead, pathTail = ntpath.split(path)
        filename = pathTail or ntpath.basename(pathHead)
        for key, val in self.rules[self.KEY_Handler].items():
            if key == filename:
                command = "python \"{}\" ".format(glob.glob(os.path.join(self.rootDirectory, val))[0])
                for pKey, pVal in params.items():
                    command += "--{} ".format(pKey)
                    for pValItem in pVal:
                        command += "\"{}\" ".format(pValItem)
                proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                result = proc.communicate()[0]
                if len(result) <= 0: return []
                result = result.decode("utf-8").split("\r\n\r\n") # read output from handler file and convert to string
                result = [x for x in result if x]
                return result
        self.logger.warn("Failed to handle {}, unknown handler".format(path))
        return []

    def shutdown(self):
        """
        Shutdown authentication handler and save updated information and log content
        """
        self._save()
        self.logger.close()