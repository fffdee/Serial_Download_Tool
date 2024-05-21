import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton, QComboBox
from PyQt5.QtCore import QThread, pyqtSignal, QObject
import serial

class SerialThread(QThread):
    new_data_signal = pyqtSignal(str)  # 定义一个信号，用于传输接收到的数据

    def __init__(self, serial_port, baud_rate):
        super().__init__()
        self.serial_port = serial_port
        self.baud_rate = baud_rate

    def run(self):
        # 创建串口对象
        self.serial = serial.Serial(self.serial_port, self.baud_rate)
        self.serial.flushInput()
        while True:
            # 这里只是模拟接收数据的过程
            data = self.serial.readline().decode('utf-8').strip()
            self.new_data_signal.emit(data)  # 发射信号，传递接收到的数据

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle('串口接收线程示例')
        self.setGeometry(100, 100, 400, 300)

        # 创建一个垂直布局
        layout = QVBoxLayout()

        # 创建一个文本编辑框
        self.textEdit = QTextEdit()
        layout.addWidget(self.textEdit)

        # 创建一个串口端口选择下拉框
  
        self.serial_port_combo = QComboBox()
    
        self.serial_port_combo.currentIndexChanged.connect(self.serial_port_changed)
        layout.addWidget(self.serial_port_combo)

        # 创建一个波特率选择下拉框
        self.baud_rate_combo = QComboBox()
        self.baud_rate_combo.addItems(['9600', '19200', '38400', '57600', '115200'])  # 添加可用的波特率选项
        layout.addWidget(self.baud_rate_combo)

        # 创建一个按钮，用于启动串口接收线程
        self.startButton = QPushButton('启动接收线程')
        self.startButton.clicked.connect(self.startThread)
        layout.addWidget(self.startButton)

        # 创建一个中心窗口并设置布局
        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        # 配置串口参数
        self.serial_port = 'COM51'  # 默认串口
        self.baud_rate = 115200  # 默认波特率

        # 创建串口接收线程
        self.serial_thread = SerialThread(self.serial_port, self.baud_rate)
        self.serial_thread.new_data_signal.connect(self.appendText)  # 连接信号和槽函数

    def serial_port_changed(self, index):
        # 当串口选择变化时，更新文本编辑框
        self.selected_port = self.serial_ports[index].portName()
        print(f"选中的串口：{self.selected_port}")
       
    def startThread(self):
        # 获取新的串口和波特率设置
        self.serial_port = self.serial_port_combo.currentText()
        self.baud_rate = int(self.baud_rate_combo.currentText())

        # 停止当前的线程（如果正在运行）
        if self.serial_thread.isRunning():
            self.stopThread()

        # 启动新的线程
        self.serial_thread.start()
        self.startButton.setText('停止接收线程')

    def stopThread(self):
        # 停止线程
        self.serial_thread.quit()  # 请求线程退出
        self.serial_thread.wait()  # 等待线程退出
        self.startButton.setText('启动接收线程')

    def appendText(self, text):
        self.textEdit.append(text)  # 将接收到的数据追加到文本编辑框

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())