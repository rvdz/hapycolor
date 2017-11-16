import sys

from hapycolor.helpers import hsl_to_rgb, rgb_to_hsl

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QDesktopWidget, QSlider, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QIcon, QPainter, QColor
from PyQt5.QtCore import QCoreApplication, Qt, pyqtSignal, QObject


class Communicate(QObject):

    updateBW = pyqtSignal(int)


class ColorSlider(QWidget):

    def __init__(self):

        super().__init__()
        self.initUI()


    def initUI(self):

        self.setMinimumSize(1, 100)
        self.saturation = 75


    def setSaturation(self, s):

        self.saturation = s


    def paintEvent(self, event):

        painter = QPainter()    
        painter.begin(self)
        self.drawWidget(painter)
        painter.end()


    def drawWidget(self, painter):

        for i, hue in enumerate(range(0, 360, 30)):

            for bright in range(101):

                rgb = hsl_to_rgb((hue, self.saturation/100, bright/100.))
                red, green, blue = rgb[0], rgb[1], rgb[2]

                color = QColor(red, green, blue)
                painter.setPen(color)  # Outline
                painter.setBrush(color)  # Fill
                painter.drawRect(30+bright*3, 10+i*30, 3, 20)


class HyperplanEditor(QWidget):
    def __init__(self):

        super().__init__()

        # Desktop properties
        self.DESKTOP_HEIGHT = QDesktopWidget().availableGeometry().height()
        self.DESKTOP_WIDTH  = QDesktopWidget().availableGeometry().width()

        # Window size and position
        self.WIDTH          = self.DESKTOP_WIDTH / 3
        self.HEIGHT         = self.DESKTOP_HEIGHT

        self.WINDOW_NAME    = "H Editor"
        
        self.__init_UI()


    def __init_UI(self):

#        button = QPushButton('Quit', self)
#        button.setGeometry(20, 10, 50, 40)
#        button.resize(button.sizeHint())
#        button.clicked.connect(self.close)

        slider = QSlider(Qt.Horizontal, self)
        slider.setFocusPolicy(Qt.NoFocus)
        slider.setRange(0, 100)
        slider.setValue(75)
        slider.setGeometry(30, 40, 150, 30)

        # Interactive Widget
        self.c = Communicate()
        self.colorSlider = ColorSlider()
        self.c.updateBW[int].connect(self.colorSlider.setSaturation)
        slider.valueChanged[int].connect(self.changeSaturation)

        hbox_slider = QHBoxLayout()
        hbox_slider.addWidget(slider)

        hbox_hue = QHBoxLayout()
        hbox_hue.addWidget(self.colorSlider)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_hue)
        vbox.addLayout(hbox_slider)
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
        self.colorSlider.repaint()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    he = HyperplanEditor()
    sys.exit(app.exec_())
