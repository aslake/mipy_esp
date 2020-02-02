"""
ESP microcontroller wifi connection related fuctions.

Aslak Einbu and Torbjørn Pettersen, Jan  2020.
"""

import network
import ujson
import os
import config
import machine
import ntptime
import crypt
import utime
import logfile

log = logfile.LogFile("Wifi-connection", config.log_filename, config.log_sizelimit,
                      config.log_level, config.log_print)

networks_stored = "networks_stored.json"       # File for storage of applied SSIDs and their passwords
networks_detected = "networks_detected.json"   # File for storage of currently present Wifi networks
networks_provisioned = "wifi.json"             # File for provisioning of known SSIDs and passwords

crypt_seed = config.crypt_seed
TypeX = crypt.Crypt(crypt_seed)

wlan_ap = network.WLAN(network.AP_IF)
wlan_ap.active(False)

wlan_sta = network.WLAN(network.STA_IF)
wlan_sta.active(False)


def read_stored_networks():
    """ Read stored wifi SSIDs and passwords. """
    log.debug("Function - read_stored_networks()")
    stored = '{}'
    try:
        with open(networks_stored, 'r') as f:
            stored = f.read()
    except:
        with open(networks_stored, "w") as f:
            f.write(stored)
    return ujson.loads(stored)


def append_stored_networks(ssid, password):
    """ Add SSID and password to stored networks. """
    log.debug("Function - append_stored_networks(%s, password)" % ssid)
    stored = read_stored_networks()
    stored[ssid] = TypeX.encrypt(password)
    log.debug("Adds SSID %s to file with stored networks." % ssid)
    with open(networks_stored, "w") as f:
        f.write(ujson.dumps(stored))


def write_networks_detected(nettworks):
    """ Write wifi-networks detected to file. """
    log.debug("Function - write_networks_detected(networks)")
    with open(networks_detected, "w") as f:
        f.write(ujson.dumps(nettworks))


def scan_networks():
    """ Scan for wifi networks present. """
    log.debug("Function - scan_networks()")
    wlan_sta.active(True)
    detected_networks = wlan_sta.scan()
    networks = {}
    AUTHMODE = {0: "open", 1: "WEP", 2: "WPA-PSK",
                3: "WPA2-PSK", 4: "WPA/WPA2-PSK"}
    present = 0
    for ssid, bssid, channel, rssi, authmode, hidden in sorted(detected_networks, key=lambda x: x[3], reverse=True):
        present += 1
        ssid = ssid.decode('utf-8')
        networks[ssid] = [channel, rssi, AUTHMODE.get(authmode, '?')]
    log.debug("Number of networks present: %s" % str(present))
    write_networks_detected(networks)
    wlan_sta.active(False)
    return networks


def connect_to_wifi(ssid, password, utc_delta=1):
    """ Connect to wifi unless already connected. """
    log.debug("Function - connect_to_stored_networks(%s, password)" % ssid)
    wlan_sta.active(True)
    if wlan_sta.isconnected():
        return True
    log.debug('Connecting to %s...' % ssid)
    wlan_sta.connect(ssid, password)
    for retry in range(100):
        connected = wlan_sta.isconnected()
        if connected:
            break
        utime.sleep(0.1)
        print('.', end='')
    if connected:
        log.info("Connected! Network config: %s" % str(wlan_sta.ifconfig()))
        append_stored_networks(ssid, password)
        ntptime.settime()
        yr, mnt, day, wday, hh, mm, sec, ms = machine.RTC().datetime()
        hh += utc_delta
        machine.RTC().datetime((yr, mnt, day, wday, hh, mm, sec, ms))
        log.info("Local time set to: {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".
                 format(yr, mnt, day, hh, mm, sec))
    else:
        log.warning('Unable to connect to ' + ssid)
    return connected


def connect_to_known_network():
    """ Attempts connects to stored networks. """
    log.debug("Function - connect_to_known_network()")
    if not wlan_sta.isconnected():
        stored = read_stored_networks()
        for ssid in stored.keys():
            try:
                password = TypeX.decrypt(stored[ssid])
                log.debug("Attempting connection to SSID: %s." % ssid)
                connect_to_wifi(ssid, password)
                if wlan_sta.isconnected():
                    return True
            except:
                pass
        log.info("No known nettworks available at the moment!")
        return False
    return True


def add_provisioned_networks():
    """ Adds provisioned networks and deletes the file. """
    log.debug("Function - add_provisioned_networks()")
    try:
        networks = '{}'
        with open(networks_provisioned, 'r') as f:
            networks = ujson.loads(f.read())
        for ssid, password in networks.items():
            append_stored_networks(ssid, password)
        for ssid, password in networks.items():
            connect_to_wifi(ssid, password)
        os.remove(networks_provisioned)
    except:
        pass

