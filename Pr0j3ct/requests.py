# requests.py
# implements HTTP Request Processer class

from Pr0j3ct.logging import Logger

import os
import socket
import threading
import mimetypes
import urllib.parse
from email.utils import formatdate

class RequestProcessor(threading.Thread):
    def __init__(self, rootDirectory, indexFile, connSocket, connSocketAddress, authHandler):
        threading.Thread.__init__(self)
        self.rootDirectory = rootDirectory
        self.indexFile = indexFile
        self.authHandler = authHandler
        self.connSocket = connSocket
        self.connSocket.settimeout(1)
        self.connSocketAddress = connSocketAddress
        self.keep_alive = True
        self.logger = Logger(self.__class__.__name__+"_{}".format(self.connSocketAddress))

    def run(self):
        """
        Start processing requests (called by thread scheduler)
        """
        while self.keep_alive:
            # recieve data from client socket
            try:
                received = self.connSocket.recv(2048)
            except socket.timeout: continue
            except socket.error as e:
                self.logger.error(e)
                self.stop()
                break
            # decode byte array to string (HTTP request)
            try:
                decodedMessage = received.decode("utf-8")
            except UnicodeDecodeError as e:
                self.logger.error(e)
                self.stop()
                break
            # handle request
            self._handle(decodedMessage)

    def stop(self):
        """
        Stop processing requests (called by thread scheduler)
        """
        self.keep_alive = False
        self.connSocket.detach()
        self.logger.close()

    def _handle(self, request):
        """
        Handle received request message (POST, GET, HEAD)
        """
        # if empty request, just skip
        if not request.strip():
            return
        # recognize message type
        type = request.split()[0].lower()
        # handle POST
        if type == "post" :
            self._handlePOST(request)
        # handle GET
        elif type == "get" :
            self._handleGET(request)
        # handle HEAD
        elif type == "head" :
            self._handleHEAD(request)
        # handle not implemented
        else:
            self.logger.warn("{} request type is not implemented")
            self._handleERROR(501, "Not Implemented")

    def _send(self, message, binary=False):
        """
        Send response to client after handling\\
        Return `True` if success\\
        Return `False` if error occured
        """
        # set timeout to blocking, for all data to be sent
        try:
            self.connSocket.settimeout(None)
            if binary:
                self.connSocket.send(message)
            else:
                self.connSocket.send(message.encode("utf-8"))
            # set back timeout
            self.connSocket.settimeout(1)
            return True
        except socket.error as e:
            self.logger.error(e)
            return False

    def _sendHEADER(self, responseCode, responseMessage, contentType, length):
        """
        send http response header
        """
        #create each line of the header
        header = [
            "HTTP/1.1 {} {}\r\n".format(responseCode, responseMessage),
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
        received = message.split("\n")[0]
        #convert URL to original string
        targetInfoParsed = urllib.parse.urlparse(received.split()[1])
        targetInfo = urllib.parse.unquote(targetInfoParsed.path)
        targetParams = urllib.parse.parse_qs(targetInfoParsed.query)
        self.logger.info("GET {}".format(targetInfo))
        #if requested root send back index file
        if targetInfo == "/":
            self.authHandler.mutex.acquire()
            data = self.authHandler.handle(os.path.join(self.rootDirectory, self.indexFile), targetParams)
            self.authHandler.mutex.release()
            if len(data) <= 0:
                with open(os.path.join(self.rootDirectory, self.indexFile), "r") as inputFile:
                    data = inputFile.read()
                self._sendHEADER(200, "OK", "text/html; charset=utf-8", len(data))
                self._send(data)
            elif len(data) == 1:
                self._send(data[0] + "\r\n\r\n")
            else:
                self._send(data[0] + "\r\n\r\n")
                self._send(data[1])
        #else try to recognize target file
        else:
            # convert to relative target path
            targetInfo = "." + targetInfo
            #get abosolute filepath
            filePath = os.path.join(self.rootDirectory, targetInfo)
            # if path not exist, send 404 error
            if not os.path.exists(filePath):
                self.logger.warn("GET {} is not a path".format(filePath))
                self._handleERROR(404, "File Not Found")
            # if request target is not a file, send 404 error.
            elif not os.path.isfile(filePath):
                self.logger.warn("GET {} is not a file".format(filePath))
                self._handleERROR(404, "File Not Found")
            #if requested file is out of the root directory, send permission denied. 
            elif os.path.commonpath([self.rootDirectory]) != os.path.commonpath([self.rootDirectory, filePath]):
                self.logger.warn("GET {} not in root directory".format(filePath))
                self._handleERROR(403, "Permission Denied")
            # else send back requested file
            else:
                self.authHandler.mutex.acquire()
                authorized = self.authHandler.auth(filePath, self.connSocketAddress)
                self.authHandler.mutex.release()
                # if not authorized
                if not authorized:
                    self.logger.warn("GET {} not authorized".format(filePath))
                    self._handleERROR(403, "Permission Denied")
                    return
                self.authHandler.mutex.acquire()
                data = self.authHandler.handle(filePath, targetParams)
                self.authHandler.mutex.release()
                if len(data) <= 0:
                    # get file size in bytes
                    fileSize = os.path.getsize(filePath)
                    # get data type
                    datatype, _ = mimetypes.guess_type(filePath)
                    if not datatype:
                        # if not able to guess, set to "application/octet-stream" (default binary file type)
                        self.logger.warn("GET {} unknown mime type, set to application/octet-stream".format(filePath))
                        datatype = "application/octet-stream"
                    # send header and data
                    self._sendHEADER(200, "OK", datatype, fileSize)
                    with open(filePath, "rb") as inputFile:
                        while True:
                            # read every 2048 bytes
                            data = inputFile.read(2048)
                            # if no more data, stop
                            if not data: break
                            # if send data failed, break
                            if not self._send(data, binary=True):
                                self.logger.warn("GET {} failed to send".format(filePath))
                                break
                elif len(data) == 1:
                    self._send(data[0] + "\r\n\r\n")
                else:
                    self._send(data[0] + "\r\n\r\n")
                    self._send(data[1])

    def _handleHEAD(self, message):
        """
        handle HEAD http request
        """
        received = message.split("\n")[0]
        #convert URL to original string
        targetInfoParsed = urllib.parse.urlparse(received.split()[1])
        targetInfo = urllib.parse.unquote(targetInfoParsed.path)
        targetParams = urllib.parse.parse_qs(targetInfoParsed.query)
        self.logger.info("HEAD {}".format(targetInfo))
        #if requested root send back index file header
        if targetInfo == "/" :
            self.authHandler.mutex.acquire()
            data = self.authHandler.handle(os.path.join(self.rootDirectory, self.indexFile), targetParams)
            self.authHandler.mutex.release()
            if len(data) <= 0:
                with open(os.path.join(self.rootDirectory, self.indexFile), "r") as inputFile:
                    data = inputFile.read()
                self._sendHEADER(200, "OK", "text/html; charset=utf-8", len(data))
            elif len(data) == 1:
                self._send(data[0] + "\r\n\r\n")
            else:
                self._send(data[0] + "\r\n\r\n") # first is header information
        else:
            # convert to relative target path
            targetInfo = "." + targetInfo
            #get abosolute filepath
            filePath = os.path.join(self.rootDirectory, targetInfo)
            # if path not exist, send 404 error
            if not os.path.exists(filePath):
                self.logger.warn("HEAD {} is not a path".format(filePath))
                self._handleERROR(404, "File Not Found", nobody=True)
            # if request target is not a file, send 404 error.
            elif not os.path.isfile(filePath):
                self.logger.warn("HEAD {} is not a file".format(filePath))
                self._handleERROR(404, "File Not Found", nobody=True)
            #if requested file is out of the root directory, send permission denied. 
            elif os.path.commonpath([self.rootDirectory]) != os.path.commonpath([self.rootDirectory, filePath]):
                self.logger.warn("HEAD {} not in root directory".format(filePath))
                self._handleERROR(403, "Permission Denied", nobody=True)
            # else send back requested file
            else:
                self.authHandler.mutex.acquire()
                authorized = self.authHandler.auth(filePath, self.connSocketAddress)
                self.authHandler.mutex.release()
                # if not authorized
                if not authorized:
                    self.logger.warn("GET {} not authorized".format(filePath))
                    self._handleERROR(403, "Permission Denied", nobody=True)
                    return
                self.authHandler.mutex.acquire()
                data = self.authHandler.handle(filePath, targetParams)
                self.authHandler.mutex.release()
                if len(data) <= 0:
                    # get file size in bytes
                    fileSize = os.path.getsize(filePath)
                    # get data type
                    datatype, _ = mimetypes.guess_type(filePath)
                    if not datatype:
                        # if not able to guess, set to "application/octet-stream" (default binary file type)
                        self.logger.warn("HEAD {} unknown mime type, set to application/octet-stream".format(filePath))
                        datatype = "application/octet-stream"
                        # send header 
                    self._sendHEADER(200, "OK", datatype, fileSize)
                elif len(data) == 1:
                    self._send(data[0] + "\r\n\r\n")
                else:
                    self._send(data[0] + "\r\n\r\n")

    def _handlePOST(self, message):
        """
        handle POST http request
        """
        # get target info and parameters
        targetInfoParsed = urllib.parse.urlparse(message.split("\n")[0].split()[1])
        targetInfo = urllib.parse.unquote(targetInfoParsed.path)
        targetParams = urllib.parse.parse_qs(message.split("\r\n\r\n")[-1])
        #convert URL to original string
        targetInfo = urllib.parse.unquote(targetInfo)
        self.logger.info("POST {}".format(targetInfo))
        # handle parameters
        self.authHandler.mutex.acquire()
        data = self.authHandler.handle(os.path.join(self.rootDirectory, targetInfo), targetParams)
        self.authHandler.mutex.release()
        if len(data) <= 0:
            self.logger.warn("POST {} is not handled".format(targetInfo))
            self._handleERROR(501, "Not Supported")
        elif len(data) == 1:
            #if is login page, do authentication as well
            if (targetInfo.lower() == "/login.html") and "username" in targetParams.keys():
                # specific case, len(data) == 1 means login success
                self.logger.info("login successful")
                self.authHandler.mutex.acquire()
                self.authHandler.updateUserSession(self.connSocketAddress, targetParams["username"][0])
                self.authHandler.mutex.release()
            self._send(data[0] + "\r\n\r\n")
        else:
            if targetInfo.lower() == "/login.html":
                self.logger.warn("login not successful")
                self.authHandler.mutex.acquire()
                self.authHandler.updateUserSession(self.connSocketAddress, None)
                self.authHandler.mutex.release()
            self._send(data[0] + "\r\n\r\n")
            self._send(data[1])

    def _handleERROR(self, errorCode, errorMessage, nobody=False):
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
        self._sendHEADER(errorCode, errorMessage, "text/html; charset=utf-8", len(body))
        if not nobody:
            #send body
            self._send(body)
