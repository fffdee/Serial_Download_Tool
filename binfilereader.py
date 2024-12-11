from PyQt5.QtWidgets import  QMessageBox
from PyQt5.QtCore import QThread,pyqtSignal
import serial
import os
import struct
import threading
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

    def run(self):
        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate)
            if self.ser.is_open:
                print("串口已成功打开。")
            else:
                print("串口打开失败。")
        except serial.SerialException as e:
            print(f"串口打开时发生错误: {e}")
            QMessageBox.warning(None, 'err!', str(e), QMessageBox.Ok)
            return

        file_size = os.path.getsize(self.file_path)
        self.filesize_signal.emit(file_size)

        try:
            with open(self.file_path, 'rb') as file:
                file_name = self.file_path.split('/')[-1]
                file.seek(0)
                self.file_count = int.from_bytes(file.read(4), byteorder='little')
                
                print(str(self.file_count))

                file.seek(4)
                self.bitrate = int.from_bytes(file.read(4), byteorder='little')
                
                print(str(self.bitrate) )
                file.seek(8)
                self.data_depth = int.from_bytes(file.read(2), byteorder='little')
                
                print(str(self.data_depth))

                file.seek(10)
                self.channel = int.from_bytes(file.read(2), byteorder='little')
                print(self.channel)


                self.ser.write(struct.pack('B', 0x01))
                self.ser.write(struct.pack('B', len(file_name)))
                self.ser.write(file_name.encode())
                self.ser.write(struct.pack('>I', self.file_count))
                self.ser.write(struct.pack('>I', self.bitrate))
                self.ser.write(struct.pack('>H', self.data_depth))
                self.ser.write(struct.pack('>H', self.channel))
                self.ser.write(struct.pack('>I', file_size))
                self.ser.write(struct.pack('>I', 0))

                index = 0
                while self.running:
                    chunk = file.read(128)
                    if not chunk:
                        break
                    self.ser.write(struct.pack('B', 0x02 if len(chunk) == 128 else 0x03))
                    self.ser.write(struct.pack('>I', index))
                    self.ser.write(chunk)
                    self.ser.write(struct.pack('>I', 0))
                    index += len(chunk)
                    self.progress_signal.emit(index)
        except Exception as e:
            QMessageBox.warning(self, 'tips!', str(e), QMessageBox.Ok)
        finally:
            self.ser.close()
            self.data_signal.emit(bytearray("ok", 'utf-8'))

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
    