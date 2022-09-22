import os
from twisted.web import resource, http, util, server
from Plugins.Plugin import PluginDescriptor
#from twisted.web.util import redirectTo
import subprocess
import os
import datetime
import time

confpath="/etc/avpn"
logpath="/tmp/avpn"

def main(session, **kwargs):
    pass


def log(logString):
    if not os.path.exists(logpath):
        os.makedirs(logpath)
    tstamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logString = "[apvn " + tstamp + "] " + logString +"\n"
    with open(logpath+"/log.txt", "a+") as f:
        f.write(logString)
    print(logString)

def waitForVpn(): #odottaa kunnes vpn ylhäällä !TODO keksi jotain muuta kuin sleep
    log("odota vpn...")
    time.sleep(3)
    log("vpn valmis, ehkä :D")

def connectOpenvpn(name):
    vpncmd="openvpn " + confpath + "/" + name + ".ovpn >" + logpath + "/openvpnstd.txt 2> " + logpath + "/openvpnerr.txt &"
    log("opening openvpn: "+vpncmd)
    os.system(vpncmd)
    waitForVpn()

def disconnectOpenvpn():
    log("closing openvpn")
    os.system("killall -2 openvpn") #!TODO openvpn:ssä olisi tuki ohjauksellekin RTFM
    waitForVpn()

def runStream(streamName):
    log("runstream "+streamName)
    with open(confpath + "/channels.cfg", "r") as f:
        lines = f.read().splitlines() 

    for line in lines:
        if len(line)>5 and not line.startswith("#"):
            name, wantedVpn, url = line.split(";")
            log("luettu konffista "+name + wantedVpn + url)
            if name == streamName:
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
                    if curVpn != wantedVpn:
                        disconnectOpenvpn() #jos vpn on väärä, tapa se
                        log("sammuta vpn " + curVpn)
                else:
                    curVpn = None

                if wantedVpn != "-" and curVpn != wantedVpn: #jos tämä striimi tarttee vpn:n (miinus niin ei tartte) ja käytössä ei oikea
                    connectOpenvpn(wantedVpn) #avaa oikea vpn
                    log("open vpn " + wantedVpn)
                return url

class AvpnSite(resource.Resource):
    req = None
    
    def render_GET(self, req): #!TODO mikä redirect kelpaisi 4097-soittimelle?
        streamName=str(req.uri).split("?")[-1][:-1] #pelkkä halutun striimin nimi ilman ylimääräistä paskaa
        streamUrl=runStream(streamName)
        req.setResponseCode(301) # Found
        req.setHeader("Location", streamUrl)
        req.setHeader("Content-Type", "text/html; charset=UTF-8")
        return streamUrl.encode()
        # req.redirect(streamUrl)
        # req.finish()
        # return server.NOT_DONE_YET
        #return req
            # util.redirectTo(streamUrl.encode(), req)
        # util.request.finish()
        # return server.NOT_DONE_YET
        #resp="HTTP/1.1 302 Found\n Location: " +streamUrl
        #return resp.encode()
        #util.redirectTo(streamUrl.encode(), req)
        #return (">"+streamUrl+"<").encode()
        
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
