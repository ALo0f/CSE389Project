# script for handling login.html parameters

import os
import sys
import argparse
from email.utils import formatdate

HEADER_Accepted = [
    "HTTP/1.1 302 Verified\r\n",
    "Date: {}\r\n".format(formatdate(timeval=None, localtime=False, usegmt=True)),
    "Server: Pr0j3ct subprocess\r\n",
    "Location: /presentation.html\r\n"
]

HEADER_Rejected = [
    "HTTP/1.1 403 Rejected\r\n",
    "Date: {}\r\n".format(formatdate(timeval=None, localtime=False, usegmt=True)),
    "Server: Pr0j3ct subprocess\r\n",
    "Content-Length: {}\r\n",
    "Content-Type: text/html; charset=utf-8\r\n"
]



def verify(rootDirectory, username, password):
    """
    Load local database and verify username and password
    """
    with open(os.path.join(rootDirectory, "users.keys"), "r") as inFile:
        data = inFile.readlines()
        for u, p in zip(data[0::2], data[1::2]):
            if username == u.strip():
                if password == p.strip(): return True
                break
    return False

def accept():
    """
    print header_accpeted
    """
    print("".join(HEADER_Accepted), end="")
    print()

def reject(rootDirectory):
    """
    print head rejected and print html content
    """
    with open(os.path.join(rootDirectory, "login.html.rejected.html"), "r") as inFile:
        data = inFile.read()
    print("".join(HEADER_Rejected).format(len(data)), end="")
    print()
    print(data, end="")
    print()

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", help="username for login")
    parser.add_argument("--password", help="password for login")
    args, _ = parser.parse_known_args()
    if (args.username) and (args.password):
        if verify(os.path.dirname(sys.argv[0]), args.username, args.password):
            accept()
        else:
            reject(os.path.dirname(sys.argv[0]))
    