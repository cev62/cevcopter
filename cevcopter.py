from server import *
from serialserver import *
import threading

class Cevcopter():
    def __init__(self):
        self.comms = Server(self.processPacket, 22333, 0.03)
        self.comms.start()

        self.serial = Serial("/dev/ttyACM0")
        self.serial.start()

        self.commsLock = threading.Lock()

        self.gyro = [0.0, 0.0, 0.0]
        self.serialData = []

    def update(self):
        self.commsLock.acquire()

        self.serialData = self.serial.getIncomingData()
        if self.serialData:
            rawGyro = self.serialData[1:4]
            self.gyro = [float(i) for i in rawGyro]
            self.gyro[1] = -self.gyro[1] * 90.0 / 70.0
            self.gyro[2] = self.gyro[2] * 90.0 / 70.0


        self.commsLock.release()

    def processPacket(self, packet):
        self.commsLock.acquire()
        print "[Client Message] " + str(packet)
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