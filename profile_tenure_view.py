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

    def items_size(self):
        """
        Computes an appropriate width and height of an items' text separated
        by a new line.
        :return: Returns a size object that fits the items' text in the list.
        :rtype: QSize
        """
        fm = QFontMetrics(self.items_font)

        return fm.size(Qt.TextWordWrap, '\n'.join(self.items))

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
            sz = fm.size(Qt.TextWordWrap, '\n'.join(items_sub))
            multiline_items =

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

        #Render social tenure entity
        #Apply a gap of 25 between items (party, STR, spatial unit)
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