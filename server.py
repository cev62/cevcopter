# This class implements a generic socket server for the quadcopter

import socket
import threading
import time

class Server(threading.Thread):
    def __init__(self, processPacket, updatePeriod = 0.03):
        """Initializes to socket server. processPacket is a callback function
            that takes the incoming packet data as input and returns any outgoing
            packet data to be sent back to the client."""
        self.HOST = "" # Host is this machine
        self.PORT = 22333 # Standard cevcopter port used on the raspberry pi
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.HOST, self.PORT))
        self.socket.listen(1)
        self.processPacket = processPacket
        self.updatePeriod = updatePeriod
        self.connections = []
        self.daemon = True
    def run(self):
        while True:
            conn, addr = self.socket.accept()
            connection = Connection(self, conn, addr, self.processPacket)
            self.connections.append(connection)
            connection.start()


class Connection(threading.Thread):
    def __init__(self, server, connection, address, processPacket):
        self.server = server
        self.connection = connection
        self.address = address
        self.processPacket = processPacket
        self.daemon = True
    def run(self):
        while True:
            incomingPacket = self.connection.recv(1024)
            outgoingPacket = self.processPacket(incomingPacket)
            self.connection.sendall(outgoingPacket)
            time.sleep(self.server.updatePeriod)
            if not incomingPacket:
                # this connection is bad.
                # TODO probably need a safe mode here
                pass