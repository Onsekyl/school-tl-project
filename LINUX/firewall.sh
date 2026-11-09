#!/bin/bash

PATH="/usr/sbin:/sbin:/usr/bin:/bin"

#
# IPv4
#

# Tyhjennetään vanhat säännöt ja asetetaan oletukset (ACCEPT)
iptables -P INPUT ACCEPT
iptables -P OUTPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -F INPUT
iptables -F OUTPUT
iptables -F FORWARD
iptables -F -t nat
iptables -F -t mangle

# Paikallinen liikenne ja sallitut verkot/osoitteet
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -s 172.20.240.0/23 -j ACCEPT # Esimerkki aliverkosta
iptables -A INPUT -s 193.167.100.97 -j ACCEPT # Takaovi (students.oamk.fi)

# Täysin avoimet palvelut
iptables -A INPUT -p tcp --dport 22 -j ACCEPT # SSH
iptables -A INPUT -p tcp --dport 80 -j ACCEPT # HTTP

# Sallitut ICMP-paketit (ping-testausta varten)
iptables -A INPUT -p icmp --icmp-type echo-request -j ACCEPT

# Sallitaan jo aloitetut ja liittyvät yhteydet takaisin
iptables -A INPUT -p ALL -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Pudotetaan muut uudet ja virheelliset saapuvat yhteydet
iptables -A INPUT -p ALL -m conntrack --ctstate NEW,INVALID -j DROP 

# Lopullinen oletusasetus sisääntulevalle liikenteelle
iptables -A INPUT -p ALL -j DROP

# Ketjujen oletukset skriptin lopussa
iptables -P INPUT ACCEPT
iptables -P OUTPUT ACCEPT
iptables -P FORWARD DROP


#
# IPv6 (sama logiikka)
#

ip6tables -P INPUT DROP
ip6tables -P OUTPUT ACCEPT
ip6tables -P FORWARD DROP
ip6tables -F INPUT
ip6tables -F OUTPUT
ip6tables -F FORWARD

ip6tables -A INPUT -i lo -j ACCEPT
ip6tables -A INPUT -p TCP --dport 22 -j ACCEPT 
ip6tables -A INPUT -p icmpv6 -j ACCEPT       
ip6tables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
ip6tables -A INPUT -j DROP

ip6tables -P INPUT ACCEPT
ip6tables -P OUTPUT ACCEPT
ip6tables -P FORWARD DROP