import sys, json, os
from contextlib import redirect_stdout

from hapycolor.helpers import hsl_to_hex, hex_to_hsl, hex_to_rgb, rgb_to_hsl
from hapycolor.hyperplan.qrangeslider import QRangeSlider as RangeSlider

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, \
                            QDesktopWidget, QSlider, QHBoxLayout, \
                            QVBoxLayout, QMainWindow, QAction, \
                            QMessageBox, QFileDialog
from PyQt5.QtGui import QIcon, QPainter, QColor
from PyQt5.QtCore import QCoreApplication, Qt, pyqtSignal, QObject


class Communicate(QObject):


    updateSaturation = pyqtSignal(int)
    modification     = pyqtSignal(int)


class ColorDisplay(QWidget):


    def __init__(self, x, csY, hueStep, initSat, sliceWidth, sliceHeight):

        super().__init__()

        self.hueStep     = hueStep
        self.sliceWidth  = sliceWidth
        self.sliceHeight = sliceHeight
        self.X            = x
        self.csY         = csY

        # Init
        self.gradient     = True
        self.start        = 30
        self.end          = 70
        self.saturation   = initSat

        self.sliders      = {}
        self.layouts      = {}
        self.VLayout      = QVBoxLayout()
        self.__points     = {}

        self.initSliders()
        self.initLayout()

    def initSliders(self):

        for hue in range(0, 360, self.hueStep):
            cMed = hsl_to_hex((hue, self.saturation/100., .5))
            name = self.genName(hue)
            self.addSlider(cMed, self.start, self.end)

    def initLayout(self):

        for name in sorted(self.sliders.keys()):
            self.layouts[name] = QHBoxLayout()
            self.layouts[name].addWidget(self.sliders[name])
            self.VLayout.addLayout(self.layouts[name])
        self.setLayout(self.VLayout)

    def setCanal(self, c):

        for name in self.sliders.keys():
            self.sliders[name].setCanal(c)

    def genName(self, hue):
        name = "hue" + str(hue)
        if hue == 0:
            name = name[:3] + '0' + name[3:]
        if hue < 100:
            name = name[:3] + '0' + name[3:]
        return name

    def setSaturation(self, s):

        for slider in self.sliders.values():
            slider.setSaturation(s)

    def addSlider(self, colorMedian, start, end):

        name = self.genName(hex_to_hsl(colorMedian)[0])
        self.sliders[name] = RangeSlider(
                            gradient=self.gradient,
                            colorMedian=colorMedian,
                            start=start,
                            end=end,
                            saturation=self.saturation)
        self.sliders[name].setRange(start, end)

    # Saturation fixed here
    # Output sorted by increasing hue
    def getPoints(self):

        for slider in self.sliders.values():
            sat = slider.saturation()
            break
        self.__points[sat] = {}
        dark = self.__points[sat]['dark'] = []
        bright = self.__points[sat]['bright'] = []
        for name in sorted(self.sliders.keys()):
            dark.append(hex_to_rgb(self.sliders[name].colorStart()))
            bright.append(hex_to_rgb(self.sliders[name].colorEnd()))
        return self.__points

    # Input sorted by increasing hue
    # Only supports same number of sliders for now
    def setPoints(self, points):

        for key in points.keys():
            sat = key
            break
        for i, key in enumerate(sorted(self.sliders.keys())):
            dark = rgb_to_hsl(tuple(points[sat]['dark'][i]))
            bright = rgb_to_hsl(tuple(points[sat]['bright'][i]))
            colorMedian = hsl_to_hex((dark[0], float(sat), 0.5))
            self.sliders[key].setColorMedian(colorMedian)
            self.sliders[key].setStart(int(dark[2]*100))
            self.sliders[key].setEnd(int(bright[2]*100))
        self.setSaturation(int(float(sat)*100))


