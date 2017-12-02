import sys, json, os
from enum import IntEnum

from hapycolor.helpers import hsl_to_hex, hex_to_hsl, hex_to_rgb, rgb_to_hsl, rgb_to_hex
from hapycolor.hyperplan.qrangeslider import QRangeSlider as RangeSlider

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, \
                            QDesktopWidget, QSlider, QHBoxLayout, \
                            QVBoxLayout, QMainWindow, QAction, \
                            QMessageBox, QFileDialog, QGridLayout
from PyQt5.QtGui import QIcon, QPainter, QColor
from PyQt5.QtCore import QCoreApplication, Qt, pyqtSignal, QObject


class Communicate(QObject):


    updateSaturation = pyqtSignal(int)
    modification     = pyqtSignal(int)


class ColorDisplay(QWidget):


    # Inspired by http://www.procato.com/rgb+index/#
    class State(IntEnum):
        ALL = 0
        RED = 1
        ORANGE = 2
        AMBER = 3
        LIME = 4
        CHARTREUSE = 5
        GREEN = 6
        MALACHITE = 7
        TURQUOISE = 8
        CYAN = 9
        AZURE = 10
        SAPPHIRE = 11
        BLUE = 12
        VIOLET = 13
        MAGENTA = 14
        FUCHSIA = 15
        RASPBERRY = 16


    def __init__(self, x, csY, hueStep, initSat):

        super().__init__()

        self.hueStep      = hueStep
        self.X            = x
        self.csY          = csY

        # Init
        self.gradient     = True
        self.start        = 30
        self.end          = 70
        self.saturation   = initSat
        self.__state      = self.State.ALL

        self.sliders      = {}
        self.layouts      = {}
        self.VLayout      = QVBoxLayout()
        self.__points     = {}

        self.initHues(self.hueStep)
        self.initSliders()
        self.initLayout()

    def initHues(self, hueStep):

        hues = {}
        for s in self.State:
            if s == self.State.ALL:
                hues[s] = [0, 360]
            else:
                hues[s] = [(int(s)-1)*self.hueStep, int(s)*self.hueStep]
        setattr(self, 'hues', hues)

    def initSliders(self):

        for hue in range(0, 3600, int(10*self.hueStep)):
            cMed = hsl_to_hex((hue/10, self.saturation/100., .5))
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

        self.saturation = s
        for i, name in enumerate(sorted(self.sliders.keys())):
            self.sliders[name].setSaturation(s)
            if str(s) in self.__points.keys():
                self.updateSlider(self.sliders[name], i)

    # JSON file replace tuple by array
    def updateSlider(self, slider, index):

        colStart = self.__points[str(self.saturation)]['dark'][index]
        colStart = rgb_to_hex(tuple(colStart))
        colEnd = self.__points[str(self.saturation)]['bright'][index]
        colEnd = rgb_to_hex(tuple(colEnd))
        if slider.colorStart() == colStart and slider.colorEnd() == colEnd:
            return
        hue = hex_to_hsl(colStart)[0]
        colMed = hsl_to_hex((hue, self.saturation/100., .5))
        slider.setEndByColor(colEnd)
        slider.setStartByColor(colStart)
        slider.setColorMedian(colMed)

    def addSlider(self, colorMedian, start, end):

        name = self.genName(hex_to_hsl(colorMedian)[0])
        self.sliders[name] = RangeSlider(
                            gradient=self.gradient,
                            colorMedian=colorMedian,
                            start=start,
                            end=end,
                            saturation=self.saturation)
        self.sliders[name].setRange(start, end)

    # Output sorted by increasing hue
    def savePoints(self):

        for slider in self.sliders.values():
            sat = str(int(slider.saturation()*100))
            break
        self.__points[sat] = {}
        dark = self.__points[sat]['dark'] = []
        bright = self.__points[sat]['bright'] = []
        for name in sorted(self.sliders.keys()):
            dark.append(hex_to_rgb(self.sliders[name].colorStart()))
            bright.append(hex_to_rgb(self.sliders[name].colorEnd()))
        print(self.__points)
        return self.__points

    # Input sorted by increasing hue
    def loadPoints(self, points):

        self.__points = points
        for key in points.keys():
            sat = key
            break
        self.setSaturation(int(sat))


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
                self.formWidget.colorSliders.loadPoints(points)
                self._saved = True
        except:
            return

    def saveFile(self):

        points = self.formWidget.colorSliders.savePoints()
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
        self.hueStep       = 22.5  # Max 1 digit after comma
        self.initSat       = 100
        self.csY           = 30
        self.MIN_SAT       = 1
        self.MAX_SAT       = 100

        # Classic sliders
        self.S_WIDTH        = 150
        self.S_HEIGHT       = 30

        # Saturation slider
        slider = QSlider(Qt.Horizontal, self)
        slider.setFocusPolicy(Qt.NoFocus)
        slider.setRange(self.MIN_SAT, self.MAX_SAT)
        slider.setValue(self.initSat)
        slider.setGeometry(parent.X_WID, 40, self.S_WIDTH, self.S_HEIGHT)

        #Save saturation button
        saveSatButton = QPushButton("Save saturation\nconfiguration", self)
        saveSatButton.resize(saveSatButton.sizeHint())

        # Color Sliders
        self.colorSliders = ColorDisplay(
                                x=parent.X_WID,
                                csY=self.csY,
                                hueStep=self.hueStep,
                                initSat=self.initSat,
                                )

        # Communication
        self.c = Communicate()
        self.c.updateSaturation[int].connect(self.colorSliders.setSaturation)
        self.c.modification.connect(parent.notSaved)
        slider.valueChanged[int].connect(self.changeSaturation)
        self.colorSliders.setCanal(self.c)
        saveSatButton.clicked.connect(self.colorSliders.savePoints)

        # Layout
        grid = QGridLayout()
        grid.addWidget(self.colorSliders, 0, 0)
        grid.addWidget(slider, 1, 0)
        grid.addWidget(saveSatButton, 1, 1)
        self.setLayout(grid)

    def changeSaturation(self, value):

        self.c.updateSaturation.emit(value)
        self.c.modification.emit(0)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    he = HyperplanEditor()
    sys.exit(app.exec_())
