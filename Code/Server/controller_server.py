from ps4_controller import *
from Led import *
from Servo import *
from Thread import *
from Buzzer import *
from Control import *
from ADC import *
from Ultrasonic import *
from Command import COMMAND as cmd

class Controller_server:
    def __init__(self):
        self.led=Led()
        self.led_mode = 1
        self.thread_led=threading.Thread(target=self.led.light, args=(["CMD_LED","255","255","255"],))
        self.adc=ADC()
        self.servo=Servo()
        self.relax_flag=False
        self.buzzer=Buzzer()
        self.control=Control()
        self.speed = 10
        self.sonic=Ultrasonic()
        self.control.Thread_conditiona.start()
        self.ps4Cont = Ps4Controller()

        self.ps4Cont.setupControlCallback(self.ps4Cont.Ps4Controls.cross, self.callback_buzzer)
        self.ps4Cont.setupControlCallback(self.ps4Cont.Ps4Controls.square, self.callback_power)
        self.ps4Cont.setupControlCallback(self.ps4Cont.Ps4Controls.triangle, self.callback_led)
        self.ps4Cont.setupControlCallback(self.ps4Cont.Ps4Controls.circle, self.callback_relax)
        self.ps4Cont.setupControlCallback(self.ps4Cont.Ps4Controls.DPAD, self.callback_move)
        self.ps4Cont.setupControlCallback(self.ps4Cont.Ps4Controls.L2, self.callback_rotate_ccw)
        self.ps4Cont.setupControlCallback(self.ps4Cont.Ps4Controls.R2, self.callback_rotate_cw)
        self.ps4Cont.setupControlCallback(self.ps4Cont.Ps4Controls.L1, self.callback_speed_down)
        self.ps4Cont.setupControlCallback(self.ps4Cont.Ps4Controls.R1, self.callback_speed_up)
        self.ps4Cont.setupControlCallback(self.ps4Cont.Ps4Controls.RTHUMBX, self.callback_head_pan)
        self.ps4Cont.setupControlCallback(self.ps4Cont.Ps4Controls.RTHUMBY, self.callback_head_tilt)
        self.ps4Cont.setupControlCallback(self.ps4Cont.Ps4Controls.options, self.callback_exit)
        
        try:
            # start the controller
            self.ps4Cont.start()
            print("ps4 controller running")
            self.start_sound()
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
            try:
                stop_thread(self.thread_led)
            except:
                pass
            
            try:
                stop_thread(self.control.Thread_conditiona)
            except:
                pass
            # stop the controller
            try:
                self.ps4Cont.stop()
            except:
                pass
            GPIO.output(self.control.GPIO_4,True)
            self.end_sound()
            sys.exit("Exiting...")

                
    # generic call back
    def controlCallBack(self, ps4ControlId, value):
        print("Control Id = {}, Value = {}".format(ps4ControlId, value))
        
    def callback_buzzer(self, value):
        if value == 1:
            self.buzzer.run("1")
        else:
            self.buzzer.run("0")
    
    def callback_power(self, value):
        if value == 0:
            batteryVoltage = self.adc.batteryPower()
            print("B1:{} B2:{}".format(batteryVoltage[0], batteryVoltage[1]))
            if batteryVoltage[0] < 5.5 or batteryVoltage[1]<6:
                for i in range(3):
                    self.short_beep()
    
    def callback_led(self, value):
        if value == 0:
            print("led_mode: {}".format(self.led_mode))
            try:
                stop_thread(self.thread_led)
            except:
                pass
            if self.led_mode == 1:
                self.thread_led=threading.Thread(target=self.led.light, args=(["CMD_LED","100","100","100"],))
                self.thread_led.start()
                try:
                    stop_thread(self.thread_led)
                except: 
                    pass
            self.thread_led=threading.Thread(target=self.led.light, args=(["CMD_LED_MOD", str(self.led_mode)],))
            self.thread_led.start()
            self.led_mode += 1
            if self.led_mode >= 6:
                self.led_mode = 0
                
    def callback_relax(self, value):
        if value == 0:
            if self.control.relax_flag==False:
                GPIO.output(self.control.GPIO_4,True)
                self.control.relax(True)
                self.control.relax_flag=True
                print("relaxed")
            else:
                GPIO.output(self.control.GPIO_4,False)
                self.control.relax(False)
                self.control.relax_flag=False
                print("ready")
            # if self.relax_flag == False:
            #     GPIO.output(self.control.GPIO_4,True)
            #     self.relax_flag = True
            #     print("relaxed")
            # else:
            #     GPIO.output(self.control.GPIO_4,False)
            #     self.relax_flag = False
            #     print("ready")
    
    def callback_move(self, value):
        directionX = str(value[0] * 35)
        directionY = str(value[1] * 35)
        speed = str(self.speed)
        cmd = ["CMD_MOVE", "1", directionX, directionY, speed, "0"]
        self.control.order = cmd
        self.control.timeout = time.time()
        print(cmd)
        
    def callback_rotate_cw(self, value):
        speed = str(self.speed)
        if value == 0:
            cmd = ["CMD_MOVE", "1", "0", "0", speed, "0"]
        else:
            cmd = ["CMD_MOVE", "1", "35", "0", speed, "10"]
        self.control.order = cmd
        self.control.timeout = time.time()
        print(cmd)
    
    def callback_rotate_ccw(self, value):
        speed = str(self.speed)
        if value == 0:
            cmd = ["CMD_MOVE", "1", "0", "0", speed, "0"]
        else:
            cmd = ["CMD_MOVE", "1", "-35", "0", speed, "-10"]
        self.control.order = cmd
        self.control.timeout = time.time()
        print(cmd)
        
    def callback_speed_up(self, value):
        if value == 0:
            if self.speed >= 10:
                self.speed = 10
                self.long_beep()
            else:
                self.speed += 1
                self.short_beep()
    
    def callback_speed_down(self, value):
        if value == 0:
            if self.speed <= 2:
                self.speed = 2
                self.long_beep()
            else:
                self.speed -= 1
                self.short_beep()
                
    def callback_head_pan(self, value):
        value *= -1
        if value > 100:
            value = 100.0
        if value < -100:
            value = -100.0
        
        angle = translate(value, -100.0, 100.0, 30, 160)
        self.servo.setServoAngle(1, int(angle))
        print(angle)
    
    def callback_head_tilt(self, value):
        if value > 100:
            value = 100.0
        if value < -100:
            value = -100.0
        
        angle = translate(value, -100.0, 100.0, 20, 160)
        if angle < 50:
            angle = 50
        self.servo.setServoAngle(0, int(angle))
        print(angle)
        
    def callback_exit(self, value):
        if value == 0:
            try:
                stop_thread(self.thread_led)
            except:
                pass
            
            try:
                stop_thread(self.control.Thread_conditiona)
            except:
                pass
            # stop the controller
            try:
                self.ps4Cont.stop()
            except:
                pass
            GPIO.output(self.control.GPIO_4,True)
            self.end_sound()
            sys.exit("Exiting...")
                
    def long_beep(self):
        self.buzzer.run("1")
        time.sleep(0.45)
        self.buzzer.run("0")
        time.sleep(0.1)
        
    def short_beep(self):
        self.buzzer.run("1")
        time.sleep(0.15)
        self.buzzer.run("0")
        time.sleep(0.1)
                
    def start_sound(self):
        self.long_beep()
        for i in range(2):
            self.short_beep()
    
    def end_sound(self):
        for i in range(2):
            self.buzzer.run("1")
            time.sleep(0.3)
            self.buzzer.run("0")
            time.sleep(0.1)
        
        
    # specific callbacks for the left thumb (X & Y)
    def leftThumbX(self, xValue):
        print("LX {}".format(xValue))


    def leftThumbY(self, yValue):
        print("LY {}".format(yValue))
        
def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)