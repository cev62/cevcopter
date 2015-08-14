# This class implements a generic socket client for the quadcopter

import socket
import threading
import time

class Client(threading.Thread):
    def __init__(self, generatePacket, processPacket, host="192.168.1.31", port=22333, updatePeriod = 0.03):
        """Initializes to socket client. generatePacket is a function that returns
            data to be sent to the server and processPacket is a function that takes
            received data as an argument. Both of these functions must deal with
            semaphores on their own."""
        self.HOST = host
        self.PORT = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.processPacket = processPacket
        self.generatePacket = generatePacket
        self.updatePeriod = updatePeriod
        self.isConnected = True
        self.daemon = True
    def run(self):
        while True:
            if not self.isConnected:
                try:
                    self.socket.connect((self.HOST, self.PORT))
                    self.isConnected = True
                except socket.error:
                    self.isConnected = False

            incomingPacket = self.socket.recv(1024)
            outgoingPacket = self.processPacket(incomingPacket)
            self.connection.sendall(outgoingPacket)
            time.sleep(self.server.updatePeriod)
            if not incomingPacket:
                # this connection is bad.
                # TODO probably need a safe mode here
                pass