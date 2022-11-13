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
        self.sonic=Ultrasonic()
        self.control.Thread_conditiona.start()
        self.ps4Cont = Ps4Controller(self.controlCallBack)
        # self.ps4Cont.setupControlCallback(self.ps4Cont.Ps4Controls.LTHUMBX, self.leftThumbX)
        # self.ps4Cont.setupControlCallback(self.ps4Cont.Ps4Controls.LTHUMBY, self.leftThumbY)
        self.ps4Cont.setupControlCallback(self.ps4Cont.Ps4Controls.cross, self.callback_buzzer)
        self.ps4Cont.setupControlCallback(self.ps4Cont.Ps4Controls.square, self.callback_power)
        self.ps4Cont.setupControlCallback(self.ps4Cont.Ps4Controls.triangle, self.callback_led)
        self.ps4Cont.setupControlCallback(self.ps4Cont.Ps4Controls.circle, self.callback_relax)
        self.ps4Cont.setupControlCallback(self.ps4Cont.Ps4Controls.DPAD, self.callback_move_0_0)
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
            stop_thread(self.thread_led)
            # stop the controller
            self.ps4Cont.stop()
            self.end_sound()
                
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
                    self.buzzer.run("1")
                    time.sleep(0.15)
                    self.buzzer.run("0")
                    time.sleep(0.1)
    
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
            # if self.control.relax_flag==False:
            #     self.control.relax(True)
            #     self.control.relax_flag=True
            # else:
            #     self.control.relax(False)
            #     self.control.relax_flag=False
            if self.relax_flag == False:
                GPIO.output(self.control.GPIO_4,True)
                self.relax_flag = True
                print("relaxed")
            else:
                GPIO.output(self.control.GPIO_4,False)
                self.relax_flag = False
    
    def callback_move_0_0(self, value):
        directionX=str(value[0] * 35)
        directionY=str(value[1] * 35)
        cmd = ["CMD_MOVE", "1", directionX, directionY, "10", "0"]
        self.control.order = cmd
        self.control.timeout = time.time()
        print(cmd)
                
    def start_sound(self):
        self.buzzer.run("1")
        time.sleep(0.45)
        self.buzzer.run("0")
        time.sleep(0.1)
        for i in range(2):
            self.buzzer.run("1")
            time.sleep(0.15)
            self.buzzer.run("0")
            time.sleep(0.1)
    
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