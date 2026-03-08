from machine import Pin, PWM
import time

class DRV8873:
    def __init__(self):
        self.in1 = PWM(Pin(12))
        self.in1.freq(50000) # 频率50千赫兹
        self.in1.duty(512) # 占空比0~1023，对应0~100%
        
        self.in2 = Pin(14, Pin.OUT)
        
    def mode(self, heat=1):
        self.in2.value(heat)
        
    def set_power(self, power):
        power = max(-100, min(100, power))
        
        if power > 0:
            self.mode(1)
            duty = int(power * 10.23)
        elif power < 0:
            self.mode(0)
            duty = int(- power * 10.23)
        else:
            duty = 0
            
        self.in1.duty(duty)
        
if __name__ == "__main__":
    temp_ctl = DRV8873()
    
    temp_ctl.set_power(60)
