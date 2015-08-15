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

    def __init__(self):
        self.state = Controls.DISABLED
        self.throttleAxis = 0.0
        self.xAxis = 0.0
        self.yAxis = 0.0
        self.turnAxis = 0.0

        self.comms = Client(self.generatePacket, self.processPacket, "192.168.1.31", 22333, 0.03)
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
                            self.comms.downloadCode()
                        if self.gamepad.get("Y"):
                            self.state = Controls.REBOOTING
                        if self.gamepad.get("BACK"):
                            self.state = Controls.POWERED_OFF
                        if self.gamepad.get("LOGITECH"):
                            # Maybe need to do some thing here.
                            sys.exit(0)
                elif self.comms.isServerPingable:
                    if self.gamepad.get("LB") and self.gamepad.get("RB"):
                        if self.gamepad.get("X"):
                            self.state = Controls.DOWNLOADING_CODE

            elif self.state == Controls.ENABLED:
                if self.comms.isConnected:
                    if self.gamepad.get("B"):
                        self.state = Controls.DISABLED
                else:
                    self.state = Controls.DISABLED

            elif self.state == Controls.DOWNLOADING_CODE:
                if self.comms.isConnected:
                    # This means it has reconnected after the download
                    self.state = Controls.DISABLED

            elif self.state == Controls.REBOOTING:
                if self.comms.isConnected:
                    # This means it has reconnected after the reboot
                    self.state = Controls.DISABLED

            elif self.state == Controls.POWERED_OFF:
                if self.comms.isConnected:
                    # This means it has reconnected after powering off
                    self.state = Controls.DISABLED

            """if self.comms.isConnected:
                if self.gamepad.get("B"):
                    # Pressing B disables the quadcopter if comms is connected
                    self.state = Controls.DISABLED
                    #print "Updated State: " + str(self.state)

                elif self.gamepad.get("LB") and self.gamepad.get("RB"):
                    # If LB and RB are pressed, major state changes can happen
                    #print "Bumpers pressed"
                    if self.state == Controls.DISABLED:
                        if self.gamepad.get("A"):
                            self.state = Controls.ENABLED
                        if self.gamepad.get("X"):
                            self.state = Controls.DOWNLOADING_CODE
                            self.comms.downloadCode()
                        if self.gamepad.get("Y"):
                            self.state = Controls.REBOOTING
                        if self.gamepad.get("BACK"):
                            self.state = Controls.POWERED_OFF
                        if self.gamepad.get("LOGITECH"):
                            # Maybe need to do some thing here.
                            sys.exit(0)
            elif self.comms.isServerPingable:
                # If the gamepad is connected, comms is not connected,
                # but the server is pingable, you can still download 
                # code via ssh
                if self.gamepad.get("LB") and self.gamepad.get("RB"):
                    # If LB and RB are pressed, major state changes can happen
                    if self.state == Controls.DISABLED:
                        if self.gamepad.get("X"):
                            self.state = Controls.DOWNLOADING_CODE"""

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

        self.commsLock.release()
        return output

    def processPacket(self,packet):
        self.commsLock.acquire()
        print "[Server Reply] " + str(packet)
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
    gui.display(Controls, c.state, axes, indicators, None, None)

    time.sleep(0.05)
    #print gp.get("LEFT_X")
gp.stop()
c.stop()
c.close()

