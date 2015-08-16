import serial
import threading
import time

class Serial(threading.Thread):
    def __init__(self, port, timeout=0.03):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.port = port
        self.timeout = timeout
        self.serial = None
        self.dataIn = ["", 0.0, 0.0, 0.0, 100, 1, 0, 0, 0, 0]
        self.dataOut = [0, 0, 0, 0]
        self.expectedDataInLength = len(self.dataIn)
        self.expectedDataOutLength = len(self.dataOut)
        self.daemon = True
        self.buffer = ""

    def run(self):
        while True:
            if not self.serial:
                try:
                    print "Trying to connect to ", self.port
                    self.serial = serial.Serial(port=self.port, baudrate=115200)
                    self.serial.open()
                    print serial == True
                except:
                    self.serial = None
            else:
                self.lock.acquire()

                try:

                    # Read incoming data
                    while self.serial.inWaiting() > 0:
                        while self.serial.inWaiting() > 0:
                            char = self.serial.read(1)
                            if char == "\n":
                                print self.buffer
                                tmpData = self.buffer.split("\t")
                                if len(tmpData) == self.expectedDataInLength:
                                    self.dataIn = tmpData
                                else:
                                    print "Got unexpected data from serial connection"
                                self.buffer = ""
                                break
                            self.buffer += char

                    # Write outgoinf data
                    #print "This is happening"
                    self.serial.write(chr(255))
                    self.serial.write(chr(self.dataOut[0]))
                    self.serial.write(chr(254))
                    self.serial.write(chr(self.dataOut[1]))
                    self.serial.write(chr(253))
                    self.serial.write(chr(self.dataOut[2]))
                    self.serial.write(chr(252))
                    self.serial.write(chr(self.dataOut[3]))

                except:
                    self.serial = None

                self.lock.release()
            time.sleep(self.timeout)

    def setOutgoingData(self, data):
        self.lock.acquire()
        if len(data) == self.expectedDataOutLength:
            self.dataOut = [min(180, max(0, int(i))) for i in data]
        self.lock.release()

    def getIncomingData(self):
        self.lock.acquire()
        output = self.dataIn
        self.lock.release()
        return output