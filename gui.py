import cv2
import numpy as np
import math

height = 450
width = 325

black = (0, 0, 0)
white = (255, 255, 255)
gray = (200, 200, 200)

blue = (255, 0, 0)
green = (0, 255, 0)
red = (0, 0, 255)
yellow = (0, 255, 255)

joystickCenter = (137, 137)
joystickRadius = 87
joystickKnobRadius = 25
joystickStroke = black
joystickFill = white
joystickKnobStroke = black
joystickKnobFill = gray

joystickTurnRadius = 105
joystickTurnKnobRadius = 10
joystickTurnKnobStroke = black
joystickTurnKnobFill = gray

throttleCorner = (260, 50)
throttleWidth = 40
throttleHeight = 175
throttleKnobWidth = 40
throttleKnobHeight = 10
throttleStroke = black
throttleFill = white
throttleKnobStroke = black
throttleKnobFill = gray

def __init__(self):
    pass

def dist(a, b):
    return math.sqrt((float(a[0]) - float(b[0]))**2 + (float(a[1]) - float(b[1]))**2)

def display(axes, indicators, message, image):
    img = np.zeros((450, 325, 3), np.uint8)
    img[:] = [255, 255, 255]

    # Joystick Display
    cv2.circle(img, joystickCenter, joystickRadius, joystickFill, -1)
    cv2.circle(img, joystickCenter, joystickRadius, joystickStroke, 1)

    # Joystick Knob
    joystickKnobCenter = ( int(joystickCenter[0] + axes[0] * (joystickRadius - joystickKnobRadius)),    \
                           int(joystickCenter[1] - axes[1] * (joystickRadius - joystickKnobRadius)))
    if dist(joystickKnobCenter, joystickCenter) > joystickRadius - joystickKnobRadius:
        theta = math.atan2(joystickKnobCenter[1] - joystickCenter[1], joystickKnobCenter[0] - joystickCenter[0])
        joystickKnobCenter = (joystickCenter[0] + int(math.cos(theta) * (joystickRadius - joystickKnobRadius)),
                              joystickCenter[1] + int(math.sin(theta) * (joystickRadius - joystickKnobRadius)))
    cv2.circle(img, joystickKnobCenter, joystickKnobRadius, joystickKnobFill, -1)
    cv2.circle(img, joystickKnobCenter, joystickKnobRadius, joystickKnobStroke, 1)

    # Joystick Turn Knob
    joystickTurnKnobCenter = (joystickCenter[0] + int(joystickTurnRadius * math.cos(-axes[2] * math.pi / 2.0 + math.pi / 2.0)),
                              joystickCenter[1] - int(joystickTurnRadius * math.sin(-axes[2] * math.pi / 2.0 + math.pi / 2.0)))
    cv2.circle(img, joystickTurnKnobCenter, joystickTurnKnobRadius, joystickTurnKnobFill, -1)
    cv2.circle(img, joystickTurnKnobCenter, joystickTurnKnobRadius, joystickTurnKnobStroke, 1)

    # Throttle Display
    cv2.rectangle(img, throttleCorner, (throttleCorner[0] + throttleWidth, throttleCorner[1] + throttleHeight), throttleFill, -1)
    cv2.rectangle(img, throttleCorner, (throttleCorner[0] + throttleWidth, throttleCorner[1] + throttleHeight), throttleStroke, 1)

    # Throttle Knob
    throttleKnobCorner = (throttleCorner[0], throttleCorner[1] + throttleHeight - int(axes[3] * (throttleHeight - throttleKnobHeight)) - throttleKnobHeight)
    cv2.rectangle(img, throttleKnobCorner, (throttleKnobCorner[0] + throttleKnobWidth, throttleKnobCorner[1] + throttleKnobHeight), throttleKnobFill, -1)
    cv2.rectangle(img, throttleKnobCorner, (throttleKnobCorner[0] + throttleKnobWidth, throttleKnobCorner[1] + throttleKnobHeight), throttleKnobStroke, 1)


    cv2.imshow("Cevcopter Controls", img)
    cv2.waitKey(1)