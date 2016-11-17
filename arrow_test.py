import sys
import math

from PyQt4.QtGui import (
    QApplication,
    QBrush,
    QColor,
    QFont,
    QFontMetrics,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QGridLayout,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPalette,
    QPen,
    QTextLayout,
    QWidget
)
from PyQt4.QtCore import (
    QFile,
    QIODevice,
    QLine,
    QLineF,
    QPoint,
    QPointF,
    QRect,
    QRectF,
    QSize,
    Qt
)

class FontPaintingUtil(object):
    FONT_WORKAROUND_SCALE = 10

    @staticmethod
    def points_to_MM(point_size):
        return point_size / 0.35278

    @staticmethod
    def scaled_font_pixel_size(font):
        scaled_font = font
        pixel_size = (FontPaintingUtil.points_to_MM(scaled_font.pointSizeF()) * \
                     FontPaintingUtil.FONT_WORKAROUND_SCALE) + 0.5

        scaled_font.setPixelSize(pixel_size)

        return scaled_font

    @staticmethod
    def draw_text(painter, rect, text, font):
        text_font = FontPaintingUtil.scaled_font_pixel_size(font)

        scaled_rect = QRectF(rect.x() * FontPaintingUtil.FONT_WORKAROUND_SCALE,
                             rect.y() * FontPaintingUtil.FONT_WORKAROUND_SCALE,
                             rect.width() * FontPaintingUtil.FONT_WORKAROUND_SCALE,
                             rect.height() * FontPaintingUtil.FONT_WORKAROUND_SCALE)

        painter.save()
        painter.setFont(text_font)

        sf = 1.0 / FontPaintingUtil.FONT_WORKAROUND_SCALE
        painter.scale(sf, sf)
        painter.drawText(scaled_rect, Qt.AlignCenter|Qt.TextWordWrap, text)

        painter.restore()


class RectItem(QGraphicsRectItem):

    def __init__(self, parent=None, scene=None):
        super(RectItem, self).__init__(parent, scene)

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.color = Qt.black
        self.setPen(QPen(self.color, 1, Qt.SolidLine,
                Qt.RoundCap, Qt.RoundJoin))

    def boundingRect(self):
        return QRectF(8, 8, 125, 125)

    def shape(self):
        path = QPainterPath()
        path.addRect(QRectF(8, 8, 125, 125))

        return path

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing, True)
        shadow_rect = QRectF(12, 12, 120, 120)

        shadow_start_pos = 12
        shadow_stop_pos = 132
        shadow_gradient = QLinearGradient(
            shadow_start_pos,
            shadow_start_pos,
            shadow_stop_pos,
            shadow_stop_pos
        )
        shadow_gradient.setColorAt(0.0, QColor('#f7f8f9'))
        shadow_gradient.setColorAt(1.0, QColor('#d1d1d1'))
        brush = QBrush(shadow_gradient)

        #Create shadow effect using linear gradient
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRect(shadow_rect)

        #Main item gradient
        gradient = QLinearGradient(
            10,
            10,
            128,
            128
        )

        gradient_light = QColor('#fcf2e3')
        gradient_dark = QColor('#e9dac2')
        gradient.setColorAt(0.0, gradient_light)
        gradient.setColorAt(1.0, gradient_dark)
        brush2 = QBrush(gradient)

        painter.setPen(self.pen())
        painter.setBrush(brush2)
        painter.drawRect(QRectF(10, 10, 118, 118))

        font = QFont('Consolas', 12, 75)
        painter.setFont(font)

        '''
        #FontPaintingUtil.draw_text(painter,text_rect, 'Rectangle', font)
        #painter.drawText(text_rect, Qt.AlignCenter, 'Rectangle')

        #UsingQTextLayout
        layout = QTextLayout('Rectangle', font)
        layout.beginLayout()
        while layout.createLine().isValid():
            pass
        layout.endLayout()

        y = 0
        max_width = 0

        #Set line position
        for i in range(layout.lineCount()):
            line = layout.lineAt(i)
            max_width = max(max_width, line.naturalTextWidth())
            line.setPosition(QPointF(0, y))
            y += line.height()

        pen = QPen(
            Qt.black,
            1,
            Qt.SolidLine,
            Qt.RoundCap,
            Qt.RoundJoin
        )
        painter.setPen(pen)

        #Apply pen in text format
        fr = QTextLayout.FormatRange()
        fr.start = 0
        fr.length = len(layout.text())
        fr.format.setTextOutline(pen)
        layout.setAdditionalFormats([fr])

        painter.drawRect(QRectF(12, 12, 114, 40))

        start_x = 12 + (114 - max_width) / 2.0
        start_y = 12 + (40 - y) / 2.0

        #Draw text
        layout.draw(painter, QPointF(start_x, start_y))
        '''


