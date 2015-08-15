
from server import *

def processPacket(packet):
    print "[Client Message] " + str(packet)
    return "Hi, I'm a server Whoo!."

s = Server(processPacket, 22333, 0.1)
s.start()

while True:
    time.sleep(0.5)

s.stop()
s.close()
