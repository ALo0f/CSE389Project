# requests.py
# implements HTTP Request Processer class

from Pr0j3ct.logging import Logger

import threading

class RequestProcessor(threading.Thread):
    def __init__(self, rootDirectory, indexFile, connSocket, connSocketAddress):
        threading.Thread.__init__(self)
        self.rootDirectory = rootDirectory
        self.indexFile = indexFile
        self.connSocket = connSocket
        self.connSocketAddress = connSocketAddress
        self.keep_alive = True
        self.logger = Logger(self.__class__.__name__)

    def run(self):
        """
        Start processing requests (called by thread scheduler)
        """
        while self.keep_alive:
            # data = self.connSocket.recv(1000)
            # print(data.decode("utf-8"))
            # recieve data from client socket
            # decode byte array to string (HTTP request)
            # handle request
            print(self.connSocketAddress)

    def stop(self):
        """
        Stop processing requests (called by thread scheduler)
        """
        self.keep_alive = False

    def _handle(self, request):
        """
        Handle received request message (POST, GET, HEAD)
        """
        # recognize message type
        # handle POST
        # handle GET
        # handle HEAD
        pass

    def _send(self, message):
        """
        Send response to client after handling
        """
        # encode the message to byte array
        # send back data to client socket
        pass