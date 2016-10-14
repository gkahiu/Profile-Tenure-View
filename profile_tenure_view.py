"""
/***************************************************************************
Name                 : ProfileTenureView
Description          : A widget for rendering a profile's social tenure
                       relationship.
Date                 : 9/October/2016
copyright            : (C) 2016 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
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

from PyQt4.QtGui import (
    QApplication,
    QBrush,
    QColor,
    QFont,
    QGridLayout,
    QLinearGradient,
    QPainter,
    QPaintEvent,
    QPalette,
    QPen,
    QWidget
)
from PyQt4.QtCore import (
    QRect,
    QSize,
    Qt
)


class BaseTenureItemRenderer(object):
    """
    Abstract class that provides core functionality for rendering entity and
    social tenure relationship objects corresponding to the entities in a
    given profile.
    """
    def __init__(self, **kwargs):
        self._default_header = QApplication.translate(
            'ProfileTenureView',
            '<<not set>>'
        )
        self.header = self._default_header
        self.items_title = ''
        self.icon_painter = kwargs.pop('icon_painter', None)
        self.items = []
        self.font_name = 'Franklin Gothic Book'
        self._entity = None

        #Distance between the primary shape and its shadow
        self.shadow_thickness = 2

        self._side = 58
        self._start_pos = 5

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
        self._text_column_color = QColor('#cc0000')
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
        return QFont(self.font_name, 6, 75)

    @property
    def items_title_font(self):
        """
        :return: Returns the font object used to render the items header text.
        :rtype: QFont
        """
        return QFont(self.font_name, 5)

    @property
    def entity(self):
        """
        :return: Returns the entity associated with the rendered.
        :rtype: Entity
        """
        return self._entity

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

    def _elided_text(self, text, font_metrics, width):
        #Returns elided version of the text if greater than the width
        return font_metrics.elidedText(text, Qt.ElideRight, width)

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

        shadow_rect = QRect(
            shadow_start_pos,
            shadow_start_pos,
            self._side,
            self._side
        )

        item_rect = QRect(
            self._start_pos,
            self._start_pos,
            self._side,
            self._side
        )

        painter_pen = painter.pen()
        painter_pen.setWidth(1)

        #Create shadow effect using linear gradient
        painter.setBrush(self._shadow_gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(shadow_rect)

        painter.setPen(painter_pen)
        painter.setBrush(self._brush)

        #Main item outline
        painter.drawRect(item_rect)
        line_y_pos = 12
        painter.drawLine(
            self._start_pos,
            self._start_pos + line_y_pos,
            self._start_pos + self._side,
            self._start_pos + line_y_pos
        )

        fm = painter.fontMetrics()

        #Draw header text
        margin = 1
        header_start_pos = self._start_pos + margin
        header_height = 10
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

        temp_title_brush = QBrush(self._gradient_dark)
        painter.fillRect(header_rect, temp_title_brush)
        painter.drawText(header_rect, Qt.AlignCenter, self.header)

        #Draw items header
        items_title_rect = QRect(
            header_start_pos,
            header_height + 8,
            self._side - (margin * 2),
            8
        )
        painter.setFont(self.items_title_font)
        painter.setPen(self._normal_text_color)
        items_title_brush = QBrush(self._gradient_dark)
        painter.fillRect(items_title_rect, items_title_brush)
        painter.drawText(items_title_rect, Qt.AlignLeft, self.items_title)


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
            'Social Tenure Relationship'
        )

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
        self._profile = profile
        self.update()

    def save_tenure_view(self, path):
        """
        Saves the profile tenure view as an image.
        :param path: Absolute path where the image will be saved.
        :type path: str
        :return: Returns True if the operation succeeded, otherwise False.
        :rtype: bool
        """
        pass

    def minimumSizeHint(self):
        return QSize(320, 180)

    def sizeHint(self):
        return QSize(480, 270)

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

        #We adjust the viewport to respect the above aspect ratio
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

        painter.scale(width/240.0, height/135.0)

        #Render party entity
        painter.translate(0, 0)
        self._party_renderer.paint(self, painter, event)

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