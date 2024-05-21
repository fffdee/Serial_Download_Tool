import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QFileDialog,QHBoxLayout,QWidget,QVBoxLayout,QComboBox,QLabel,QTextEdit,QProgressBar
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtGui import QPixmap,QIcon
from PyQt5.QtCore import Qt,QThread,pyqtSignal
import serial



class SerialThread(QThread):
    new_data_signal = pyqtSignal(str)  # 定义一个信号，用于传输接收到的数据
    def __init__(self, serial_port, baud_rate):
        super().__init__()
        self.serial_port = serial_port
        self.baud_rate = baud_rate
    def run(self):
        # 串口接收数据的代码将被放在这里
        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate)
            if self.ser.is_open:
             print("串口已成功打开。")
            else:
             print("串口打开失败。")
            return
        except serial.SerialException as e:
            print(f"串口打开时发生错误: {e}")
        
        self.ser.flushInput()
       # self.ser.write(B"helloWorld!\n")
        while True:
            # 这里只是模拟接收数据的过程
            if self.ser.in_waiting > 0:
                # 如果有数据可读，读取数据
                data = self.ser.read(self.ser.in_waiting).decode('utf-8').strip()  # 读取所有可读数据
                print(f"Received data: {data}")
                self.new_data_signal.emit(data)  # 发射信号，传递接收到的数据
            # data = self.ser.readline().decode('utf-8').strip()
            
           # print("n")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.update_serial_ports()
        
    def initUI(self):
        # 创建一个按钮
        self.button = QPushButton("选择文件", self)
        self.button.setFixedWidth(100)
        self.button.setFixedHeight(40)
        self.button.setStyleSheet(("QPushButton { background-color: #111111; color: white; }"
                     "QPushButton:hover { background-color: #FFFFFF;color: black; }"
                     "QPushButton:pressed { background-color: #00FF00; }"))
        self.button.clicked.connect(self.select_file)
        self.all = QVBoxLayout()
        
        self.label = QLabel(self)
        pixmap = QPixmap('BanGO.png') 
        scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label.setPixmap(scaled_pixmap)
        self.baud_rate = 115200
       # self.setStyleSheet("QVBoxLayout { background-color:#FF5733; }")
        # 创建一个文本编辑框
        self.file_path_edit = QLineEdit(self)
        self.file_path_edit.setStyleSheet(" QLineEdit { background-color: #FFFFFF ;color: #111111; }")
        self.file_path_edit.setFixedHeight(40)
        self.file_path_edit.setReadOnly(True)
        
    
        # 创建一个文本
        self.COMText = QLabel(self)
        self.COMText.setStyleSheet("QLabel { color: #000; font-size: 20px; }")
        self.COMText.setText("选择串口:")
        
        self.openCOM = QPushButton("打开串口", self)
        self.openCOM.setCheckable(True)
        self.openCOM.setChecked(False)
        self.openCOM.setFixedWidth(100)
        self.openCOM.setFixedHeight(40)
        self.openCOM.setStyleSheet(("QPushButton { background-color: #111111; color: white; }"
                     "QPushButton:hover { background-color: #FFFFFF;color: black; }"
                     "QPushButton:pressed { background-color: #00FF00; }"))
        self.openCOM.toggled.connect(self.switch_changed)
        
         # 创建一个可用串口选择器
        self.serial_port_combobox = QComboBox(self)
        self.serial_port_combobox.setFixedWidth(100)
        self.serial_port_combobox.setFixedHeight(40)
        self.serial_port_combobox.setStyleSheet("QComboBox { background-color: #EEEEEE; color: #000; font-size: 20px; }")
        self.serial_port_combobox.currentIndexChanged.connect(self.serial_port_changed)

        self.baudRateLabel = QLabel('波特率:')
        self.baudRateLabel.setStyleSheet("QLabel { color: #000; font-size: 20px; }")
        self.baudRateComboBox = QComboBox()
        self.baudRateComboBox.addItems(['312500','9600', '19200', '38400', '57600', '115200' ])
       
        self.baudRateComboBox.setFixedWidth(100)
        self.baudRateComboBox.setFixedHeight(40)
        self.baudRateComboBox.setStyleSheet("QComboBox { background-color: #EEEEEE; color: #000; font-size: 20px; }")
        self.dataBitsLabel = QLabel('数据位: 8')
        self.dataBitsLabel.setStyleSheet("QLabel { color: #000; font-size: 20px; }")
        self.parityLabel = QLabel('校验位: None')
        self.parityLabel.setStyleSheet("QLabel { color: #000; font-size: 20px; }")
        self.stopBitsLabel = QLabel('停止位: 1')
        self.stopBitsLabel.setStyleSheet("QLabel { color: #000; font-size: 20px; }")

        self.debugLabel = QLabel('DebugView:')
        self.debugLabel.setStyleSheet("QLabel { color: #000; font-size: 20px; }")
        self.debugText = QTextEdit(self)
        self.debugText.setStyleSheet("QTextEdit { color: #000; font-size: 14px; }")

        self.progressBar = QProgressBar(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)

        self.DOWNLOAD = QPushButton("开始下载", self)
        self.DOWNLOAD.setCheckable(True)
        self.DOWNLOAD.setChecked(False)
        self.DOWNLOAD.setFixedWidth(100)
        self.DOWNLOAD.setFixedHeight(40)
        self.DOWNLOAD.setStyleSheet(("QPushButton { background-color: #111111; color: white; }"
                     "QPushButton:hover { background-color: #FFFFFF;color: black; }"
                     "QPushButton:pressed { background-color: #00FF00; }"))
        self.DOWNLOAD.toggled.connect(self.Download_changed)

        # self.selected_port = 'COM51'
        # self.baud_rate = 9600
        # self.serial_thread = SerialThread(self.selected_port,self.baud_rate)
        # self.serial_thread.new_data_signal.connect(self.appendText)  # 连接信号和槽函数
        
     #----------------------------------------------------------LAYOUT----------------------------------------------------  
        self.layout0 = QHBoxLayout()
        self.layout0.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.layout0.setSpacing(20)
        self.layout0.addWidget(self.label)
        self.layout0.setContentsMargins(20, 00, 20, 0)
         # 设置布局
        self.layout1 = QHBoxLayout()
        self.layout1.setSpacing(20)
        self.layout1.addWidget(self.file_path_edit)
        self.layout1.addWidget(self.button)
        self.layout1.setContentsMargins(20, 00, 20, 0)

        self.layout2 = QHBoxLayout()
        self.layout2.setSpacing(20)
        self.layout2.addWidget(self.COMText)
        self.layout2.addWidget(self.openCOM)
        self.layout2.addWidget(self.serial_port_combobox)
        self.layout2.setContentsMargins(20, 0, 20, 0)

        self.layout3 = QHBoxLayout()
        self.layout3.setSpacing(20)
        self.layout3.addWidget(self.baudRateLabel)
        self.layout3.addWidget(self.baudRateComboBox)
        self.layout3.addWidget(self.dataBitsLabel)
        self.layout3.addWidget(self.parityLabel)
        self.layout3.addWidget(self.stopBitsLabel)
        self.layout3.setContentsMargins(20, 0, 20, 0)

        self.layout4 = QVBoxLayout()
        self.layout4.setSpacing(20)
        self.layout4.addWidget(self.debugLabel)
        self.layout4.addWidget(self.debugText) 
        self.layout4.setContentsMargins(20, 0, 20, 0)

        self.layout5 = QHBoxLayout()
        self.layout5.setSpacing(10)
        self.layout5.addWidget(self.progressBar)
        self.layout5.addWidget(self.DOWNLOAD)
        self.layout5.setContentsMargins(20, 0, 20, 0)

        # 总布局
        self.all.addLayout(self.layout0)
        self.all.addLayout(self.layout1)
        self.all.addLayout(self.layout2)
        self.all.addLayout(self.layout3)
        self.all.addLayout(self.layout4)
        self.all.addLayout(self.layout5)
       
        
        # 设置中心窗口
        central_widget = QWidget()
        central_widget.setLayout(self.all)
        central_widget.setStyleSheet("QWidget { background-color: white; }")
        self.setCentralWidget(central_widget)
        
        self.setGeometry(600, 600, 500, 480)
        self.setWindowTitle('SAM5704下载工具')
        self.setWindowIcon(QIcon('BanGO.png'))
        self.setStyleSheet("QMainWindow { font-size: 20px; }")

    #————————————————————————————————————————————————后端回调代码——————————————————————————————————————————————————————————————
    def update_serial_ports(self):
        # 清空串口列表
        self.serial_port_combobox.clear()
        # 获取系统中所有可用的串口
        self.serial_ports = QSerialPortInfo.availablePorts()
        # 将串口名称添加到下拉列表中
        for port in self.serial_ports:
            self.serial_port_combobox.addItem(port.portName())
 
    def serial_port_changed(self, index):
        # 当串口选择变化时，更新文本编辑框
        self.selected_port = self.serial_ports[index].portName()
        print(f"选中的串口：{self.selected_port}")
        self.debugText.append("选中的串口："+self.selected_port)
    
        
    def select_file(self):
        # 显示文件选择对话框
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "选取文件", "", "下载文件 (*.bin)", options=options)
        
        # 如果用户选择了文件
        if file_path:
            # 更新文本编辑框的内容
            self.file_path_edit.setText(file_path)
            self.debugText.append("读取的文件："+file_path)

    def switch_changed(self, state):
        if state == True:
            
            self.startThread()
           # self.debugText.append('打开串口：'+str(self.selected_port)+','+str(self.baud_rate))
            self.openCOM.setText("关闭串口")
        else:
            self.debugText.append('关闭串口')
            self.stopThread()
            self.openCOM.setText("打开串口")
         
    def Download_changed(self, state):
        if state == True:
            self.debugText.append("开始下载")
            self.DOWNLOAD.setText("取消下载")
        else:
            self.debugText.append('取消下载')
            self.DOWNLOAD.setText("开始下载")
    #  ————————————————————————————————————————————————串口接收线程系列函数——————————————————————————————————————————————————            
    def startThread(self):
        # 获取新的串口和波特率设置
        self.selected_port = self.serial_port_combobox.currentText()
        self.baud_rate = int(self.baudRateComboBox.currentText())
        self.serial_thread = SerialThread(self.selected_port,self.baud_rate)
        self.serial_thread.new_data_signal.connect(self.appendText)  # 连接信号和槽函数
        self.debugText.append('打开串口：'+str(self.selected_port)+','+str(self.baud_rate))
        # 停止当前的线程（如果正在运行）
        if self.serial_thread.isRunning():
            self.stopThread()
            print("有在运行")
        # 启动新的线程
        self.serial_thread.start()

       

    def stopThread(self):
       print("结束")
       try:
           self.serial_thread.ser.close()
       except serial.SerialException as e:
            print(f"串口打开时发生错误: {e}")
       
       self.serial_thread.quit()  # 请求线程退出
       try:
            self.serial_thread.wait()  # 等待线程退出
            print("结束")
       except Exception as e:
            print(f"等待线程退出时出现错误: {e}")

    def appendText(self, text):
        self.debugText.append(text)  # 将接收到的数据追加到文本编辑框
    # ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
