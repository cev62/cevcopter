# Class that deals with

from gamepad import *
import time
from client import *
import gui
import threading
import sys

class Controls():

    # States
    DISABLED            = 0
    ENABLED             = 1
    DOWNLOADING_CODE    = 2
    REBOOTING           = 3
    POWERED_OFF         = 4
    INITIALIZING        = 5

    def __init__(self):
        self.state = Controls.DISABLED
        self.throttleAxis = 0.0
        self.xAxis = 0.0
        self.yAxis = 0.0
        self.turnAxis = 0.0

        self.gyro = [0.0, 0.0, 0.0]

        self.comms = Client(self.generatePacket, self.processPacket, "192.168.1.20", 22333, 0.03)
        self.commsLock = threading.Lock()
        self.comms.start()

        self.gamepad = GamePad("/dev/input/js1")

    def update(self):
        # Update self.state
        if self.gamepad.isConnected:

            if self.state == Controls.DISABLED:
                if self.comms.isConnected:
                    if self.gamepad.get("LB") and self.gamepad.get("RB"):
                        if self.gamepad.get("A"):
                            self.state = Controls.ENABLED
                        if self.gamepad.get("X"):
                            self.state = Controls.DOWNLOADING_CODE
                            self.comms.isDownloadingCode = True
                        if self.gamepad.get("Y"):
                            self.state = Controls.REBOOTING
                            self.comms.isRebooting = True
                        if self.gamepad.get("BACK"):
                            self.state = Controls.POWERED_OFF
                            self.comms.isPoweringOff = True
                        if self.gamepad.get("START"):
                            self.state = Controls.INITIALIZING
                        if self.gamepad.get("LOGITECH"):
                            # Maybe need to do some thing here.
                            sys.exit(0)
                elif self.comms.isServerPingable:
                    if self.gamepad.get("LB") and self.gamepad.get("RB"):
                        if self.gamepad.get("X"):
                            self.state = Controls.DOWNLOADING_CODE
                            self.comms.isDownloadingCode = True
                        if self.gamepad.get("Y"):
                            self.state = Controls.REBOOTING
                            self.comms.isRebooting = True
                        if self.gamepad.get("BACK"):
                            self.state = Controls.POWERED_OFF
                            self.comms.isPoweringOff = True
                        if self.gamepad.get("LOGITECH"):
                            # Maybe need to do some thing here.
                            sys.exit(0)

            elif self.state == Controls.ENABLED:
                if self.comms.isConnected:
                    if self.gamepad.get("B"):
                        self.state = Controls.DISABLED
                else:
                    self.state = Controls.DISABLED

            elif self.state == Controls.DOWNLOADING_CODE:
                if not self.comms.isDownloadingCode:
                    # This means it is done downloading code
                    self.state = Controls.DISABLED

            elif self.state == Controls.REBOOTING:
                if not self.comms.isRebooting:
                    # This means it has reconnected after the reboot
                    self.state = Controls.DISABLED

            elif self.state == Controls.POWERED_OFF:
                if not self.comms.isPoweringOff:
                    # This means it has reconnected after powering off
                    self.state = Controls.DISABLED

            elif self.state == Controls.INITIALIZING:
                if self.comms.isConnected:
                    if self.gamepad.get("B"):
                        self.state = Controls.DISABLED
        else:
            # Need to have the gamepad connected to do anything
            self.state = Controls.DISABLED

        # Read new axis values from gamepad
        self.throttleAxis = min(self.gamepad.get("RIGHT_TRIGGER") + self.gamepad.get("LEFT_TRIGGER"), 1.0)
        self.xAxis = self.gamepad.get("LEFT_X")
        self.yAxis = self.gamepad.get("LEFT_Y")
        self.turnAxis = self.gamepad.get("RIGHT_X")

    def generatePacket(self):
        self.commsLock.acquire()
        #output = "Hi, I'm a client."
        """
        Packet format:

        state,throttleAxis,xAxis,yAxis,turnAxis
          |      |             |      |      |
        [int] [float]       [float][float][float]

        """

        output = str(self.state)            + "," \
               + str(self.throttleAxis)     + "," \
               + str(self.xAxis)            + "," \
               + str(self.yAxis)            + "," \
               + str(self.turnAxis)
        #print output
        self.commsLock.release()
        return output

    def processPacket(self,packet):
        self.commsLock.acquire()
        if len(packet.split("\t")) == 3:
            #print "[Server Reply] " + str(packet)
            self.gyro = [float(i) for i in packet.split("\t")[0:3]]
            print self.throttleAxis
        self.commsLock.release()

c = Controls()

while True:
    c.update()
    axes = [c.xAxis, c.yAxis, c.turnAxis, c.throttleAxis]
    indicators = [("Gamepad", c.gamepad.isConnected),   \
                  ("Ping", c.comms.isServerPingable),       \
                  ("Comms", c.comms.isConnected)]
    #print axes
    #print c.gamepad.get("LB"), c.gamepad.get("RB")
    gui.display(Controls, c.state, axes, c.gyro, indicators, None, None)

    time.sleep(0.05)
