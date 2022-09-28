# enigma2-avpn
![Kaavio](/doc/kaavio.png)

----- 

## Automaattinen vpn-yhteyden vaihtaja enigma2 kanavalistan striimeille. 
  
  
Vaihtaa automaattisesti sopivan vpn-palvelimen kun kanavalistalla vaihdetaan kanavaa.  
openvpn on asennettava ensin ja sitten vasta tämä lisäosa.  
.ovpn-tiedostot tulee sijaita hakemistossa /etc/avpn.  
  
  
-----
asetustiedosto /etc/avpn/channels.cfg:  
kanavan_nimi;vpn_nimi;striimin_url  
  
Jos kyseinen striimi ei tarvitse vpn-yhteyttä, laita striimin nimeksi pelkkä "-".  
  
  
  

-----
# TODO
- [ ] Omaksi prosesssikseen tai ainakin ei-blokkaavaksi (nyt time.sleep esim)  
- [ ] konffien hakemisto?

