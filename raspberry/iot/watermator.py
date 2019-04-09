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
from Battery import *
from WaterMeter import *
from TrashCan import *
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
    if object_type == Battery:
        print("do some battery stuff")
        thing_speak.publish(field, value)

    if object_type == WaterMeter:
        print("do some water meter stuff")
        thing_speak.publish(field, value)

    if object_type == TrashCan:
        process_trash_can_data(object_id, value, alarm_severity)

    print(object_id, value, alarm_severity)

    if alarm_severity > ALARM_NONE:
        on_alarm(object_type, object_id, value, alarm_severity)

def on_alarm(object_type, object_id, value, alarm_severity):
    #Do something exciting
    return 0

def process_trash_can_data(object_id, value, alarm_severity):
    if value[0] == "Temp":
        data = value[1]
        thing_speak.publish("field2", data)
        mqtt.publish("DATA", data, "IoT_Can/3/temp")
        if alarm_severity == ALARM_CRITICAL:
            mqtt.publish("DISPLAY", "Warning: Freezing temp!")
    elif value[0] == "Distance":
        data = value[1]
        thing_speak.publish("field1", data)
        mqtt.publish("DATA", data, "IoT_Can/3/trashlevel")        
        if alarm_severity == ALARM_CRITICAL:
            mqtt.publish("DISPLAY", "Trashcan is almost full!")
    elif value[0] == "Lock":
        data = value[1]
        thing_speak.publish("field3", data)
        mqtt.publish("DATA", data, "IoT_Can/3/3/1/toilet")
        if alarm_severity == ALARM_CRITICAL:
            mqtt.publish("DISPLAY", "Toilet: Occupied!")
        else:
            mqtt.publish("DISPLAY", "Toilet: Free!")            

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
    #Add Two Battery Devices and start them
#    battery_one = Battery(\
#        name="BatteryOne", field="field1", max_voltage=12.00)
#    battery_one.set_serial_conn(
#        conn_port='/dev/ttyUSB0', conn_baudrate=9600, conn_timeout=100)
#    battery_one.start(on_data_received)
#    devices.append(battery_one)

    trashcan_one = TrashCan(\
        name="ThrashCan", field="field2",)
    trashcan_one.set_serial_conn(
        conn_port='/dev/ttyUSB2', conn_baudrate=9600, conn_timeout=100)
    trashcan_one.set_reporting_frequency(60)
    trashcan_one.start(on_data_received)
    devices.append(trashcan_one)

    #Add Water Meter and start it
#    water_meter = WaterMeter(name="WaterOne", field="field3")
#    water_meter.set_serial_conn(
#        conn_port='/dev/ttyUSB2', conn_baudrate=9600, conn_timeout=100)
#    water_meter.start(on_data_received)
#    devices.append(water_meter)

#    startit()

    sleep(60)
    trashcan_one.stop()
#    battery_one.stop()
#    battery_two.stop()
#    water_meter.stop()