class ProfileTenureView(QGraphicsView):
    MIN_DPI = 72
    MAX_DPI = 300

    def __init__(self, parent=None):
        super(ProfileTenureView, self).__init__(parent)

        self._scene = QGraphicsScene(self)
        self._scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        self._scene.setSceneRect(QRectF(0, 0, 960, 540))

        self.setScene(self._scene)

        item = RectItem()
        self._scene.addItem(item)

        self.centerOn(0.0, 0.0)

    def minimumSizeHint(self):
        return QSize(320, 180)

    def sizeHint(self):
        return QSize(560, 315)

    def save_image_to_file(self, path, resolution=96):
        """
        Saves the profile tenure view image to file using A4 paper size.
        :param path: Absolute path where the image will be saved.
        :type path: str
        :param resolution: Resolution in dpi. Default is 96.
        :type resolution: int
        :return: Returns True if the operation succeeded, otherwise False. If
        False then a corresponding message is returned as well.
        :rtype: (bool, str)
        """
        image = self.image(resolution)

        if image.isNull():
            msg = self.tr('Constructed image is null.')

            return False, msg

        #Test if file is writeable
        fl = QFile(path)
        if not fl.open(QIODevice.WriteOnly):
            msg = self.tr('The image file cannot be saved in the '
                          'specified location.')

            return False, msg

        #Attempt to save to file
        save_op = image.save(fl)

        if not save_op:
            msg = self.tr('Image operation failed.')

            return False, msg

        return True, ''

    def image(self, resolution):
        """
        Renders the view onto a QImage object.
        :param resolution: Resolution of the image in dpi.
        :type resolution: int
        :return: Returns a QImage object corresponding to the profile STR
        view.
        :rtype: QImage
        """
        #Ensure resolution is within limits
        if resolution < ProfileTenureView.MIN_DPI:
            resolution = ProfileTenureView.MIN_DPI
        if resolution > ProfileTenureView.MAX_DPI:
            resolution = ProfileTenureView.MAX_DPI

        #In mm
        res = resolution / 25.4

        #In metres
        dpm = res * 1000

        #A4 landscape size
        width = 297 * res
        height = 210 * res

        img = QImage(int(width), int(height), QImage.Format_ARGB32)
        img.setDotsPerMeterX(int(dpm))
        img.setDotsPerMeterY(int(dpm))
        img.fill(Qt.white)

        painter = QPainter(img)
        painter.setRenderHint(QPainter.Antialiasing)

        self.scene().render(painter)
        painter.end()

        return img

if __name__ == '__main__':
    app = QApplication(sys.argv)

    test_win = QWidget()
    tenure_view = ProfileTenureView()

    p = 'D:/Temp/Test_Font_Scaling.png'
    status, msg = tenure_view.save_image_to_file(p, 300)

    layout = QGridLayout()
    layout.addWidget(tenure_view, 0, 0, 1, 1)
    test_win.setLayout(layout)
    test_win.show()

    sys.exit(app.exec_())