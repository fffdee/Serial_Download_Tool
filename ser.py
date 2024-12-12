import sys
import serial
import struct
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel

class SerialSender(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.ser = None

    def initUI(self):
        self.setWindowTitle('Serial Sender')
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        # 创建文本输入框
        self.inputLineEdit = QLineEdit(self)
        layout.addWidget(self.inputLineEdit)

        # 创建标签显示状态
        self.statusLabel = QLabel('Status: Not connected', self)
        layout.addWidget(self.statusLabel)

        # 创建按钮
        self.connectButton = QPushButton('Connect', self)
        self.connectButton.clicked.connect(self.connectSerial)
        layout.addWidget(self.connectButton)

        self.sendButton = QPushButton('Send', self)
        self.sendButton.clicked.connect(self.sendData)
        layout.addWidget(self.sendButton)

        self.setLayout(layout)

    def connectSerial(self):
        try:
            # 连接到串口，需要根据实际情况修改端口和波特率
            self.ser = serial.Serial('COM34', 31250, timeout=1)
            self.statusLabel.setText('Status: Connected')
        except serial.SerialException as e:
            self.statusLabel.setText(f'Status: {e}')

    def sendData(self):
        if self.ser and self.ser.is_open:
            # 获取用户输入的数据
            data = self.inputLineEdit.text()
            try:
                # 将输入的数据转换为整数
                num = int(data)
                # 使用struct打包数据，这里假设我们发送一个整数
                packed_data = struct.pack('>I', num)
                # 发送数据
                self.ser.write(packed_data)
                self.statusLabel.setText(f'Status: Data sent')
            except ValueError:
                self.statusLabel.setText('Status: Invalid input')
        else:
            self.statusLabel.setText('Status: Not connected')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    sender = SerialSender()
    sender.show()
    sys.exit(app.exec_())
