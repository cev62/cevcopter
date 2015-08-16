import cv2
import numpy as np
import math

height = 450
width = 325

black = (0, 0, 0)
white = (255, 255, 255)
gray = (200, 200, 200)
darkGray = (100, 100, 100)

blue = (255, 0, 0)
green = (0, 255, 0)
red = (0, 0, 255)
yellow = (0, 255, 255)
paleBlue = (255, 192, 192)
paleGreen = (192, 255, 192)
paleRed = (192, 192, 255)
paleYellow = (192, 255, 255)

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

indicatorCenter = (37, 262)
indicatorSpacing = 25
indicatorRadius = 10
indicatorStroke = gray

def dist(a, b):
    return math.sqrt((float(a[0]) - float(b[0]))**2 + (float(a[1]) - float(b[1]))**2)

def display(Controls, state, axes, gyro, indicators, message, image):
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

    for i, (name, value) in enumerate(indicators):
        fill = red
        if value:
            fill = green
        cv2.circle(img, (indicatorCenter[0], indicatorCenter[1] + i * indicatorSpacing), indicatorRadius, fill, -1)
        cv2.circle(img, (indicatorCenter[0], indicatorCenter[1] + i * indicatorSpacing), indicatorRadius, indicatorStroke, 1)
        cv2.putText(img, name, (indicatorCenter[0] + 2 * indicatorRadius, indicatorCenter[1] + i * indicatorSpacing + indicatorRadius - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)

    # State indicator box
    solidFill = gray
    paleFill = gray
    stateName = "Unknown State"
    if state == Controls.DISABLED:
        solidFill = red
        paleFill = paleRed
        stateName = "Disabled"
    if state == Controls.ENABLED:
        solidFill = green
        paleFill = paleGreen
        stateName = "Enabled"
    if state == Controls.DOWNLOADING_CODE:
        solidFill = blue
        paleFill = paleBlue
        stateName = "Downloading"
    if state == Controls.REBOOTING:
        solidFill = yellow
        paleFill = paleYellow
        stateName = "Rebooting"
    if state == Controls.POWERED_OFF:
        solidFill = yellow
        paleFill = paleYellow
        stateName = "Powered Off"
    if state == Controls.INITIALIZING:
        solidFill = red
        paleFill = paleYellow
        stateName = "Initializing"


    topLeftCorner = (indicatorCenter[0] - indicatorRadius, indicatorCenter[1] + len(indicators)  *indicatorSpacing)
    bottomRightCorner = (width - indicatorSpacing, topLeftCorner[1] + 44)
    cv2.rectangle(img, topLeftCorner, bottomRightCorner, solidFill, -1)
    delta = 5
    cv2.rectangle(img, (topLeftCorner[0] + delta, topLeftCorner[1] + delta), (bottomRightCorner[0] - delta, bottomRightCorner[1] - delta), paleFill, -1)
    cv2.rectangle(img, topLeftCorner, bottomRightCorner, gray, 1)


    textSize = cv2.getTextSize(stateName, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 1)
    cv2.putText(img, stateName, ((topLeftCorner[0] + bottomRightCorner[0] - textSize[0][0]) / 2, topLeftCorner[1] + 32), cv2.FONT_HERSHEY_SIMPLEX, 1.0, black, 1)

    # Gyro display
    gx = gyro[2]#int(gyro[2] / 30.0 * joystickRadius)
    gy = gyro[1]#int(gyro[1] / 30.0 * joystickRadius)
    #print gx, gy
    length = 20
    gyroCenter = (joystickCenter[0] + int(gyro[2] / 30.0 * joystickRadius), joystickCenter[1] - int(gyro[1] / 30.0 * joystickRadius))
    if dist(gyroCenter, joystickCenter) > joystickRadius - length:
        theta = math.atan2(gyroCenter[1] - joystickCenter[1], gyroCenter[0] - joystickCenter[0])
        gyroCenter = (joystickCenter[0] + int(math.cos(theta) * (joystickRadius - length)),
                              joystickCenter[1] + int(math.sin(theta) * (joystickRadius - length)))
    
    #cv2.rectangle(img, (gyroCenter[0] - thickness, gyroCenter[1] - length), (gyroCenter[0] + thickness, gyroCenter[1] + length), darkGray, -1)
    #cv2.rectangle(img, (gyroCenter[0] - length, gyroCenter[1] - thickness), (gyroCenter[0] + length, gyroCenter[1] + thickness), darkGray, -1)

    baseTheta = -gyro[0] * math.pi / 180.0 + math.pi / 4
    thetas = [baseTheta + i*math.pi/2 for i in range(4)]
    for i, theta in enumerate(thetas):
        fill = darkGray
        if i == 0 or i == 3:
            fill = green
        cv2.line(img, (gyroCenter[0] - int(length*math.sin(theta)), gyroCenter[1] - int(length*math.cos(theta))), (gyroCenter[0], gyroCenter[1]), fill, 2)

    cv2.imshow("Cevcopter Controls", img)
    cv2.waitKey(1)