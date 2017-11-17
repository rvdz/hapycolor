import sys

from hapycolor.helpers import hsl_to_rgb, rgb_to_hsl

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QDesktopWidget, QSlider, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QIcon, QPainter, QColor
from PyQt5.QtCore import QCoreApplication, Qt, pyqtSignal, QObject


class Communicate(QObject):

    updateBW = pyqtSignal(int)


class ColorDisplay(QWidget):

    def __init__(self, x, cs_y, hue_step, init_sat, slice_width, slice_height):

        super().__init__()

        self.HUE_STEP     = hue_step
        self.SLICE_WIDTH  = slice_width
        self.SLICE_HEIGHT = slice_height
        self.X            = x
        self.CS_Y         = cs_y
        self.saturation   = init_sat


    def setSaturation(self, s):

        self.saturation   = s


    def paintEvent(self, event):

        painter = QPainter()
        painter.begin(self)
        self.drawWidget(painter)
        painter.end()


    def drawWidget(self, painter):

        for i, hue in enumerate(range(0, 360, self.HUE_STEP)):

            for bright in range(101):

                rgb = hsl_to_rgb((hue, self.saturation/100, bright/100.))
                red, green, blue = rgb[0], rgb[1], rgb[2]

                color = QColor(red, green, blue)
                painter.setPen(color)  # Outline
                painter.setBrush(color)  # Fill
                painter.drawRect(self.X + bright*5, self.CS_Y + i*30, self.SLICE_WIDTH, self.SLICE_HEIGHT)


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
        self.HUE_STEP       = 20
        self.INIT_SAT       = 100
        self.SLICE_WIDTH    = 5
        self.SLICE_HEIGHT   = 20
        self.CS_Y           = 30
        self.CS_WIDTH       = self.WIDTH
        self.CS_HEIGHT      = self.SLICE_HEIGHT * 360 / self.HUE_STEP

        # Classic sliders
        self.S_WIDTH        = 150
        self.S_HEIGHT       = 30

        self.__init_UI()


    def __init_UI(self):

        slider = QSlider(Qt.Horizontal, self)
        slider.setFocusPolicy(Qt.NoFocus)
        slider.setRange(self.MIN_SAT, self.MAX_SAT)
        slider.setValue(self.INIT_SAT)
        slider.setGeometry(self.X_WID, 40, self.S_WIDTH, self.S_HEIGHT)

        # Interactive Widget
        self.c = Communicate()
        self.colorDisplay = ColorDisplay(
                                x=self.X_WID,
                                cs_y=self.CS_Y,
                                hue_step=self.HUE_STEP,
                                init_sat=self.INIT_SAT,
                                slice_width=self.SLICE_WIDTH,
                                slice_height=self.SLICE_HEIGHT
                                )
        self.c.updateBW[int].connect(self.colorDisplay.setSaturation)
        slider.valueChanged[int].connect(self.changeSaturation)

        hbox_slider = QHBoxLayout()
        hbox_slider.addWidget(slider)

        hbox_hue = QHBoxLayout()
        hbox_hue.addWidget(self.colorDisplay)

        vbox = QVBoxLayout()
        #vbox.addLayout(hbox_hue, 360 / self.HUE_STEP)
        #vbox.addLayout(hbox_slider, 1)
        #vbox.addStretch(1)
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

        self.c.updateBW.emit(value)
        self.colorDisplay.repaint()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    he = HyperplanEditor()
    sys.exit(app.exec_())
