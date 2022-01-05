import sys
import os
import xml.etree.cElementTree as ET
import time
from pathlib import Path
from main import Ui_MainWindow
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QFileDialog, QMessageBox, QCompleter)
from PySide6.QtCore import (QObject, QStringListModel, QThread, Signal)
# import pysnooper


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
        self.ui.statusbar.size
        self.ui.statusbar.setStyleSheet("QStatusBar::item{border: 1px}")
        self.msg = QLabel(aboutmeText)
        self.msg.setScaledContents(True)
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
        dirs = self.slm.stringList()
        self.threadCount = len(dirs)
        self.totalRuntime = float(0)
        self.start = time.time()
        if str.strip(self.ui.lineEdit_2.text()) != '' and str.strip(self.ui.lineEdit.text()) != '':
            oldstar = self.ui.lineEdit_2.text()
            newstar = self.ui.lineEdit.text()
            aboutmeText = '开始更新影星姓名'
            self.msg.setText(aboutmeText)
            self.ui.pushButton_3.setEnabled(False)
            for baseDir in dirs:
                self.works = chgWork(baseDir, oldstar, newstar)
                self.worksThread = QThread(self)
                self.works.moveToThread(self.worksThread)
                self.works.fin.connect(self.finish)
                self.worksThread.started.connect(self.works.do)
                self.worksThread.start()
                # 不知为何，如果此处不暂停一下再新建线程，会莫名其妙的有线程不能被建立
                time.sleep(0.1)
                self.worksThread.exit(0)
                QApplication.processEvents()
        else:
            QMessageBox.warning(self, "你有压力", "得先输入新旧影星名字")

    def finish(self, s):
        self.totalRuntime += s['time']
        self.threadCount -= 1
        aboutmeText = s['dirPath'] + ' 完成'
        self.msg.setText(aboutmeText)
        QApplication.processEvents()
        if self.threadCount == 0:
            self.ui.pushButton_3.setEnabled(True)
            aboutmeText = '更新结束 共用时 %s 秒' % format(self.totalRuntime, '.2f')
            self.msg.setText(aboutmeText)

    def saveDirList(self):
        with open('dirList.txt', 'w', encoding='utf-8') as f:
            for index in range(self.slm.rowCount()):
                f.write(self.slm.data(self.slm.index(index)) + '\n')


class chgWork(QObject):
    fin = Signal(dict)

    def __init__(self, dirPath, oldStar, newStar):
        super(chgWork, self).__init__()
        self.dirPath = dirPath
        self.oldStar = oldStar
        self.newStar = newStar

    def do(self):
        start = time.time()
        changeStarName(self.dirPath, self.oldStar, self.newStar)
        end = time.time()
        res = {'dirPath': self.dirPath,
               'time': end-start}
        self.fin.emit(res)


# @pysnooper.snoop()
def changeStarName(dirPath, oldStar, newStar):
    res = walkFile(dirPath)
    oldstar = oldStar
    newstar = newStar
    for nfo in res:
        tree = ET.ElementTree(file=nfo.absolute())
        root = tree.getroot()
        nfores = root.findall('./actor/name')
        for n in nfores:
            if n.text == oldstar:
                n.text = newstar
                tree.write(nfo.absolute(), encoding="utf-8",
                           xml_declaration=True)

# 遍历文件夹


def walkFile(file):
    rootdir = Path(file)
    return list(rootdir.glob('**/*.nfo'))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()

    window.show()
    sys.exit(app.exec())
