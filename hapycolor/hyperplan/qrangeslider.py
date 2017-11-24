import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets
from hapycolor.helpers import hsl_to_hex, hex_to_hsl

__all__ = ['QRangeSlider']

DEFAULT_CSS = """
QRangeSlider * {
    border: 0px;
    padding: 0px;
}
QRangeSlider #Head {
    background: #222;
}
QRangeSlider #Span {
    background: #000;
}
QRangeSlider #Span:active {
    background: #000;
}
QRangeSlider #Tail {
    background: #222;
}
QRangeSlider > QSplitter::handle {
    background: #393;
}
QRangeSlider > QSplitter::handle:vertical {
    height: 4px;
}
QRangeSlider > QSplitter::handle:pressed {
    background: #ca5;
}
"""

def scale(val, src, dst):
    return int(((val - src[0]) / float(src[1]-src[0])) * (dst[1]-dst[0]) + dst[0])


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("QRangeSlider")
        Form.resize(300, 30)
        Form.setStyleSheet(DEFAULT_CSS)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self._splitter = QtWidgets.QSplitter(Form)
        self._splitter.setMinimumSize(QtCore.QSize(0, 0))
        self._splitter.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self._splitter.setOrientation(QtCore.Qt.Horizontal)
        self._splitter.setObjectName("splitter")
        self._head = QtWidgets.QGroupBox(self._splitter)
        self._head.setTitle("")
        self._head.setObjectName("Head")
        self._handle = QtWidgets.QGroupBox(self._splitter)
        self._handle.setTitle("")
        self._handle.setObjectName("Span")
        self._tail = QtWidgets.QGroupBox(self._splitter)
        self._tail.setTitle("")
        self._tail.setObjectName("Tail")
        self.gridLayout.addWidget(self._splitter, 0, 0, 1, 1)
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("QRangeSlider", "QRangeSlider"))


class Element(QtWidgets.QGroupBox):
    def __init__(self, parent, main):
        super(Element, self).__init__(parent)
        self.main = main

    def setStyleSheet(self, style):
        self.parent().setStyleSheet(style)

    def textColor(self):
        return getattr(self, '__textColor', QtGui.QColor(125, 125, 125))

    def setTextColor(self, color):
        if type(color) == tuple and len(color) == 3:
            color = QtGui.QColor(color[0], color[1], color[2])
        elif type(color) == int:
            color = QtGui.QColor(color, color, color)
        setattr(self, '__textColor', color)

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.main.drawValues():
            self.drawText(event, qp)
        qp.end()


class Head(Element):
    def __init__(self, parent, main):
        super(Head, self).__init__(parent, main)

    def drawText(self, event, qp):
        qp.setPen(self.textColor())
        qp.setFont(QtGui.QFont('Arial', 10))
        qp.drawText(event.rect(), QtCore.Qt.AlignLeft, str(self.main.min()))


class Tail(Element):
    def __init__(self, parent, main):
        super(Tail, self).__init__(parent, main)

    def drawText(self, event, qp):
        qp.setPen(self.textColor())
        qp.setFont(QtGui.QFont('Arial', 10))
        qp.drawText(event.rect(), QtCore.Qt.AlignRight, str(self.main.max()))


class Handle(Element):
    def __init__(self, parent, main):
        super(Handle, self).__init__(parent, main)

    def drawText(self, event, qp):
        qp.setPen(self.textColor())
        qp.setFont(QtGui.QFont('Arial', 10))
        qp.drawText(event.rect(), QtCore.Qt.AlignLeft, str(self.main.start()))
        qp.drawText(event.rect(), QtCore.Qt.AlignRight, str(self.main.end()))

    def mouseMoveEvent(self, event):
        event.accept()
        mx = event.globalX()
        _mx = getattr(self, '__mx', None)
        if not _mx:
            setattr(self, '__mx', mx)
            dx = 0
        else:
            dx = mx - _mx
        setattr(self, '__mx', mx)
        if dx == 0:
            event.ignore()
            return
        elif dx > 0:
            dx = 1
        elif dx < 0:
            dx = -1
        s = self.main.start() + dx
        e = self.main.end() + dx
        if s >= self.main.min() and e <= self.main.max():
            self.main.setRange(s, e)


