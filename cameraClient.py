import ast, socket


class CameraClient:

    PACKET_LENGTH = 1024

    # Configure the TCP session with the overhead camera
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # SOCK_STREAM defines a TCP socket as opposed to UDP

    def connect(self):
        try:
            self.conn.connect((self.host, self.port))

            response = 'OK'
            self.conn.send(response.encode())
        except ConnectionRefusedError as e:
            raise e


    def receive_points(self):

        # Receive the first message in a TCP transmission from the server
        data = self.conn.recv(CameraClient.PACKET_LENGTH).decode()

        # Decode and receive each message in the transmission until an End of Transmission message is sent
        points = []
        while data != 'EOT':

            # Default response is OK
            response = 'OK'

            # Decode the message into individual (x, y) coordinate points
            try:
                points += ast.literal_eval(data)

            # If the received message is not decoded properly
            # change the response to let the server know there is an error
            except:
                response = 'BAD'

            # Send the response to the server
            self.conn.send(response.encode())

            # Get the next message in the transmission
            data = self.conn.recv(CameraClient.PACKET_LENGTH).decode()

        # Send a final OK to let the server know the EOT was received
        self.conn.send('OK'.encode())

        return points

    def close(self):
        self.conn.close()
