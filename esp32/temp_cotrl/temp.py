from machine import SPI, Pin
import time

class MAX6675:
    def __init__(self, cs_pin=5):
        self.cs = Pin(cs_pin, Pin.OUT)
        self.cs.value(1)  # 初始状态拉高，不选中
        # ESP32默认SPI引脚：SCK=GPIO18, MISO=GPIO19, MOSI=GPIO23
        self.spi = SPI(2, baudrate=1000000, polarity=0, phase=0, sck=Pin(18), mosi=None, miso=Pin(19))
        self.temperature = 0.0
        
    def read(self):
        """
        MAX6675模块在SPI通信时，会返回一个16位的数据帧
        16~14：保留位，始终为零
        13~3：12位温度数据，表示实际温度值
        2：故障检测位，值为1表示开路或其他故障
        1：空位始终为零
        """
        self.cs.value(0)  # 拉低CS开始读取
        time.sleep_us(1)  # 短暂延时
        
        try:
            # 读取2字节数据（16位）
            data = self.spi.read(2)
        finally:
            self.cs.value(1)  # 确保CS被拉高
        
        if data and len(data) == 2:
            # 合并两个字节
            raw_data = (data[0] << 8) | data[1]
            
            # 检查热电偶是否断开（D2位）
            if raw_data & 0x04:
                print("警告：热电偶未连接或断开")
                return None
            
            # 提取温度数据（D15-D3），右移3位，与十六进制数0x0FFF（1111 1111 1111）进行与运算
            temp_raw = (raw_data >> 3) & 0x0FFF
            
            # 转换为摄氏度（分辨率0.25°C）
            self.temperature = int(temp_raw * 2.5) / 10
            return self.temperature
        return None

if __name__ == "__main__":
    # 创建MAX6675对象，CS接GPIO5
    max6675 = MAX6675()

    print("MAX6675 K型热电偶温度读取")
    print("=" * 30)

    while True:
        temp = max6675.read()
        
        if temp is not None:
            print(f"温度: {temp}°C")
        else:
            print("读取失败，请检查热电偶连接")
        
        # MAX6675转换时间至少100ms，建议250ms以上
        time.sleep(1)
