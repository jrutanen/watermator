from personal import *
from urllib.request import urlopen

class ThingSpeak:
    """Interface towards ThingSpeak
    This class is used update data in the ThingSpeak server
    """
    update_url = ""

    def __init__(self):
        config = getConfig()
        self.update_url = config.ThingSpeak_BaseURL\
                       + 'api_key='\
                       + config.ThingSpeak_Write_API_key\
                       + '&'

    def publish(self, field, value):
        """Sends update data to the ThingSpeak server
        
        Parameters:
        field (string): Field name in ThingSpeak
                        (field1, field2, ..., field8)
        value (string): numeric value to be sent to the server
        """
        #Update url with field and value
        url = self.update_url + field +'=' + str(value)
        print(url)
        #Send update to ThingSpeak
        conn = urlopen(url)
        print('ThingSpeak publish entry: ' + str(conn.read().decode()))
        # Closing the connection
        conn.close()
