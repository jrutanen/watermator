#!/usr/bin/env python3

"""
MQTT topics must start with: EricssonONE/esignum/
Example: "EricssonONE/edallam/MQTT_Display/text"
"""

from urllib.request import urlopen
import sys
import socket
import os
from time import sleep
import json 
import datetime
# For MQTT
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from personal import *
from WateringDevice import *
from ThingSpeak import *
from Mqtt import *
from constants import *

unix_socket = None

def create_unix_domain_socket():
    print("Creating a socket")
    # Make sure the socket does not already exist
    try:
        os.unlink(server_address)
    except OSError:
        if os.path.exists(server_address):
            raise

    unix_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    print("Socket created")
    unix_socket.bind(server_address)
    unix_socket.listen(1)
    print("Listening to socket")
    return unix_socket

def check_socket_connection(unix_socket):
    connection, client_address = unix_socket.accept()
    try:
        data = connection.recv(16)
        message = data.decode()
        print("Message received: " + message)

        if message == "stop":
            stop_iot_can()
    finally:
        # Clean up the connection
        connection.close()

def on_data_received(\
    object_type, object_id, value, alarm_severity, field, topic):
    if object_type == WateringDevice:
        process_watering_data(object_id, value, alarm_severity)
        thing_speak.publish(field, value)

    if alarm_severity > ALARM_NONE:
        on_alarm(object_type, object_id, value, alarm_severity)

def on_alarm(object_type, object_id, value, alarm_severity):
    #Do something exciting
    return 0

def process_watering_data(object_id, value, alarm_severity):
    if value[0] == "moisture":
        data = value[1]
        thing_speak.publish("field1", data)
        #mqtt.publish("DATA", data, "IoT_Can/3/temp")
        #if alarm_severity == ALARM_CRITICAL:
        #    mqtt.publish("DISPLAY", "Warning: Freezing temp!")
    elif value[0] == "valve":
        data = value[1]
        thing_speak.publish("field2", data)
        #mqtt.publish("DATA", data, "IoT_Can/3/trashlevel")        
        #if alarm_severity == ALARM_CRITICAL:
        #    mqtt.publish("DISPLAY", "Trashcan is almost full!")

def startit():
    while True:
        check_socket_connection(unix_socket)

def stop_iot_can():
    for device in devices:
        device.stop()
    print("All connected devices stopped. Shutting down.")
    sys.exit(1)

##################################################################
if __name__ == "__main__":
    #Create Unix Domain Socket
    unix_socket = create_unix_domain_socket()

    #ThingSpeak connection
    thing_speak = ThingSpeak()
    #MQTT connection
    mqtt = Mqtt()

    #list of connected devices
    devices = []

    #Add connected devices
    watering_device = WateringDevice(\
        name="Watering Device", field="field1",)
    watering_device.set_serial_conn(
        conn_port='/dev/ttyUSB0', conn_baudrate=9600, conn_timeout=100)
    watering_device.start(on_data_received)
    devices.append(watering_device)

#    startit()

    sleep(60)
    watering_device.stop()
