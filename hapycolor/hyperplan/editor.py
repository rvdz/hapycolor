import sys

from hapycolor.helpers import hsl_to_hex
from hapycolor.hyperplan.qrangeslider import QRangeSlider as RangeSlider

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QDesktopWidget, QSlider, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QIcon, QPainter, QColor
from PyQt5.QtCore import QCoreApplication, Qt, pyqtSignal, QObject


class Communicate(QObject):

    updateSaturation = pyqtSignal(int)


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

        self.initSliders()
        self.initLayout()


    def initSliders(self):

        for hue in range(0, 360, self.hueStep):
            cMed = hsl_to_hex((hue, self.saturation/100., .5))
            name = "hue" + str(hue)
            if hue == 0:
                name = name[:3] + '0' + name[3:]
            if hue < 100:
                name = name[:3] + '0' + name[3:]
            self.sliders[name] = RangeSlider(
                                gradient=self.gradient,
                                colorMedian=cMed,
                                start=self.start,
                                end=self.end,
                                saturation=self.saturation)
            self.sliders[name].setRange(self.start, self.end)


    def initLayout(self):

        for name in sorted(self.sliders.keys()):
            self.layouts[name] = QHBoxLayout()
            self.layouts[name].addWidget(self.sliders[name])
            self.VLayout.addLayout(self.layouts[name])
        self.setLayout(self.VLayout)


    def setSaturation(self, s):

        for slider in self.sliders.values():
            slider.setSaturation(s)


class HyperplanEditor(QWidget):

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

        self.MIN_SAT        = 0
        self.MAX_SAT        = 100

        # Color Slider
        self.hueStep       = 20
        self.initSat       = 100
        self.sliceWidth    = 5
        self.sliceHeight   = 20
        self.csY           = 30
        self.CS_WIDTH       = self.WIDTH
        self.CS_HEIGHT      = self.sliceHeight * 360 / self.hueStep

        # Classic sliders
        self.S_WIDTH        = 150
        self.S_HEIGHT       = 30

        self.__initUI()


    def __initUI(self):

        slider = QSlider(Qt.Horizontal, self)
        slider.setFocusPolicy(Qt.NoFocus)
        slider.setRange(self.MIN_SAT, self.MAX_SAT)
        slider.setValue(self.initSat)
        slider.setGeometry(self.X_WID, 40, self.S_WIDTH, self.S_HEIGHT)

        # Interactive Widget
        self.c = Communicate()
        self.colorSliders = ColorDisplay(
                                x=self.X_WID,
                                csY=self.csY,
                                hueStep=self.hueStep,
                                initSat=self.initSat,
                                sliceWidth=self.sliceWidth,
                                sliceHeight=self.sliceHeight
                                )
        self.c.updateSaturation[int].connect(self.colorSliders.setSaturation)
        slider.valueChanged[int].connect(self.changeSaturation)

        hboxSliderSat = QHBoxLayout()
        hboxSliderSat.addWidget(slider)

        hboxColorSliders = QHBoxLayout()
        hboxColorSliders.addWidget(self.colorSliders)

        vbox = QVBoxLayout()
        vbox.addLayout(hboxColorSliders, 360 / self.hueStep)
        vbox.addLayout(hboxSliderSat, 1)
        self.setLayout(vbox)

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

        reply = QMessageBox.question(self, 'WARNING', "Are you sure to quit?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


    def changeSaturation(self, value):

        self.c.updateSaturation.emit(value)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    he = HyperplanEditor()
    sys.exit(app.exec_())
