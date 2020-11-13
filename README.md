# CSE389Project
CSE 389 Final Project

------

Test run
```cmd
python main.py website 12345
```

----
## Features:  
HTTP:  
- [X] GET 
- [X] HEAD
- [X] POST
- [X] ERROR Message  

Logging:  
- [X] information
- [X] warning
- [X] Error
- [X] cacheManagement
- [x] logFilesManagement

multi-threading:
- [x] task queue
- [x] thread status tracker
- [x] limit max threads

## Extra Feature:
- [X] authentication
- [x] SSL
- [X] support for all file types
- [X] support for large files (>1GB)

------

## HTTPS Configuration
This section shows how to generate certificate and install it for HTTPS server

### Certificate Generation
Generate SSL X509 certificate by script
```cmd
pip install pyOpenSSL
python gencert.py
```

### Certificate Installation
In order for local browser to connect HTTPS server, need to install generated certificate on local machine  

#### Windows  
Install certificate on Windows (run command in admin mode)
```cmd
python gencert.py -install
```

If no longer need certificate, delete it by  
```cmd
python gencert.py -uninstall
```
Can also manage installed certificate using `mmc`, in `certificates/Trusted Root Certification Authorities/Certificates`, find `Pr0j3ct`  

#### Linux
Install certificate on Linux
```bash
python gencert.py -install
```
To uninstall it, run
```bash
python gencert.py -uninstall
```
For `Ubuntu/Debian`, the certificate is installed at `/usr/local/share/ca-certificates/Pr0j3ct.crt`  
For `Red Hat/CentOS`, the certificate is installed at `/etc/pki/ca-trust/source/anchors/Pr0j3ct.crt`  
For `Arch Linux`, the certificate is installed at `/etc/ca-certificates/trust-source/anchors/Pr0j3ct.crt`

------

## Authentication Rules

A `rules.json` should be put in root directory of the website, which has the format:  
```json
{
    "Allow": [
        "index.html"
    ],
    "Forbidden": [
        "*"
    ],
    "Exception": [
        {
            "Username": "somebody",
            "Files": [
                "somepage.html"
            ]
        }
    ],
    "Database": "database",
    "Handler": {
        "somepage.html": "somepage.html.py"
    }
}
```
* `Allow` -> all allowed pages for all users  
* `Forbidden` -> all forbidden pages, unless specified in `Exception`  
* `Exception` -> accessible files for each specific user  
* `Database` -> a database for the website, storing username and password, can be empty string if no database  
* `Handler` -> script file for handling parameters for each specific html page, script should take in parameters and return new html page in String or None  

