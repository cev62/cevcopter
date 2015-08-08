# Class that deals with 

from gamepad import *

gp = GamePad("/dev/input/js1")
gp.start()
while True:
    time.sleep(0.01)
    print gp.get("LEFT_X")
gp.stop()