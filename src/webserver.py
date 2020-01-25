"""
ESP access point webserver.

Aslak Einbu, Jan  2020.
"""

import os
import gc
import socket
import ure
import utime
import config
import logfile
import wifi

log = logfile.LogFile("Webserver", config.log_filename, config.log_sizelimit,
                      config.log_level, config.log_print)

gc.enable()

files_on_chip = os.listdir()

mimetypes = {'.html': 'text/html',
             '.css': 'text/css',
             '.js': 'application/javascript',
             '.png': 'image/png',
             '.svg': 'image/svg',
             '.ico': 'image/vnd.microsoft.icon',
             '.py': 'text/html',
             '.txt': 'text/css',
             '.json': 'application/json'}

binary = ['.svg', '.png', '.ico']


def send_header(client, status_code=200, content_type='text/html', content_length=None):
    """ Send header to socket. """
    client.sendall("HTTP/1.0 {} OK\r\n".format(status_code))
    client.sendall("Content-Type: {}\r\n".format(content_type))
    if content_length is not None:
        client.sendall("Content-Length: {}\r\n".format(content_length))
    client.sendall("\r\n")


def send_response(client, payload, content_type, status_code=200):
    """ Send header + payload to socket. """
    content_length = len(payload)
    send_header(client, status_code, content_type, content_length)
    if content_length > 0:
        client.sendall(payload)
    client.close()
    gc.collect()


def handle_file(client, url):
    """ Sends file to socket. """
    log.debug("Handling file {}".format(url))
    for key in mimetypes.keys():
        if url.endswith(key):
            content_type = mimetypes[key]
    if url[-4:] in binary:
        readtype = 'rb'
    else:
        readtype = 'r'
    with open(url, readtype) as f:
        fil = f.read()
    send_response(client, fil, content_type, status_code=200)
    gc.collect()


def handle_not_found(client, url):
    """ Sends 404 message upon path not found. """
    send_response(client, "Path not found: {}".format(url),
                  content_type="text/html", status_code=404)

def url_parse(url):
    """ Extracts query params password and ssid from url. """
    query_params = ure.search("\?(.*?) HTTP", url.decode('utf-8')).group(1)
    parameters = {}
    ampersandsplit = query_params.split("&")
    for element in ampersandsplit:
        equalsplit = element.split("=")
        if equalsplit[1] != "":
            parameters[equalsplit[0]] = equalsplit[1]

    codelist = {"%20" : " ",
                "%21" : "!",
                "%23" : "#",
                "%24" : "$",
                "%2F" : "/"}

    for key, value in parameters.items():
        for code in codelist.keys():
            value = value.replace(code, codelist[code]).rstrip("/")
            parameters[key] = value.replace(code, codelist[code])
    if "password" in parameters and "ssid" in parameters:
        return parameters["ssid"], parameters["password"]
    else:
        return None, None


def ap_webserver_start():
    """ Starting access point webserver for serving of files on chip. """
    gc.collect()

    log.debug("Function - ap_webserver_start()")
    wifi.wlan_ap.active(True)
    wifi.wlan_ap.config(essid=config.ap_ssid,
                        password=config.ap_password, authmode=3)

    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    server_socket = socket.socket()
    server_socket.bind(addr)
    server_socket.listen(3)

    log.debug('Connect to ssid ' + config.ap_ssid +
             ', with password: ' + config.ap_password)
    log.debug('Contact access point webserver at 192.168.4.1.')

    utime.sleep(2)

    log.debug("Starting AP webserver!")
    return server_socket


def ap_webserver_loop(server_socket):
    """ Looping access point webserver. """
    log.debug("Function - ap_webserver_loop()")

    client, addr = server_socket.accept()
    log.debug('Client connected from {}'.format(addr))

    try:
        client.settimeout(5.0)
        request = b""
        try:
            while "\r\n\r\n" not in request:
                request += client.recv(512)
        except OSError:
            pass

        log.debug("Request is: {}".format(request))
        if "HTTP" in request:  # skip invalid requests

            url = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP",
                             request).group(1).decode("utf-8").rstrip("/")

            log.debug("URL is {}".format(url))

            if url == "":
                handle_file(client, "index.html")

            elif url == "rescan":
                wifi.scan_networks()
                handle_file(client, "index.html")

            elif url == "kobletil":
                log.debug("Will connect to network...")
                ssid, passord = url_parse(request)
                wifi.connect_to_wifi(ssid, passord)

            elif url in files_on_chip:
                handle_file(client, url)

            else:
                handle_not_found(client, url)
    except:
        pass
    client.close()


def ap_webserver_stop(server_socket):
    """ Shutting down access point webserver. """
    log.debug("Function - ap_webserver_stop()")
    log.debug("Shutting down ESP acces point webserver!")
    if server_socket:
        server_socket.close()
        server_socket = None
    wifi.wlan_ap.active(False)
    return server_socket
