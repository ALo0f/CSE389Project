# requests.py
# implements HTTP Request Processer class

from Pr0j3ct.logging import Logger

import socket
import threading
from email.utils import formatdate

class RequestProcessor(threading.Thread):
    def __init__(self, rootDirectory, indexFile, connSocket, connSocketAddress):
        threading.Thread.__init__(self)
        self.rootDirectory = rootDirectory
        self.indexFile = indexFile
        self.connSocket = connSocket
        self.connSocket.settimeout(0.1)
        self.connSocketAddress = connSocketAddress
        self.keep_alive = True
        self.logger = Logger(self.__class__.__name__+" {}".format(self.connSocketAddress))

    def run(self):
        """
        Start processing requests (called by thread scheduler)
        """
        while self.keep_alive:
            # recieve data from client socket
            try:
                received = self.connSocket.recv(2048)
            except socket.timeout: continue
            # decode byte array to string (HTTP request)
            decodedMessage = received.decode("utf-8")
            #debug by using logger function
            # self.logger.info(decodedMessage)
            # handle request
            self._handle(decodedMessage)

    def stop(self):
        """
        Stop processing requests (called by thread scheduler)
        """
        self.keep_alive = False
        self.connSocket.detach()

    def _handle(self, request):
        """
        Handle received request message (POST, GET, HEAD)
        """
        # recognize message type
        # handle POST
        # handle GET
        # handle HEAD
        # handle not implemented
        self._handleERROR(501, "Not Implemented")

    def _send(self, message):
        """
        Send response to client after handling
        """
        self.connSocket.send(message.encode("utf-8"))

    def _sendHEADER(self, responseMessage, contentType, length):
        """
        send http response header
        """
        #create each line of the header
        header = [
            "{}\r\n".format(responseMessage),
            "Date: {}\r\n".format(formatdate(timeval=None, localtime=False, usegmt=True)),
            "Server: Pr0j3ct\r\n",
            "Content-Length: {}\r\n".format(length),
            "Content-Type: {}\r\n".format(contentType),
        ]
        #convert header to a single string
        header = "".join(header)
        header += "\r\n"
        #send header
        self._send(header)

    def _handleGET(self, message):
        """
        handle GET http request
        """
        pass

    def _handleHEAD(self, message):
        """
        handle HEAD http request
        """
        pass

    def _handlePOST(self, message):
        """
        handle POST http request
        """
        pass

    def _handleERROR(self, errorCode, errorMessage):
        """
        handle http request ERROR
        """
        #create each line for the response html
        body = [
            "<!DOCTYPE html>\r\n",
            "<html>\r\n",
            "<head>\r\n",
            "<title>{}</title>\r\n",
            "</head>\r\n",
            "<body>\r\n",
            "<h1>HTTP Error {}: {}</h1>\r\n"
            "</body>\r\n",
            "</html>\r\n",
        ]
        #convert body to a single string
        body = "".join(body).format(errorMessage, errorCode, errorMessage)
        #send header
        self._sendHEADER("HTTP/1.1 {} {}".format(errorCode, errorMessage), "text/html; charset=utf-8", len(body))
        #send body
        self._send(body)