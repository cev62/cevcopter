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
        self.dataIn = []
        self.dataOut = []
        self.daemon = True
        self.buffer = ""

    def run(self):
        while True:
            if not self.serial:
                try:
                    self.serial = serial.Serial(port=self.port, baudrate=115200)
                except:
                    self.serial = None
            else:
                self.lock.acquire()

                # Read incoming data
                while self.serial.inWaiting() > 0:
                    while self.serial.inWaiting() > 0:
                        char = self.serial.read(1)
                        if char == "\n":
                            self.dataIn = self.buffer.split("\t")
                            self.buffer = ""
                            break
                        self.buffer += char

                # Write outgoinf data
                # @TODO implement

                self.lock.release()
            time.sleep(self.timeout)

    def setOutgoingData(self, data):
        self.lock.acquire()
        self.dataOut = data
        self.lock.release()

    def getIncomingData(self):
        self.lock.acquire()
        output = self.dataIn
        self.lock.release()
        return output