class QRangeSlider(QtWidgets.QWidget, Ui_Form):
    endValueChanged = QtCore.pyqtSignal(int)
    maxValueChanged = QtCore.pyqtSignal(int)
    minValueChanged = QtCore.pyqtSignal(int)
    startValueChanged = QtCore.pyqtSignal(int)
    saturationChanged = QtCore.pyqtSignal(float)
    colorsChanged = QtCore.pyqtSignal(int)

    _SPLIT_START    = 1
    _SPLIT_END      = 2
    _COLOR_MIN      = '#000000'
    _COLOR_MAX      = '#FFFFFF'
    _INIT_SAT       = 1.

    def __init__(self, parent=None, gradient=True, colorMedian='#FF0000', saturation=100, start=30, end=70):
        super(QRangeSlider, self).__init__(parent)
        self.staticGradient = gradient
        self.setupUi(self)
        self.setMouseTracking(False)
        self._splitter.splitterMoved.connect(self._handleMoveSplitter)
        self._head_layout = QtWidgets.QHBoxLayout()
        self._head_layout.setSpacing(0)
        self._head_layout.setContentsMargins(0, 0, 0, 0)
        self._head.setLayout(self._head_layout)
        self.head = Head(self._head, main=self)
        self._head_layout.addWidget(self.head)
        self._handle_layout = QtWidgets.QHBoxLayout()
        self._handle_layout.setSpacing(0)
        self._handle_layout.setContentsMargins(0, 0, 0, 0)
        self._handle.setLayout(self._handle_layout)
        self.handle = Handle(self._handle, main=self)
        self.handle.setTextColor((150, 255, 150))
        self._handle_layout.addWidget(self.handle)
        self._tail_layout = QtWidgets.QHBoxLayout()
        self._tail_layout.setSpacing(0)
        self._tail_layout.setContentsMargins(0, 0, 0, 0)
        self._tail.setLayout(self._tail_layout)
        self.tail = Tail(self._tail, main=self)
        self._tail_layout.addWidget(self.tail)
        self.saturationChanged.connect(self._handleSaturation)
        if self.staticGradient:
            self.colorsChanged.connect(self._setLinearGradientBgStyle)
        self.setMin(0)
        self.setMax(100)
        self.setRange(start, end)
        self._initHue(colorMedian)
        self.setColorMedian(colorMedian)
        self.setSaturation(saturation)
        self.setDrawValues(True)
        self.show()
        self.setRange(start, end)

    def setStaticGradient(self, boolean):
        self.staticGradient = boolean

    def saturation(self):
        return getattr(self, '__saturation', None)

    def setSaturation(self, value):
        setattr(self, '__saturation', value/100.)
        self.saturationChanged.emit(value/100.)

    def _handleSaturation(self, sat):
        newMedHSL = (self.hue(), sat, hex_to_hsl(self.colorMedian())[2])
        self.setColorMedian(hsl_to_hex(newMedHSL))

    def hue(self):
        return getattr(self, '__hue', None)

    def _initHue(self, colorMedian):
        setattr(self, '__hue', hex_to_hsl(colorMedian)[0])

    def colorMedian(self):
        return getattr(self, '__color_median', None)

    def setColorMedian(self, value):
        setattr(self, '__color_median', value)
        if self.saturation() is None:
            setattr(self, '__saturation', self._INIT_SAT)
        start, end = self.getRange()
        self._setColorStart(start)
        self._setColorEnd(end)

    def colorMin(self):
        return self._COLOR_MIN

    def colorMax(self):
        return self._COLOR_MAX

    def setColorMin(self, value):
        self._COLOR_MIN = value
        self.colorsChanged.emit(value)

    def setColorMax(self, value):
        self._COLOR_MAX = value
        self.colorsChanged.emit(value)

    def colorStart(self):
        return getattr(self, '__color_start', None)

    def colorEnd(self):
        return getattr(self, '__color_end', None)

    def setColorStart(self, value):
        setattr(self, '__color_start', value)
        self.colorsChanged.emit(value)

    def setColorEnd(self, value):
        setattr(self, '__color_end', value)
        self.colorsChanged.emit(value)

    def _setColorStart(self, pos):
        ratio = (float(pos) - self.min()) / (self.max() - self.min())
        hsl_value = (self.hue(), self.saturation(), ratio)
        self.setColorStart(hsl_to_hex(hsl_value))

    def _setColorEnd(self, pos):
        ratio = (float(pos) - self.min()) / (self.max() - self.min())
        hsl_value = (self.hue(), self.saturation(), ratio)
        self.setColorEnd(hsl_to_hex(hsl_value))

    def min(self):
        return getattr(self, '__min', None)

    def max(self):
        return getattr(self, '__max', None)

    def setMin(self, value):
        setattr(self, '__min', value)
        self.minValueChanged.emit(value)

    def setMax(self, value):
        setattr(self, '__max', value)
        self.maxValueChanged.emit(value)

    def start(self):
        return getattr(self, '__start', None)

    def end(self):
        return getattr(self, '__end', None)

    def _setStart(self, value):
        setattr(self, '__start', value)
        self.startValueChanged.emit(value)

    def setStart(self, value):
        v = self._valueToPos(value)
        self._splitter.splitterMoved.disconnect()
        self._splitter.moveSplitter(v, self._SPLIT_START)
        self._splitter.splitterMoved.connect(self._handleMoveSplitter)
        self._setStart(value)

    def _setEnd(self, value):
        setattr(self, '__end', value)
        self.endValueChanged.emit(value)

    def setEnd(self, value):
        v = self._valueToPos(value)
        self._splitter.splitterMoved.disconnect()
        self._splitter.moveSplitter(v, self._SPLIT_END)
        self._splitter.splitterMoved.connect(self._handleMoveSplitter)
        self._setEnd(value)

    def drawValues(self):
        return getattr(self, '__drawValues', None)

    def setDrawValues(self, draw):
        setattr(self, '__drawValues', draw)

    def getRange(self):
        return (self.start(), self.end())

    def setRange(self, start, end):
        self.setStart(start)
        self.setEnd(end)

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Left:
            s = self.start()-1
            e = self.end()-1
        elif key == QtCore.Qt.Key_Right:
            s = self.start()+1
            e = self.end()+1
        else:
            event.ignore()
            return
        event.accept()
        if s >= self.min() and e <= self.max():
            self.setRange(s, e)

    def setBackgroundStyle(self, style):
        self._tail.setStyleSheet(style)
        self._head.setStyleSheet(style)

    def setHeadBgStyle(self, style):
        self._head.setStyleSheet(style)

    def setTailBgStyle(self, style):
        self._tail.setStyleSheet(style)

    def setSpanStyle(self, style):
        self._handle.setStyleSheet(style)

    def _linGradStyle(self, *arg):
        if len(arg) < 8 or len(arg) % 2 == 1:
            print('Missing gradient arguments')
            raise Exception
        x1, y1, x2, y2 = arg[0], arg[1], arg[2], arg[3]
        stopStyle = ''
        for i in range(4, len(arg), 2):
            stopStyle += ' stop:{} {}'.format(arg[i], arg[i+1])
        style = 'background: qlineargradient(x1:{}, y1:{}, x2:{}, y2:{},{} );'.format(x1, y1, x2, y2, stopStyle)
        return style

    def _setLinearGradientBgStyle(self):
        start, end = self.getRange()
        middle = (self.max() + self.min()) / 2
        cMin, cMax = self.colorMin(), self.colorMax()
        cS, cE, cMed = self.colorStart(), self.colorEnd(), self.colorMedian()
        if start >= middle:
            mid = (middle - self.min()) / (start - self.min())
            self.setHeadBgStyle(self._linGradStyle(0, 0, 1, 0, 0, cMin, mid, cMed, 1, cS))
            self.setSpanStyle(self._linGradStyle(0, 0, 1, 0, 0, cS, 1, cE))
            self.setTailBgStyle(self._linGradStyle(0, 0, 1, 0, 0, cE, 1, cMax))

        elif start < middle < end:
            mid = (middle - start) / (end - start)
            self.setHeadBgStyle(self._linGradStyle(0, 0, 1, 0, 0, cMin, 1, cS))
            self.setSpanStyle(self._linGradStyle(0, 0, 1, 0, 0, cS, mid, cMed, 1, cE))
            self.setTailBgStyle(self._linGradStyle(0, 0, 1, 0, 0, cE, 1, cMax))

        else:
            mid = (middle - end) / (self.max() - end)
            self.setHeadBgStyle(self._linGradStyle(0, 0, 1, 0, 0, cMin, 1, cS))
            self.setSpanStyle(self._linGradStyle(0, 0, 1, 0, 0, cS, 1, cE))
            self.setTailBgStyle(self._linGradStyle(0, 0, 1, 0, 0, cE, mid, cMed, 1, cMax))

    def _valueToPos(self, value):
        return scale(value, (self.min(), self.max()), (0, self.width()))

    def _posToValue(self, xpos):
        return scale(xpos, (0, self.width()), (self.min(), self.max()))

    def _handleMoveSplitter(self, xpos, index):
        hw = self._splitter.handleWidth()
        def _lockWidth(widget):
            width = widget.size().width()
            widget.setMinimumWidth(width)
            widget.setMaximumWidth(width)
        def _unlockWidth(widget):
            widget.setMinimumWidth(0)
            widget.setMaximumWidth(16777215)
        v = self._posToValue(xpos)
        if index == self._SPLIT_START:
            _lockWidth(self._tail)
            if v >= self.end():
                return
            offset = -20
            w = xpos + offset
            self._setColorStart(v)
            self._setStart(v)
        elif index == self._SPLIT_END:
            _lockWidth(self._head)
            if v <= self.start():
                return
            offset = -40
            w = self.width() - xpos + offset
            self._setColorEnd(v)
            self._setEnd(v)
        if self.staticGradient:
            self.colorsChanged.emit(0)
        _unlockWidth(self._tail)
        _unlockWidth(self._head)
        _unlockWidth(self._handle)

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    rs = QRangeSlider(gradient=True)
    rs.show()
    rs.setRange(15, 35)
    rs.setSaturation(100)
    rs.setColorStart('#440000')
    rs.setColorEnd('#990000')
    app.exec_()
