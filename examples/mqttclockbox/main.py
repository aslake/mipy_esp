"""
Micropython ESP framework.

Application: MQTT clock- and code-beacon.

Author: Aslak Einbu
"""

import utime
import config
import webserver
import wifi
import gc
import esp
from leds import toggle, blink
from machine import Pin
import tm1637

utime.sleep(1)

gc.enable()
gc.collect()
esp.osdebug(config.esp_osdebug)

# TM1637 4 digit 7-segment led display:
tm = tm1637.TM1637(clk=Pin(4), dio=Pin(5))
tm.show("")

# Two leds:
red = Pin(0, Pin.OUT)
green = Pin(2, Pin.OUT)
red.off()
green.off()

blink(green, 3, 0.1, 0.1)


tm.show("CONN")
# Appending provisioned SSIDs with password to stored networks and attempts to connect.
wifi.add_provisioned_networks()

if not wifi.wlan_sta.isconnected():
    tm.show("SCAN")
    wifi.scan_networks()            # Scanning for wifi networks.

    # Attempts connection to stored wifi networks. Broadcasts accesspoint webserver if no success.
    tm.show("CONN")
    if not wifi.connect_to_known_network():
        server_socket = webserver.ap_webserver_start()
        while not wifi.wlan_sta.isconnected():
            tm.show(" AP ")
            webserver.ap_webserver_loop(server_socket)
        webserver.ap_webserver_stop(server_socket)


import socket
import umqttsimple
import logfile
from scheduler_light import Scheduler, Job
from buttons import Button
import ure
from utilities import Countdown

utime.sleep(1)

mqtt_timer = Countdown(5)  # Timer for checking recieved mqtt message last 5 seconds.


display_clock = True      # Global variable - box mode time (True) or code (False) 


log = logfile.LogFile("Box1", config.log_filename, config.log_sizelimit,
                      config.log_level, config.log_print)




# Establish MQTT client:
mqtt_client = umqttsimple.MQTTClient(config.client_id,
                                     config.mqtt_broker,
                                     config.mqtt_port,
                                     config.mqtt_user,
                                     config.mqtt_password)

# MQTT callbacks:
def callback_mqtt_subscription(topic, msg):
    """ Callback upon MQTT publication of subscribed topics. """
    # log.debug("MQTT message recieved:")
    # log.debug('%s,%s' % (topic.decode('utt-8'), msg.decode('utf-8')))

    if topic == b'server/beacon':
        mqtt_timer.start()
        urstreng = ure.search("(.)(.)(....)(....)", msg.decode('utf-8'))
        red_led = int(urstreng.group(2))
        green_led = int(urstreng.group(1))
        tid = urstreng.group(3)
        kode = urstreng.group(4)

        green.value(green_led)  # Sets green led from msg
        red.value(red_led)      # Sets red led from msg

        if display_clock:
            tm.show(tid)        # Sets time from msg to display 
        else:
            tm.show(kode)       # Sets kode from msg to display


def mqtt_subscriptions():
    """ Subscribe to MQTT topics. """
    log.info("Subscribing to topic 'server/beacon'")
    mqtt_client.subscribe("server/beacon")


def mqtt_connect():
    """ Connect to MQTT broker """
    mqtt_client.set_callback(callback_mqtt_subscription)
    mqtt_client.connect()
    log.info('Connected to %s MQTT broker ' % config.mqtt_broker)
    mqtt_subscriptions()
    return mqtt_client


# Prepares for main loop:
log.debug("Connection to MQTT broker.")
mqtt_connect()


# Jobs:
def heartbeat():
    mqtt_client.publish("/esp8266/%s" % config.device_name, config.heartbeat_message)


# Setting scheduled jobs
schedule = Scheduler("Procedures",
                     Job("Heartbeat", heartbeat, 5, -1))


# Hardware I/O:

def display_toggle():
    """ Toggles display time or code """
    global display_clock
    log.debug("Both buttons pressed")
    display_clock = not display_clock


def press_callback1():
    """ Button 1 press callback"""
    global display_clock
    if knapp2.is_on():
        display_toggle()
        return
    else:
        log.debug("Button 1 pressed!")
        if display_clock:
            mqtt_client.publish("server/button2", "led")
        else:
            mqtt_client.publish("server/button1", "step")


def press_callback2():
    """ Button 2 press callback"""
    global display_clock
    if knapp1.is_on():
        display_toggle()
        return
    else:
        log.debug("Button 2 pressed!")
        if display_clock:
            mqtt_client.publish("server/button1", "led")
        else:
            mqtt_client.publish("server/button2", "step")


# Two push buttons:
knapp1 = Button(13, press_callback1)
knapp2 = Button(14, press_callback2)


# Microcontroller main loop:
while True:
    if wifi.wlan_sta.isconnected():
        # Loop events when connected to wifi:
        mqtt_client.check_msg()
        utime.sleep(0.1)
        knapp1.check_pressed()
        schedule.follow_up_jobs()
        knapp2.check_pressed()
        if mqtt_timer.is_overdue():
            tm.show("    ")

    else:
        # Actions upon lost connection to wifi:
        log.warning("No connection to wifi...")
        red.on()
        tm.show("CONN")
        while not wifi.wlan_sta.isconnected():
            log.debug("Attempting wifi reconnect.")
            wifi.connect_to_known_network()  # Attempt reconnect to wifi upon lost network connection. 
        blink(green, 5, 0.1, 0.1)
        red.off()
        log.debug("Wifi connection re-established! Re-connecting to MQTT-broker...")
        mqtt_connect()                               # Re-establish MQTT connection upon reestablihed wifi connection.     
