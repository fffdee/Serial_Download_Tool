import sys,os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox,QPushButton, QLineEdit, QFileDialog,QHBoxLayout,QWidget,QVBoxLayout,QComboBox,QLabel,QTextEdit,QProgressBar
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtGui import QPixmap,QIcon
from PyQt5.QtCore import Qt,QThread,pyqtSignal
import serial


from binfilereader import BinFileReader ,SerialThread

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

        # 创建一个文本编辑框
        self.file_path_edit = QLineEdit(self)
        self.file_path_edit.setStyleSheet(" QLineEdit { background-color: #FFFFFF ;color: #111111; }")
        self.file_path_edit.setFixedHeight(40)
        self.file_path_edit.setReadOnly(True)
        self.file_path = None
    
        # 创建一个文本
        self.COMText = QLabel(self)
        self.COMText.setStyleSheet("QLabel { color: #000; font-size: 20px; }")
        self.COMText.setText("选择串口:")
        
    
        
         # 创建一个可用串口选择器
        self.serial_port_combobox = QComboBox(self)
        self.serial_port_combobox.setFixedWidth(100)
        self.serial_port_combobox.setFixedHeight(40)
        self.serial_port_combobox.setStyleSheet("QComboBox { background-color: #EEEEEE; color: #000; font-size: 20px; }")
        self.serial_port_combobox.currentIndexChanged.connect(self.serial_port_changed)

        self.baudRateLabel = QLabel('下载模式:')
        self.baudRateLabel.setStyleSheet("QLabel { color: #000; font-size: 20px; }")
        self.baudRateComboBox = QComboBox()
        self.baudRateComboBox.setEditable(True)
        self.baudRateComboBox.addItems(['115200','MIDI','9600', '19200', '38400', '57600' ])
       
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
    

        self.sendText = QTextEdit(self)
        self.sendText.setStyleSheet("QTextEdit { color: #000; font-size: 14px; }")
        
       
        self.send = QPushButton("发送", self)
        self.send.setFixedWidth(100)
        self.send.setFixedHeight(40)
        self.send.setStyleSheet(("QPushButton { background-color: #111111; color: white; }"
                     "QPushButton:hover { background-color: #FFFFFF;color: black; }"
                     "QPushButton:pressed { background-color: #00FF00; }"))
        self.send.clicked.connect(self.senddata)

        self.clean = QPushButton("清空", self)
        self.clean.setFixedWidth(100)
        self.clean.setFixedHeight(40)
        self.clean.setStyleSheet(("QPushButton { background-color: #111111; color: white; }"
                     "QPushButton:hover { background-color: #FFFFFF;color: black; }"
                     "QPushButton:pressed { background-color: #00FF00; }"))
        self.clean.clicked.connect(self.cleandata)
        
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

        self.layout4 = QHBoxLayout()
        self.layout4.setSpacing(20)
        self.layout4.addWidget(self.debugLabel)
        self.layout4.setContentsMargins(20, 0, 20, 0)

        self.layout5 = QHBoxLayout()
        self.layout5.setSpacing(10)
        self.layout5.addWidget(self.debugText)
        self.layout5.setContentsMargins(20, 0, 20, 0)

        self.layouty = QHBoxLayout()
        self.layouty.setSpacing(10)
        self.layouty.addWidget(self.send)
        self.layouty.addWidget(self.clean)
        self.layouty.setContentsMargins(20, 0, 20, 0)


        self.layoutx = QVBoxLayout()
        self.layoutx.setSpacing(10)
        self.layoutx.addWidget(self.sendText)
        self.layoutx.addLayout(self.layouty)
        self.layoutx.setContentsMargins(20, 0, 20, 0)

      

        self.layout6 = QHBoxLayout()
        self.layout6.setSpacing(10)
        self.layout6.addWidget(self.progressBar)
        self.layout6.addWidget(self.DOWNLOAD)
        self.layout6.setContentsMargins(20, 0, 20, 0)

        # 总布局
        self.all.addLayout(self.layout0)
        self.all.addLayout(self.layout1)
        self.all.addLayout(self.layout2)
        self.all.addLayout(self.layout3)
        self.all.addLayout(self.layout4)
        self.all.addLayout(self.layout5)
        self.all.addLayout(self.layout6)

        # 设置中心窗口
        central_widget = QWidget()
        central_widget.setLayout(self.all)
        central_widget.setStyleSheet("QWidget { background-color: white; }")
        self.setCentralWidget(central_widget)
        
        self.setGeometry(600, 600, 500, 480)
        self.setWindowTitle('SAM5704调试工具')
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
            if port.portName()!= 'COM1':
                self.serial_port_combobox.addItem(port.portName())
 
    def serial_port_changed(self, index):
        # 当串口选择变化时，更新文本编辑框
        self.selected_port = self.serial_ports[index].portName()
       
    
        
    def select_file(self):
        # 显示文件选择对话框
        options = QFileDialog.Options()
        self.file_path, _ = QFileDialog.getOpenFileName(self, "选取文件", "", "下载文件 (*.bin *.bg)", options=options)
        
        # 如果用户选择了文件
        if  self.file_path != None:
            # 更新文本编辑框的内容
            self.file_path_edit.setText( self.file_path)
            self.debugText.append("读取的文件："+ self.file_path)
        


       
    def senddata(self):
        self.serial_thread.ser.write(self.sendText.toPlainText().encode('utf-8'))

    def cleandata(self):
        self.debugText.clear()

    def Download_changed(self, state):
        if state == True:
            self.debugText.append("开始下载")
            self.selected_port = self.serial_port_combobox.currentText()
            if self.baudRateComboBox.currentText()=="MIDI":
                self.baud_rate = 312500
            else :
                self.baud_rate = int(self.baudRateComboBox.currentText())
            self.debugText.append('打开串口：'+str(self.selected_port)+','+str(self.baud_rate))
            if self.file_path == None:
                QMessageBox.warning(self, 'warning!', "文件为空！！！", QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
                self.DOWNLOAD.setChecked(False)
                return
            else :
                self.bin_reader = BinFileReader(self.file_path,self.selected_port,self.baud_rate)
            self.filesize = 100
                
            self.bin_reader.progress_signal.connect(self.setprogress)  # 连接信号和槽函数
            self.bin_reader.data_signal.connect(self.displayData)  # 连接信号和槽函数
            self.bin_reader.filesize_signal.connect(self.getfilesize)  # 连接信号和槽函数
            self.bin_reader.start()
            self.DOWNLOAD.setText("取消下载")
        else:
       
            # self.debugText.append('取消下载')
            # self.stopThread()
            # self.bin_reader.stop()
            
            self.DOWNLOAD.setText("开始下载")
    #  ————————————————————————————————————————————————串口接收线程系列函数——————————————————————————————————————————————————            
    def startThread(self):
        # 获取新的串口和波特率设置
        self.selected_port = self.serial_port_combobox.currentText()
        if self.baudRateComboBox.currentText()=="MIDI":
            self.baud_rate = 312500
        else :
            self.baud_rate = int(self.baudRateComboBox.currentText())
        self.serial_thread = SerialThread(self.selected_port,self.baud_rate)
        
        self.serial_thread.new_data_signal.connect(self.appendText)  # 连接信号和槽函数
        
        self.debugText.append('打开串口：'+str(self.selected_port)+','+str(self.baud_rate))
        
        # 停止当前的线程（如果正在运行）
        if self.serial_thread.isRunning():
            
            self.stopThread()
            
        # 启动新的线程
        self.serial_thread.start()

    def serialThreadClosed(self):
        # 串口接收线程已关闭
        self.debugText.append("串口接收线程已关闭")  # 将接收到的数据追加到文本编辑框
        print("串口接收线程已关闭")

    def stopThread(self):
      
      self.serial_thread.ser.close()

      self.serial_thread.quit()  # 请求线程退出
      try:
        self.serial_thread.wait()  # 等待线程退出
        print("结束")
      except Exception as e:
        print(f"等待线程退出时出现错误: {e}")

    
    def appendText(self, text):
        self.debugText.append(text)  # 将接收到的数据追加到文本编辑框

    #————————————————————————————————---下载相关函数——————————————————————————————————————————————————


    def displayData(self, data):
        bytes_data = bytes(data)
        # 显示文件内容
        if bytes_data[-1] == 0x6B:
            QMessageBox.warning(self, 'wuhu~',"发送成功！", QMessageBox.Ok , QMessageBox.Ok)
            self.DOWNLOAD.setText("开始下载") 
            self.DOWNLOAD.setChecked(False)  
            # 将bytes对象转换为十六进制字符串
        hex_string = ' '.join(f'{b:02X}' for b in bytes_data)
        self.debugText.append(hex_string ) 
    def getfilesize(self, size):
        print("filesize:"+str(size))
        self.filesize = size
    def setprogress(self,index):
       # print(str(index))
        self.progressBar.setValue(int((index/self.filesize)*100))
        self.debugText.append('下载进度：'+str(int((index/self.filesize)*100))+'%')

    # ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    # def restartApp(self):
    #     # 关闭所有窗口
    #     self.close()

    #     # 创建一个新的QApplication实例
    #     new_app = QApplication(sys.argv)

    #     # 重新创建主窗口
    #     new_main_window = MainWindow()
    #     new_main_window.show()

    #     # 退出旧的应用程序实例
    #     sys.exit(new_app.exec_())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
