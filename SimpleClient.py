#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import sys
import xlrd
import socket
from PyQt4 import QtGui, QtCore

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    def update_figure(self):
        sock = socket.socket()
        sock.connect(('localhost', 45454))
        sock.send('RCV'.encode('utf-8'))
        data = [axis.split(',') for axis in sock.recv(1024).decode('utf-8').split(';')[:2]]
        points = [[float(data[i][j]) for j in range(10)] for i in range(2)]
        self.axes.plot(points[0], points[1], 'k.')
        self.draw()        
        aw.statusBar().showMessage("Data was successfully received!", 2000)
        sock.send('DSC'.encode('utf-8'))
        sock.close()

class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Simple Client")

        self.main_widget = QtGui.QWidget(self)

        l = QtGui.QVBoxLayout(self.main_widget)
        sc = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        sendfile = QtGui.QPushButton('Send File', self.main_widget)
        sendfile.clicked.connect(self.sendfileEvent)
        getdata = QtGui.QPushButton('Get Data', self.main_widget)
        getdata.clicked.connect(sc.update_figure)
        l.addWidget(sc)
        l.addWidget(sendfile)
        l.addWidget(getdata)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("Welcome!", 2000)

    def sendfileEvent(self):
        sock = socket.socket()
        sock.connect(('localhost', 45454))
        xlsfilename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', './')
        if xlsfilename:
            workbook = xlrd.open_workbook(xlsfilename)
        else:
            sock.send('DSC'.encode('utf-8'))
            sock.close()
            return
        worksheet = workbook.sheet_by_index(0)
        #data = array([[worksheet.cell(i, j).value for i in range(10)] for j in range(2)])
        data = 'SND'+''.join(','.join(str(worksheet.cell(i, j).value) for i in range(10))+';' for j in range(2))
        
        sock.send(data.encode('utf-8'))
        msg = sock.recv(1024).decode('utf-8')

        if msg == 'OK':
            sock.send('DSC'.encode('utf-8'))
            sock.close()
            self.statusBar().showMessage("Data was successfully uploaded!", 2000)

qApp = QtGui.QApplication(sys.argv)

aw = ApplicationWindow()
aw.show()
sys.exit(qApp.exec_())
