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

def log(*t):
    ss=" ".join(map(str,t))
    print("[AVPN] "+ss)

def bgprocess(): #!TODO mieti miten tää olis järkevää **avaa prosessin joka vahtii milloin openvpn-yhteyttä ei enää tarvita
    cmd="ps ax|grep avpnbg.py|grep -ve grep"
    try:
        avpnbgpros=subprocess.check_output(cmd, shell=True).decode().rstrip()
        log("avpnbg prosessi on jo päällä "+avpnbgpros)
    except:
        log("virhe saada nykyinen avpnbg prosessi, luodaan se!")
        cmd="python3 "+os.path.dirname(os.path.realpath(__file__))+"/avpnbg.py &"
        os.system(cmd)

def waitForVpn(ud): #odottaa kunnes vpn ylhäällä(1) tai alhaalla(0) !TODO keksi jotain muuta kuin sleep
    log("odota vpn...")
    if ud == 1: #vpn on menossa päälle
        for i in range(1, 50):
            ofile = printpath+"/openvpnstd.txt" # vai err???
            # log("vpnwaitloop", i, ofile)
            if os.path.isfile(ofile): 
                log("on")
                with open(ofile,"r") as f:
                    lines=f.readlines()
                    if len(lines) > 1:
                        if "Sequence Completed" in lines[-1]: #vpn on nyt yhdistetty
                            log("vpn YHDISTETTY!")
                            break
            time.sleep(0.2)
    else: #vpn on menossa alas
        #ifconfig|grep tun
        for i in range(1, 50):
            log("vpn_OFF_waitloop", i)
            cmd="ifconfig|grep tun|grep -ve grep"
            try:
                avpnbgpros=subprocess.check_output(cmd, shell=True).decode().rstrip()
                #log("openvpn vielä päällä")
            except:
                log("openvpn on POIS")
                break
            time.sleep(0.2)
        log("vpn tila valmis, ehkä :D")

def connectOpenvpn(name):
    bgprocess() #avaa taustaprosessi
    if not os.path.exists("/dev/net/tun"):
        os.system("mkdir -p /dev/net && mknod /dev/net/tun c 10 200 && chmod 600 /dev/net/tun")
    if not os.path.exists(printpath):
        os.mkdir(printpath)
    vpncmd="openvpn " + confpath + "/" + name + ".ovpn >" + printpath + "/openvpnstd.txt 2> " + printpath + "/openvpnerr.txt &"
    log("opening openvpn: "+vpncmd)
    os.system(vpncmd)
    waitForVpn(1)

def disconnectOpenvpn():
    log("closing openvpn")
    os.system("killall -2 openvpn") #!TODO openvpn:ssä olisi tuki ohjauksellekin RTFM
    waitForVpn(0)

def runVpn(ovpnName):
    log("runvpn "+ovpnName)
    # with open(confpath + "/channels.cfg", "r") as f:
    #     lines = f.read().splitlines() 

    # for line in lines:
    #     if len(line)>5 and not line.startswith("#"):
    #         name, wantedVpn, url = line.split(";")
    #         log("luettu konffista "+name + wantedVpn + url)
    #         if name == streamName:
    cmd="ps ax|grep openvpn|grep -ve grep"
    try:
        ovpnpros=subprocess.check_output(cmd, shell=True).decode().rstrip()
        log("openvpn prosessi "+ovpnpros)
    except:
        ovpnpros=None
        log("virhe saada nykyinen openvpn prosessi")

    if ovpnpros: #jos openvpn-asiakas on käynnissä
        curVpn=ovpnpros.split("/")[-1].replace(".ovpn", "") #käytössä olevan vpn-palvelimen nimi ilman .ovpn-päätettä
        log("nykyinen vpn " + curVpn)
        if curVpn != ovpnName:
            disconnectOpenvpn() #jos vpn on väärä, tapa se
            log("sammuta vpn " + curVpn)
    else:
        curVpn = None

    if ovpnName != "-" and curVpn != ovpnName: #jos tämä striimi tarttee vpn:n (miinus niin ei tartte) ja käytössä ei oikea
        connectOpenvpn(ovpnName) #avaa oikea vpn
        log("open vpn " + ovpnName)
    return

class AvpnUrlHelper(resource.Resource): #******************************************************************************************************
    req = None
    
    def render_GET(self, req):
        htmlfile=os.path.dirname(os.path.realpath(__file__))+"/avpnurlhelper.html"
        return open(htmlfile).read().encode()
  
    def GET(self, var):
        return self.req.args.get(var, None)[0]

class AvpnSite(resource.Resource): #******************************************************************************************************
    req = None
    
    def render_GET(self, req): #!TODO mikä redirect kelpaisi 4097-soittimelle?
        log("AAAAA", str(req.args))
        try:
            svpn=req.args[b"vpn"][0].decode()
            surl=req.args[b"url"][0].decode()
        except:
            log("Virhe pyynnössä")
            return None
        log("Avataan", svpn, surl)
        time.sleep(2)
        #streamName=str(req.uri).split("?")[-1][:-1] #pelkkä halutun striimin nimi ilman ylimääräistä paskaa
        #streamUrl=runStream(streamName) #qqq korvaa avaavpn
        runVpn(svpn)
        req.setResponseCode(302) # Found
        req.setHeader("Location", surl)
        req.setHeader("Content-Type", "text/html; charset=UTF-8")
        return surl.encode()
  
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
            addExternalChild( ("avpnurlhelper", AvpnUrlHelper(), "Avpn", "1", True) ) 
        else:                                                                                  
            log("[avpn] Webif not found")
