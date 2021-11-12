import mercury
import socket
import time


class ArduinoHandler:
    """Arduino Communication object

    Establishes and handles all communication with the ESP8266 via LAN.

    Attributes:
        connection: A socket connected to the ESP-8266.
        port: An integer value of the ESP-8266 Wifi Server's Port.
        host: A String of the ESP-8266's IP.
        move_time: An integer of the default time delay for a servo to move (in sec)
    """

    def __init__(self, host, port=80, move_time=2):
        """
        Initializes with a given host and port. The port is 80 by default.
        :param host: String of Local IP of the ESP-8266.
        :param port: integer of the port containing the ESP-8366 Wifi Server.
        :param move_time: integer of the time (in millisec) given to the servos to move
        """
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((host, port))
        self.move_time = move_time

    def send_angles(self, angles):
        """
        Sends angles to the ESP-8266 to relay to the Arduino.
        :param angles: tuple of angles to be sent.
        """
        for angle in angles:
            self.connection.send((str(angle)+'\r').encode('utf-8'))
            time.sleep(self.move_time/2)
        time.sleep(self.move_time)


class MercuryHandler:
    """Mercury RFID Reader Object

    Establishes and handles all communication with the Mercury RFID Reader.

    Attributes:
        port: A String of the Mercury's IP.
        base_read_power: An integer of the base read power if not overridden.
    """

    def __init__(self, host, base_read_power=2500):
        """
        Initializes the MercuryHandler object with given port.
        :param: host: A String of the local IP.
        :param: base_read_power: integer of the base read power of the reader (in dB)
        """
        self.reader = mercury.Reader(f'tmr://{host}')
        self.reader.set_read_powers([1], [base_read_power])

    def set_read_power(self, read_power):
        """
        Sets the read_power of the Mercury RFID Reader.
        :param read_power: Integer of the new Read Power (in dB)
        """
        self.reader.set_read_powers([1], [read_power])

    def make_read(self):
        """
        Instructs the Mercury RFID Reader to make a reading.
        :return: List of tuples containing the tag IDs and # of reads
        """
        identified_tag_objs = self.reader.read(timeout=500)
        time.sleep(0.5)
        identified_tags = []
        for tag_obj in identified_tag_objs:
            identified_tags.append(tag_obj.epc.decode())
        return identified_tags
