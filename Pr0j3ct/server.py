# server.py
# implements HTTP Server class

from Pr0j3ct.requests import RequestProcessor
from Pr0j3ct.logging import Logger
from Pr0j3ct.scheduler import Scheduler
from Pr0j3ct.authhandler import AuthHandler

import os
import ssl
import socket


"""
This class starts a server socket and listen for any connections and start threads for these connections.
"""
class Server:
    def __init__(self, rootDirectory, port, indexFile="index.html", enableSSL=False):
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
        self.logger = Logger(self.__class__.__name__)
        # log information
        self.logger.info("Server port: {}".format(self.port))
        self.logger.info("Server document root: {}".format(self.rootDirectory))
        # load authentication handler
        self.authHandler = AuthHandler(self.rootDirectory)
        # try to load SSL certificate
        self.SSL_cert_file = os.path.join("certificates", "signed.crt")
        self.SSL_key_file = os.path.join("certificates", "signed.private.key")
        if os.path.isfile(self.SSL_cert_file) and os.path.isfile(self.SSL_key_file) and enableSSL:
            self.SSL_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.SSL_context.load_cert_chain(self.SSL_cert_file, self.SSL_key_file)
            self.SSL_enabled = True
            self.logger.info("Server SSL enabled")
        else:
            self.SSL_context = None
            self.SSL_cert_file = ""
            self.SSL_key_file = ""
            self.SSL_enabled = False
        
        if self.SSL_enabled:
            self.logger.info("Website address is: https://{}:{}".format("localhost", self.port))
        else:
            self.logger.info("Website address is: http://{}:{}".format("localhost", self.port))


    def start(self):
        # create server socket
        try:
            serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serversocket.bind(("", self.port))
            serversocket.listen(5)
            serversocket.settimeout(1)
        except socket.error as e:
            self.logger.error("{}".format(e))
            return
        self.logger.info("Server started")
        # start listening
        try:
            while True:
                try:
                    clientsocket, clientaddress = serversocket.accept()
                    clientaddress = "{}:{}".format(clientaddress[0], clientaddress[1])
                    if self.SSL_enabled:
                        clientsocket = self.SSL_context.wrap_socket(clientsocket, server_side=True)
                    self.logger.info("Client connected: {}".format(clientaddress))
                    processor = RequestProcessor(self.rootDirectory, self.indexFile, clientsocket, clientaddress, self.authHandler)
                    self.scheduler.add(processor)
                except socket.timeout: pass
                except ssl.SSLError as e:
                    # ignore HTTP request error in HTTPS mode
                    self.logger.error(e)
                except ConnectionAbortedError as e:
                    self.logger.error(e)
        except KeyboardInterrupt:
            # on keyboard interrupt, close server and all running sub-threads
            self.logger.info("Server stopped")
            self.scheduler.shutdown()
            self.authHandler.shutdown()
            self.logger.close()
            serversocket.close()