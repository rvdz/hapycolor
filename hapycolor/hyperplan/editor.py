import sys, json, os
from enum import IntEnum

from hapycolor.helpers import hsl_to_hex, hex_to_hsl, hex_to_rgb, rgb_to_hsl, rgb_to_hex
from hapycolor.hyperplan.qrangeslider import QRangeSlider as RangeSlider

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, \
                            QDesktopWidget, QSlider, QHBoxLayout, \
                            QVBoxLayout, QMainWindow, QAction, \
                            QMessageBox, QFileDialog, QGridLayout, \
                            QLabel, QLineEdit
from PyQt5.QtGui import QIcon, QPainter, QColor
from PyQt5.QtCore import QCoreApplication, Qt, pyqtSignal, QObject


class Communicate(QObject):


    updateSaturation = pyqtSignal(int)
    modification     = pyqtSignal(int)
    removeSavedSat   = pyqtSignal(int)


class ColorDisplay(QWidget):


    saveSaturation = pyqtSignal(int)

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
        self.__names      = {}

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

    def genName(self, state):

        if state not in self.__names.keys():
            self.__names[state] = []
            num = "0"
        else:
            num = str(len(self.__names[state]))
        if len(self.__names[state]) < 10:
            name = "0" + num
        else:
            name = num
        self.__names[state].append(name)
        return name

    def setSaturation(self, s):

        self.saturation = s
        for name in self.sliders.keys():
            self.sliders[name].setSaturation(s)
            if str(s) in self.__points.keys():
                self.loadSliderRange(self.sliders[name], int(name))

    # JSON file replace tuple by array
    def loadSliderRange(self, slider, index):

        colStart = self.__points[str(self.saturation)]['dark'][index]
        colStart = rgb_to_hex(tuple(colStart))
        colEnd = self.__points[str(self.saturation)]['bright'][index]
        colEnd = rgb_to_hex(tuple(colEnd))
        if slider.colorStart() == colStart and slider.colorEnd() == colEnd:
            return
        slider.setEndByColor(colEnd)
        slider.setStartByColor(colStart)

    def updateSliderSat(self, slider, sat):

        slider.setSaturation(sat)

    def updateSliderColorMed(self, slider, color):

        slider.setColorMedian(color)

    def updateSliders(self, sat, state):

        for i, color in enumerate(self.__points[sat]['bright']):
            hue = rgb_to_hsl(tuple(color))[0]
            colorMed = (hue, int(sat), .5)
            slider = self.sliders[hue/self.hueStep]
            self.updateSliderColorMed(slider, colorMed)
            self.updateSliderRange(slider, i)

    def addSlider(self, colorMedian, start, end):

        name = self.genName(self.State.ALL)
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
        if sat not in self.__points.keys():
            self.saveSaturation.emit(int(sat))
        self.__points[sat] = {}
        dark = self.__points[sat]['dark'] = []
        bright = self.__points[sat]['bright'] = []
        for name in sorted(self.sliders.keys()):
            dark.append(hex_to_rgb(self.sliders[name].colorStart()))
            bright.append(hex_to_rgb(self.sliders[name].colorEnd()))
        return self.__points

    # Input sorted by increasing hue
    def loadPoints(self, points):

        self.__points = points
        for key in points.keys():
            sat = key
            break
        self.setSaturation(int(sat))
        self.updateSliders(sat, self.State.ALL)
        return int(sat)

    def removeSatPoints(self, sat):

        del self.__points[str(sat)]


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
                sat = self.formWidget.colorSliders.loadPoints(points)
                self._saved = True
                self.formWidget.updateSatSlider(sat)
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
        self.parent = parent

        # Color Slider
        self.hueStep       = 22.5  # Max 1 digit after comma
        self.initSat       = 100
        self.csY           = 30
        self.MIN_SAT       = 1
        self.MAX_SAT       = 100

        # Classic sliders
        self.S_WIDTH        = 150
        self.S_HEIGHT       = 30

        # Buttons
        self.MAX_COL        = 3
        self.MAX_ROW        = 18

        # Saturation slider
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.slider.setRange(self.MIN_SAT, self.MAX_SAT)
        self.slider.setValue(self.initSat)
        self.slider.setGeometry(parent.X_WID, 40, self.S_WIDTH, self.S_HEIGHT)

        # Save saturation button
        self.saveSatButton = QPushButton("Save saturation\nconfiguration", self)
        self.saveSatButton.resize(self.saveSatButton.sizeHint())

        # Color Sliders
        self.colorSliders = ColorDisplay(
                                x=parent.X_WID,
                                csY=self.csY,
                                hueStep=self.hueStep,
                                initSat=self.initSat,
                                )

        # Saved saturation buttons
        self.dynGrid = QGridLayout()
        self.dynGrid.addWidget(QLabel('Saved\nsaturations', self), 1, 0)
        self.dynGrid.setRowStretch(0, 1)
        self.dynSatButtons = {}
        self.removeSatButton = QPushButton("Remove sat", self)
        self.removeSatButton.resize(self.removeSatButton.sizeHint())
        self.dynGrid.addWidget(self.removeSatButton, 1, 1)
        self.removeSatTextBox = QLineEdit(self)
        self.removeSatTextBox.resize(self.removeSatButton.size())
        self.dynGrid.addWidget(self.removeSatTextBox, 1, 2)

        # Communication
        self.c = Communicate()
        self.c.updateSaturation[int].connect(self.colorSliders.setSaturation)
        self.c.modification.connect(self.colorSliderUpdate)
        self.c.removeSavedSat[int].connect(self.colorSliders.removeSatPoints)
        self.slider.valueChanged[int].connect(self.changeSaturation)
        self.colorSliders.setCanal(self.c)
        self.colorSliders.saveSaturation[int].connect(self.addSavedSat)
        self.saveSatButton.clicked.connect(self.colorSliders.savePoints)
        self.removeSatButton.clicked.connect(self.removeSavedSat)

        # Layout
        grid = QGridLayout()
        grid.addWidget(self.colorSliders, 0, 0)
        grid.addLayout(self.dynGrid, 0, 1)
        grid.addWidget(self.slider, 1, 0)
        grid.addWidget(self.saveSatButton, 1, 1)
        self.setLayout(grid)

    def removeSavedSat(self):

        if self.dynGrid.rowCount() < 3:
            print("Warning: no sat to be removed")
            return
        textBox = self.removeSatTextBox.text()
        if textBox not in self.dynSatButtons.keys():
            print("Warning: trying to remove invalid sat")
            return
        toRemove = self.dynSatButtons[textBox]
        self.dynGrid.removeWidget(toRemove)
        toRemove.deleteLater()
        toRemove = None
        del self.dynSatButtons[textBox]
        self.c.removeSavedSat.emit(int(textBox))

    def addSavedSat(self, sat):

        row = self.dynGrid.rowCount() - 1
        if self.dynGrid.itemAtPosition(row, self.MAX_COL-1) is not None or row == 1:
            row += 1
        for i in range(self.MAX_COL):
            col = i
            if self.dynGrid.itemAtPosition(row, col) == None:
                break;
        name = str(sat)
        self.dynSatButtons[name] = QPushButton(name, self)
        self.dynSatButtons[name].resize(self.dynSatButtons[name].sizeHint())
        self.dynSatButtons[name].clicked.connect(lambda: self.loadSavedSat(sat))
        self.dynGrid.addWidget(self.dynSatButtons[name], row, col)

    def loadSavedSat(self, sat):

        self.changeSaturation(sat)
        self.updateSatSlider(sat)

    def updateSatSlider(self, value):

        self.slider.setValue(value)

    def changeSaturation(self, value):

        self.c.updateSaturation.emit(value)
        self.c.modification.emit(0)

    def colorSliderUpdate(self):

        self.parent.notSaved()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    he = HyperplanEditor()
    sys.exit(app.exec_())
