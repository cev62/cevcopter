# This class implements a generic socket client for the quadcopter

import socket
import threading
import time
import subprocess
import os

class Client(threading.Thread):
    def __init__(self, generatePacket, processPacket, host="192.168.1.31", port=22333, updatePeriod = 0.03):
        """Initializes to socket client. generatePacket is a function that returns
            data to be sent to the server and processPacket is a function that takes
            received data as an argument. Both of these functions must deal with
            semaphores on their own."""
        threading.Thread.__init__(self)
        self.HOST = host
        self.PORT = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.processPacket = processPacket
        self.generatePacket = generatePacket
        self.updatePeriod = updatePeriod
        self.isConnected = False
        self.isServerPingable = False
        self.daemon = True
        self.majorRestartLock = threading.Lock()
    def run(self):
        while True:
            self.majorRestartLock.acquire()
            if not self.isConnected:
                try:
                    #print "Pinging..."
                    ping = subprocess.Popen(["ping", "-c 1", "-w 1", self.HOST], stdout=subprocess.PIPE)
                    o,e = ping.communicate()
                    if ping.returncode:
                        #print "FAILED"
                        self.isServerPingable = False
                    else:
                        #print "SUCCESS"
                        self.isServerPingable = True
                    print "Attempting to connect..."
                    self.socket.connect((self.HOST, self.PORT))
                    self.socket.sendall("*Super secret handshake*")
                    if self.socket.recv(1024) != "Accepted":
                        print "Server rejected connection..."
                        self.isConnected = False
                        self.socket.close()
                        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        continue
                    self.isConnected = True
                    self.socket.sendall(self.generatePacket())
                except socket.error:
                    self.isConnected = False
            else:
                try:
                    self.processPacket(self.socket.recv(1024))
                    self.socket.sendall(self.generatePacket())
                except socket.error:
                    #print "[ERROR] Reconnecting..."
                    self.socket.close()
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.isConnected = False
            self.majorRestartLock.release()

            time.sleep(self.updatePeriod)

    def downloadCode(self):
        self.majorRestartLock.acquire()

        #List of commands to be run:

        # To kill the old cevcopter processes:
        os.system("ssh pi@192.168.1.31 \"/home/pi/kill_cevcopter_processes\"")

        # To delete old files:
        os.system("ssh pi@192.168.1.31 \"rm -f ~/cevcopter-bin/*\"")

        # To copy in new files:
        os.system("scp /home/aaron/cevcopter/cevcopter.py /home/aaron/cevcopter/server.py pi@192.168.1.31:~/cevcopter-bin")

        # To start running new code:
        os.system("ssh pi@192.168.1.31 \"python /home/pi/cevcopter-bin/cevcopter.py > foo.out 2> foo.err < /dev/null &\"")


        self.isConnected = False
        self.socket.close()                    
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.majorRestartLock.release()

    def close(self):
        self.stop()
        if self.socket != None:
            self.socket.close()
        self.isConnected = False