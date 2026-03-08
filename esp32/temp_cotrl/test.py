from led import Screen
from set_temp import Key
from temp import MAX6675
from pid import PID
from change_temp import DRV8873
from time import sleep

class App:
    def __init__(self):
        self.real_temp = 40
        self.ideal_temp = 60
        self.temp_data = []
        self.Kp, self.Ki, self.Kd = 3, 0, 0

        self.screen = Screen()
        self.key = Key()
        self.temp = MAX6675()
        self.pid = PID(self.Kp, self.Ki, self.Kd, self.ideal_temp)
        self.temp_ctl = DRV8873()

        self.show_curve = False
        
    def change_temp(self):
        if self.real_temp - self.ideal_temp > 5:
            self.temp_ctl.set_power(100)
        elif self.ideal_temp - self.real_temp > 5:
            self.temp_ctl.set_power(-100)
        else:
            power = self.pid.update(self.real_temp)
            self.temp_ctl.set_power(power)
            print(power)
            
    def main(self):
        cont = 0
        while True:
            if self.key.press():
                self.temp_ctl.set_power(0)
                if self.key.double_press():
                    self.show_curve, self.Kp, self.Ki, self.Kd = self.key.set_arg(self.screen, self.show_curve, self.Kp, self.Ki, self.Kd)
                else:
                    self.ideal_temp = self.key.set_temp(self.screen, self.ideal_temp)
                    self.pid.set_ideal_temp(self.ideal_temp)
                    
            if self.temp.read() is not None:
                self.real_temp = self.temp.read()
                self.change_temp()
                
            if cont > 3:
                cont = 0
                self.temp_data.append(self.screen.point_mapping(self.real_temp))
                if len(self.temp_data) > 90:
                    self.temp_data.pop(0)
            else:
                cont += 1
            
            if self.show_curve:
                self.screen.update_graph(self.temp_data, int(self.real_temp), self.ideal_temp)
            else:
                self.screen.update(self.real_temp, self.ideal_temp)
                
            sleep(0.1)
