import sys
import math

from PyQt4.QtGui import (
    QApplication,
    QBrush,
    QColor,
    QFont,
    QFontMetrics,
    QGridLayout,
    QLinearGradient,
    QPainter,
    QPaintEvent,
    QPalette,
    QPen,
    QWidget
)
from PyQt4.QtCore import (
    QLine,
    QLineF,
    QPoint,
    QPointF,
    QRect,
    QSize,
    Qt
)


class ProfileTenureView(QWidget):
    """
    A widget for rendering a profile's social tenure relationship. It also
    includes functionality for saving the view as an image.
    """
    def __init__(self, parent=None, profile=None):
        QWidget.__init__(self, parent)
        self._profile = profile

        self.setBackgroundRole(QPalette.Base)
        self.setAutoFillBackground(True)

        self.pen = QPen(
            QColor('#EDBB99'),
            1,
            Qt.SolidLine,
            Qt.RoundCap,
            Qt.MiterJoin
        )

    @property
    def profile(self):
        """
        :return: The profile object being rendered.
        :rtype: Profile
        """
        return self._profile

    @profile.setter
    def profile(self, profile):
        """
        Sets the profile object whose STR view is to rendered.
        :param profile: Profile object to be rendered.
        :type profile: Profile
        """
        if profile is None:
            return

        self._profile = profile

        str_ent = profile.social_tenure

        #Set renderer entities
        self._party_renderer.entity = str_ent.party
        self._sp_unit_renderer.entity = str_ent.spatial_unit
        self._str_renderer.entity = str_ent
        self._supporting_doc_renderer.entity = str_ent

        self.update()

    def set_party(self, party):
        """
        Set the party entity.
        :param party: Entity corresponding to a party in a profile's STR
        relationship.
        :type party: Entity
        """
        self._party_renderer.entity = party
        self.update()

    def party(self):
        """
        :return: Returns the entity corresponding to a party in a profile's
        STR relationship.
        :rtype: Entity
        """
        return self._party_renderer.entity

    def set_spatial_unit(self, spatial_unit):
        """
        Set the spatial unit entity.
        :param spatial_unit: Entity corresponding to a spatial unit in a
        profile's STR relationship.
        :type spatial_unit: Entity
        """
        self._sp_unit_renderer.entity = spatial_unit
        self.update()

    def spatial_unit(self):
        """
        :return: Returns the entity corresponding to a spatial unit in a
        profile's STR relationship.
        :rtype: Entity
        """
        return self._sp_unit_renderer.entity

    def save_tenure_view(self, path):
        """
        Saves the profile tenure view as an image.
        :param path: Absolute path where the image will be saved.
        :type path: str
        :return: Returns True if the operation succeeded, otherwise False.
        :rtype: bool
        """
        pass

    def valid(self):
        """
        :return: Returns False if the respective party and spatial unit
        entities have not been set. Otherwise True.
        :rtype: bool
        """
        if self._party_renderer.entity is None:
            return False

        if self._sp_unit_renderer.entity is None:
            return False

        return True

    def minimumSizeHint(self):
        return QSize(320, 180)

    def sizeHint(self):
        return QSize(560, 315)

    def paintEvent(self, event):
        """
        Render social tenure relationship in the widget.
        :param event: Paint event handler.
        :type event: QPaintEvent
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        painter.save()

        width, height = self.width(), self.height()

        aspect_ratio = 16/9.0

        #We adjust the view port to respect the above aspect ratio
        adjusted_height = width * (1/aspect_ratio)

        if adjusted_height > height:
            adjusted_width = aspect_ratio * height
            adjusted_height = height
            height = adjusted_height
        else:
            adjusted_width = width

        painter.setViewport(
            0,
            (height - adjusted_height)/2,
            adjusted_width,
            adjusted_height
        )

        painter.setWindow(0, 0, 240, 135)

        end_point = QPointF(10.0, 120.0)
        start_point = QPointF(200.0,40.0)
        line = QLineF(start_point, end_point)

        painter.drawLine(line.toLine())

        #Draw arrow head
        arrow_tip_angle = 20
        ang_rad = math.radians(arrow_tip_angle)
        arrow_head_width = 10
        arrow_length = line.length()

        #Setup computation parameters
        cnt_factor = (arrow_head_width)/(math.tan(ang_rad) * arrow_length)
        cnt_point_delta = arrow_head_width/arrow_length

        #Get arrow base along the line
        arrow_base_x = end_point.x() - (line.dx() * cnt_factor)
        arrow_base_y = end_point.y() - (line.dy() * cnt_factor)

        #Get position of arrow points
        cnt_point_dx = -(line.dy() * cnt_point_delta)
        cnt_point_dy = line.dx() * cnt_point_delta

        #A1 position
        a1_x = arrow_base_x - cnt_point_dx
        a1_y = arrow_base_y - cnt_point_dy
        a1 = QPointF(a1_x, a1_y)

        line_a1 = QLineF(a1, end_point)
        painter.drawLine(line_a1)

        #A2 position
        a2_x = arrow_base_x + cnt_point_dx
        a2_y = arrow_base_y + cnt_point_dy
        a2 = QPointF(a2_x, a2_y)

        line_a2 = QLineF(a2, end_point)
        painter.drawLine(line_a2)

        painter.restore()

        #Draw outline
        painter.setPen(QColor('#ABB2B9'))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(QRect(0, 0, width, height))

if __name__ == '__main__':
    app = QApplication(sys.argv)

    test_win = QWidget()
    tenure_view = ProfileTenureView()

    layout = QGridLayout()
    layout.addWidget(tenure_view, 0, 0, 1, 1)
    test_win.setLayout(layout)
    test_win.show()

    sys.exit(app.exec_())