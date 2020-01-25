"""
Micropython ESP framework.

Application: Legarage MQTT Power relay app.
Author: Aslak Einbu, Jan 2020
"""

import utime
import config
import webserver
import wifi
import gc
import esp
from machine import Pin

utime.sleep(1)

gc.enable()
gc.collect()
esp.osdebug(config.esp_osdebug)

# Appending provisioned SSIDs with password to stored networks and attempts to connect.
wifi.add_provisioned_networks()

if not wifi.wlan_sta.isconnected():
    wifi.scan_networks()            # Scanning for wifi networks.

    # Attempts connection to stored wifi networks. Broadcasts accesspoint webserver if no success.
    if not wifi.connect_to_known_network():
        server_socket = webserver.ap_webserver_start()
        while not wifi.wlan_sta.isconnected():
            webserver.ap_webserver_loop(server_socket)
        webserver.ap_webserver_stop(server_socket)


relay = Pin(14, Pin.OUT)    # Relay pin.
relay.off()                 # Relay off at start.


import umqttsimple
import logfile
from scheduler_light import Scheduler, Job
from utilities import Countdown

utime.sleep(1)

mqtt_timer = Countdown(5)  # Timer for checking recieved mqtt message last 5 seconds.


log = logfile.LogFile("Relay-1", config.log_filename, config.log_sizelimit,
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
    if topic == b'switches/relay-1/state/read':
        mqtt_timer.start()
        message = msg.decode('utf-8')
        log.debug(message)
        if message == "ON":
            relay.on()
        if message == "OFF":
            relay.off()


def mqtt_subscriptions():
    """ Subscribe to MQTT topics. """
    log.info("Subscribing to topic 'switches/relay-1/state/read'")
    mqtt_client.subscribe("switches/relay-1/state/read")


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
    mqtt_client.publish("/esp8266/%s/heartbeat" % config.device_name, config.heartbeat_message)


# Setting scheduled jobs
schedule = Scheduler("Procedures",
                     Job("Heartbeat", heartbeat, 5, -1))


# Microcontroller main loop:
while True:
    if wifi.wlan_sta.isconnected():
        # Loop events when connected to wifi:
        mqtt_client.check_msg()
        utime.sleep(0.1)
        schedule.follow_up_jobs()
        if mqtt_timer.is_overdue():
            log.debug("No MQTT message in the last 5 secs.")
    else:
        # Actions upon lost connection to wifi:
        log.debug("No connection to wifi...")
        while not wifi.wlan_sta.isconnected():
            log.debug("Attempting wifi reconnect.")
            wifi.connect_to_known_network()  # Attempt reconnect to wifi upon lost network connection. 
        log.debug("Wifi connection re-established! Re-connecting to MQTT-broker...")
        mqtt_connect()                               # Re-establish MQTT connection upon reestablihed wifi connection.     
