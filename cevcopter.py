from server import *
from serialserver import *
import threading

class Cevcopter():
    def __init__(self):
        self.comms = Server(self.processPacket, 22333, 0.03)
        self.comms.start()

        self.serial = Serial("/dev/arduino.uno")
        self.serial.start()

        self.commsLock = threading.Lock()

        self.gyro = [0.0, 0.0, 0.0]
        self.serialData = []

        self.controlCommands = [0, 0.0, 0.0, 0.0, 0.0]
        self.exceptedControlCommandsLength = len(self.controlCommands)

    def update(self):
        self.commsLock.acquire()

        print self.controlCommands
        # Speed controls: anything below ~72 (probably 90) is off, and the motor 
        # varies from 72 to 180.
        if self.controlCommands[0] == 0:
            # Disabled, so always write 72 to turn motors off but keep initialization
            self.serial.setOutgoingData([72 for i in range(4)])
        elif self.controlCommands[0] == 1:
            # Enabled, so map commands to 72-180 for flight
            self.serial.setOutgoingData([int(self.controlCommands[1]*(180 - 72) + 72) for i in range(4)])
        elif self.controlCommands[0] == 5:
            # Initializing, so map commands to 0-180 for initialization
            self.serial.setOutgoingData([int(self.controlCommands[1]*180) for i in range(4)])
        else:
            self.serial.setOutgoingData([int(self.controlCommands[1]*(180)) for i in range(4)])

        

        self.serialData = self.serial.getIncomingData()
        #print "[Serial] " + str(self.serialData)
        if self.serialData:
            rawGyro = self.serialData[1:4]
            self.gyro = [float(i) for i in rawGyro]
            self.gyro[1] = -self.gyro[1] * 90.0 / 70.0
            self.gyro[2] = self.gyro[2] * 90.0 / 70.0


        self.commsLock.release()

    def processPacket(self, packet):
        self.commsLock.acquire()
        #print "[Client Message] " + str(packet)

        # Process incoming
        print packet
        dataFromController = packet.split(",")
        if len(dataFromController) == self.exceptedControlCommandsLength:
            self.controlCommands = [float(i) for i in dataFromController]
            self.controlCommands[0] = int(self.controlCommands[0])

        # Process outgoing
        gyroStr = []
        for i in self.gyro:
            gyroStr.append(str(i))
        data = "\t".join(gyroStr)
        self.commsLock.release()
        return data

c = Cevcopter()

while True:
    c.update()
    time.sleep(0.03)