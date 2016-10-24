"""
/***************************************************************************
Name                 : ProfileTenureView
Description          : A widget for rendering a profile's social tenure
                       relationship.
Date                 : 9/October/2016
copyright            : John Kahiu
email                : gkahiu at gmail dot com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
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
    QPolygonF,
    QWidget
)
from PyQt4.QtCore import (
    QLineF,
    QPointF,
    QRect,
    QSize,
    Qt
)


class ArrowItem(object):
    """
    Renders an arrow object (with line and arrow head) from one point to
    another. The arrow head size can be customized by specifying the angle
    and width of the arrow base.
    """
    def __init__(self, start_point, end_point, base_width=None,
                 tip_angle=None, fill_arrow_head=False):
        """
        Class constructor
        :param start_point: Arrow start point.
        :type start_point: QPointF
        :param end_point: Arrow end point.
        :type end_point: QPointF
        :param base_width: Width (in pixels) of the arrow base. If not
        specified, it defaults to 20.0.
        :type base_width: float
        :param tip_angle: Angle (in radians) between the two line components
        at the tip of the arrow. If not specified, it defaults to
        math.radians(40.0).
        Minimum math.radians(10.0)
        Maximum math.radians(<90.0)
        :type tip_angle: float
        :param fill_arrow_head: True to close and fill the arrow head with
        the specified pen and brush settings. Defaults to False.
        :type fill_arrow_head: bool
        """
        self._start_point = start_point
        self._end_point = end_point
        self._line = QLineF(self._start_point, self._end_point)

        self.base_width = base_width
        if self.base_width is None:
            self.base_width = 7

        self._angle = tip_angle
        if tip_angle is None:
            self._angle = math.radians(50.0)

        self.fill_arrow_head = fill_arrow_head

        self.pen = QPen(
            Qt.black,
            0,
            Qt.SolidLine,
            Qt.RoundCap,
            Qt.MiterJoin
        )
        self.brush = QBrush(Qt.black)

        self._arrow_points = []

    @property
    def start_point(self):
        """
        :return: Returns the arrow start point.
        :rtype: QPointF
        """
        return self._start_point

    @property
    def end_point(self):
        """
        :return: Returns the arrow end point.
        :rtype: QPointF
        """
        return self._end_point

    @property
    def line(self):
        """
        :return: Returns the line component of the arrow.
        :rtype: QLineF
        """
        return self._line

    @property
    def angle(self):
        """
        :return: Returns the value of the angle at the tip in radians.
        :rtype: float
        """
        return self._angle

    @angle.setter
    def angle(self, angle):
        """
        Sets the value of the angle to be greater than or equal to
        math.radians(10.0) and less than math.radians(90).
        :param angle: Angle at the tip of the arrow in radians.
        :type angle: float
        """
        min_angle = math.radians(10.0)
        max_angle = math.radians(90)

        if angle < min_angle:
            self._angle = min_angle
        elif angle > max_angle:
            self._angle = max_angle
        else:
            self._angle = angle

    @property
    def arrow_points(self):
        """
        :return: Returns a collection of points used to draw the arrow head.
        :rtype: list(QPointF)
        """
        return self._arrow_points

    def paint(self, widget, painter, event):
        """
        Performs the painting of the arrow item.
        :param widget: The calling parent widget.
        :type widget: QWidget
        :param painter: Painter object that has already been setup.
        :type painter: QPainter
        :param event: Paint event of the calling widget.
        :type event: QPaintEvent
        """
        if self._start_point == self._end_point:
            return

        arrow_length = self._line.length()

        #Setup computation parameters
        cnt_factor = (self.base_width/2.0)/(math.tan(self._angle/2.0) * arrow_length)
        cnt_point_delta = (self.base_width/2.0)/arrow_length

        #Get arrow base along the line
        arrow_base_x = self._end_point.x() - (self._line.dx() * cnt_factor)
        arrow_base_y = self._end_point.y() - (self._line.dy() * cnt_factor)

        #Get deltas to arrow points from centre point of arrow base
        cnt_point_dx = -(self._line.dy() * cnt_point_delta)
        cnt_point_dy = self._line.dx() * cnt_point_delta

        #Compute absolute arrow positions
        A1 = QPointF(arrow_base_x - cnt_point_dx, arrow_base_y - cnt_point_dy)
        A2 = QPointF(arrow_base_x + cnt_point_dx, arrow_base_y + cnt_point_dy)

        #Update arrow points
        self._arrow_points = [A1, A2, self._end_point]

        painter.save()

        painter.setPen(self.pen)

        painter.drawLine(self._line)

        if not self.fill_arrow_head:
            painter.drawLine(A1, self._end_point)
            painter.drawLine(self._end_point, A2)

        else:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.brush)

            arrow_poly = QPolygonF(self._arrow_points)
            painter.drawPolygon(arrow_poly)

        painter.restore()


class BaseTenureItemRenderer(object):
    """
    Abstract class that provides core functionality for rendering entity and
    social tenure relationship objects corresponding to the entities in a
    given profile.
    """
    def __init__(self, **kwargs):
        self._default_header = QApplication.translate(
            'ProfileTenureView',
            'Not Defined'
        )
        self.header = self._default_header
        self.items_title = ''
        self.icon_painter = kwargs.pop('icon_painter', None)
        self.items = ['first_name', 'last_name', 'gender','date_of_birth', 'marital_status', 'education', 'origin', 'monthly_income']
        self.font_name = 'Consolas'
        self._entity = None

        #Distance between the primary shape and its shadow
        self.shadow_thickness = 2

        self._side = 58
        self._start_pos = 4

        #The start and stop positions match the size of the item
        stop_position = self._start_pos + self._side

        #Main item gradient
        self._gradient = QLinearGradient(
            self._start_pos,
            self._start_pos,
            stop_position,
            stop_position
        )

        self._gradient_light = QColor('#fcf2e3')
        self._gradient_dark = QColor('#e9dac2')
        self._gradient.setColorAt(0.0, self._gradient_light)
        self._gradient.setColorAt(1.0, self._gradient_dark)
        self._brush = QBrush(self._gradient)

        #Shadow gradient
        #The start and stop positions match the size of the item
        shadow_start_pos = self._start_pos + self.shadow_thickness
        shadow_stop_pos = self._start_pos + self._side + self.shadow_thickness
        self._shadow_gradient = QLinearGradient(
            shadow_start_pos,
            shadow_start_pos,
            shadow_stop_pos,
            shadow_stop_pos
        )
        self._shadow_gradient.setColorAt(0.0, QColor('#f7f8f9'))
        self._shadow_gradient.setColorAt(1.0, QColor('#d1d1d1'))
        self._brush = QBrush(self._gradient)

        self._text_highlight_color = QColor('#E74C3C')
        self._text_item_color = QColor('#CC0000')
        self._normal_text_color = Qt.black

    @property
    def brush(self):
        """
        :return: Returns the brush used for rendering the entity item.
        :rtype: QBrush
        """
        return self._brush

    @property
    def header_font(self):
        """
        :return: Returns the font object used to render the header text.
        :rtype: QFont
        """
        return QFont(self.font_name, 5, 75)

    @property
    def items_title_font(self):
        """
        :return: Returns the font object used to render the items header text.
        :rtype: QFont
        """
        return QFont(self.font_name, 4)

    @property
    def items_font(self):
        """
        :return: Returns the font object used to render multiline items.
        :rtype: QFont
        """
        return QFont(self.font_name, 4)

    @property
    def entity(self):
        """
        :return: Returns the entity associated with the rendered.
        :rtype: Entity
        """
        return self._entity

    def auto_adjust_height(self):
        """
        :return: True if the height should be automatically adjusted to fit
        the number of items specified. Otherwise, False; in this case, the
        height is equal to the default height of the item. Items that exceed
        the height of the items area will not be shown.
        To be overridden by sub-classes.
        :rtype: bool
        """
        return True

    @entity.setter
    def entity(self, entity):
        """
        Sets the current entity object.
        :param entity: Entity object.
        :type entity: Entity
        """
        self._entity = entity
        self._on_set_entity()

    def _on_set_entity(self):
        """
        Update attributes based on the entity's attributes. To be implemented
        by subclasses.
        """
        raise NotImplementedError

    @property
    def width(self):
        """
        :return: Returns the logical width of the item. This equals the
        height since the item is a square.
        """
        return self._side + self.shadow_thickness

    def _elided_text(self, painter, text, width):
        #Returns elided version of the text if greater than the width
        fm = painter.fontMetrics()

        return unicode(fm.elidedText(text, Qt.ElideRight, width))

    def _elided_items(self, painter, width):
        #Formats each item text to incorporate an elide if need be and
        # return the items in a list.
        return map(
            lambda item: self._elided_text(painter, item, width),
            self.items
        )

    def items_size(self, items):
        """
        Computes an appropriate width and height of an items' text separated
        by a new line.
        :param items: Iterable containing string items for which the size
        will be computed.
        :type items: list
        :return: Returns a size object that fits the items' text in the list.
        :rtype: QSize
        """
        fm = QFontMetrics(self.items_font)

        return fm.size(Qt.TextWordWrap, '\n'.join(items))

    def items_by_height(self, height, items):
        """
        :param height: Height in pixels in which the subset of items will fit.
        :type height: int
        :return: Returns a subset of items which fit the specified height.
        :rtype: list
        """
        items_sub = []

        fm = QFontMetrics(self.items_font)

        for i in items:
            sz = self.items_size(items_sub)
            if sz.height() > height:
                break

            items_sub.append(i)

        return items_sub

    def paint(self, widget, painter, event):
        """
        Performs the painting of the tenure item based on the object's
        attributes.
        :param widget: The calling parent widget.
        :type widget: QWidget
        :param painter: Painter object that has already been setup.
        :type painter: QPainter
        :param event: Paint event of the calling widget.
        :type event: QPaintEvent
        """
        shadow_start_pos = self._start_pos + self.shadow_thickness

        #Use height of subsections to compute the appropriate height
        header_height = 10
        items_title_height = 8
        margin = 1

        fixed_height = header_height + items_title_height + (6 * margin)

        if self.auto_adjust_height():
            items_height = self.items_size(self.items).height()
            main_item_height = max(self._side, fixed_height + items_height)

        else:
            items_height = self._side - fixed_height
            main_item_height = self._side

        shadow_rect = QRect(
            shadow_start_pos,
            shadow_start_pos,
            self._side,
            main_item_height
        )

        main_item_rect = QRect(
            self._start_pos,
            self._start_pos,
            self._side,
            main_item_height
        )

        painter_pen = painter.pen()
        painter_pen.setColor(self._normal_text_color)
        painter_pen.setWidth(0)

        #Create shadow effect using linear gradient
        painter.setBrush(self._shadow_gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(shadow_rect)

        painter.setPen(painter_pen)
        painter.setBrush(self._brush)

        #Main item outline
        painter.drawRect(main_item_rect)
        line_y_pos = 12
        painter.drawLine(
            self._start_pos,
            self._start_pos + line_y_pos,
            self._start_pos + self._side,
            self._start_pos + line_y_pos
        )

        #Draw header text
        header_start_pos = self._start_pos + margin
        header_rect = QRect(
            header_start_pos,
            header_start_pos,
            self._side - (margin * 2),
            header_height
        )

        painter.setFont(self.header_font)

        if self.header == self._default_header:
            painter.setPen(self._text_highlight_color)
        else:
            painter.setPen(self._normal_text_color)

        elided_header = self._elided_text(
            painter,
            self.header,
            header_rect.width()
        )
        painter.drawText(header_rect, Qt.AlignCenter, elided_header)

        #Draw items header
        items_title_rect = QRect(
            header_start_pos,
            header_height + items_title_height,
            self._side - (margin * 2),
            7
        )
        painter.setFont(self.items_title_font)
        painter.setPen(QColor('#c3b49c'))
        items_title_brush = QBrush(self._gradient_dark)
        painter.setBrush(items_title_brush)
        painter.drawRect(items_title_rect)

        #Adjust left margin of items title
        items_title_rect.adjust(1, 0, 0, 0)
        painter.setPen(self._normal_text_color)
        painter.drawText(items_title_rect, Qt.AlignLeft, self.items_title)

        #Items listing
        items_margin = 4
        items_vertical_pos = header_height + items_title_height + 7
        items_w = self._side - (items_margin * 2)
        items_rect = QRect(
            header_start_pos + items_margin,
            items_vertical_pos,
            items_w,
            items_height + (margin * 2)
        )

        painter.setFont(self.items_font)
        painter.setPen(self._text_item_color)
        multiline_items = self._elided_items(painter, items_w)

        #If auto-adjust is disabled then extract subset that will fit
        if not self.auto_adjust_height():
            multiline_items = self.items_by_height(
                items_height,
                multiline_items
            )

        multiline_items = '\n'.join(multiline_items)
        painter.drawText(items_rect, Qt.AlignLeft, multiline_items)


class EntityRenderer(BaseTenureItemRenderer):
    """
    Renders Party and SpatialUnit items in a profile's social tenure
    relationship.
    """
    def __init__(self, **kwargs):
        BaseTenureItemRenderer.__init__(self, **kwargs)
        columns = QApplication.translate(
            'ProfileTenureView',
            'columns'
        )
        self.items_title = u'<<{0}>>'.format(columns)

    def _on_set_entity(self):
        if not self._entity is None:
            self.header = self.entity.short_name
            self.items = self.entity.columns.keys()


class TenureRelationshipRenderer(BaseTenureItemRenderer):
    """
    Renders the profile's tenure relationship by listing the tenure types.
    """
    def __init__(self, **kwargs):
        BaseTenureItemRenderer.__init__(self, **kwargs)
        tenure_types = QApplication.translate(
            'ProfileTenureView',
            'tenure types'
        )
        self.items_title = u'<<{0}>>'.format(tenure_types)
        self.header = QApplication.translate(
            'ProfileTenureView',
            'Social Tenure'
        )
        self.items = ['Tenancy', 'Ownership', 'Lease']

    def auto_adjust_height(self):
        #Base class override
        return False

    def _on_set_entity(self):
        if not self._entity is None:
            self.items = self.entity.tenure_type_lookup.value_list.lookups()


class TenureDocumentRenderer(BaseTenureItemRenderer):
    """
    Renders the document types for the social tenure relationship.
    """
    def __init__(self, **kwargs):
        BaseTenureItemRenderer.__init__(self, **kwargs)
        tenure_types = QApplication.translate(
            'ProfileTenureView',
            'document types'
        )
        self.items_title = u'<<{0}>>'.format(tenure_types)
        self.header = QApplication.translate(
            'ProfileTenureView',
            'Supporting Documents'
        )

    def auto_adjust_height(self):
        #Base class override
        return False

    def _on_set_entity(self):
        if not self._entity is None:
            supporting_doc = self.entity.supporting_doc
            self.items = supporting_doc.doc_type.value_list.lookups()


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

        #Set STR item renderers
        self._party_renderer = EntityRenderer()
        self._sp_unit_renderer = EntityRenderer()
        self._str_renderer = TenureRelationshipRenderer()
        self._supporting_doc_renderer = TenureDocumentRenderer()

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

        #Render party entity
        painter.translate(0, 0)
        self._party_renderer.paint(self, painter, event)

        arrow = ArrowItem(QPointF(62.0,30.0), QPointF(89.0,30.0), fill_arrow_head=True)
        arrow.paint(self, painter, event)

        #Render social tenure entity
        #Apply a gap of 25 pixels between items (party, STR, spatial unit)
        painter.translate(85, 0)
        self._str_renderer.paint(self, painter, event)

        #Render spatial unit entity
        painter.translate(85, 0)
        self._sp_unit_renderer.paint(self, painter, event)

        #Render supporting documents entity
        painter.translate(-85, 70)
        self._supporting_doc_renderer.paint(self, painter, event)

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