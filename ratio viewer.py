import os

import numpy as np
import matplotlib.pyplot as plt
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QSize, QPoint, QPointF, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage, QMouseEvent, QWheelEvent, QColor, QPen, QCursor
from PyQt6.QtWidgets import QMainWindow, QApplication, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QSizePolicy, \
    QTextBrowser, QGraphicsRectItem, QSlider, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QFileDialog, \
    QMessageBox, QRadioButton, QSpacerItem, QMenu
from PyQt6.QtCore import Qt

from qtgraph import init_3dplot
import pyqtgraph.opengl as gl


class Ui_ratio(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 720)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(1280, 720))
        MainWindow.setSizeIncrement(QtCore.QSize(0, 0))
        MainWindow.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMinimumSize(QtCore.QSize(1280, 720))
        self.centralwidget.setSizeIncrement(QtCore.QSize(0, 0))
        self.centralwidget.setMouseTracking(False)
        self.centralwidget.setObjectName("centralwidget")
        self.mainLayout = QGridLayout(self.centralwidget)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(1, 1, 1, 1)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))


class ImgGraphicsView(QGraphicsView):
    sigMouseMovePoint = pyqtSignal(QPoint)
    sigCal = pyqtSignal(np.ndarray)
    sigRangeCancel = pyqtSignal(int)
    sigSave = pyqtSignal(int)

    def __init__(self, parent=None, scrollbar_x=True, scrollbar_y=True, range_select=True):
        super(ImgGraphicsView, self).__init__(parent)
        self.dragStartPos = QPointF(0, 0)
        self.selectStartPos = QPointF(0, 0)
        self.selectCurrentPos = QPointF(0, 0)

        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn if scrollbar_x else Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn if scrollbar_y else Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        # self.setDragMode(QGraphicsView.DragMode.)

        self.range_select = range_select
        if self.range_select:
            self.selectPlot = QGraphicsRectItem()
            pen = QPen()
            color = QColor()
            color.setNamedColor('red')
            pen.setColor(color)
            pen.setWidth(1)
            pen.setStyle(Qt.PenStyle.SolidLine)
            self.selectPlot.setPen(pen)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragStartPos = event.pos()
            menu = QMenu()
            action = menu.addAction('save')
            action.triggered.connect(self.save_action)
            menu.exec(QCursor.pos())
        elif event.button() == Qt.MouseButton.RightButton:
            if self.range_select:# and event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                self.selectStartPos = self.mapToScene(event.pos())
                self.selectCurrentPos = self.mapToScene(event.pos())
                self.selectPlot.setRect(self.selectStartPos.x(), self.selectStartPos.y(), 0, 0)
                self.scene().addItem(self.selectPlot)
            else:
                # delta = self.selectStartPos - self.selectCurrentPos
                # if delta.y() == 0 and delta.x() == 0:
                #     return
                pass
        return

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            pass
        elif event.button() == Qt.MouseButton.RightButton:
            pass
        return

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            pass
        if event.button() == Qt.MouseButton.RightButton:
            if self.range_select:
                #if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                delta = self.selectStartPos - self.selectCurrentPos
                if delta.y() == 0 and delta.x() == 0:
                    self.sigRangeCancel.emit(0)
                    self.selectStartPos = QPointF(0, 0)
                    self.selectCurrentPos = QPointF(0, 0)
                    self.scene().removeItem(self.selectPlot)
                self.sigCal.emit(np.array([self.selectStartPos.y(), self.selectCurrentPos.y(),
                                            self.selectStartPos.x(), self.selectCurrentPos.x()]).astype(int))
        return

    def mouseMoveEvent(self, event):
        mpt = event.pos()
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            return
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = mpt - self.dragStartPos
            self.dragStartPos = mpt

            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
        elif event.buttons() == Qt.MouseButton.RightButton:
            if self.range_select:
                #if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                    delta = self.mapToScene(mpt) - self.selectStartPos
                    self.selectCurrentPos = self.mapToScene(mpt)
                    self.selectPlot.setRect(self.selectStartPos.x(), self.selectStartPos.y(), delta.x(), delta.y())

        self.sigMouseMovePoint.emit(mpt)
        return

    def save_action(self):
        self.sigSave.emit(0)


