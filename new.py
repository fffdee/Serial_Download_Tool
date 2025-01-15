from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
import serial
import os
import struct
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
        self.running = True

    def run(self):
        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate)
            if self.ser.is_open:
                print("串口已成功打开。")
            else:
                print("串口打开失败。")
                return

            file_size = os.path.getsize(self.file_path)
            self.filesize_signal.emit(file_size)
            crc16_func = crcmod.predefined.mkPredefinedCrcFun('crc-ccitt-false')

            with open(self.file_path, 'rb') as file:
                file_name = self.file_path.split('/')[-1].split('.')[0]
                file.seek(12)  # Skip the header as it's already sent

                index = 0
                while self.running:
                    chunk = file.read(128)
                    if not chunk:
                        break
                    self.send_chunk(chunk, index, crc16_func)
                    index += len(chunk)
                    self.progress_signal.emit(index)

                    # Wait for 0xFF acknowledgement
                    if not self.wait_for_ack():
                        print("Did not receive 0xFF acknowledgement.")
                        break

        except Exception as e:
            QMessageBox.warning(self, 'Error!', str(e), QMessageBox.Ok)
        finally:
            self.ser.close()
            self.data_signal.emit(bytearray("ok", 'utf-8'))

    def send_chunk(self, chunk, index, crc16_func):
        data = bytearray()
        if len(chunk) == 128:
            data += struct.pack('B', 0x02)
        else:
            data += struct.pack('B', 0x03)  # Assuming 0x03 is the last frame identifier
        data += struct.pack('>I', index)
        data += chunk
        data += struct.pack('>H', crc16_func(data))
        self.ser.write(data)
        print(f"Sent data: {data.hex()}")

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
    new_data_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(serial.Serial)

    def __init__(self, serial_port, baud_rate):
        super().__init__()
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.stop_event = threading.Event()

    def close_serial(self):
        if self.ser is not None:
            self.stop_event.set()
            self.ser.close()

    def run(self):
        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate)
            if self.ser.is_open:
                print("串口已成功打开。")
                self.ser.flushInput()
            else:
                print("串口打开失败。")
                return

            while not self.stop_event.is_set():
                if self.ser.in_waiting > 0:
                    data = self.ser.read(self.ser.in_waiting).decode('utf-8').strip()
                    print(f"Received data: {data}")
                    self.new_data_signal.emit(data)

        except serial.SerialException as e:
            print(f"串口打开时发生错误: {e}")
        finally:
            if self.ser:
                self.ser.close()
                self.finished_signal.emit(self.ser)

# Usage example:
# bin_file_reader = BinFileReader('path/to/file.bin', 'COM3', 115200)
# bin_file_reader.start()