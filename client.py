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
        self.isDownloadingCode = False
        self.isRebooting = False
        self.isPoweringOff = False
        self.daemon = True
    def run(self):
        while True:
            if not self.isServerPingable:
                self.ping()

            if self.isDownloadingCode:                

                self.isConnected = False
                self.socket.close()                    
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # To kill the old cevcopter processes:
                os.system("ssh pi@192.168.1.31 \"/home/pi/kill_cevcopter_processes\"")

                # To delete old files:
                os.system("ssh pi@192.168.1.31 \"rm -f ~/cevcopter-bin/*\"")

                # To copy in new files:
                os.system("scp /home/aaron/cevcopter/cevcopter.py /home/aaron/cevcopter/server.py /home/aaron/cevcopter/serialserver.py pi@192.168.1.31:~/cevcopter-bin > /dev/null")

                # To start running new code:
                os.system("ssh pi@192.168.1.31 \"python /home/pi/cevcopter-bin/cevcopter.py > /dev/null 2> /dev/null < /dev/null &\"")

                self.isDownloadingCode = False

            if self.isRebooting:
                self.isConnected = False
                self.socket.close()                    
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                os.system("ssh pi@192.168.1.31 \"sudo reboot\"")
                # Wait until the pi powers down
                while self.ping() == 0:
                    time.sleep(1.0)
                # Wait until it powers back up
                while self.ping() != 0:
                    time.sleep(1.0)
                self.isRebooting = False
                continue
                

            if self.isPoweringOff:
                self.isConnected = False
                self.socket.close()                    
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                os.system("ssh pi@192.168.1.31 \"sudo halt\"")
                # Wait until the pi powers down
                while self.ping() == 0:
                    time.sleep(1.0)
                # Wait until it powers back up
                while self.ping() != 0:
                    time.sleep(1.0)
                self.isPoweringOff = False
                continue


            if not self.isConnected:
                try:
                    self.ping()
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

            time.sleep(self.updatePeriod)

    def close(self):
        self.stop()
        if self.socket != None:
            self.socket.close()
        self.isConnected = False

    def ping(self):
        ping = subprocess.Popen(["ping", "-c 1", "-w 1", self.HOST], stdout=subprocess.PIPE)
        o,e = ping.communicate()
        self.isServerPingable = ping.returncode == 0
        return ping.returncode