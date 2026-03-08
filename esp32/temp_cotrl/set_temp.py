from machine import Pin
from time import sleep

class Key:
    def __init__(self):
        self.add_temp = Pin(15, Pin.IN, Pin.PULL_DOWN)
        self.reduce_temp = Pin(16, Pin.IN, Pin.PULL_DOWN)
        
    def press(self):
        if self.add_temp.value() or self.reduce_temp.value():
            return True
        else:
            return False
        
    def double_press(self):
        if self.add_temp.value() and self.reduce_temp.value():
            return True
        else:
            return False
    
    def limit(self, temp):
        if temp > 70:
            temp = 70
        elif temp < 40:
            temp = 40
        return temp
    
    def set_K(self, screen, name, value):
        screen.set_K(name, value)
        cont = 0
        sleep(0.2)
        while True:
            if self.add_temp.value():
                cont = 0
                sleep(0.2)
                if self.add_temp.value():
                    while self.add_temp.value():
                        value += 0.1
                        screen.set_K(name, value)
                        sleep(0.1)
                else:
                    value += 1
                    screen.set_K(name, value)
                        
            elif self.reduce_temp.value():
                cont = 0
                sleep(0.2)
                if self.reduce_temp.value() == 1:
                    while self.reduce_temp.value() == 1:
                        value -= 0.1
                        screen.set_K(name, value)
                        sleep(0.1)
                else:
                    value -= 1
                    screen.set_K(name, value)
            else:
                if cont == 20:
                    #return round(value, 1)
                    return int(value * 10) / 10
                sleep(0.1)
                cont += 1

    def set_arg(self, screen, show_curve, Kp, Ki, Kd):
        screen.menu(show_curve, Kp, Ki, Kd, 0)
        select = 0
        sleep(0.4)
        while True:
            if self.double_press():
                sleep(0.2)
                break
            elif self.add_temp.value():
                cont = 0
                if select == 0:
                    show_curve = not show_curve
                    screen.menu(show_curve, Kp, Ki, Kd, select)
                    sleep(0.4)
                    break
                elif select == 1:
                    Kp = self.set_K(screen, "Kp", Kp)
                elif select == 2:
                    Ki = self.set_K(screen, "Ki", Ki)
                else:
                    Kd = self.set_K(screen, "Kd", Kd)
            elif self.reduce_temp.value():
                cont = 0
                if select == 3:
                    select = 0
                else:
                    select += 1
            
            screen.menu(show_curve, Kp, Ki, Kd, select)
            sleep(0.1)
            
        return show_curve, Kp, Ki, Kd

    def set_temp(self, screen, temp):
        screen.config(temp)
        cont = 0
        while True:
            if self.add_temp.value():
                cont = 0
                sleep(0.2)
                if self.add_temp.value():
                    while self.add_temp.value():
                        temp += 0.1
                        temp = self.limit(temp)
                        screen.config(temp)
                        sleep(0.1)
                else:
                    temp += 5
                    temp = self.limit(temp)
                    screen.config(temp)
                        
            elif self.reduce_temp.value():
                cont = 0
                sleep(0.2)
                if self.reduce_temp.value():
                    while self.reduce_temp.value():
                        temp -= 0.1
                        temp = self.limit(temp)
                        screen.config(temp)
                        sleep(0.1)
                else:
                    temp -= 5
                    temp = self.limit(temp)
                    screen.config(temp)
            else:
                if cont == 10:
                    return int(temp * 10) / 10
                sleep(0.1)
                cont += 1

if __name__ =="__main__":
    from led import Screen
    screen = Screen()
    key = Key()
    
    key.set_arg(screen, True, 5, 1, 4)
