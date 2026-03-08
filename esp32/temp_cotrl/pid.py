import time

class PID:
    def __init__(self, Kp, Ki, Kd, ideal_temp=40, limits=(-100, 100)):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.ideal_temp = ideal_temp
        self.limits = limits
        
        self.integral = 0
        self.last_error = 0
        self.last_time = None
        
    def reset(self):
        self.integral = 0
        self.last_error = 0
        self.last_time = None
        
    def update(self, real_temp):
        now = time.ticks_ms()
        error = self.ideal_temp - real_temp
        
        # 计算时间差(秒)
        if self.last_time is None:
            dt = 0
        else:
            dt = time.ticks_diff(now, self.last_time) / 1000.0
        
        self.last_time = now
        
        # 比例项
        proportional = self.Kp * error
        
        # 积分项(带抗积分饱和)
        if dt > 0:
            self.integral += error * dt
            
            i_limit = (self.limits[1] - self.limits[0]) / 2
            self.integral = max(-i_limit, min(i_limit, self.integral))
            
        integral = self.Ki * self.integral
        
        # 微分项
        if dt > 0:
            derivative = self.Kd * (error - self.last_error) / dt
        else:
            derivative = 0
        
        self.last_error = error
        
        output = proportional + integral + derivative
        
        output = min(self.limits[1], max(self.limits[0], output))
        
        return output
    
    def set_K(self, Kp=None, Ki=None, Kd=None):
        if Kp is not None: self.Kp = Kp
        if Ki is not None: self.Ki = Ki
        if Kd is not None: self.Kd = Kd
        
    def set_ideal_temp(self, ideal_temp):
        self.ideal_temp = ideal_temp
        
if __name__ == "__main__":
    pid = PID(1, 0, 0, ideal_temp=60)
    output = pid.update(50)
    print(output)