class HyperplanEditor(QMainWindow):


    def __init__(self):

        super().__init__()

        # Desktop properties
        self.DESKTOP_HEIGHT = QDesktopWidget().availableGeometry().height()
        self.DESKTOP_WIDTH  = QDesktopWidget().availableGeometry().width()

        # Window size and position
        self.WIDTH          = self.DESKTOP_WIDTH / 2
        self.HEIGHT         = self.DESKTOP_HEIGHT

        self.X_WID          = 30
        self.WINDOW_NAME    = "H Editor"
        self.fileName       = None
        self._saved          = False

        self.__initUI()

    def __initUI(self):

        self.formWidget = FormWidget(self)
        self.setCentralWidget(self.formWidget)

        # Menubar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')

        openAct = QAction('Open', self)
        openAct.setShortcut('Ctrl+O')
        openAct.triggered.connect(self.openFile)
        fileMenu.addAction(openAct)

        saveAct = QAction('Save', self)
        saveAct.setShortcut('Ctrl+S')
        saveAct.triggered.connect(self.saveFile)
        fileMenu.addAction(saveAct)

        exitAct = QAction('Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(self.close)
        fileMenu.addAction(exitAct)

        # Dynamic Window
        self.resize(self.WIDTH, self.HEIGHT)
        self.center()
        self.setWindowTitle(self.WINDOW_NAME)

        self.show()

    def center(self):

        geom = self.frameGeometry()
        c = QDesktopWidget().availableGeometry().center()
        geom.moveCenter(c)
        self.move(geom.topLeft())

    def closeEvent(self, event):

        if not self._saved:
            modifs = ', \nyou have unsaved changes?'
        else:
            modifs = '?\n'
        reply = QMessageBox.question(self, 'WARNING', "Are you sure to "
                "quit" + modifs,
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def notSaved(self):

        self._saved = False

    def openFile(self):

        self.fileName = QFileDialog.getOpenFileName(self, 'Open file', '/home')[0]
        try:
            with open(self.fileName, 'r') as f:
                points = json.load(f)
                self.setWindowTitle(self.WINDOW_NAME + ": " + os.path.basename(self.fileName))
                self.formWidget.colorSliders.setPoints(points)
                self._saved = True
        except:
            return

    def saveFile(self):

        points = self.formWidget.colorSliders.getPoints()
        if self.fileName:
            outFile = QFileDialog.getSaveFileName(self, 'Save file', self.fileName)[0]
        else:
            outFile = QFileDialog.getSaveFileName(self, 'Save file', '/home')[0]
        try:
            with open(outFile, 'w') as f:
                json.dump(points, f)
                self._saved = True
        except:
            return


class FormWidget(QWidget):


    def __init__(self, parent):

        super(FormWidget, self).__init__(parent)

        # Color Slider
        self.hueStep       = 20
        self.initSat       = 100
        self.sliceWidth    = 5
        self.sliceHeight   = 20
        self.csY           = 30
        self.MIN_SAT       = 0
        self.MAX_SAT       = 100
        self.CS_WIDTH      = parent.WIDTH
        self.CS_HEIGHT     = self.sliceHeight * 360 / self.hueStep

        # Classic sliders
        self.S_WIDTH        = 150
        self.S_HEIGHT       = 30

        # Saturation slider
        slider = QSlider(Qt.Horizontal, self)
        slider.setFocusPolicy(Qt.NoFocus)
        slider.setRange(self.MIN_SAT, self.MAX_SAT)
        slider.setValue(self.initSat)
        slider.setGeometry(parent.X_WID, 40, self.S_WIDTH, self.S_HEIGHT)

        # Color Sliders
        self.colorSliders = ColorDisplay(
                                x=parent.X_WID,
                                csY=self.csY,
                                hueStep=self.hueStep,
                                initSat=self.initSat,
                                sliceWidth=self.sliceWidth,
                                sliceHeight=self.sliceHeight
                                )

        # Communication
        self.c = Communicate()
        self.c.updateSaturation[int].connect(self.colorSliders.setSaturation)
        self.c.modification.connect(parent.notSaved)
        slider.valueChanged[int].connect(self.changeSaturation)
        self.colorSliders.setCanal(self.c)

        # Layout
        hboxSliderSat = QHBoxLayout()
        hboxSliderSat.addWidget(slider)
        hboxColorSliders = QHBoxLayout()
        hboxColorSliders.addWidget(self.colorSliders)
        vbox = QVBoxLayout()
        vbox.addLayout(hboxColorSliders, 360 / self.hueStep)
        vbox.addLayout(hboxSliderSat, 1)
        self.setLayout(vbox)

    def changeSaturation(self, value):

        self.c.updateSaturation.emit(value)
        self.c.modification.emit(0)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    he = HyperplanEditor()
    sys.exit(app.exec_())
