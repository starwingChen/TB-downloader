import sys
import re
from PyQt5.QtWidgets import (QWidget, QPushButton, QApplication, QFileDialog,
                             QLabel, QLineEdit, QGridLayout, QRadioButton, QMessageBox)
from PyQt5 import QtCore
from PyQt5.QtGui import QPainter, QPixmap, QIcon
from TBSpider import TBSpider


class UI(QWidget):
    def __init__(self):
        # 引用父类__init__函数
        super().__init__()
        self.Init_UI()

    def Init_UI(self):
        # 设置窗口大小及名称
        self.resize(800, 300)
        self.setWindowTitle('贴吧高清图下载器')
        self.setWindowIcon(QIcon('./icon.ico'))

        '''添加各类组件组件'''

        self.urlLabel = QLabel('帖子地址:')
        # 设置组件对齐方式
        self.urlLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.url = QLineEdit('')
        # 为输入框设置占位字段
        self.url.setPlaceholderText('必填，如：https://tieba.baidu.com/p/6203103182')
        self.only = QRadioButton('仅限楼主')
        self.rate = QLabel('下载进度：0/0')

        self.pathLabel = QLabel('存储位置:')
        self.pathLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.path = QLineEdit('')
        self.path.setPlaceholderText('必填，如：C:/Users/Desktop')

        self.browseAct = QPushButton('浏览')
        # 绑定事件
        self.browseAct.clicked.connect(self.browse)

        self.nameLabel = QLabel('图片名称:')
        self.nameLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.name = QLineEdit('')
        self.name.setPlaceholderText('选填，若有多张将以 名称_序号 命名')

        self.startAct = QPushButton('开始下载')
        self.startAct.clicked.connect(self.start)
        self.hint = QLabel('GitHub主页：https://github.com/starwingChen')
        self.hint.setStyleSheet('color:red;')

        # 使用空label控件充当占位
        holder1 = QLabel('')
        holder2 = QLabel('')
        holder3 = QLabel('')

        # 使用网格布局
        grid = QGridLayout()
        # 设置控件间间距
        grid.setSpacing(10)

        '''将控件添加进布局中，并进行渲染'''

        grid.addWidget(holder1, 0, 0)
        grid.addWidget(holder3, 0, 4)
        grid.addWidget(holder2, 8, 0)

        # 帖子相关
        grid.addWidget(self.urlLabel, 1, 0)  # 添加至第1行第0列
        grid.addWidget(self.url, 1, 1, 1, 3)  # 添加至第1行第1列，并跨1行3列
        grid.addWidget(self.only, 2, 1)

        # 存储相关
        grid.addWidget(self.nameLabel, 4, 0)
        grid.addWidget(self.name, 4, 1, 1, 3)
        grid.addWidget(self.pathLabel, 5, 0)
        grid.addWidget(self.path, 5, 1, 1, 3)
        grid.addWidget(self.browseAct, 6, 3)

        # 其他组件
        grid.addWidget(self.rate, 6, 1)
        grid.addWidget(self.startAct, 7, 1, 1, 3)
        grid.addWidget(self.hint, 9, 0, 1, 2)
        self.setLayout(grid)

    # 重载背景绘制事件的函数，设置背景图片
    def paintEvent(self, event):
        painter = QPainter(self)
        # 将图片平铺到整个窗口，大小随着窗口改变而改变
        pixmap = QPixmap("./bg.png")
        # 绘制背景
        painter.drawPixmap(self.rect(), pixmap)

    def browse(self):
        # 保存目录
        directory = QFileDialog.getExistingDirectory(self, '选取文件夹', 'C:/')
        self.path.setText(directory)

    def start(self):
        # 规范化输入的url
        url = re.match(r'.+/p/\d+', self.url.text()).group(0)
        if url[:5] != 'https':
            url = 'https://' + url
        # 判断“仅限楼主”按钮是否被选中
        if self.only.isChecked():
            url += '?see_lz=1'
        # 实例化TBSpider对象
        tb = TBSpider(url, self.path.text())
        # 获取图片url列表
        piclis = tb.get_source()
        # 无法获取网址时，弹出提示
        if not piclis:
            QMessageBox.information(self, '错误', '网页获取异常，请在良好的网络环境下输入正确的网址')
        else:
            count, length = 0, len(piclis)
            # 在图片列表中循环，逐张下载图片
            for pic in piclis:
                if self.name.text():
                    name = self.name.text() + f'_{count + 1}.{pic[-3:]}'
                else:
                    name = pic
                # 通过download的返回值判断是否正确下载，并显示下载进度
                if tb.download(pic, name):
                    count += 1
                    self.rate.setText(f'下载进度：{count}/{length}')
                # 存储路径非法时弹出提示
                else:
                    QMessageBox.information(self, '错误', '请输入正确的存储路径')
                    return
                # 刷新界面，显示进度
                QApplication.processEvents()
            # 下载成功后弹出提示
            QMessageBox.information(self, '下载完成', f'成功 {count} 个 失败 {length - count} 个')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = UI()
    ex.show()
    app.exit(app.exec_())
