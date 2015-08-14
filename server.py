# This class implements a generic socket server for the quadcopter

import socket
import threading
import time

class Server(threading.Thread):
    def __init__(self, processPacket, port = 22333, updatePeriod = 0.03):
        """Initializes to socket server. processPacket is a callback function
            that takes the incoming packet data as input and returns any outgoing
            packet data to be sent back to the client."""
        threading.Thread.__init__(self)
        self.HOST = "" # Host is this machine
        self.PORT = 22333 # Standard cevcopter port used on the raspberry pi
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.HOST, self.PORT))
        self.socket.listen(5)
        self.processPacket = processPacket
        self.updatePeriod = updatePeriod
        self.connections = []
        self.daemon = True
    def run(self):
        while True:
            print "Listening on port " + str(self.PORT)
            conn, addr = self.socket.accept()
            if conn.recv(1024) == "*Super secret handshake*":
                conn.sendall("Accepted")
                print "Accepted a connection!"
                connection = Connection(self, conn, addr, self.processPacket)
                self.connections.append(connection)
                connection.start()
            else:
                conn.close()
            time.sleep(self.updatePeriod)

    def close(self):
        self.stop()
        if self.socket != None:
            self.socket.close()
        self.isConnected = False
        for c in self.connections:
            c.stop()
            c.socket.close()




class Connection(threading.Thread):
    def __init__(self, server, connection, address, processPacket):
        threading.Thread.__init__(self)
        self.server = server
        self.connection = connection
        self.address = address
        self.processPacket = processPacket
        self.daemon = True
    def run(self):
        while True:
            try:
                incomingPacket = self.connection.recv(1024)
                outgoingPacket = self.processPacket(incomingPacket)
                self.connection.sendall(outgoingPacket)
                if not incomingPacket:
                    # this connection is bad.
                    # TODO probably need a safe mode here
                    pass
            except socket.error:
                print "[ERROR] Closing connection"
                self.connection.close()
                return
        time.sleep(self.server.updatePeriod)