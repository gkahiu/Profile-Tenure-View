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
    QPolygonF,
    QTextLayout,
    QWidget
)
from PyQt4.QtCore import (
    QChar,
    QFile,
    QIODevice,
    QLineF,
    QPointF,
    QRect,
    QRectF,
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


class BaseTenureItem(QGraphicsItem):
    """Abstract class that provides core functionality for rendering entity and
    social tenure relationship objects corresponding to the entities in a
    given profile."""
    Type = QGraphicsItem.UserType + 1

    def __init__(self, parent=None, scene=None, **kwargs):
        super(BaseTenureItem, self).__init__(parent, scene)
        self.setFlag(QGraphicsItem.ItemIsMovable)

        self.pen = QPen(
            Qt.black,
            0.9,
            Qt.SolidLine,
            Qt.RoundCap,
            Qt.RoundJoin
        )

        #Display properties
        self._default_header = QApplication.translate(
            'ProfileTenureView',
            'Not Defined'
        )
        self.header = self._default_header
        self.items_title = ''
        self.icon_painter = kwargs.pop('icon_painter', None)
        self.items = []
        self.font_name = 'Consolas'
        self._entity = None

        #Distance between the primary shape and its shadow
        self.shadow_thickness = 4

        self._side = 156
        self._height = self._side
        self._start_pos = 10

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

    def type(self):
        return BaseTenureItem.Type

    def boundingRect(self):
        extra = self.pen.widthF() / 2.0

        return QRectF(
            self._start_pos - extra,
            self._start_pos - extra,
            self.width + self.shadow_thickness + extra,
            self.height + self.shadow_thickness + extra
        )

    def invalidate(self):
        """
        Reset the title and items.
        """
        self.header = self._default_header
        self.items = []

        self.update()

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
        return QFont(self.font_name, 12, 63)

    @property
    def items_title_font(self):
        """
        :return: Returns the font object used to render the items header text.
        :rtype: QFont
        """
        return QFont(self.font_name, 10)

    @property
    def items_font(self):
        """
        :return: Returns the font object used to render multiline items.
        :rtype: QFont
        """
        return QFont(self.font_name, 9)

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
        :return: Returns the logical width of the item.
        :rtype: float
        """
        return float(self._side + self.shadow_thickness)

    @property
    def height(self):
        """
        :return: Returns the logical height of the item. If
        auto_adjust_height is True then the height will be automatically
        adjusted to match number of items, else it will be equal to the width
        of the item.
        """
        return float(self._height + self.shadow_thickness)

    def _elided_text(self, font, text, width):
        #Returns elided version of the text if greater than the width
        fm = QFontMetrics(font)

        return unicode(fm.elidedText(text, Qt.ElideRight, width))

    def _elided_items(self, font, width):
        #Formats each item text to incorporate an elide if need be and
        # return the items in a list.
        return map(
            lambda item: self._elided_text(font, item, width),
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

    def _font_height(self, font, text):
        """
        Computes the height for the given font object.
        :param font: Font object.
        :type font: QFont
        :param text: Text
        :type text: str
        :return: Returns the minimum height for the given font object.
        :rtype: int
        """
        fm = QFontMetrics(font)

        return fm.size(Qt.TextSingleLine, text).height()

    def draw_text(self, painter, text, font, bounds, alignment=Qt.AlignCenter):
        """
        Provides a device independent mechanism for rendering fonts
        regardless of te device's resolution. By default, the text will be
        centred. This is a workaround for the font scaling issue for devices
        with different resolutions.
        :param painter: Painter object.
        :type painter: QPainter
        :param text: Text to be rendered.
        :type text: str
        :param font: Font for rendering the text.
        :type font: QFont
        :param bounds: Rect object which will provide the reference point for
        drawing the text.
        :type bounds: QRectF
        :param alignment: Qt enums used to describe alignment. AlignCenter is
        the default. Accepts bitwise OR for horizontal and vertical flags.
        :type alignment: int
        """
        layout = QTextLayout(text, font)

        layout.beginLayout()
        #Create the required number of lines in the layout
        while layout.createLine().isValid():
            pass
        layout.endLayout()

        y = 0
        max_width = 0

        #Set line positions relative to the layout
        for i in range(layout.lineCount()):
            line = layout.lineAt(i)
            max_width = max(max_width, line.naturalTextWidth())
            line.setPosition(QPointF(0, y))
            y += line.height()

        #Defaults
        start_x = bounds.left()
        start_y = bounds.top()

        #Horizontal flags
        if (alignment & Qt.AlignLeft) == Qt.AlignLeft:
            start_x = bounds.left()
        elif (alignment & Qt.AlignCenter) == Qt.AlignCenter or \
                        (alignment & Qt.AlignHCenter) == Qt.AlignHCenter:
            start_x = bounds.left() + (bounds.width() - max_width) / 2.0

        #Vertical flags
        if (alignment == Qt.AlignTop) == Qt.AlignTop:
            start_y = bounds.top()
        elif (alignment & Qt.AlignCenter) == Qt.AlignCenter or \
                        (alignment & Qt.AlignVCenter) == Qt.AlignVCenter:
            start_y = bounds.top() + (bounds.height() - y) / 2.0

        layout.draw(painter, QPointF(start_x, start_y))

    def paint(self, painter, option, widget=None):
        """
        Performs the painting of the tenure item based on the object's
        attributes.
        :param painter: Performs painting operation on the item.
        :type painter: QPainter
        :param option: Provides style option for the item.
        :type option: QStyleOptionGraphicsItem
        :param widget: Provides points to the widget that is being painted on.
        :type widget: QWidget
        """
        shadow_start_pos = self._start_pos + self.shadow_thickness

        #Use height of subsections to compute the appropriate height
        header_height = self._font_height(self.header_font, self.header)
        items_title_height = self._font_height(
            self.items_title_font,
            self.items_title
        )
        margin = 1

        fixed_height = header_height + items_title_height + (6 * margin)

        if self.auto_adjust_height():
            items_height = self.items_size(self.items).height() + 2
            main_item_height = max(self._side, fixed_height + items_height)

        else:
            items_height = self._side - fixed_height
            main_item_height = self._side

        self._height = main_item_height

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

        painter.setPen(self.pen)
        painter.setBrush(self._brush)

        #Main item outline
        painter.drawRect(main_item_rect)
        line_y_pos = header_height + margin * 2
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
            self.header_font,
            self.header,
            header_rect.width()
        )
        #print elided_header
        self.draw_text(painter, elided_header, self.header_font, header_rect)

        #Draw items header
        items_title_rect = QRect(
            header_start_pos + 1,
            header_height + items_title_height - 1,
            self._side - (margin * 4),
            items_title_height
        )
        painter.setFont(self.items_title_font)
        painter.setPen(QColor('#c3b49c'))
        items_title_brush = QBrush(self._gradient_dark)
        painter.setBrush(items_title_brush)
        painter.drawRect(items_title_rect)

        #Adjust left margin of items title
        items_title_rect.adjust(1, 0, 0, 0)
        painter.setPen(self._normal_text_color)
        self.draw_text(
            painter,
            self.items_title,
            self.items_title_font,
            items_title_rect
        )

        #Items listing
        items_margin = 6
        items_vertical_pos = header_height + items_title_height + 16
        items_w = self._side - (items_margin * 2)
        items_rect = QRect(
            header_start_pos + items_margin,
            items_vertical_pos,
            items_w,
            items_height
        )

        #Draw if there are items
        if len(self.items) > 0:
            painter.setFont(self.items_font)
            painter.setPen(self._text_item_color)
            multiline_items = self._elided_items(self.items_font, items_w)

            #If auto-adjust is disabled then extract subset that will fit
            if not self.auto_adjust_height():
                multiline_items = self.items_by_height(
                    items_height,
                    multiline_items
                )

            #QTextLayout requires the unicode character of the line separator
            multiline_items = u'\u2028'.join(multiline_items)
            self.draw_text(
                painter,
                multiline_items,
                self.items_font,
                items_rect,
                Qt.AlignLeft|Qt.AlignTop
            )


class EntityItem(BaseTenureItem):
    """
    Represents a Party or a SpatialUnit items in a profile's social tenure
    relationship.
    """
    Type = QGraphicsItem.UserType + 2

    def __init__(self, *args, **kwargs):
        super(EntityItem, self).__init__(*args, **kwargs)
        columns = QApplication.translate(
            'ProfileTenureView',
            'columns'
        )
        self.items_title = u'<<{0}>>'.format(columns)

    def type(self):
        return EntityItem.Type

    def _on_set_entity(self):
        if not self._entity is None:
            self.header = self.entity.short_name
            self.items = self.entity.columns.keys()
            self.update()


class TenureRelationshipItem(BaseTenureItem):
    """
    Renders the profile's tenure relationship by listing the tenure types.
    """
    Type = QGraphicsItem.UserType + 3

    def __init__(self, *args, **kwargs):
        super(TenureRelationshipItem, self).__init__(*args, **kwargs)
        tenure_types = QApplication.translate(
            'ProfileTenureView',
            'tenure types'
        )
        self.items_title = u'<<{0}>>'.format(tenure_types)
        self.header = QApplication.translate(
            'ProfileTenureView',
            'Social Tenure'
        )

        self.items = ['Ownership', 'Tenancy', 'Farming Rights']

    def type(self):
        return TenureRelationshipItem.Type

    def auto_adjust_height(self):
        #Base class override
        return False

    def _on_set_entity(self):
        if not self._entity is None:
            self.items = self.entity.tenure_type_lookup.value_list.lookups()
            self.update()


class TenureDocumentItem(BaseTenureItem):
    """
    Renders the document types for the social tenure relationship.
    """
    Type = QGraphicsItem.UserType + 4

    def __init__(self, *args, **kwargs):
        super(TenureDocumentItem, self).__init__(*args, **kwargs)
        tenure_types = QApplication.translate(
            'ProfileTenureView',
            'document types'
        )
        self.items_title = u'<<{0}>>'.format(tenure_types)
        self.header = QApplication.translate(
            'ProfileTenureView',
            'Documents'
        )

    def type(self):
        return TenureDocumentItem.Type

    def auto_adjust_height(self):
        #Base class override
        return False

    def _on_set_entity(self):
        if not self._entity is None:
            supporting_doc = self.entity.supporting_doc
            self.items = supporting_doc.doc_type.value_list.lookups()

            self.update()


class ProfileTenureView(QGraphicsView):
    """
    A widget for rendering a profile's social tenure relationship. It also
    includes functionality for saving the view as an image.
    """
    MIN_DPI = 72
    MAX_DPI = 600

    def __init__(self, parent=None, profile=None):
        super(ProfileTenureView, self).__init__(parent)

        #Init items
        #Container for party entities and corresponding items
        self._default_party_item = EntityItem()
        self._party_items = {}
        self._sp_item = EntityItem()
        self._str_item = TenureRelationshipItem()
        self._supporting_doc_item = TenureDocumentItem()

        self.profile = profile

        scene_rect = QRectF(0, 0, 960, 540)

        scene = QGraphicsScene(self)
        scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        scene.setSceneRect(scene_rect)

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

        self.setScene(scene)

        #Add items to view
        self.scene().addItem(self._default_party_item)
        self.scene().addItem(self._str_item)
        self.scene().addItem(self._sp_item)
        self.scene().addItem(self._supporting_doc_item)

        #Position items
        self._default_party_item.setPos(200, 20)
        self._str_item.setPos(400, 20)
        self._sp_item.setPos(600, 20)
        self._supporting_doc_item.setPos(400, 220)

        #Ensure vertical scroll is at the top
        self.centerOn(480.0, 20.0)

    @property
    def profile(self):
        """
        :return: The profile object being rendered.
        :rtype: Profile
        """
        return self._profile

    def _update_profile(self):
        #Update profile objects and render
        if self._profile is None:
            return

        str_ent = self._profile.social_tenure
        # Set renderer entities
        self._sp_item.entity = str_ent.spatial_unit
        self._str_item.entity = str_ent
        self._supporting_doc_item.entity = str_ent

    @profile.setter
    def profile(self, profile):
        """
        Sets the profile object whose STR view is to rendered.
        :param profile: Profile object to be rendered.
        :type profile: Profile
        """
        self._profile = profile

        self._update_profile()

    def set_spatial_unit(self, spatial_unit):
        """
        Set the spatial unit entity.
        :param spatial_unit: Entity corresponding to a spatial unit in a
        profile's STR relationship.
        :type spatial_unit: Entity
        """
        self._sp_item.entity = spatial_unit

        self._sp_item.update()

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
        res = resolution/25.4

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

    def valid(self):
        """
        :return: Returns False if the respective party and spatial unit
        entities have not been set. Otherwise True.
        :rtype: bool
        """
        #TODO: Refactor
        if self._party_renderer.entity is None:
            return False

        if self._sp_unit_renderer.entity is None:
            return False

        return True

    def minimumSizeHint(self):
        return QSize(480, 270)

    def sizeHint(self):
        return QSize(560, 315)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    test_win = QWidget()
    tenure_view = ProfileTenureView()

    #Test image
    p = 'D:/Temp/STR_Image.png'
    status, msg = tenure_view.save_image_to_file(p, 300)

    layout = QGridLayout()
    layout.addWidget(tenure_view, 0, 0, 1, 1)
    test_win.setLayout(layout)
    test_win.show()

    sys.exit(app.exec_())