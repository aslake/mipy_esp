# Micropython ESP framework system config parameters
# ----------------------------------------------------

# Chip info:
device_name = "uniquename"
framework_commit = "a2ce907 "       # Framework code applied for application (Repository commit)

# Logging and debug:
esp_osdebug = 0                     # 0:debug to uart, None: no debug
debug = True                        # Logging & debug [True/False]

# Access Point:
ap_ssid = "pythonESP"               # ESP AP SSID
ap_password = "secret!!!"           # ESP AP SSID password
utc_delta = 1                       # adjusting time to Norwegian time

# Encryption:
crypt_seed = "Passord4passorD"      # encryption key

# MQTT:
mqtt_port = 1883                    # MQTT broker port    
mqtt_user = 'username'              # MQTT broker user name
mqtt_password = 'password'          # MQTT broker user name password
client_id = 'uniqueid'              # MQTT client unique ID
mqtt_broker = '85.119.83.194'       # IP address to test.mosquitto.org MQTT broker
heartbeat_interval = 5.             # Interval [sec] for chip sign-of-life MQTT beacon
heartbeat_message = 'alive'         # Chip sign-of-life message

# Logging
log_sizelimit = 1000                # log file < x bytes
log_level = "INFO"                  # DEBUG < INFO < WARNING < ERROR (dont write to logfile  if log level lower than)
log_print = True                    # UART print log entries [True/False]
log_filename = "client.log"         # Log file name
