#taustaprosessi joka valvoo milloin openvpn-yhteyttä ei enää tarvita 


import time
import os
import requests

while True:
    r=requests.get("http://127.0.0.1/web/subservices")

    if not "avpn?" in r.text: #apvn-toisto ei käynnissä
        os.system("killall -2 openvpn")
        quit()
    time.sleep(1)