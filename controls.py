# Class that deals with 

from gamepad import *
import time
from client import *
import gui
import threading

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

        self.throttleDeadzone = 0.05

        self.comms = Client(self.generatePacket, self.processPacket, "localhost", 22333, 0.03)
        self.commsLock = threading.Lock()
        self.comms.start()

        self.gamepad = GamePad("/dev/input/js1")

    def update(self):
        # Update self.state
        if self.gamepad.isConnected:
            if self.comms.isConnected:
                if self.gamepad.get("B"):
                    # Pressing B disables the quadcopter if comms is connected
                    self.state = Controls.DISABLED
                if self.gamepad.get("LB") and self.gamepad.get("RB"):
                    # If LB and RB are pressed, major state changes can happen
                    if self.state == Controls.DISABLED:
                        if self.GamePad.get("A"):
                            self.state = Controls.ENABLE
            elif self.comms.isServerPingable:
                # If the gamepad is connected, comms is not connected,
                # but the server is pingable, you can still download 
                # code via ssh
                if self.gamepad.get("LB") and self.gamepad.get("RB"):
                    # If LB and RB are pressed, major state changes can happen
                    if self.state == Controls.DISABLED:
                        if self.GamePad.get("X"):
                            self.state = Controls.DOWNLOADING_CODE
        else:
            # Need to have the gamepad connected to do anything
            self.state = Controls.DISABLED

        # Read new axis values from gamepad
        self.throttleAxis = max(self.gamepad.get("LEFT_Y"), 0.0)
        # Throttle deadzone:
        if self.throttleAxis < self.throttleDeadzone:
            self.throttleAxis = 0.0
        self.xAxis = self.gamepad.get("RIGHT_X")
        self.yAxis = self.gamepad.get("RIGHT_Y")
        self.turnAxis = self.gamepad.get("LEFT_X")

    def generatePacket(self):
        self.commsLock.aquire()
        #output = "Hi, I'm a client."
        """
        Packet format:

        state,throttleAxis,xAxis,yAxis,turnAxis
          |      |             |      |      |
        [int] [float]       [float][float][float]

        """

        output = str(self.state)            + "," + \
               + str(self.throttleAxis)    + "," + \
               + str(self.xAxis)           + "," + \
               + str(self.yAxis)           + "," + \
               + str(self.turnAxis)    

        self.commsLock.release()
        return output

    def processPacket(self,packet):
        self.commsLock.aquire()
        print "[Server Reply] " + str(packet)
        self.commsLock.release()

c = Controls()

while True:
    c.update()
    axes = [c.xAxis, c.yAxis, c.turnAxis, (c.throttleAxis - c.throttleDeadzone) / (1.0 - c.throttleDeadzone)]
    print axes
    gui.display(axes, None, None, None)

    time.sleep(0.05)
    #print gp.get("LEFT_X")
gp.stop()
c.stop()
c.close()

