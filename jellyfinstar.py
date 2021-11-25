import sys
import os
import xml.etree.cElementTree as ET
import time
from main import Ui_MainWindow
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QFileDialog, QMessageBox, QCompleter)
from PySide6.QtCore import (QStringListModel, QThread,)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(
            self.on_pushButton_clicked)  # 添加目录按钮
        self.ui.pushButton_2.clicked.connect(
            self.on_pushButton_2_clicked)  # 删除目录按钮
        self.ui.pushButton_3.clicked.connect(
            self.on_pushButton_3_clicked)  # 执行按钮
        aboutmeText = '欢迎使用大枣系列小工具'
        # 设置下面状态条内容
        self.ui.statusbar.setStyleSheet("QStatusBar::item{border: 1px}")
        self.msg = QLabel(aboutmeText)
        self.ui.statusbar.addPermanentWidget(self.msg)

        # 初始化目录列表
        self.slm = QStringListModel()
        dirList = ''
        # 判断目录列表文件是否存在
        if os.path.isfile('dirList.txt'):
            with open('dirList.txt', 'r', encoding='utf-8') as fs:
              # splitlines比readlines相比可以少读入一个\n
                dirList = fs.read().splitlines()
        self.slm.setStringList(dirList)
        self.ui.listView.setModel(self.slm)
        # 默认自动选中第一行，如果不设置，则没有选中效果，但实际上还是选中了，体验不好
        self.ui.listView.setCurrentIndex(self.slm.index(0))
        # 输入列表自动补全
        with open('gflist.txt', 'r', encoding='utf-8') as fs:
            starList = fs.read().splitlines()
        completer = QCompleter(starList)
        self.ui.lineEdit_2.setCompleter(completer)
        self.ui.lineEdit.setCompleter(completer)

    def on_pushButton_clicked(self):
        dirName_choose = QFileDialog.getExistingDirectory(
            self, "选取文件夹", "")
        if dirName_choose:
            self.slm.insertRow(0)
            self.slm.setData(self.slm.index(0), dirName_choose)
            self.saveDirList()

    def on_pushButton_2_clicked(self):
        index = self.ui.listView.currentIndex()
        self.slm.removeRow(index.row())
        self.saveDirList()

    def on_pushButton_3_clicked(self):
        start = time.perf_counter()
        dirs = self.slm.stringList()
        if str.strip(self.ui.lineEdit_2.text()) != '' and str.strip(self.ui.lineEdit.text()) != '':
            oldstar = self.ui.lineEdit_2.text()
            newstar = self.ui.lineEdit.text()
            aboutmeText = '开始更新影星姓名'
            self.msg.setText(aboutmeText)
            for baseDir in dirs:
                works = chgWork(baseDir, oldstar, newstar)
                works.start()
                works.wait()
            end = time.perf_counter()
            #print('Running time: %s Seconds' % (end-start))
            aboutmeText = '更新结束 共用时 %s 秒' % format((end-start), '.3f')
            self.msg.setText(aboutmeText)

        else:
            QMessageBox.warning(self, "你有压力", "得先输入新旧影星名字")

    def saveDirList(self):
        with open('dirList.txt', 'w', encoding='utf-8') as f:
            for index in range(self.slm.rowCount()):
                f.write(self.slm.data(self.slm.index(index)) + '\n')


class chgWork(QThread):
    def __init__(self, dirPath, oldStar, newStar):
        super(chgWork, self).__init__()
        self.dirPath = dirPath
        self.oldStar = oldStar
        self.newStar = newStar

    def run(self):
        changeStarName(self.dirPath, self.oldStar, self.newStar)


def changeStarName(dirPath, oldStar, newStar):
    res = walkFile(dirPath)
    oldstar = oldStar
    newstar = newStar
    for nfo in res:
        tree = ET.ElementTree(file=nfo)
        root = tree.getroot()
        nfores = root.findall('./actor/name')
        for n in nfores:
            if n.text == oldstar:
                print(nfo+' '+n.text)
                n.text = newstar
                print(n.text)

# 遍历文件夹


def walkFile(file):
    fullFilePath = []
    for root, dirs, files in os.walk(file):
        # 遍历文件
        for f in files:
            if f.endswith('.nfo'):
                sourceFileName = os.path.abspath(root)+'/'+f
                sourceFileName = sourceFileName.replace('\\', '/')
                fullFilePath.append(sourceFileName)
    return fullFilePath


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()

    window.show()
    sys.exit(app.exec())
