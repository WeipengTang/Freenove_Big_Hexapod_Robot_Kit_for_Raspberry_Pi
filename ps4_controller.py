import pygame
from pygame.locals import *
import os, sys
import threading
import time

"""
NOTES - pygame events and values

JOYAXISMOTION
event.axis              event.value
0 - x axis left thumb   (+1 is right, -1 is left)
1 - y axis left thumb   (+1 is down, -1 is up)
2 - x axis right thumb  (+1 is right, -1 is left)
3 - y axis right thumb  (+1 is down, -1 is up)
4 - right trigger
5 - left trigger

JOYBUTTONDOWN | JOYBUTTONUP
event.button
A = 0
B = 1
X = 2
Y = 3
LB = 4
RB = 5
BACK = 6
START = 7
XBOX = 8
LEFTTHUMB = 9
RIGHTTHUMB = 10

JOYHATMOTION
event.value
[0] - horizontal
[1] - vertival
[0].0 - middle
[0].-1 - left
[0].+1 - right
[1].0 - middle
[1].-1 - bottom
[1].+1 - top

"""


# Main class for reading the ps4 controller values
class Ps4Controller(threading.Thread):
    # internal ids for the ps4 controls
    class Ps4Controls():
        LTHUMBX = 0
        LTHUMBY = 1
        L2 = 2
        RTHUMBX = 3
        RTHUMBY = 4
        R2 = 5
        cross = 6
        circle = 7
        triangle = 8
        square = 9
        L1 = 10
        R1 = 11
        L2 = 12
        R2 = 13
        share = 14
        options = 15
        ps = 16
        LEFTTHUMB = 17
        RIGHTTHUMB = 18
        DPAD = 19
    
    class PyGameAxis():
        LTHUMBX = 0
        LTHUMBY = 1
        L2 = 2
        RTHUMBX = 3
        RTHUMBY = 4
        R2 = 5
    
    class PyGameButtons():
        cross = 0
        circle = 1
        triangle = 2
        square = 3
        L1 = 4
        R1 = 5
        L2 = 6
        R2 = 7
        share = 8
        options = 9
        ps = 10
        LEFTTHUMB = 11
        RIGHTTHUMB = 12

    # map between pygame axis (analogue stick) ids and ps4 control ids
    AXISCONTROLMAP = {PyGameAxis.LTHUMBX: Ps4Controls.LTHUMBX,
                      PyGameAxis.LTHUMBY: Ps4Controls.LTHUMBY,
                      PyGameAxis.RTHUMBX: Ps4Controls.RTHUMBX,
                      PyGameAxis.RTHUMBY: Ps4Controls.RTHUMBY}

    # map between pygame axis (trigger) ids and ps4 control ids
    TRIGGERCONTROLMAP = {PyGameAxis.R2: Ps4Controls.R2,
                         PyGameAxis.L2: Ps4Controls.L2}

    # map between pygame buttons ids and ps4 contorl ids
    BUTTONCONTROLMAP = {PyGameButtons.cross: Ps4Controls.cross,
                        PyGameButtons.circle: Ps4Controls.circle,
                        PyGameButtons.triangle: Ps4Controls.triangle,
                        PyGameButtons.square: Ps4Controls.square,
                        PyGameButtons.L1: Ps4Controls.L1,
                        PyGameButtons.L2: Ps4Controls.L2,
                        PyGameButtons.R1: Ps4Controls.R1,
                        PyGameButtons.R2: Ps4Controls.R2,
                        PyGameButtons.share: Ps4Controls.share,
                        PyGameButtons.options: Ps4Controls.options,
                        PyGameButtons.ps: Ps4Controls.ps,
                        PyGameButtons.LEFTTHUMB: Ps4Controls.LEFTTHUMB,
                        PyGameButtons.RIGHTTHUMB: Ps4Controls.RIGHTTHUMB}

    # setup ps4 controller class
    def __init__(self,
                 controllerCallBack=None,
                 joystickNo=0,
                 deadzone=30,
                 scale=100,
                 invertYAxis=True):

        # setup threading
        threading.Thread.__init__(self)

        # persist values
        self.running = False
        self.controllerCallBack = controllerCallBack
        self.joystickNo = joystickNo
        self.lowerDeadzone = deadzone * -1
        self.upperDeadzone = deadzone
        self.scale = scale
        self.invertYAxis = invertYAxis
        self.controlCallbacks = {}

        # setup controller properties
        self.controlValues = {self.Ps4Controls.LTHUMBX: 0,
                              self.Ps4Controls.LTHUMBY: 0,
                              self.Ps4Controls.RTHUMBX: 0,
                              self.Ps4Controls.RTHUMBY: 0,
                              self.Ps4Controls.R1: 0,
                              self.Ps4Controls.L1: 0,
                              self.Ps4Controls.R2: 0,
                              self.Ps4Controls.L2: 0,
                              self.Ps4Controls.triangle: 0,
                              self.Ps4Controls.circle: 0,
                              self.Ps4Controls.cross: 0,
                              self.Ps4Controls.square: 0,
                              self.Ps4Controls.share: 0,
                              self.Ps4Controls.options: 0,
                              self.Ps4Controls.ps: 0,
                              self.Ps4Controls.LEFTTHUMB: 0,
                              self.Ps4Controls.RIGHTTHUMB: 0,
                              self.Ps4Controls.DPAD: (0, 0)}

        # setup pygame
        self._setupPygame(joystickNo)

    # Create controller properties
    @property
    def LTHUMBX(self):
        return self.controlValues[self.Ps4Controls.LTHUMBX]

    @property
    def LTHUMBY(self):
        return self.controlValues[self.Ps4Controls.LTHUMBY]

    @property
    def RTHUMBX(self):
        return self.controlValues[self.Ps4Controls.RTHUMBX]

    @property
    def RTHUMBY(self):
        return self.controlValues[self.Ps4Controls.RTHUMBY]

    @property
    def R2(self):
        return self.controlValues[self.Ps4Controls.R2]

    @property
    def L2(self):
        return self.controlValues[self.Ps4Controls.L2]

    @property
    def triangle(self):
        return self.controlValues[self.Ps4Controls.triangle]

    @property
    def circle(self):
        return self.controlValues[self.Ps4Controls.circle]

    @property
    def square(self):
        return self.controlValues[self.Ps4Controls.square]

    @property
    def cross(self):
        return self.controlValues[self.Ps4Controls.cross]

    @property
    def L1(self):
        return self.controlValues[self.Ps4Controls.L1]

    @property
    def R2(self):
        return self.controlValues[self.Ps4Controls.R2]

    @property
    def share(self):
        return self.controlValues[self.Ps4Controls.share]

    @property
    def options(self):
        return self.controlValues[self.Ps4Controls.options]

    @property
    def ps(self):
        return self.controlValues[self.Ps4Controls.ps]

    @property
    def LEFTTHUMB(self):
        return self.controlValues[self.Ps4Controls.LEFTTHUMB]

    @property
    def RIGHTTHUMB(self):
        return self.controlValues[self.Ps4Controls.RIGHTTHUMB]

    @property
    def DPAD(self):
        return self.controlValues[self.Ps4Controls.DPAD]

    # setup pygame
    def _setupPygame(self, joystickNo):
        # set SDL to use the dummy NULL video driver, so it doesn't need a windowing system.
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        # init pygame
        pygame.init()
        # create a 1x1 pixel screen, its not used so it doesnt matter
        screen = pygame.display.set_mode((1, 1))
        # init the joystick control
        pygame.joystick.init()
        # how many joysticks are there
        # print pygame.joystick.get_count()
        # get the first joystick
        joy = pygame.joystick.Joystick(joystickNo)
        # init that joystick
        joy.init()

    # called by the thread
    def run(self):
        self._start()

    # start the controller
    def _start(self):

        self.running = True

        # run until the controller is stopped
        while (self.running):
            # react to the pygame events that come from the ps4 controller
            for event in pygame.event.get():

                # thumb sticks, trigger buttons
                if event.type == JOYAXISMOTION:
                    # is this axis on our ps4 controller
                    if event.axis in self.AXISCONTROLMAP:
                        # is this a y axis
                        yAxis = True if (
                                event.axis == self.PyGameAxis.LTHUMBY or event.axis == self.PyGameAxis.RTHUMBY) else False
                        # update the control value
                        self.updateControlValue(self.AXISCONTROLMAP[event.axis],
                                                self._sortOutAxisValue(event.value, yAxis))
                    # is this axis a trigger
                    if event.axis in self.TRIGGERCONTROLMAP:
                        # update the control value
                        self.updateControlValue(self.TRIGGERCONTROLMAP[event.axis],
                                                self._sortOutTriggerValue(event.value))
                        
                # d pad
                elif event.type == JOYHATMOTION:
                    # update control value
                    self.updateControlValue(self.Ps4Controls.DPAD, event.value)

                # button pressed and unpressed
                elif event.type == JOYBUTTONUP or event.type == JOYBUTTONDOWN:
                    # is this button on our ps4 controller
                    if event.button in self.BUTTONCONTROLMAP:
                        # update control value
                        self.updateControlValue(self.BUTTONCONTROLMAP[event.button],
                                                self._sortOutButtonValue(event.type))

    # stops the controller
    def stop(self):
        self.running = False

    # updates a specific value in the control dictionary
    def updateControlValue(self, control, value):
        # if the value has changed update it and call the callbacks
        if self.controlValues[control] != value:
            self.controlValues[control] = value
            self.doCallBacks(control, value)

    # calls the call backs if necessary
    def doCallBacks(self, control, value):
        # call the general callback
        if self.controllerCallBack != None: self.controllerCallBack(control, value)

        # has a specific callback been setup?
        if control in self.controlCallbacks:
            self.controlCallbacks[control](value)

    # used to add a specific callback to a control
    def setupControlCallback(self, control, callbackFunction):
        # add callback to the dictionary
        self.controlCallbacks[control] = callbackFunction

    # scales the axis values, applies the deadzone
    def _sortOutAxisValue(self, value, yAxis=False):
        # invert yAxis
        if yAxis and self.invertYAxis: value = value * -1
        # scale the value
        value = value * self.scale
        # apply the deadzone
        if value < self.upperDeadzone and value > self.lowerDeadzone: value = 0
        return value

    # turns the trigger value into something sensible and scales it
    def _sortOutTriggerValue(self, value):
        # trigger goes -1 to 1 (-1 is off, 1 is full on, half is 0) - I want this to be 0 - 1
        value = max(0, (value + 1) / 2)
        # scale the value
        value = value * self.scale
        return value

    # turns the event type (up/down) into a value
    def _sortOutButtonValue(self, eventType):
        # if the button is down its 1, if the button is up its 0
        value = 1 if eventType == JOYBUTTONDOWN else 0
        return value


# tests
if __name__ == '__main__':

    # generic call back
    def controlCallBack(ps4ControlId, value):
        print("Control Id = {}, Value = {}".format(ps4ControlId, value))


    # specific callbacks for the left thumb (X & Y)
    def leftThumbX(xValue):
        print("LX {}".format(xValue))


    def leftThumbY(yValue):
        print("LY {}".format(yValue))


    # setup ps4 controller, set out the deadzone and scale, also invert the Y Axis (for some reason in Pygame negative is up - wierd!
    ps4Cont = Ps4Controller(controlCallBack, deadzone=30, scale=100, invertYAxis=True)

    # setup the left thumb (X & Y) callbacks
    ps4Cont.setupControlCallback(ps4Cont.Ps4Controls.LTHUMBX, leftThumbX)
    ps4Cont.setupControlCallback(ps4Cont.Ps4Controls.LTHUMBY, leftThumbY)

    try:
        # start the controller
        ps4Cont.start()
        print("ps4 controller running")
        while True:
            time.sleep(1)

    # Ctrl C
    except KeyboardInterrupt:
        print("User cancelled")

    # error
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    finally:
        # stop the controller
        ps4Cont.stop()
