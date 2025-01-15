from PyQt5.QtWidgets import  QMessageBox
from PyQt5.QtCore import QThread,pyqtSignal
import serial
import os
import struct
import threading
import time
import crcmod
class BinFileReader(QThread):

    data_signal = pyqtSignal(bytearray)
    progress_signal = pyqtSignal(int)
    filesize_signal = pyqtSignal(int)

    def __init__(self, file_path, serial_port, baud_rate, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.bitrate = 0
        self.channel = 0
        self.file_count = 0
        self.running = True  # 控制线程运行的标志
        self.data = bytearray()  # 初始化 self.data 为一个空字节串
    def run(self):
        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate)
            if self.ser.is_open:
                print("串口已成功打开。")
                # self.ser.write(0x666666)
            else:
                print("串口打开失败。")
        except serial.SerialException as e:
            print(f"串口打开时发生错误: {e}")
            QMessageBox.warning(None, 'err!', str(e), QMessageBox.Ok)
            return

        file_size = os.path.getsize(self.file_path)
        self.filesize_signal.emit(file_size)
        crc16_func = crcmod.predefined.mkPredefinedCrcFun('crc-ccitt-false')
        try:
            with open(self.file_path, 'rb') as file:
                file_name = self.file_path.split('/')[-1]
                file_name=file_name.split('.')[0]
                # print(file_name)
                # file.seek(0)
                # self.file_count = int.from_bytes(file.read(4), byteorder='little')
                
                # print(str(self.file_count))

                # file.seek(4)
                # self.bitrate = int.from_bytes(file.read(4), byteorder='little')
                
                # print(str(self.bitrate) )
                # file.seek(8)
                # self.data_depth = int.from_bytes(file.read(2), byteorder='little')
                
                # print(str(self.data_depth))

                # file.seek(10)
                # self.channel = int.from_bytes(file.read(2), byteorder='little')
                # print(self.channel)
                
                # self.data +=struct.pack('B', 0x01)
                # self.data +=struct.pack('B', len(file_name.split('.')[0]))
                # self.data +=file_name.encode()
                # # self.data +=struct.pack('>I', self.file_count)
                # # self.data +=struct.pack('>I', self.bitrate)
                # # self.data +=struct.pack('>H', self.data_depth)
                # # self.data +=struct.pack('>H', self.channel)
                # self.data +=struct.pack('>I', file_size)
                # # self.data +=struct.pack('>H', crc16_func(self.data))
                # self.ser.write(self.data)
                

                # print(f"Sent data: {self.data.hex()}")  # 日志记录发送的数据
                # print(len(self.data))    

                # if not self.wait_for_ack():
                #         print("Did not receive 0xFF acknowledgement.")
                # else:       
                #         print("receive 0xFF acknowledgement.")
                     
    
                # # # print(self.data.hex())
                # chunk = file.read(64)
             
                # self.data = b''
                #     # if len(chunk) == 128:
                #     #     self.data += struct.pack('B', 0x02)
                #     # else:
                #     #     self.data += struct.pack('B', 0x02)
                #     # self.data += struct.pack('>I', index)
                # self.data =chunk
                #     # self.data +=struct.pack('>I', crc16_func(self.data))
                # self.ser.write(self.data)
                # print(self.data.hex())
               
                # if not self.wait_for_ack():
                #     print("Did not receive 0xFF acknowledgement.")
                # else:       
                #     print("receive 0xFF acknowledgement.")    
                index = 0
                count = 0
                while self.running:
                    if count==0:
                        self.data = b'' 
                        chunk = file.read(62)
                        self.data+=struct.pack('B', 0x7F)
                        self.data+=struct.pack('B', 0xF0)
                        self.data+=chunk
                    else:
                        self.data = b''
                        chunk = file.read(64)
                        self.data +=chunk
                 

                    # self.data = b''
                    # chunk = file.read(64)
                    if not chunk:
                        break
                    # self.data +=chunk
                    self.ser.write(self.data)
                    # if len(chunk) == 128:
                    #     self.data += struct.pack('B', 0x02)
                    # else:
                    #     self.data += struct.pack('B', 0x02)
                    # self.data += struct.pack('>I', index)
                    
                    # self.data +=struct.pack('>I', crc16_func(self.data))
                    count += 1
                    if count > 3:
                        count=0
                    
                    print(self.data.hex())
                    index += len(chunk)
                    if not self.wait_for_ack():
                        print("Did not receive 0xFF acknowledgement.")
                    else:       
                        print("receive 0xFF acknowledgement.")
                        self.progress_signal.emit(index)
        except Exception as e:
            QMessageBox.warning(self, 'tips!', str(e), QMessageBox.Ok)
        finally:
            self.ser.close()
            self.data_signal.emit(bytearray("ok", 'utf-8'))
    


    def wait_for_ack(self):
        timeout = 5000  # 5 seconds timeout
        start_time = time.time()
        while time.time() - start_time < timeout / 1000:
            if self.ser.in_waiting > 0:
                ack = self.ser.read(1)
                if ack == b'\xff':
                    return True
        return False
    
    def stop(self):
        self.running = False
        self.wait()



class SerialThread(QThread):
    new_data_signal = pyqtSignal(str)  # 定义一个信号，用于传输接收到的数据
    finished_signal = pyqtSignal(serial.Serial)
   
    def __init__(self, serial_port, baud_rate):
        super().__init__()
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.stop_event = threading.Event()  # 创建一个停止事件

    def close_serial(self):
        if self.ser is not None:
            self.stop_event.set()
            self.ser.close()
           

    def run(self):
        # 串口接收数据的代码将被放在这里
        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate)
            if self.ser.is_open:
             print("串口已成功打开。")
             self.ser.flushInput()
            else:
             print("串口打开失败。")
            
        except serial.SerialException as e:
            print(f"串口打开时发生错误: {e}")
            
        
        
       # self.ser.write(B"helloWorld!\n")
        while not self.stop_event.is_set():
            # 这里只是模拟接收数据的过程
            if self.ser.in_waiting > 0:
                # 如果有数据可读，读取数据
                data = self.ser.read(self.ser.in_waiting).decode('utf-8').strip()  # 读取所有可读数据
                print(f"Received data: {data}")
                self.new_data_signal.emit(data)  # 发射信号，传递接收到的数据
                
            # data = self.ser.readline().decode('utf-8').strip()
    