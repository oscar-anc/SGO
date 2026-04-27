# coding:utf-8
from enum import Enum

from theme import QSSA
from PySide6.QtCore import QFile, QPointF, QRectF, Qt, Property
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QAbstractButton
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtXml import QDomDocument

from .._rc import resource


class TitleBarButtonState(Enum):
    """ Title bar button state """
    NORMAL = 0
    HOVER = 1
    PRESSED = 2


class TitleBarButton(QAbstractButton):
    """ Title bar button """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setCursor(Qt.ArrowCursor)
        self.setFixedSize(46, QSSA.get('titlebar_fixed_height', 32))
        self._state = TitleBarButtonState.NORMAL

        # icon color
        self._normalColor = QColor(0, 0, 0)
        self._hoverColor = QColor(0, 0, 0)
        self._pressedColor = QColor(0, 0, 0)

        # background color
        self._normalBgColor = QColor(0, 0, 0, 0)
        self._hoverBgColor = QColor(0, 0, 0, 26)
        self._pressedBgColor = QColor(0, 0, 0, 51)

    def setState(self, state):
        """ set the state of button

        Parameters
        ----------
        state: TitleBarButtonState
            the state of button
        """
        self._state = state
        self.update()

    def isPressed(self):
        """ whether the button is pressed """
        return self._state == TitleBarButtonState.PRESSED

    def getNormalColor(self):
        """ get the icon color of the button in normal state """
        return self._normalColor

    def getHoverColor(self):
        """ get the icon color of the button in hover state """
        return self._hoverColor

    def getPressedColor(self):
        """ get the icon color of the button in pressed state """
        return self._pressedColor

    def getNormalBackgroundColor(self):
        """ get the background color of the button in normal state """
        return self._normalBgColor

    def getHoverBackgroundColor(self):
        """ get the background color of the button in hover state """
        return self._hoverBgColor

    def getPressedBackgroundColor(self):
        """ get the background color of the button in pressed state """
        return self._pressedBgColor

    def setNormalColor(self, color):
        """ set the icon color of the button in normal state

        Parameters
        ----------
        color: QColor
            icon color
        """
        self._normalColor = QColor(color)
        self.update()

    def setHoverColor(self, color):
        """ set the icon color of the button in hover state

        Parameters
        ----------
        color: QColor
            icon color
        """
        self._hoverColor = QColor(color)
        self.update()

    def setPressedColor(self, color):
        """ set the icon color of the button in pressed state

        Parameters
        ----------
        color: QColor
            icon color
        """
        self._pressedColor = QColor(color)
        self.update()

    def setNormalBackgroundColor(self, color):
        """ set the background color of the button in normal state

        Parameters
        ----------
        color: QColor
            background color
        """
        self._normalBgColor = QColor(color)
        self.update()

    def setHoverBackgroundColor(self, color):
        """ set the background color of the button in hover state

        Parameters
        ----------
        color: QColor
            background color
        """
        self._hoverBgColor = QColor(color)
        self.update()

    def setPressedBackgroundColor(self, color):
        """ set the background color of the button in pressed state

        Parameters
        ----------
        color: QColor
            background color
        """
        self._pressedBgColor = QColor(color)
        self.update()

    def enterEvent(self, e):
        self.setState(TitleBarButtonState.HOVER)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.setState(TitleBarButtonState.NORMAL)
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return

        self.setState(TitleBarButtonState.PRESSED)
        super().mousePressEvent(e)

    def _getColors(self):
        """ get the icon color and background color """
        if self._state == TitleBarButtonState.NORMAL:
            return self._normalColor, self._normalBgColor
        elif self._state == TitleBarButtonState.HOVER:
            return self._hoverColor, self._hoverBgColor

        return self._pressedColor, self._pressedBgColor

    normalColor = Property(QColor, getNormalColor, setNormalColor)
    hoverColor = Property(QColor, getHoverColor, setHoverColor)
    pressedColor = Property(QColor, getPressedColor, setPressedColor)
    normalBackgroundColor = Property(
        QColor, getNormalBackgroundColor, setNormalBackgroundColor)
    hoverBackgroundColor = Property(
        QColor, getHoverBackgroundColor, setHoverBackgroundColor)
    pressedBackgroundColor = Property(
        QColor, getPressedBackgroundColor, setPressedBackgroundColor)


