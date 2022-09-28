#
# opkg update && opkg install openvpn enigma2-plugin-systemplugins-serviceapp
#

from genericpath import isfile
from twisted.web import resource, http, util, server
from Plugins.Plugin import PluginDescriptor
#from twisted.web.util import redirectTo
import subprocess
import os
import datetime
import time

confpath="/etc/avpn" #!TODO mikä oikea paikka?
printpath="/tmp/avpn"

def main(session, **kwargs):
    pass

def bgprocess(): #!TODO mieti miten tää olis järkevää **avaa prosessin joka vahtii milloin openvpn-yhteyttä ei enää tarvita
    cmd="ps ax|grep avpnbg.py|grep -ve grep"
    try:
        avpnbgpros=subprocess.check_output(cmd, shell=True).decode().rstrip()
        print("avpnbg prosessi on jo päällä "+avpnbgpros)
    except:
        print("virhe saada nykyinen avpnbg prosessi, luodaan se!")
        cmd="python3 "+os.path.dirname(os.path.realpath(__file__))+"/avpnbg.py &"
        os.system(cmd)

def waitForVpn(ud): #odottaa kunnes vpn ylhäällä(1) tai alhaalla(0) !TODO keksi jotain muuta kuin sleep
    print("odota vpn...")
    if ud == 1: #vpn on menossa päälle
        for i in range(1, 10):
            ofile = printpath+"/openvpnstd.txt" # vai err???
            if os.path.isfile(ofile): 
                with open(ofile,"r") as f:
                    lines=f.readlines()
                    if "opo" in lines: #vpn on nyt yhdistetty
                        break
            time.sleep(0.2)
    else: #vpn on menossa alas
        time.sleep(1)
    print("vpn tila valmis, ehkä :D")

def connectOpenvpn(name):
    bgprocess() #avaa taustaprosessi
    if not os.path.exists("/dev/net/tun"):
        os.system("mkdir -p /dev/net && mknod /dev/net/tun c 10 200 && chmod 600 /dev/net/tun")
    if not os.path.exists(printpath):
        os.mkdir(printpath)
    vpncmd="openvpn " + confpath + "/" + name + ".ovpn >" + printpath + "/openvpnstd.txt 2> " + printpath + "/openvpnerr.txt &"
    print("opening openvpn: "+vpncmd)
    os.system(vpncmd)
    waitForVpn(1)

def disconnectOpenvpn():
    print("closing openvpn")
    os.system("killall -2 openvpn") #!TODO openvpn:ssä olisi tuki ohjauksellekin RTFM
    waitForVpn(0)

def runStream(streamName):
    print("runstream "+streamName)
    with open(confpath + "/channels.cfg", "r") as f:
        lines = f.read().splitlines() 

    for line in lines:
        if len(line)>5 and not line.startswith("#"):
            name, wantedVpn, url = line.split(";")
            print("luettu konffista "+name + wantedVpn + url)
            if name == streamName:
                cmd="ps ax|grep openvpn|grep -ve grep"
                try:
                    ovpnpros=subprocess.check_output(cmd, shell=True).decode().rstrip()
                    print("openvpn prosessi "+ovpnpros)
                except:
                    ovpnpros=None
                    print("virhe saada nykyinen openvpn prosessi")

                if ovpnpros: #jos openvpn-asiakas on käynnissä
                    curVpn=ovpnpros.split("/")[-1].replace(".ovpn", "") #käytössä olevan vpn-palvelimen nimi ilman .ovpn-päätettä
                    print("nykyinen vpn " + curVpn)
                    if curVpn != wantedVpn:
                        disconnectOpenvpn() #jos vpn on väärä, tapa se
                        print("sammuta vpn " + curVpn)
                else:
                    curVpn = None

                if wantedVpn != "-" and curVpn != wantedVpn: #jos tämä striimi tarttee vpn:n (miinus niin ei tartte) ja käytössä ei oikea
                    connectOpenvpn(wantedVpn) #avaa oikea vpn
                    print("open vpn " + wantedVpn)
                return url

class AvpnSite(resource.Resource):
    req = None
    
    def render_GET(self, req): #!TODO mikä redirect kelpaisi 4097-soittimelle?
        streamName=str(req.uri).split("?")[-1][:-1] #pelkkä halutun striimin nimi ilman ylimääräistä paskaa
        streamUrl=runStream(streamName)
        req.setResponseCode(302) # Found
        req.setHeader("Location", streamUrl)
        req.setHeader("Content-Type", "text/html; charset=UTF-8")
        return streamUrl.encode()
  
    def GET(self, var):
        return self.req.args.get(var, None)[0]

def Plugins(path, **kwargs):
        return [
                    # PluginDescriptor(name="Avpn", description="Avpn",where = PluginDescriptor.WHERE_PLUGINMENU, icon="plugin.png", fnc=main),
                    # PluginDescriptor(name="Avpn", where = PluginDescriptor.WHERE_EXTENSIONSMENU, icon="plugin.png", fnc=main),
          PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=sessionstart, needsRestart=False)
    ]

def sessionstart(reason, **kwargs):                                               
    if reason == 0 and "session" in kwargs:                                                        
        if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/WebInterface/WebChilds/Toplevel.py"):
            from Plugins.Extensions.WebInterface.WebChilds.Toplevel import addExternalChild
            addExternalChild( ("avpn", AvpnSite(), "Avpn", "1", True) )          
        else:                                                                                  
            print("[avpn] Webif not found")