class MainWindow(QMainWindow, Ui_ratio):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("triRatio")
        self.mainLayout.setRowStretch(0, 1)
        self.mainLayout.setRowStretch(1, 1)
        self.mainLayout.setRowStretch(2, 1)
        self.mainLayout.setRowStretch(3, 1)
        self.mainLayout.setRowStretch(4, 1)
        self.mainLayout.setRowStretch(5, 1)
        self.mainLayout.setColumnStretch(0, 2)
        self.mainLayout.setColumnStretch(1, 1)
        self.mainLayout.setColumnStretch(2, 1)

        self.select = np.zeros(4)
        self.mean_ratio = np.zeros(3)

        # f_co =r'D:\data\H054_Co_1x1_0x0_zoom-0.dat'
        # f_fe =r'D:\data\H054_Fe_1x1_0x0_zoom-0.dat'
        # f_mn =r'D:\data\H054_Mn_1x1_0x0_zoom-0.dat'
        self.co = np.array([])
        self.fe = np.array([])
        self.mn = np.array([])
        self.imgarray = np.array([])
        self.darray = np.array([])
        self.darray_r = np.array([])
        self.point_list = []
        self.r_distri = np.array([])
        self.point = np.array([])
        self.rmap = np.array([])
        azi = np.arange(91) / 180 * np.pi  # y
        ele = np.arange(91) / 180 * np.pi  # x
        self.ratio_co = np.sin(ele[None, :]) * np.cos(azi[:, None])
        self.ratio_fe = np.sin(ele[None, :]) * np.sin(azi[:, None])
        self.ratio_mn = np.cos(ele)

        # r distribution
        self.rView = ImgGraphicsView(scrollbar_x=False, scrollbar_y=False)
        self.rView.setObjectName('rView')
        self.mainLayout.addWidget(self.rView, 1, 1, 2, 2)
        self.pixitem_r = QGraphicsPixmapItem()
        self.scene_r = QGraphicsScene()
        self.x_r, self.y_r = 0, 0
        self.mouse_xy_r = QPoint(0, 0)
        self.rView.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.pic_r = QPixmap()
        self.rView.sigSave.connect(self.imgSaveEvent)

        # 3d
        self.g3d = gl.GLViewWidget()
        self.mainLayout.addWidget(self.g3d, 1, 0, 2, 1)
        self.scatter = gl.GLScatterPlotItem()

        # img
        self.imgView = ImgGraphicsView(scrollbar_x=False, scrollbar_y=False, range_select=False)
        self.imgView.setObjectName('imgView')
        self.mainLayout.addWidget(self.imgView, 3, 0, 2, 2)
        self.pixitem_img = QGraphicsPixmapItem()
        self.scene_img = QGraphicsScene()
        self.x_img, self.y_img = 0, 0
        self.mouse_xy_img = QPoint(0, 0)
        self.imgView.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.imgView.sigSave.connect(self.imgSaveEvent)

        self.img = np.array([])
        self.pic_img = QPixmap()
        self.currect_img = 0

        # browser
        self.textBrowser = QTextBrowser()
        self.mainLayout.addWidget(self.textBrowser, 3, 2, 2, 1)

        # slider
        self.sliderLayout = QHBoxLayout()
        self.sliderLayout.setObjectName("sliderLayout")
        self.mainLayout.addLayout(self.sliderLayout, 5, 1, 1, 2)
        self.sliderLabel = QLabel(parent=self.centralwidget)
        self.sliderLabel.setObjectName("sliderLabel")
        self.sliderLabel.setText(f"R filter [{0:>5}]  ")
        self.sliderLayout.addWidget(self.sliderLabel)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 10000)
        self.slider.setTickInterval(1000)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.valueChanged.connect(self.slicerChange)
        self.sliderLayout.addWidget(self.slider)
        self.slicePosi = 0

        # img select
        self.imgButtonLayout = QHBoxLayout()
        self.sliderLayout.setObjectName("imgButtonLayout")
        self.mainLayout.addLayout(self.imgButtonLayout, 5, 0, 1, 1)
        self.imgButtonLayout.addWidget(QLabel('image control: '))
        img_name = ['Sum ', 'Co ', 'Fe ', 'Mn ']
        self.imgButton = np.array([QRadioButton(img_name[i], parent=self.centralwidget) for i in range(4)], dtype=QRadioButton)
        self.imgButton[0].setChecked(True)
        for i in range(4):
            self.imgButton[i].setObjectName(img_name[i])
            self.imgButtonLayout.addWidget(self.imgButton[i])
            self.imgButton[i].setEnabled(False)
            self.imgButton[i].clicked.connect(self.img_select)
        spacer = QSpacerItem(40, 20, hPolicy=QSizePolicy.Policy.Expanding, vPolicy=QSizePolicy.Policy.Minimum)
        self.imgButtonLayout.addItem(spacer)

        # r map select
        self.imgButtonLayout.addWidget(QLabel('r map control: '))
        r_name = ['rmax ', 'points ', 'weight ']
        self.rButton = np.array([QRadioButton(r_name[i], parent=self.centralwidget) for i in range(3)],
                                  dtype=QRadioButton)
        self.rButton[0].setChecked(True)
        for i in range(3):
            self.rButton[i].setObjectName(r_name[i])
            self.imgButtonLayout.addWidget(self.rButton[i])
            self.rButton[i].setEnabled(False)
            self.rButton[i].clicked.connect(self.rmap_select)
        self.current_rmap = 0
        self.imgButtonLayout.addWidget(QLabel('   ||    '))

        # file reader
        self.fileLayout = QGridLayout()
        self.fileLayout.setObjectName("fileLayout")
        self.mainLayout.addLayout(self.fileLayout, 0, 0, 1, 3)
        self.file1Label = QLabel('Co ', parent=self.centralwidget)
        self.file2Label = QLabel('Fe ', parent=self.centralwidget)
        self.file3Label = QLabel('Mn ', parent=self.centralwidget)
        self.fileLayout.addWidget(self.file1Label, 0, 0, 1, 1)
        self.fileLayout.addWidget(self.file2Label, 1, 0, 1, 1)
        self.fileLayout.addWidget(self.file3Label, 2, 0, 1, 1)

        self.file1Button = QPushButton('...', parent=self.centralwidget)
        self.file2Button = QPushButton('...', parent=self.centralwidget)
        self.file3Button = QPushButton('...', parent=self.centralwidget)
        self.fileLayout.setObjectName("file1")
        self.fileLayout.setObjectName("file2")
        self.fileLayout.setObjectName("file3")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum,
                                           QtWidgets.QSizePolicy.Policy.Minimum)
        self.file1Button.setSizePolicy(sizePolicy)
        self.file2Button.setSizePolicy(sizePolicy)
        self.file3Button.setSizePolicy(sizePolicy)
        self.fileLayout.addWidget(self.file1Button, 0, 1, 1, 1)
        self.fileLayout.addWidget(self.file2Button, 1, 1, 1, 1)
        self.fileLayout.addWidget(self.file3Button, 2, 1, 1, 1)
        self.file1Button.clicked.connect(self.read_name)
        self.file2Button.clicked.connect(self.read_name)
        self.file3Button.clicked.connect(self.read_name)

        self.f_list = [r'D:\data\H017_Co_1x1_0x0-0-0.dat',
                       r'D:\data\H017_Fe_1x1_0x0-0-0.dat',
                       r'D:\data\H017_Mn_1x1_0x0-0-0.dat']
        self.fileLine = np.array([QLineEdit(self.f_list[i], parent=self.centralwidget) for i in range(3)])
        for i in range(3):
            self.fileLayout.addWidget(self.fileLine[i], i, 2, 1, 1)
            self.fileLine[i].setReadOnly(True)

        self.runButton = QPushButton('Run', parent=self.centralwidget)
        self.runButton.setSizePolicy(sizePolicy)
        self.fileLayout.addWidget(self.runButton, 2, 3, 1, 1)
        self.runButton.clicked.connect(self.load_dat)

    def read_name(self):
        file_dialog = QFileDialog(self, "select dat files...", "", "DAT Files (*.dat)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
        else:
            return
        if len(file_paths) > 1:
            name = ['Co', 'Fe', 'Mn']
            for i in range(len(name)):
                for j in file_paths:
                    if not j.find(name[i]) == -1:
                        self.f_list[i] = j
                        self.fileLine[i].setText(j)
        else:
            button = self.sender().objectName()
            for i in range(3):
                if button == f'file{i+1}':
                    self.f_list[i] = file_paths[0]
                    self.fileLine[i].setText(file_paths[0])

    def load_dat(self):
        with open(self.f_list[0], 'r') as f:
            while True:
                temp = f.readline()
                if not temp.find('X-NUM') == -1:
                    width = int(temp.split()[2])-1
                    height = int(f.readline().split()[2])-1
                    break
                if not temp:
                    break
        self.co = np.loadtxt(self.f_list[0], usecols=2, dtype=float, delimiter=',').reshape(height, width)
        print(self.co.max())
        self.co[self.co > 5000] = 0
        self.fe = np.loadtxt(self.f_list[1], usecols=2, dtype=float, delimiter=',')#.reshape(height, width)
        print(self.fe.max())
        if not self.fe.size == height * width:
            self.warning_window('Data array of Fe have different size')
        else:
            self.fe = self.fe.reshape(height, width)
        #self.fe[self.fe > 10000] = 0
        self.mn = np.loadtxt(self.f_list[2], usecols=2, dtype=float, delimiter=',')#.reshape(height, width)
        print(self.mn.max())
        if not self.mn.size == height * width:
            self.warning_window('Data array of Mn have different size')
        else:
            self.mn = self.mn.reshape(height, width)

        self.imgarray = self.co + self.fe + self.mn
        self.darray = np.vstack((self.co.flatten(), self.fe.flatten(), self.mn.flatten())).T
        self.analysis()
        self.rmap = self.r_distri

        # r distribution
        r_map = ((self.rmap - self.rmap.min()) / (self.rmap.max() - self.rmap.min()) * 255
                 ).astype(np.uint8)[:, :, None].repeat(3, 2)
        self.pic_r = QPixmap.fromImage(QImage(r_map.data, r_map.shape[1], r_map.shape[0], r_map.shape[1] * 3,
                                              QImage.Format.Format_RGB888))
        self.pixitem_r.setPixmap(self.pic_r)
        self.scene_r.addItem(self.pixitem_r)
        self.rView.setScene(self.scene_r)
        self.rView.fitInView(self.scene_r.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.rView.sigMouseMovePoint.connect(self.mouselocation_r)
        self.rView.sigCal.connect(self.updatePixmap)

        init_3dplot(self.g3d, grid=False, background=[0, 0, 0], alpha=1.0, view=50000, title='example',
                    size=[int(self.darray.max()), int(self.darray.max()), int(self.darray.max())])
        self.scatter = gl.GLScatterPlotItem(pos=self.darray, color=(1, 1, 1, 1), size=5)
        self.g3d.addItem(self.scatter)

        # img
        self.img0 = ((self.imgarray - self.imgarray.min()) / (self.imgarray.max() - self.imgarray.min()) * 255
                    ).astype(np.uint8)[:, :, None].repeat(3, 2)
        self.img = self.img0.copy()
        self.pic_img = QPixmap.fromImage(
            QImage(self.img.data, self.img.shape[1], self.img.shape[0], self.img.shape[1] * 3,
                   QImage.Format.Format_RGB888))
        self.pixitem_img.setPixmap(self.pic_img)
        self.scene_img.addItem(self.pixitem_img)
        self.imgView.setScene(self.scene_img)
        self.imgView.fitInView(self.scene_img.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.imgView.sigMouseMovePoint.connect(self.mouselocation_img)
        # scale = max((self.pic_img.width()) / (self.imgView.width() - 13),
        #             (self.pic_img.height()) / (self.imgView.height() - 13))
        #self.imgView.scale(scale, scale)

        self.slider.setRange(0, int(self.darray_r.max()))
        self.slider.setTickInterval(int(self.darray_r.max()) // 10)

        self.runButton.setEnabled(False)
        for i in range(4):
            self.imgButton[i].setEnabled(True)
        for i in range(3):
            self.rButton[i].setEnabled(True)

    def updatePixmap(self, select: np.ndarray):
        self.select = select
        if self.select[1] < self.select[0]:
            self.select[1], self.select[0] = self.select[0], self.select[1]
        if self.select[3] < self.select[2]:
            self.select[3], self.select[2] = self.select[2], self.select[3]
        self.select[1] = min(self.select[1], self.rmap.shape[0])
        self.select[3] = min(self.select[3], self.rmap.shape[1])

        self.img = self.img0.copy()
        if (self.select[1] + self.select[3] - self.select[0] - self.select[2]) > 0:
            target_index = np.array([], dtype=int)
            for i in np.arange(self.select[0], self.select[1]):
                for j in np.arange(self.select[2], self.select[3]):
                    temp = self.point_list[int(i*self.rmap.shape[0]+j)]
                    if not len(temp) == 0:
                        temp = temp[np.where(self.darray_r[temp] >= self.slicePosi)[0]]
                        target_index = np.append(target_index, temp)

            self.mean_ratio = self.darray[target_index].mean(0)
            self.mean_ratio /= self.mean_ratio.sum()

            color = np.zeros((self.darray.shape[0], 4)) + 1
            color.T[1][target_index] = 0
            color.T[2][target_index] = 0
            self.scatter.setData(color=color)

            target_index = np.unravel_index(target_index, self.co.shape)
            self.img.transpose(2, 0, 1)[0][target_index] = 255
            self.img.transpose(2, 0, 1)[1][target_index] = 0
            self.img.transpose(2, 0, 1)[2][target_index] = 0
        self.pic_img = QPixmap.fromImage(QImage(self.img.data, self.img.shape[1], self.img.shape[0],
                                                self.img.shape[1] * 3, QImage.Format.Format_RGB888))
        self.pixitem_img.setPixmap(self.pic_img)

    def img_select(self):
        name = self.sender().objectName()
        name_list = {'Sum ': 0, 'Co ': 1, 'Fe ': 2, 'Mn ': 3}
        target_img = name_list[name]
        if not self.currect_img == target_img:
            for i in range(4):
                if not i == target_img:
                    self.imgButton[i].setChecked(False)
            if target_img == 0:
                img = self.imgarray
            elif target_img == 1:
                img = self.co
            elif target_img == 2:
                img = self.fe
            else:
                img = self.mn
            self.img0 = ((img - img.min()) / (img.max() - img.min()) * 255
                         ).astype(np.uint8)[:, :, None].repeat(3, 2)
        self.currect_img = target_img
        self.updatePixmap(self.select)

    def rmap_select(self):
        name = self.sender().objectName()
        name_list = {'rmax ': 0, 'points ': 1, 'weight ': 2}
        target_rmap = name_list[name]
        if not self.current_rmap == target_rmap:
            for i in range(3):
                if not i == target_rmap:
                    self.imgButton[i].setChecked(False)
            if target_rmap == 0:
                self.rmap = self.r_distri
            elif target_rmap == 1:
                self.rmap = self.point
            else:
                self.rmap = self.r_distri * self.point
            r_map = ((self.rmap - self.rmap.min()) / (self.rmap.max() - self.rmap.min()) * 255
                         ).astype(np.uint8)[:, :, None].repeat(3, 2)
            self.pic_r = QPixmap.fromImage(QImage(r_map.data, r_map.shape[1], r_map.shape[0], r_map.shape[1] * 3,
                                                  QImage.Format.Format_RGB888))
            self.pixitem_r.setPixmap(self.pic_r)
        self.current_rmap = target_rmap

    def slicerChange(self, x):
        self.slicePosi = x
        self.sliderLabel.setText(f"R filter [{self.slicePosi:>5}]  ")
        if self.select.size > 0:
            self.updatePixmap(self.select)
            self.locationUpdate()

    def mouselocation_img(self, mpt):
        sc_xy = self.imgView.mapToScene(mpt.x(), mpt.y())
        self.mouse_xy_img = self.pixitem_img.mapFromScene(sc_xy).toPoint()
        if self.mouse_xy_img.y() >= self.pic_img.height():
            self.mouse_xy_img.setY(int(self.pic_img.height() - 1))
        elif self.mouse_xy_img.y() <= 0:
            self.mouse_xy_img.setY(0)
        else:
            pass
        if self.mouse_xy_img.x() >= self.pic_img.width():
            self.mouse_xy_img.setX(int(self.pic_img.width() - 1))
        elif self.mouse_xy_img.x() <= 0:
            self.mouse_xy_img.setX(0)
        else:
            pass
        self.x_img, self.y_img = self.mouse_xy_img.x(), self.mouse_xy_img.y()
        self.locationUpdate()

    def mouselocation_r(self, mpt):
        sc_xy = self.rView.mapToScene(mpt.x(), mpt.y())
        self.mouse_xy_r = self.pixitem_r.mapFromScene(sc_xy).toPoint()
        if self.mouse_xy_r.y() >= self.pic_r.height():
            self.mouse_xy_r.setY(int(self.pic_r.height() - 1))
        elif self.mouse_xy_r.y() <= 0:
            self.mouse_xy_r.setY(0)
        else:
            pass
        if self.mouse_xy_r.x() >= self.pic_r.width():
            self.mouse_xy_r.setX(int(self.pic_r.width() - 1))
        elif self.mouse_xy_r.x() <= 0:
            self.mouse_xy_r.setX(0)
        else:
            pass
        self.x_r, self.y_r = self.mouse_xy_r.x(), self.mouse_xy_r.y()
        self.locationUpdate()

    def locationUpdate(self):
        img_index = int(self.y_img*self.co.shape[0] + self.x_img)
        img_ratio = self.darray[img_index].astype(int)
        text = (f'img\nx:{self.x_img}  y:{self.y_img}\n'
                f'Pointed data:\n'
                f'Co:{img_ratio[0]}\n'
                f'Fe:{img_ratio[1]}\n'
                f'Mn:{img_ratio[2]}\n\n'
                f'sphere map\nx:{self.x_r}  y:{self.y_r}\n'
                f'Pointed ratio:\n'
                f'Co:{self.ratio_co[self.y_r][self.x_r]:.2f}\n'
                f'Fe:{self.ratio_fe[self.y_r][self.x_r]:.2f}\n'
                f'Mn:{self.ratio_mn[self.y_r]:.2f}\n\n'
                f'Area Average:\n'
                f'Co:{self.mean_ratio[0]:.2f}\n'
                f'Fe:{self.mean_ratio[1]:.2f}\n'
                f'Mn:{self.mean_ratio[2]:.2f}\n')
        self.textBrowser.setText(text)

    def analysis(self):
        self.darray_r = np.sqrt((self.darray ** 2).sum(1))
        darray_ele = np.zeros_like(self.darray_r)
        darray_ele[self.darray_r > 0] = np.arccos(
            self.darray[self.darray_r > 0, 2] / self.darray_r[self.darray_r > 0]) / np.pi * 180
        darray_azi = np.zeros_like(self.darray_r)
        darray_azi[(self.darray_r > 0) & (self.darray[:, 0] > 0)] = np.arctan(
            self.darray[(self.darray_r > 0) & (self.darray[:, 0] > 0), 1] / self.darray[
                (self.darray_r > 0) & (self.darray[:, 0] > 0), 0]) / np.pi * 180
        darray_map = np.unique(np.round(np.vstack((darray_azi, darray_ele)).T, 0).astype(int), axis=0,
                               return_inverse=True)
        self.r_distri = np.zeros((91, 91))
        self.point = np.zeros((91, 91))
        self.point_list = [np.array([]), ] * self.point.size
        for i in np.unique(darray_map[1]):
            locate = darray_map[0][i]
            self.r_distri[locate[0]][locate[1]] = self.darray_r[np.where(darray_map[1] == i)[0]].max()
            self.point_list[int(locate[0] * self.point.shape[0] + locate[1])] = np.where(darray_map[1] == i)[0]
            self.point[locate[0]][locate[1]] = np.where(darray_map[1] == i)[0].size
        self.point[0] = 0
        self.point[-1] = 0
        self.point[:, 0] = 0
        self.point[:, -1] = 0

    def imgSaveEvent(self, a0):
        if self.sender().objectName() == 'imgView':
            address = os.path.dirname(self.f_list[0]) + r'/image.png'
            name = QFileDialog.getSaveFileName(self, 'select save path...', address)[0]
            if name == '':
                return
            plt.imsave(name, self.img)
        else:
            address = os.path.dirname(self.f_list[0]) + r'/r distribution.png'
            name = QFileDialog.getSaveFileName(self, 'select save path...', address)[0]
            if name == '':
                return
            img = ((self.rmap - self.rmap.min()) / (
                    self.rmap.max() - self.rmap.min()) * 255
                   ).astype(np.uint8)[:, :, None].repeat(3, 2)
            if (self.select[1] + self.select[3] - self.select[0] - self.select[2]) > 0:
                red = np.array([255, 0, 0])
                img[self.select[0], self.select[2]:self.select[3]+1] = red
                img[self.select[1], self.select[2]:self.select[3]+1] = red
                img[self.select[0]:self.select[1]+1, self.select[2]] = red
                img[self.select[0]:self.select[1]+1, self.select[3]] = red
            plt.imsave(name, img)

    def warning_window(self, massage):
        QMessageBox.critical(self, 'Error', massage)



# rdf = np.unique(co//100*100, return_counts=True)
# plt.bar(rdf[0]-25, rdf[1], width=50)
# rdf = np.unique(fe//100*100, return_counts=True)
# plt.bar(rdf[0], rdf[1], width=50)
# rdf = np.unique(mn//100*100, return_counts=True)
# plt.bar(rdf[0]+25, rdf[1], width=50)
# plt.subplot(311)
# plt.scatter(co, fe)
# plt.xlabel('Co')
# plt.ylabel('Fe')
# plt.subplot(312)
# plt.scatter(fe, mn)
# plt.xlabel('Fe')
# plt.ylabel('Mn')
# plt.subplot(313)
# plt.scatter(mn, co)
# plt.xlabel('Mn')
# plt.ylabel('Co')
if __name__ == '__main__':
    from sys import argv, exit
    #file = r'D:\data\H017_Co_1x1_0x0-0-0.dat'
    # file = r'D:\data\H054_Co_1x1_0x0_zoom-0.dat'
    # f_co = r'D:\data\H054_Co_1x1_0x0_zoom-0.dat'
    # f_fe = r'D:\data\H054_Fe_1x1_0x0_zoom-0.dat'
    # f_mn = r'D:\data\H054_Mn_1x1_0x0_zoom-0.dat'
    # f_co = r'D:\data\H017_Co_1x1_0x0-0-0.dat'
    # f_fe = r'D:\data\H017_Fe_1x1_0x0-0-0.dat'
    # f_mn = r'D:\data\H017_Mn_1x1_0x0-0-0.dat'
    # with open(f_co, 'r') as f:
    #     while True:
    #         temp = f.readline()
    #         if not temp.find('X-NUM') == -1:
    #             width = int(temp.split()[2]) - 1
    #             height = int(f.readline().split()[2]) - 1
    #             break
    #         if not temp:
    #             break
    # co = np.loadtxt(f_co, usecols=2, dtype=float, delimiter=',').reshape(height, width)
    # co[co > 5000] = 0
    # fe = np.loadtxt(f_fe, usecols=2, dtype=float, delimiter=',').reshape(height, width)
    # fe[fe > 10000] = 0
    # mn = np.loadtxt(f_mn, usecols=2, dtype=float, delimiter=',').reshape(height, width)
    # darray = np.vstack((co.flatten(), fe.flatten(), mn.flatten())).T
    # darray_r = np.sqrt((darray**2).sum(1))
    # darray_ele = np.zeros_like(darray_r)
    # darray_ele[darray_r>0] = np.arccos(darray[darray_r > 0, 2]/darray_r[darray_r > 0])/np.pi*180
    # darray_azi = np.zeros_like(darray_r)
    # darray_azi[(darray_r > 0)&(darray[:, 0]>0)] = np.arctan(darray[(darray_r > 0)&(darray[:, 0]>0), 1] / darray[(darray_r > 0)&(darray[:, 0]>0), 0])/np.pi*180
    # darray_map = np.unique(np.round(np.vstack((darray_azi, darray_ele)).T, 0).astype(int), axis=0, return_inverse=True)
    # # darray_map[1]: index sequence in darray size
    # r_distri = np.zeros((91, 91))
    # point = np.zeros((91, 91))
    # point_list = [np.array([]), ] * point.size
    # print(np.unique(darray_map[1]).size)
    # for i in np.unique(darray_map[1]):
    #     locate = darray_map[0][i]
    #     point_list[int(locate[0]*point.shape[0] + locate[1])] = np.where(darray_map[1] == i)[0]
    #     r_distri[locate[0]][locate[1]] = darray_r[np.where(darray_map[1] == i)[0]].max()
    #     point[locate[0]][locate[1]] = np.where(darray_map[1] == i)[0].size
    # point[0] = 0
    # point[-1] = 0
    # point[:, 0] = 0
    # point[:, -1] = 0
    # weight_r = r_distri#*point
    # target_max = np.unravel_index(np.argmax(weight_r), weight_r.shape)
    # # target_index = np.array([], dtype=int)
    # # for i in np.arange(target_max[0]-5, target_max[0]+5):
    # #     for j in np.arange(target_max[1] - 5, target_max[1] + 5):
    # #         target_index = np.append(target_index, point_list[int(i*weight_r.shape[0]+j)])
    # target_index = point_list[np.argmax(weight_r)]
    # target_index = np.unravel_index(target_index, co.shape)
    #
    # #plt.subplot(211)
    # plt.imshow(r_distri, 'gray')
    # plt.ylabel('Φ', fontsize=15)
    # plt.xlabel('θ', fontsize=15)
    # # plt.subplot(212)
    # # alpha = np.zeros_like(co)
    # # alpha[target_index] = 1
    # # plt.imshow(alpha, 'Reds', alpha=alpha)
    # # plt.imshow(co+fe+mn, 'gray', alpha=1-alpha)
    # # plt.ylabel('azi')
    # # plt.xlabel('ele')
    # azi = np.arange(90)/180*np.pi
    # ele = np.arange(90)/180*np.pi
    # #cartesian = np.array([np.sin(ele) * np.cos(azi), np.sin(ele) * np.sin(azi), np.cos(ele)])
    # rmax_i = np.unravel_index(np.argmax(weight_r), weight_r.shape)
    # ele, azi = rmax_i[0]/180*np.pi, rmax_i[1]/180*np.pi
    # print(rmax_i, np.sin(ele) * np.cos(azi), np.sin(ele) * np.sin(azi), np.cos(ele))
    # plt.show()



    app = QApplication(argv)
    main = MainWindow()
    main.show()
    exit(app.exec())