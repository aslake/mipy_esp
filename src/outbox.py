"""
Buffering of MQTT publish upon lost network connection.

Authors: Aslak Einbu, Jan 2020

"""

import wifi
from logfile import _timestamp
from main import mqtt_publish
import ure


def send_mqtt_outbox(topic, message):
    """ Send given message + all in outbox. If not network => write message to outbox """
    if wifi.wlan_sta.isconnected():
        # Send current message:
        mqtt_publish(topic, message)

        # Send buffered messages:
        with open("outbox.txt", "r+") as f:
            lines = f.readlines()
            f.seek(0)
            for i in lines:
                lineregexp = ure.search("client:(.*?)message:(.*?)", i.decode('utf-8'))
                stored_topic = lineregexp.group[1]
                stored_message = lineregexp.group[2]
                if not mqtt_publish(stored_topic, stored_message):
                    f.write(i)
            f.truncate()
    else:
        # Write message to outbox file:
        with open("outbox.txt", "a+") as f:
            f.write("{} topic:{}message:{}\n".format(_timestamp, topic, message))



