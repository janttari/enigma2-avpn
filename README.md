# enigma2-avpn
![Kaavio](/doc/kaavio.png)

----- 

## Automaattinen vpn-yhteyden vaihtaja enigma2 kanavalistan striimeille. 
  
  
Vaihtaa automaattisesti sopivan vpn-palvelimen kun kanavalistalla vaihdetaan kanavaa.  
openvpn on asennettava ensin ja sitten vasta tämä lisäosa.  
.ovpn-tiedostot tulee sijaita hakemistossa /etc/avpn.  
  
  
-----
Tee userbouquetiin rivi käyttämällä avustinta: http://[enigma2_ip]/avpnurlhelper  
Anna .ovpn-nimi ilman tiedostopäätettä.  

  
Jos kyseinen striimi ei tarvitse vpn-yhteyttä, laita striimin nimeksi pelkkä "-".  
  
  
  

-----
# TODO
- [ ] Omaksi prosesssikseen tai ainakin ei-blokkaavaksi (nyt time.sleep esim)  
- [ ] konffien hakemisto?  
- [ ] Virheiden käsittely, esim jos .ovpn-tiedostoa ei löydy  
- [ ] Pois OpenWebif-listalta avpn  
  

