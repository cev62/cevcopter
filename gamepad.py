# Class that handles input from the GamePad

import threading

class GamePad(threading.Thread):

    # Static constants
    buttonMap = {
        "A"         : 0,
        "B"         : 1,
        "X"         : 2,
        "Y"         : 3,
        "LB"        : 4,
        "RB"        : 5,
        "BACK"      : 6,
        "START"     : 7,
        "LOGITECH"  : 8,
        "LJS"       : 9,
        "RJS"       : 10
    }

    axisMap = {
        "LEFT_X"        : 0,
        "LEFT_Y"        : 1,
        "LEFT_TRIGGER"  : 2,
        "RIGHT_X"       : 3,
        "RIGHT_Y"       : 4,
        "RIGHT_TRIGGER" : 5,
        "DPAD_X"        : 6,
        "DPAD_Y"        : 7
    }

    packetLength = 8
    packetTypeByte = 6
    packetNameByte = 7
    packetButtonByte = 4
    packetAxisByte = 5

    def __init__(self, filename):
        threading.Thread.__init__(self)
        self.isStopped = False
        self.daemon = True
        self.isConnected = False
        self.filename = filename
        self.fd = None
        self.packet = []
        self.lock = threading.Lock()
        self.buttons = [False for i in GamePad.buttonMap.keys()]
        self.axes = [0.0 for i in GamePad.axisMap.keys()]
        self.start()

    def run(self):
        while True:
            if self.isStopped:
                return
            if not self.fd:
                try:
                    self.fd = open(self.filename, "r")
                    self.isConnected = True
                except IOError:
                    self.isConnected = False
                    self.fd = None
                    continue
            try:
                for char in self.fd.read(1):
                    self.packet += [ord(char)]
                    if len(self.packet) == GamePad.packetLength:
                        self.lock.acquire()
                        #print "packet"
                        typeByte = self.packet[GamePad.packetTypeByte]
                        nameByte = self.packet[GamePad.packetNameByte]
                        if typeByte == 1:
                            self.buttons[nameByte] = self.packet[GamePad.packetButtonByte] == 1
                        elif typeByte == 2:
                            axisValue = self.convertByteToFloat(self.packet[GamePad.packetAxisByte])
                            self.axes[self.packet[GamePad.packetNameByte]] = self.convertByteToFloat(self.packet[GamePad.packetAxisByte])
                            if nameByte == GamePad.axisMap["LEFT_Y"]        \
                                or nameByte == GamePad.axisMap["RIGHT_Y"]   \
                                or nameByte == GamePad.axisMap["DPAD_Y"]:
                                    axisValue = -axisValue
                                    if axisValue == 0.0:
                                        axisValue = 0.0 # To get rid of -0.0
                            if nameByte == GamePad.axisMap["LEFT_TRIGGER"]  \
                                or nameByte == GamePad.axisMap["RIGHT_TRIGGER"]:
                                axisValue = (axisValue + 1.0) / 2.0

                            self.axes[nameByte] = axisValue
                        self.lock.release()
                        self.packet = []
            except IOError:
                self.fd.close()
                self.fd = None
                self.isConnected = False
                self.resetValues()

    def get(self, input):
        output = 0
        self.lock.acquire()
        if input in GamePad.buttonMap.keys():
            output = self.buttons[GamePad.buttonMap[input]]
        elif input in GamePad.axisMap.keys():
            output = self.axes[GamePad.axisMap[input]]
        self.lock.release()
        return output

    def convertByteToFloat(self, byte):
        if byte >= 128:
            byte = byte - 256
            return float(byte) / 128.0
        else:
            return float(byte) / 127.0

    def resetValues(self):
        self.buttons = [False for i in GamePad.buttonMap.keys()]
        self.axes = [0.0 for i in GamePad.axisMap.keys()]

    def close(self):
        self.isStopped = True
        if self.fd:
            self.fd.close()
        self.resetValues()

# Test functions for GamePad:
def test_gamepad():
    gp = GamePad("/dev/input/js1")
    assert gp != None
    assert gp.daemon == True
    assert gp.filename == "/dev/input/js1"
    assert gp.buttons == [False for i in gp.buttons]
    assert gp.axes == [0.0 for i in gp.axes]
    assert gp.convertByteToFloat(127) == 1
    assert gp.convertByteToFloat(0) == 0
    assert gp.convertByteToFloat(128) == -1
    gp.close()
    assert not gp.fd