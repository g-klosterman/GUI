import ast, socket, json


class CameraClient:

    # Server session constants
    _DEFAULT_HOST = 'overheadcam'
    _ALTERNATE_HOST = '192.168.0.1'
    _TEST_HOST = 'localhost'
    _PORT = 5000

    # Default packet length. Must be the same in the client and server.
    DEFAULT_PACKET_SIZE = 2048

    def __init__(self, test, use_ip):
        """
        Configure the client for the overhead camera.
        """

        # Configure the TCP connection settings
        self._host = self._DEFAULT_HOST
        if test:
            self._host = self._TEST_HOST
        elif use_ip:
            self._host = self._ALTERNATE_HOST

        self._port = self._PORT

        self._packet_size = self.DEFAULT_PACKET_SIZE

        # Open a TCP socket to make the connection
        self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        """
        Establish the TCP connection between this client and the server.
        :return:        Passes a ConnectionRefusedError if the server refuses the connection
        """

        config_dict = None

        try:
            self._conn.connect((self._host, self._port))

            # Receive and decode the config settings from the server
            config_json = self._conn.recv(self.DEFAULT_PACKET_SIZE).decode()

            config_dict = json.loads(config_json)
            self._packet_size = config_dict['PACKET_SIZE']

        except socket.gaierror as e:
            print(f"DNS resolution failed for {self._host}. Error: {e}")
            print("Please ensure the hostname is correct or try using an IP address.")
            return False
        except ConnectionRefusedError:
            print(f"Connection refused to {self._host}:{self._port}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

        return config_dict

    def receive_points(self):
        """
        Receive a transmission of robot coordinate points and decode them into a list of 2D field coordinates.
        The units of the coordinates are feet as per the original design of this application.
        If the units are changed in the server application, the same units will be used here.

        :return:        A list of (x, y) tuples of robot coordinates
        """

        # Receive the first message in a TCP transmission from the server
        data = self._conn.recv(self._packet_size).decode()

        '''# Decode and receive each message in the transmission until an End of Transmission message is sent
        points = []
        while data != 'EOT':

            # Default response is OK
            response = 'OK'

            # Decode the message into individual (x, y) coordinate points
            try:
                points += ast.literal_eval(data)

            # If the received message is not decoded properly,
            # change the response to let the server know there is an error
            except:
                response = 'BAD'

            # Send the response to the server
            self._conn.send(response.encode())

            # Get the next message in the transmission
            data = self._conn.recv(CameraClient.PACKET_LENGTH).decode()

        # Send a final OK to let the server know the EOT was received
        '''
        self._conn.send('OK'.encode())
        points = json.loads(data)
        print(points)

        return points

    def close(self):
        """
        Close the TCP session.
        This method should always be called if connect() has previously been called to close the TCP sockets in the
        client and server.
        """
        self._conn.close()
