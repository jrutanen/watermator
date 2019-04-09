from personal import *
from urllib.request import urlopen
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

class Mqtt:
    """Interface towards ThingSpeak
    This class is used update data in the ThingSpeak server
    """
    client = None
    config = None

    def __init__(self):
        config = getConfig()
        
        client = mqtt.Client()

        #Assigning the object attribute to the Callback Function
        client.will_set("EricssonONE/egarage/IoT_Can/status",\
                         payload="Offline",\
                         qos=0,\
                         retain=True)

        client.username_pw_set(\
            username = config.MQTT_auth['username'],\
            password = config.MQTT_auth['username'])

        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect

        client.connect(config.broker_address,\
                       config.broker_portno)

        self.config = config
        self.client = client

    #callback functions
    def on_connect(self, client, userdata, flags, rc):
         print("PUBLISH: Connected With Result Code {}".format(rc))
         client.publish(topic = "EricssonONE/egarage/IoT_Can/status",\
                        payload="Online",\
                        qos=0,\
                        retain=True) #TODO: change to a publish with "auth"

    def on_disconnect(self, client, userdata, rc):
         client.publish(topic = "EricssonONE/egarage/MQTT_Display/text",\
                        payload = "IoT_Can disconnected")
         print("PUBLISH: Disconnected From Broker")
         client.publish(topic = "EricssonONE/egarage/IoT_Can/status",\
                        payload="Offline",\
                        qos=0,
                        retain=True) #TODO: change to a publish with "auth"

    def publish(self, device, value, topic=""):
        """Sends update data to the MQTT server

        Parameters:
        field (string): MQTT Device 
        value (string): string to be sent to the server
        """
        if device == 'DISPLAY':
            topic = 'MQTT_Display/text'

        self.publish_mqtt(topic, value)

    def publish_mqtt(self, topic, payload):
        egarageTopic = "EricssonONE/egarage/{}".format(topic)
        publish.single(\
        topic = egarageTopic, \
        payload = payload, \
        hostname = self.config.broker_address, \
        client_id ="", \
        keepalive = 60, \
        will = None, \
        auth = self.config.MQTT_auth, \
        tls = None, \
        protocol = mqtt.MQTTv311, \
        transport = "tcp")

        print("Publish topic: {} payload: {}"\
            .format(egarageTopic,payload))
        
