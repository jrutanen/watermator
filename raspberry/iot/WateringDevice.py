from SerialDevice import *

class WateringDevice (SerialDevice):
    """Watering device class connected via serial port.
    """
    #reporting frequency
    reporting_freq = 600 #every 10 minutes
    time_of_last_measurement = None

    def __init__(self, **kwds):
        super(WateringDevice, self).__init__(**kwds)

    def read_data(self):
        """Process to continuously read data from serial port. This
        process will update measurments list with new values. Check for
        alarms and publish data.
        """
        while True:
            value = self.read()
            self.measurements.append(value)
            self.set_alarm_severity(value)
            current_time = datetime.datetime.now()
            if self.time_of_last_measurement is None:
                self.time_of_last_measurement = current_time
            time_diff = (current_time-self.time_of_last_measurement)\
                        .total_seconds()
            if time_diff == 0\
                or time_diff >= self.reporting_freq\
                or self.alarm_severity == ALARM_CRITICAL: 
                self.callback(\
                    type(self), self.id, value, self.alarm_severity,\
                    self.thing_speak_field, self.topic)
                self.time_of_last_measurement = current_time

    def read(self):
        """Reads data from the serial port. Expected values are as
        follows:
        moisture:int between 0 and 1023 
        valve:0 or 1 (off/on)

        Returns:
        tuple: (sensor,value)
        """
        data =\
            self.serial_conn.readline().decode().replace('\r\n', '')
        value = self.decode_data(data)
        return value

    def write(self, user_input):
        """Command to write data to the device. Valid commands are
        "open\n" and "close\n" to turn on and off the water valve

        Parameters:
        user_input (string): value to be sent to the device.
        """
        self.serial_conn.write(user_input + '\n')
        return None

    def set_alarm_severity(self, value):
        """Command to set alarm severity for the device. Shall be
        overriden by child class.

        Parameters:
        value (string): Alarm severity value to set: ALARM_NONE,
                        ALARM_MINOR, ALARM_MAJOR or ALARM_CRITICAL
        """        
        return ALARM_NONE

    def decode_data(self, data):
        sensor = ""
        #This device has one sensor and one solenoid connected to it
        #Moisure 'moisture:'
        #Water valve 'valve:'
        if 'moisture' in data:
            sensor = "moisture"
        elif 'valve' in data:
            sensor = "valve"
        else:
            print("Unknown sensor type: " + str(data))
            sensor = "unkown"

        value = (data[data.find(':')+1 :]).strip()

        return (sensor, value)