class SvgTitleBarButton(TitleBarButton):
    """ Title bar button using svg icon """

    def __init__(self, iconPath, parent=None):
        """
        Parameters
        ----------
        iconPath: str
            the path of icon

        parent: QWidget
            parent widget
        """
        super().__init__(parent)
        self._svgDom = QDomDocument()
        self.setIcon(iconPath)

    def setIcon(self, iconPath):
        """ set the icon of button

        Parameters
        ----------
        iconPath: str
            the path of icon
        """
        f = QFile(iconPath)
        f.open(QFile.ReadOnly)
        self._svgDom.setContent(f.readAll())
        f.close()

    def paintEvent(self, e):
        painter = QPainter(self)
        color, bgColor = self._getColors()

        # draw background
        painter.setBrush(bgColor)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        # draw icon
        color = color.name()
        pathNodes = self._svgDom.elementsByTagName('path')
        for i in range(pathNodes.length()):
            element = pathNodes.at(i).toElement()
            element.setAttribute('stroke', color)

        renderer = QSvgRenderer(self._svgDom.toByteArray())
        # Fixed 16px icon height — same absolute size as Min/Max icons (10px line/rect).
        # Using fixed px ensures visual parity regardless of titlebar height changes.
        # Width is calculated from SVG aspect ratio to avoid distortion.
        bw = self.width()
        bh = self.height()
        vb = renderer.viewBox()
        svg_ratio = (vb.width() / vb.height()) if vb.height() > 0 else 1.5
        icon_h = 20.0                # fixed — slightly larger than min/max line for X weight
        icon_w = icon_h * svg_ratio  # ~30px width for 15.875x10.583 viewBox
        cx = (bw - icon_w) / 2
        cy = (bh - icon_h) / 2
        renderer.render(painter, QRectF(cx, cy, icon_w, icon_h))


class MinimizeButton(TitleBarButton):
    """ Minimize button """

    def paintEvent(self, e):
        painter = QPainter(self)
        color, bgColor = self._getColors()

        # Background
        painter.setBrush(bgColor)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        # Minimize icon from svgs.py — 14x14 centered
        from svgs import get_svg_minimize_btn
        from PySide6.QtCore import QByteArray
        svg_data = get_svg_minimize_btn(color.name())
        renderer = QSvgRenderer(QByteArray(svg_data.encode()))
        icon_sz = 14.0  # consistent 14px for all titlebar icons
        cx = (self.width()  - icon_sz) / 2
        cy = (self.height() - icon_sz) / 2
        renderer.render(painter, QRectF(cx, cy, icon_sz, icon_sz))


class MaximizeButton(TitleBarButton):
    """ Maximize button """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._isMax = False

    def setMaxState(self, isMax):
        """ update the maximized state and icon """
        if self._isMax == isMax:
            return

        self._isMax = isMax
        self.setState(TitleBarButtonState.NORMAL)

    def paintEvent(self, e):
        painter = QPainter(self)
        color, bgColor = self._getColors()

        # Background
        painter.setBrush(bgColor)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        # Maximize/Restore icon from svgs.py — 14x14 centered
        from svgs import get_svg_maximize_btn, get_svg_restore_btn
        from PySide6.QtCore import QByteArray
        svg_fn = get_svg_restore_btn if self._isMax else get_svg_maximize_btn
        svg_data = svg_fn(color.name())
        renderer = QSvgRenderer(QByteArray(svg_data.encode()))
        icon_sz = 14.0  # consistent 14px for all titlebar icons
        cx = (self.width()  - icon_sz) / 2
        cy = (self.height() - icon_sz) / 2
        renderer.render(painter, QRectF(cx, cy, icon_sz, icon_sz))


class CloseButton(TitleBarButton):
    """ Close button — uses get_svg_close_btn from svgs.py """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHoverColor(Qt.white)
        self.setPressedColor(Qt.white)
        self.setHoverBackgroundColor(QColor(232, 17, 35))
        self.setPressedBackgroundColor(QColor(241, 112, 122))

    def paintEvent(self, e):
        painter = QPainter(self)
        color, bgColor = self._getColors()
        painter.setBrush(bgColor)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())
        from svgs import get_svg_close_btn
        from PySide6.QtCore import QByteArray
        renderer = QSvgRenderer(QByteArray(get_svg_close_btn(color.name()).encode()))
        # 18px matches visual weight of Min/Max 14px icons (Close viewBox is 14x14)
        icon_sz = 18.0
        cx = (self.width()  - icon_sz) / 2
        cy = (self.height() - icon_sz) / 2
        renderer.render(painter, QRectF(cx, cy, icon_sz, icon_sz))
