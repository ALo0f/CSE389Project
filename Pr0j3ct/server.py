# server.py
# implements HTTP Server class

from Pr0j3ct.requests import RequestProcessor
from Pr0j3ct.logging import Logger
from Pr0j3ct.scheduler import Scheduler

import os
import sys
import socket

class Server:
    def __init__(self, rootDirectory, port, indexFile="index.html"):
        # check arguments
        if not os.path.exists(rootDirectory):
            raise ValueError("rootDirectory: {} not found".format(rootDirectory))
        self.rootDirectory = os.path.abspath(rootDirectory)
        if port > 65535 or port < 0:
            raise ValueError("port: {} should be in [0,65535]".format(port))
        self.port = port
        if not os.path.isfile(os.path.join(self.rootDirectory, indexFile)):
            raise ValueError("indexFile: {} is not found under {}".format(indexFile, self.rootDirectory))
        self.indexFile = indexFile
        # initialize variables
        self.scheduler = Scheduler()
        self.logger = Logger()
        # log information
        self.logger.info("Server port: {}".format(self.port))
        self.logger.info("Server document root: {}".format(self.rootDirectory))

    def start(self):
        # create server socket
        try:
            serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serversocket.bind((socket.gethostbyname(), self.port))
            serversocket.listen(5)
        except socket.error as e:
            self.logger.error("{}".format(e))
            return
        self.logger.info("Server started")
        # start listening
        try:
            while True:
                clientsocket, clientaddress = serversocket.accept()
                self.logger.info("Client connected: {}".format(clientaddress))
                processor = RequestProcessor(self.rootDirectory, self.indexFile, clientsocket)
                self.scheduler.add(processor)
        except KeyboardInterrupt:
            self.logger.info("Server stopped")
        finally:
            self.scheduler.shutdown()
            serversocket.close()