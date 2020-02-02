"""
Micropython ESP MiPy-ESP framework.
Authors: Aslak Einbu & Torbjørn Pettersen

Application: Legarage MQTT Power relay app.
Author: Aslak Einbu, Jan 2020
"""

# ------------------------- HOOKUP ------------------------------------------------------------------
import config
import utime
import wifi
import webserver
import gc
import esp

utime.sleep(2)                      # Digesting time for imports

gc.enable()                         # Enable RAM management.
gc.collect()                        # Collecting garbage RAM.
esp.osdebug(config.esp_osdebug)     # Setting ESP debug setting from config.


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


# ------------------------- SETUP -------------------------------------------------------------------
import umqttsimple
import logfile
from scheduler_light import Scheduler, Job
from machine import Pin
from timers import Countdown

mqtt_timer = Countdown(5)   # Timer for checking recieved mqtt message last 5 seconds.

relay = Pin(14, Pin.OUT)    # Relay pin.
relay.off()                 # Relay off at start.

utime.sleep(1)                      # Digesting time, imports.


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
     log.info("Subscribing to topic 'test'")
     if mqtt_client.subscribe("test") == "Error":
         log.error("Could not subscribe - broker down?")


def mqtt_connect():
    """ Connect to MQTT broker """
    mqtt_client.set_callback(callback_mqtt_subscription)
    if mqtt_client.connect() == "Error":
        log.error("Could not connect - broker down?")
    else:
        log.info('Connected to %s MQTT broker ' % config.mqtt_broker)
        mqtt_subscriptions()
        return mqtt_client


def mqtt_publish(topic, message):
    if mqtt_client.publish(topic,message) == "Error":
        log.error("Could not publish - broker down?")



# Prepares for main loop:
log.debug("Connection to MQTT broker.")
mqtt_connect()



def heartbeat():
    mqtt_publish("/esp8266/%s/heartbeat" % config.device_name, config.heartbeat_message)


# Setting scheduled jobs
schedule = Scheduler("Test program",
                     Job("Heartbeat", heartbeat, 5, -1))



# ------------------------- MAIN LOOP --------------------------------------------------------------
while True:
    if wifi.wlan_sta.isconnected():
        # Loop events when connected to wifi:
        if mqtt_client.check_msg() == "Error":
            log.error("No connection to MQTT broker - attempting reconnect...")
            mqtt_connect()
        utime.sleep(0.1)
        schedule.follow_up_jobs()
        if mqtt_timer.is_overdue():
            log.debug("No MQTT message in the last 5 secs.")
    else:
        # Actions upon lost connection to wifi:
        log.warning("No connection to wifi...")
        while not wifi.wlan_sta.isconnected():
            log.debug("Attempting wifi reconnect.")
            wifi.connect_to_known_network()  # Attempt reconnect to wifi upon lost network connection. 
        log.info("Wifi connection re-established!")
        mqtt_connect()
