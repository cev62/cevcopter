# Class that deals with 

from gamepad import *
import time
from client import *

gp = GamePad("/dev/input/js1")

def generatePacket():
    return "Hi, I'm a client."

def processPacket(packet):
    print "[Server Reply] " + str(packet)

c = Client(generatePacket, processPacket, "localhost", 22333, 0.1)
c.start()

while True:
    time.sleep(0.5)
    #print gp.get("LEFT_X")
gp.stop()
c.stop()
c.close()

