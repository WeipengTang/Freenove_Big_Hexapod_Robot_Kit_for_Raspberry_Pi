from ps4_controller import *
from Thread import *
from Command import COMMAND as cmd
import socket
import struct
import fcntl

class Controller_client:
    def __init__(self):
        # control parameters
        self.led_mode = 1
        self.speed = 10
        
        # start client socket
        self.turn_on_socket()
        # init ps4 controller
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
        # self.ps4Cont.setupControlCallback(self.ps4Cont.Ps4Controls.options, self.callback_exit)
        
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
            # stop the controller
            try:
                self.ps4Cont.stop()
            except:
                pass
            self.end_sound()
            sys.exit("Exiting...")
            
    def get_interface_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                                            0x8915,
                                            struct.pack('256s',b'wlan0'[:15])
                                            )[20:24])
            
    def turn_on_socket(self):
        # HOST = self.get_interface_ip()
        HOST = '127.0.0.1'
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, 5002))
    
    def send_data(self, data):
        try:
            data += '\n'
            self.client_socket.send(data.encode('utf-8'))
        except Exception as e:
            print(e)
    
    def receive_data(self):
        try:
            return self.client_socket.recv(1024).decode('utf-8')
        except Exception as e:
            print(e)
            return None
        
    def callback_buzzer(self, value):
        if value == 1:
            self.send_data("CMD_BUZZER#1")
        else:
            self.send_data("CMD_BUZZER#0")
    
    def callback_power(self, value):
        if value == 0:
            self.send_data("CMD_POWER")
            data = self.receive_data()
            if data != None and data != "":
                data=data.split('\n')[0]
                if data != None and data != "":
                    batteryVoltage = data.split('#')
                    if cmd.CMD_POWER in batteryVoltage:
                        print("B1:{} B2:{}".format(batteryVoltage[1], batteryVoltage[2]))

    
    def callback_led(self, value):
        if value == 0:
            print("led_mode: {}".format(self.led_mode))
            if self.led_mode == 1:
                self.send_data("CMD_LED#100#100#100")
            self.send_data("CMD_LED_MOD#{}".format(self.led_mode))
            self.led_mode += 1
            if self.led_mode >= 6:
                self.led_mode = 0
                
    def callback_relax(self, value):
        if value == 0:
            self.send_data("CMD_RELAX")

    
    def callback_move(self, value):
        data = self.cat_move_cmd(1, value[0] * 35, value[1] * 35, self.speed, 0)
        self.send_data(data)
        print(data)
        
    def callback_rotate_cw(self, value):
        speed = str(self.speed)
        if value == 0:
            data = self.cat_move_cmd(1, 0, 0, speed, 0)
        else:
            data = self.cat_move_cmd(1, 35, 0, speed, 5)
        self.send_data(data)
        print(data)
    
    def callback_rotate_ccw(self, value):
        speed = str(self.speed)
        if value == 0:
            data = self.cat_move_cmd(1, 0, 0, speed, 0)
        else:
            data = self.cat_move_cmd(1, -35, 0, speed, -5)
        self.send_data(data)
        print(data)
        
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
        data = cmd.CMD_HEAD + "#" + "1" + "#" + str(round(angle))
        self.send_data(data)
        print(data)
    
    def callback_head_tilt(self, value):
        if value > 100:
            value = 100.0
        if value < -100:
            value = -100.0
        
        angle = translate(value, -100.0, 100.0, 20, 160)
        if angle < 50:
            angle = 50
        data = cmd.CMD_HEAD + "#" + "0" + "#" + str(round(angle))
        self.send_data(data)
        print(data)
        
    def callback_exit(self, value):
        if value == 0:
            # stop the controller
            try:
                self.ps4Cont.stop()
            except:
                pass
            self.end_sound()
            sys.exit("Exiting...")
                
    def long_beep(self):
        self.send_data("CMD_BUZZER#1")
        time.sleep(0.45)
        self.send_data("CMD_BUZZER#0")
        time.sleep(0.1)
        
    def short_beep(self):
        self.send_data("CMD_BUZZER#1")
        time.sleep(0.15)
        self.send_data("CMD_BUZZER#0")
        time.sleep(0.1)
                
    def start_sound(self):
        self.long_beep()
        for i in range(2):
            self.short_beep()
    
    def end_sound(self):
        for i in range(2):
            self.send_data("CMD_BUZZER#1")
            time.sleep(0.3)
            self.send_data("CMD_BUZZER#0")
            time.sleep(0.1)
            
    def cat_move_cmd(self, gait_flag, x, y, speed, angle):
        rc = cmd.CMD_MOVE
        rc +="#"
        rc += str(gait_flag)
        rc += "#"
        rc += str(round(x))
        rc += "#"
        rc += str(round(y))
        rc += "#"
        rc += str(speed)
        rc += "#"
        rc += str(round(angle))
        return rc
        
        
# specific callbacks for the left thumb (X & Y)
def leftThumbX(xValue):
    print("LX {}".format(xValue))


def leftThumbY(yValue):
    print("LY {}".format(yValue))
        
def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

# generic call back
def controlCallBack(ps4ControlId, value):
    print("Control Id = {}, Value = {}".format(ps4ControlId, value))

if __name__ == '__main__':
    client = Controller_client()