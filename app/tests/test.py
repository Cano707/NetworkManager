import requests

# Defintion of Metadata



class Test:
    """ Metadata """ 
    class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKCYAN = '\033[96m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    def test_add_device(self):
        fh_router = '''{
            "hostname": "FH-Router",
            "autodetect": false,
            "vendor": "cisco",
            "model": "2911",
            "secret": "admin",
            "ssh": {
                "username": "admin",
                "password": "admin",
                "host": "10.10.10.254",
                "port": "22"
            }
        }'''

        response = requests.post('http://localhost:8000/api/v1/device/router/fhrouter', headers=self.headers, data=fh_router)

        if not response:
            raise Exception("[!] Failed - test_add_device")
        
        print(f"{self.bcolors.OKBLUE}[i] Passed - test_add_device")
        
    def test_get_device(self):
        expected_response = {
            "key": "fhrouter",
            "hostname": "FH-Router",
            "model": "2911",
            "secret": "admin",
            "serial": {
                "username": "",
                "password": "",
                "device_type": ""
                },
            "ssh": {
                "username": "admin",
                "password": "falschesPasswort",
                "host": "10.10.10.254",
                "port": "22",
                "device_type": ""},
            "telnet": {
                "username": "", "password": "",
                "host": "", 
                "port": "23", 
                "device_type": ""
                },
            "vendor":"cisco"
        }

        response = requests.get('http://localhost:8000/api/v1/device/router/fhrouter', headers=self.headers)

        if response != expected_response:
            raise Exception(f"{self.bcolors.FAIL}[!] Failed - test_get_device: {response} does not equal {expected_response}")

        print(f"{self.bcolors.OKBLUE}[i] Passed - test_get_device")

    def test_update_device(self):
        fh_router = '''{
            "ssh": {
                "password": "admin"
            }
        }'''

        response = requests.put('http://localhost:8000/api/v1/device/router/fhrouter', headers=self.headers, data=fh_router)

        if response:
            raise Exception(f"{self.bcolors.FAIL}[!] Failed - test_update_device")

        print(f"{self.bcolors.OKBLUE}[i] Passed: Update FH-Router")

    def test_get_after_update_device(self):
        expected_response = {
            
        }


    def test_add_device_autodetect(self):
        fh_router = '''{
            "hostname": "FH-Router", 
            "autodetect": true,
            "secret": "admin",
            "ssh": {
                "username": "admin",
                "password": "admin",
                "host": "10.10.10.254",
                "port": "22",
                }
        }'''

        response = requests.post('http://localhost:8000/api/v1/device/router/fhrouter', headers=self.headers, data=fh_router)

        if not response:
            raise Exception(f"{self.bcolors.FAIL}[!] Adding FH-Router failed")
    
#### Add FH-Router - Autodetect ####

#### Get FH-Router - Autodetect ####

response = requests.get('http://localhost:8000/api/v1/device/router/fhrouter', headers=headers)

expected_response = {}




