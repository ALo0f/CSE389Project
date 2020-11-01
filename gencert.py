# This file creates a X509 certificate for HTTPS support
# reference: https://stackoverflow.com/questions/27164354/create-a-self-signed-x509-certificate-in-python

import os
import sys
import socket
from OpenSSL import crypto

FILE_FOLDER = "certificates"
FILE_CRT = "signed.cert"
FILE_KEY = "signed.private.key"

def generate_certificate():
    if not os.path.exists(FILE_FOLDER):
        os.makedirs(FILE_FOLDER)
    if (not os.path.isfile(os.path.join(FILE_FOLDER, FILE_CRT))) or \
       (not os.path.isfile(os.path.join(FILE_FOLDER, FILE_KEY))):
        # generate a new pair
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)
        # create and fill a X509 certificate
        cert = crypto.X509()
        cert.get_subject().C = "US"                     # country
        cert.get_subject().ST = "New York"              # state/province
        cert.get_subject().L = "Syracuse"               # locality
        cert.get_subject().O = "CSE389 Pr0j3ct Team"    # orgnization
        cert.get_subject().OU = "CSE389 Team"           # orgnization unit
        cert.get_subject().CN = "Pr0j3ct"               # common name
        cert.set_serial_number(2077)                    # serial number
        cert.set_version(2)                             # version
        cert.add_extensions([
            crypto.X509Extension(b'subjectAltName', False,
                ",".join([
                    "DNS:{}".format(socket.gethostname()),
                    "DNS:*.{}".format(socket.gethostname()),
                    "DNS:localhost",
                    "DNS:*.localhost"
                ]).encode()),
            crypto.X509Extension(b"basicConstraints", True, b"CA:true")
        ])                                              # set extensions
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10*365*24*60*60)       # expiration time in seconds
        cert.set_issuer(cert.get_subject())             # issuer
        cert.set_pubkey(key)                            # public key
        cert.sign(key, "SHA256")                        # sign
        # save files
        with open(os.path.join(FILE_FOLDER, FILE_CRT), "wb") as certFile:
            certFile.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        with open(os.path.join(FILE_FOLDER, FILE_KEY), "wb") as keyFile:
            keyFile.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
        print("certificate generated successfully")
    else:
        print("certificate file already exists")

def install_certificate():
    if os.name == "nt":
        os.system("certutil -addstore root .\certificates\signed.cert")
    elif os.name == "posix":
        os.system("")
    else:
        raise Exception("{} platform is not supported".format(os.name))

def uninstall_certificate():
    if os.name == "nt":
        os.system("certutil -delstore root \"Pr0j3ct\"")
    elif os.name == "posix":
        os.system("")
    else:
        raise Exception("{} platform is not supported".format(os.name))

if __name__=="__main__":
    generate_certificate()
    if len(sys.argv) >= 2:
        if sys.argv[1] == "-install":
            install_certificate()
        elif sys.argv[1] == "-uninstall":
            uninstall_certificate()
        else:
            print("Only support argument \"-install\" or \"-uninstall\"")