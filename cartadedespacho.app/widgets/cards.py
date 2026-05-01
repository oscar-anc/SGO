# coding: utf-8
"""
widgets/card.py — Card container widgets.

CardWidget:            Collapsible card with navy header and body.
InsuredGroupCard:      Transparent-header accordion grouping by insured party.
EndorsementPolicyCard: Navy-header per-policy card in cesiones section.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QSizePolicy, QCheckBox, QTextEdit,
)
from PySide6.QtCore import Qt, Signal, QByteArray, QRectF
from PySide6.QtGui import QFont, QColor, QPainter, QPixmap, QIcon
from PySide6.QtSvg import QSvgRenderer
from theme import QSSA
from svgs import get_svg_chevron

class CardWidget(QWidget):
    """
    Custom card widget with slate header + dark body.
    Drop-in visual replacement for QGroupBox.
    Supports optional collapsible (accordion) behavior.
    """

    # Colors — change here to restyle all cards at once
    # Colors defined in theme.py QSSA and applied via QSS selectors
    # #CardHeader, #CardBody, #CardTitle, #CardToggle — no hardcoded colors here

    def __init__(self, title="", collapsible=False, bold_title=False, parent=None):
        super().__init__(parent)
        self._collapsible  = collapsible
        self._collapsed    = False
        self._bold_title   = bold_title
        self._buildLayout(title)

    def _buildLayout(self, title):
        """Build the header + body vertical layout.
        NO setStyleSheet calls here — all styles handled via QSS selectors
        #CardHeader and #CardBody defined in build_qss() in theme.py.
        This prevents CardWidget from blocking QSS rules for child widgets.
        """
        self.setAutoFillBackground(False)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(*QSSA['margins_zero'])
        outer.setSpacing(QSSA['spacing_zero'])

        # ── Header bar ────────────────────────────────────────────────────────
        self._header = QWidget()
        self._header.setObjectName("CardHeader")
        self._header.setMinimumHeight(QSSA['card_header_fixed_height'])
        # WA_StyledBackground required so QSS background-color paints correctly
        # when the widget is used in contexts without global setStyleSheet propagation
        self._header.setAttribute(Qt.WA_StyledBackground, True)

        headerLayout = QHBoxLayout(self._header)
        headerLayout.setContentsMargins(*QSSA['margins_card_header'])
        headerLayout.setSpacing(QSSA['spacing_card_header'])

        # Title label — styled via #CardHeader QLabel in QSS
        self._titleLabel = QLabel(title.upper())
        self._titleLabel.setObjectName("CardTitle")
        headerLayout.addWidget(self._titleLabel)
        headerLayout.addStretch()

        # Collapse toggle button (only when collapsible=True)
        if self._collapsible:
            self._toggleBtn = QPushButton()
            self._toggleBtn.setObjectName("CardToggle")
            self._toggleBtn.setProperty('role', 'accordion')
            self._toggleBtn.setCheckable(True)
            self._toggleBtn.setChecked(True)  # expanded by default
            self._toggleBtn.setFixedSize(*QSSA['card_toggle_fixed_size'])
            color = QSSA.get('card_header_toggle')
            self._toggleBtn.setIcon(self._chevronIcon(expanded=True, color=color))
            self._toggleBtn.toggled.connect(self._onToggle)
            headerLayout.addWidget(self._toggleBtn, 0, Qt.AlignVCenter)

        outer.addWidget(self._header)

        # ── Body area ─────────────────────────────────────────────────────────
        self._body = QWidget()
        self._body.setObjectName("CardBody")
        # WA_StyledBackground required so QSS background-color paints correctly
        self._body.setAttribute(Qt.WA_StyledBackground, True)

        self._bodyLayout = QVBoxLayout(self._body)
        self._bodyLayout.setContentsMargins(*QSSA['margins_card_body'])
        self._bodyLayout.setSpacing(QSSA['spacing_card_body'])

        outer.addWidget(self._body)

    # ── Public API ────────────────────────────────────────────────────────────

    def addContent(self, item):
        """
        Add a widget or layout to the card body.
        Use this instead of setLayout() for new code.
        """
        if isinstance(item, QWidget):
            self._bodyLayout.addWidget(item)
        else:
            # Wrap layout in a container widget.
            # setAutoFillBackground(False) + explicit stylesheet prevents
            # Qt's style engine from drawing a panel/frame border around it.
            container = QWidget()
            container.setAutoFillBackground(False)
            # No setStyleSheet on container — prevents blocking child widget QSS
            container.setLayout(item)
            self._bodyLayout.addWidget(container)

    def setLayout(self, layout):
        """
        Compatibility alias for addContent(layout).
        Allows existing QGroupBox.setLayout() call-sites to work unchanged.
        """
        self.addContent(layout)

    def layout(self):
        """Return the body layout for compatibility with existing code."""
        return self._bodyLayout

    def setTitle(self, title):
        """Update the header title text."""
        self._titleLabel.setText(title.upper())

    def title(self):
        """Return current title text."""
        return self._titleLabel.text()

    def setCollapsed(self, collapsed):
        """Programmatically collapse or expand the card body."""
        if not self._collapsible:
            return
        self._collapsed = collapsed
        self._body.setVisible(not collapsed)
        if hasattr(self, '_toggleBtn'):
            color = QSSA.get('card_header_toggle')
            self._toggleBtn.blockSignals(True)
            self._toggleBtn.setChecked(not collapsed)
            self._toggleBtn.setIcon(self._chevronIcon(expanded=not collapsed, color=color))
            self._toggleBtn.blockSignals(False)

    def isCollapsed(self):
        """Return True if the card is currently collapsed."""
        return self._collapsed

    def _chevronIcon(self, expanded=True, color='#ffffff'):
        """Return QIcon from chevron pixmap for QPushButton."""
        return QIcon(self._chevronPixmap(expanded=expanded, color=color))

    @staticmethod
    def _chevronPixmap(expanded=True, size=16, color="#ffffff"):
        """
        Generate a chevron SVG as a QPixmap.
        Uses centralized get_svg_chevron from svgs.py.
        expanded=True  → chevron pointing down  (body is visible)
        expanded=False → chevron pointing right (body is collapsed)
        color: should match card_header_toggle from the active theme.
        size: icon dimensions in pixels.
        """
        svg = get_svg_chevron(expanded=expanded, color=color, size=size)
        renderer = QSvgRenderer(QByteArray(svg.encode()))
        pixmap   = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        painter  = QPainter(pixmap)
        renderer.render(painter, QRectF(0, 0, size, size))
        painter.end()
        return pixmap

    # ── Private slot ──────────────────────────────────────────────────────────

    def _onToggle(self):
        """Toggle collapsed state when the user clicks the header button."""
        self.setCollapsed(not self._collapsed)



class InsuredGroupCard(QWidget):
    """
    Header-only CardWidget for grouping policies under an insured name.
    Header: transparent background, dark text (insured_group_text from theme).
    Body: contains EndorsementPolicyCard children.
    Collapsible via chevron button.
    """

    def __init__(self, insuredName="", parent=None):
        super().__init__(parent)
        self._collapsed = False
        self._buildLayout(insuredName)

    def _buildLayout(self, insuredName):

        outer = QVBoxLayout(self)
        outer.setContentsMargins(*QSSA['margins_zero'])
        outer.setSpacing(QSSA['spacing_zero'])

        # Header — transparent bg, dark text
        self._header = QWidget()
        self._header.setObjectName("InsuredGroupHeader")
        self._header.setAttribute(Qt.WA_StyledBackground, True)
        self._header.setMinimumHeight(QSSA['card_header_fixed_height'])

        headerLayout = QHBoxLayout(self._header)
        headerLayout.setContentsMargins(*QSSA['margins_card_header'])
        headerLayout.setSpacing(QSSA['spacing_card_header'])

        self._titleLabel = QLabel(insuredName.upper())
        self._titleLabel.setObjectName("CardTitle")
        headerLayout.addWidget(self._titleLabel)
        headerLayout.addStretch()

        # Accordion toggle button
        color = QSSA.get('card_header_toggle')
        self._toggleBtn = QPushButton()
        self._toggleBtn.setObjectName("CardToggle")
        self._toggleBtn.setProperty('role', 'accordion')
        self._toggleBtn.setCheckable(True)
        self._toggleBtn.setChecked(False)  # collapsed by default
        self._toggleBtn.setFixedSize(*QSSA['card_toggle_fixed_size'])
        self._toggleBtn.setIcon(CardWidget._chevronPixmap(expanded=False, color=color))
        self._toggleBtn.toggled.connect(self._onToggle)
        headerLayout.addWidget(self._toggleBtn)

        outer.addWidget(self._header)

        # Body
        self._body = QWidget()
        self._body.setObjectName("InsuredGroupBody")
        self._body.setAttribute(Qt.WA_StyledBackground, True)
        self._bodyLayout = QVBoxLayout(self._body)
        self._bodyLayout.setContentsMargins(*QSSA['margins_policy_card_body'])
        self._bodyLayout.setSpacing(QSSA['spacing_policy_card_body'])
        self._body.setVisible(False)  # collapsed by default
        outer.addWidget(self._body)


    def bodyLayout(self):
        """Return body QVBoxLayout for adding child widgets externally."""
        return self._bodyLayout

    def addPolicyCard(self, card):
        """Add an EndorsementPolicyCard to this insured group."""
        self._bodyLayout.addWidget(card)

    def _onToggle(self, expanded: bool):
        self._collapsed = not expanded
        self._body.setVisible(expanded)
        color = QSSA.get('card_header_toggle')
        self._toggleBtn.setIcon(
            CardWidget._chevronPixmap(expanded=expanded, color=color)
        )

    def setTitle(self, name):
        self._titleLabel.setText(name.upper())



class EndorsementPolicyCard(QWidget):
    """
    Per-policy card with checkbox in header (controls docx inclusion)
    and collapsible body (controls screen visibility).
    Follows GuaranteesEditor pattern — no inheritance from CardWidget.

    Header: classic navy CardWidget style + QCheckBox + count indicator + chevron.
    Body: contains CesionesWidget or TrecWidget.

    Checkbox: checked = include in docx + show body + show chevron.
              unchecked = exclude from docx + hide body + hide chevron.
    Chevron:  independent of checkbox — only collapses/expands body.
    Count indicator: shows record/group count when collapsed and checked.
    """

    def __init__(self, label="", checked=False, parent=None):
        super().__init__(parent)
        self._label      = label
        self._collapsed  = False
        self._countText  = ""
        self._buildLayout(label, checked)

    def _buildLayout(self, label, checked):

        outer = QVBoxLayout(self)
        outer.setContentsMargins(*QSSA['margins_zero'])
        outer.setSpacing(QSSA['spacing_zero'])

        # Header — classic CardWidget style
        self._header = QWidget()
        self._header.setObjectName("CardHeader")
        self._header.setMinimumHeight(QSSA['card_header_fixed_height'])
        self._header.setAttribute(Qt.WA_StyledBackground, True)

        headerLayout = QHBoxLayout(self._header)
        headerLayout.setContentsMargins(*QSSA['margins_card_header'])
        headerLayout.setSpacing(QSSA['spacing_card_header'])

        # Checkbox — controls docx inclusion
        self._cb = QCheckBox(label)
        self._cb.setChecked(checked)
        self._cb.setObjectName("CardTitle")
        self._cb.toggled.connect(self._onCheckChanged)
        headerLayout.addWidget(self._cb)

        # Count indicator — shown when collapsed + checked
        headerLayout.addStretch()

        self._countLabel = QLabel("")
        self._countLabel.setObjectName("CardTitle")
        font = self._countLabel.font()
        font.setPointSize(max(font.pointSize() - 2, 7))
        font.setBold(False)
        self._countLabel.setFont(font)
        self._countLabel.setVisible(False)
        headerLayout.addWidget(self._countLabel)

        # Accordion toggle button
        color = QSSA.get('card_header_toggle')
        self._toggleBtn = QPushButton()
        self._toggleBtn.setObjectName("CardToggle")
        self._toggleBtn.setProperty('role', 'accordion')
        self._toggleBtn.setCheckable(True)
        self._toggleBtn.setChecked(False)  # collapsed by default
        self._toggleBtn.setFixedSize(*QSSA['card_toggle_fixed_size'])
        self._toggleBtn.setIcon(CardWidget._chevronPixmap(expanded=False, color=color))
        self._toggleBtn.toggled.connect(self._onToggle)
        self._toggleBtn.setVisible(checked)
        headerLayout.addWidget(self._toggleBtn)

        outer.addWidget(self._header)

        # Body
        self._body = QWidget()
        self._body.setObjectName("CardBody")
        self._body.setAttribute(Qt.WA_StyledBackground, True)
        self._bodyLayout = QVBoxLayout(self._body)
        self._bodyLayout.setContentsMargins(*QSSA['margins_card_body'])
        self._bodyLayout.setSpacing(QSSA['spacing_policy_card_body'])
        self._body.setVisible(False)  # collapsed by default
        outer.addWidget(self._body)

    def _onCheckChanged(self, checked):
        self._body.setVisible(checked and not self._collapsed)
        self._toggleBtn.setVisible(checked)
        if not checked:
            # Reset collapsed state when unchecking
            self._collapsed = False
            color = QSSA.get('card_header_toggle')
            self._toggleBtn.blockSignals(True)
            self._toggleBtn.setChecked(False)
            self._toggleBtn.setIcon(CardWidget._chevronPixmap(expanded=False, color=color))
            self._toggleBtn.blockSignals(False)
            self._countLabel.setVisible(False)

    def _onToggle(self, expanded: bool):
        self._collapsed = not expanded
        self._body.setVisible(expanded)
        color = QSSA.get('card_header_toggle')
        self._toggleBtn.setIcon(
            CardWidget._chevronPixmap(expanded=expanded, color=color)
        )
        # Show count indicator when collapsed
        if self._collapsed and self._countText:
            self._countLabel.setText(self._countText)
            self._countLabel.setVisible(True)
        else:
            self._countLabel.setVisible(False)

    def setContentWidget(self, widget):
        """Set the main content widget inside the body."""
        while self._bodyLayout.count():
            item = self._bodyLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._bodyLayout.addWidget(widget)

    def updateCount(self, n, is_trec=False):
        """Update the count indicator text. Always stores; shows when collapsed+checked."""
        if is_trec:
            self._countText = S['endorsement_groups_count'].format(n=n)
        else:
            self._countText = S['endorsement_records_count'].format(n=n)
        # Always update label text so it's ready when the card collapses
        self._countLabel.setText(self._countText)
        # Only show if currently collapsed and checked
        self._countLabel.setVisible(self._collapsed and self._cb.isChecked())

    def isChecked(self):
        return self._cb.isChecked()

    def setChecked(self, val):
        self._cb.setChecked(val)

    def setCollapsed(self, collapsed):
        if collapsed != self._collapsed:
            self._onToggle()


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM DIALOG BASE  (frameless window with app-style titlebar)
# ─────────────────────────────────────────────────────────────────────────────


class GuaranteesCard(QWidget):
    """
    Collapsible card for a single Garantias Particulares policy entry.

    Header contains:
      - Optional QCheckBox (multi-policy mode) or QLabel (single-policy mode)
      - Chevron toggle for collapse/expand

    Body contains:
      - Rich-text toolbar (bold, italic, underline, bullet, clear)
      - QTextEdit for free-form guarantee text

    Usage (single policy — no checkbox):
        card = GuaranteesCard(branch_name='Incendio', show_checkbox=False)

    Usage (multiple policies — with checkbox):
        card = GuaranteesCard(branch_name='Incendio', show_checkbox=True)
        card.checked  → bool
        card.toggled  → Signal(bool)

    Data API:
        card.getHtml()        → str
        card.setHtml(html)    → None
        card.isEmpty()        → bool
        card.isChecked()      → bool (always True if show_checkbox=False)
        card.branchName       → str
    """

    toggled = Signal(bool)   # emitted when checkbox state changes

    def __init__(self, branch_name: str, show_checkbox: bool = False,
                 parent=None):
        super().__init__(parent)
        self._branch       = branch_name
        self._showCheckbox = show_checkbox
        self._buildUI()

    def _buildUI(self):
        from strings import S
        from helpers import resource_path
        from theme import QSSA

        outer = QVBoxLayout(self)
        outer.setContentsMargins(*QSSA['margins_annex_toolbar_outer'])
        outer.setSpacing(QSSA['spacing_annex_toolbar_outer'])

        # ── Header ────────────────────────────────────────────────────────────
        headerWidget = QWidget()
        headerWidget.setObjectName('CardHeader')
        headerWidget.setMinimumHeight(QSSA['annex_toolbar_min_height'])
        headerLayout = QHBoxLayout(headerWidget)
        headerLayout.setContentsMargins(*QSSA['margins_annex_toolbar_inner'])

        if self._showCheckbox:
            self._cb = QCheckBox(self._branch)
            self._cb.setObjectName('CardTitle')
            self._cb.toggled.connect(self._onCheckToggled)
            headerLayout.addWidget(self._cb)
            self._titleLabel = None
        else:
            self._cb = None
            self._titleLabel = QLabel(self._branch)
            self._titleLabel.setObjectName('CardTitle')
            headerLayout.addWidget(self._titleLabel)

        headerLayout.addStretch()

        # Chevron toggle
        self._toggleBtn = QPushButton()
        self._toggleBtn.setObjectName('CardToggle')
        self._toggleBtn.setProperty('role', 'accordion')
        self._toggleBtn.setCheckable(True)
        self._toggleBtn.setChecked(False)  # collapsed by default
        self._toggleBtn.setFixedSize(*QSSA['annex_toolbar_btn_size'])
        color = QSSA.get('card_header_toggle')
        self._toggleBtn.setIcon(CardWidget._chevronPixmap(expanded=False, color=color))
        self._toggleBtn.toggled.connect(self._onToggle)
        headerLayout.addWidget(self._toggleBtn)

        outer.addWidget(headerWidget)

        # ── Body ──────────────────────────────────────────────────────────────
        self._body = QWidget()
        self._body.setObjectName('CardBody')
        self._body.setAttribute(Qt.WA_StyledBackground, True)
        bodyLayout = QVBoxLayout(self._body)
        bodyLayout.setContentsMargins(*QSSA['margins_annex_body'])
        bodyLayout.setSpacing(QSSA['spacing_annex_body'])

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(QSSA['spacing_annex_toolbar_items'])

        def _toolbarBtn(svg_fn, tooltip, callback):
            from PySide6.QtCore import QByteArray
            icon_color = QSSA.get('toolbar_button_text', '#4f5f6f')
            btn_w   = int(QSSA.get('toolbar_btn_width',    '28'))
            btn_h   = int(QSSA.get('toolbar_btn_height',   '28'))
            icon_sz = int(QSSA.get('toolbar_btn_icon_size', '14'))
            btn = QPushButton()
            btn.setObjectName('ToolbarButton')
            btn.setToolTip(tooltip)
            btn.setFixedSize(btn_w, btn_h)
            px = QPixmap()
            px.loadFromData(QByteArray(svg_fn(icon_color).encode('utf-8')), 'SVG')
            if not px.isNull():
                btn.setIcon(QIcon(px.scaled(
                    icon_sz, icon_sz,
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                )))
            btn.clicked.connect(callback)
            return btn

        self._btnBold      = _toolbarBtn(get_svg_bold,         S['toolbar_bold_tip'],      self._toggleBold)
        self._btnItalic    = _toolbarBtn(get_svg_italic,       S['toolbar_italic_tip'],    self._toggleItalic)
        self._btnUnderline = _toolbarBtn(get_svg_underline,    S['toolbar_underline_tip'], self._toggleUnderline)
        self._btnBullet    = _toolbarBtn(get_svg_list_bullet,  S['toolbar_list_tip'],      self._insertBulletList)
        self._btnClear     = _toolbarBtn(get_svg_clear_format, S['toolbar_clear_tip'],     self._clearListFormat)

        for btn in (self._btnBold, self._btnItalic, self._btnUnderline,
                    self._btnBullet, self._btnClear):
            toolbar.addWidget(btn)
        toolbar.addStretch()
        bodyLayout.addLayout(toolbar)

        # Editor
        self._editor = QTextEdit()
        self._editor.setMinimumHeight(QSSA['annex_editor_min_height'])
        self._editor.setAcceptRichText(True)
        bodyLayout.addWidget(self._editor)

        self._body.setVisible(False)  # collapsed by default
        outer.addWidget(self._body)

    # ── Checkbox ──────────────────────────────────────────────────────────────

    def _onCheckToggled(self, checked: bool):
        self.toggled.emit(checked)

    # ── Collapse / expand ─────────────────────────────────────────────────────

    def _onToggle(self, expanded: bool):
        self._body.setVisible(expanded)
        color = QSSA.get('card_header_toggle')
        self._toggleBtn.setIcon(CardWidget._chevronPixmap(expanded=expanded, color=color))

    # ── Toolbar actions ───────────────────────────────────────────────────────

    def _insertBulletList(self):
        from PySide6.QtGui import QTextListFormat
        cursor = self._editor.textCursor()
        fmt = QTextListFormat()
        fmt.setStyle(QTextListFormat.Style.ListDisc)
        fmt.setIndent(1)
        cursor.createList(fmt)
        self._editor.setFocus()

    def _toggleBold(self):
        from PySide6.QtGui import QTextCharFormat, QFont
        cursor = self._editor.textCursor()
        is_bold = cursor.charFormat().fontWeight() >= 600
        if cursor.hasSelection():
            fmt = QTextCharFormat()
            fmt.setFontWeight(QFont.Weight.Normal if is_bold else QFont.Weight.Bold)
            cursor.mergeCharFormat(fmt)
        else:
            self._editor.setFontWeight(
                QFont.Weight.Normal if is_bold else QFont.Weight.Bold)
        self._editor.setFocus()

    def _toggleItalic(self):
        from PySide6.QtGui import QTextCharFormat
        cursor = self._editor.textCursor()
        is_italic = cursor.charFormat().fontItalic()
        if cursor.hasSelection():
            fmt = QTextCharFormat()
            fmt.setFontItalic(not is_italic)
            cursor.mergeCharFormat(fmt)
        else:
            self._editor.setFontItalic(not is_italic)
        self._editor.setFocus()

    def _toggleUnderline(self):
        from PySide6.QtGui import QTextCharFormat
        cursor = self._editor.textCursor()
        is_underline = cursor.charFormat().fontUnderline()
        if cursor.hasSelection():
            fmt = QTextCharFormat()
            fmt.setFontUnderline(not is_underline)
            cursor.mergeCharFormat(fmt)
        else:
            self._editor.setFontUnderline(not is_underline)
        self._editor.setFocus()

    def _clearListFormat(self):
        from PySide6.QtGui import QTextBlockFormat
        cursor = self._editor.textCursor()
        block  = cursor.block()
        lst    = block.textList()
        if lst:
            lst.remove(block)
        blockFmt = QTextBlockFormat()
        blockFmt.setIndent(0)
        blockFmt.setTextIndent(0.0)
        cursor.setBlockFormat(blockFmt)
        self._editor.setFocus()

    # ── Public API ────────────────────────────────────────────────────────────

    def getHtml(self) -> str:
        return self._editor.toHtml()

    def setHtml(self, html: str):
        if html:
            self._editor.setHtml(html)

    def isEmpty(self) -> bool:
        return not self._editor.toPlainText().strip()

    def isChecked(self) -> bool:
        """Always True for single-policy (no checkbox). Checkbox state for multi."""
        return self._cb.isChecked() if self._cb else True

    def setChecked(self, checked: bool):
        if self._cb:
            self._cb.setChecked(checked)

    @property
    def branchName(self) -> str:
        return self._branch


class GuaranteesTableCard(QWidget):
    """
    Per-policy card for Garantías Particulares.

    Header: checkbox (policy branch name) + Ver + Editar buttons.
    Body:   managed via dialogs — no inline editor.

    Mirrors EndorsementTableCard structure but stores rich-text HTML
    instead of tabular rows/columns.

    Public API:
        card.isChecked()      → bool
        card.setChecked(bool)
        card.getHtml()        → str
        card.setHtml(str)
        card.branchName       → str
        card.numero           → str  (policy number, for document heading)
    """

    def __init__(self, branch_name: str, checked: bool = False,
                 show_checkbox: bool = True, parent=None):
        super().__init__(parent)
        self._branch       = branch_name
        self._html         = ''
        self._numero       = ''
        self._showCheckbox = show_checkbox
        self._buildLayout(checked)

    def _buildLayout(self, checked: bool):
        from strings import S
        from svgs import SVG_VIEW, SVG_EDIT
        from theme import QSSA

        outer = QVBoxLayout(self)
        outer.setContentsMargins(*QSSA['margins_annex_toolbar_outer'])
        outer.setSpacing(QSSA['spacing_annex_toolbar_outer'])

        # ── Header ────────────────────────────────────────────────────────────
        header = QWidget()
        header.setObjectName('EndorsementCard')
        header.setAttribute(Qt.WA_StyledBackground, True)
        header.setMinimumHeight(QSSA['card_header_fixed_height'])
        hl = QHBoxLayout(header)
        hl.setContentsMargins(*QSSA['margins_endtable_header'])
        hl.setSpacing(QSSA['spacing_endtable_header'])

        btn_sz  = int(QSSA.get('btn_endtable_size'))
        icon_sz = btn_sz - 6
        from PySide6.QtCore import QByteArray

        if self._showCheckbox:
            # Multiple policies — checkbox controls visibility of buttons
            self._cb = QCheckBox(self._branch)
            self._cb.setObjectName('CardTitle')
            self._cb.setChecked(checked)
            self._cb.toggled.connect(self._onCheckChanged)
            hl.addWidget(self._cb, 1)
        else:
            # Single policy — label, buttons always visible
            self._cb = None
            lbl = QLabel(self._branch)
            lbl.setObjectName('CardTitle')
            hl.addWidget(lbl, 1)

        # View / Edit buttons
        self._btnView = QPushButton()
        self._btnView.setProperty('role', 'endtable-view')
        self._btnView.setFixedSize(btn_sz, btn_sz)
        self._btnView.setToolTip(S['endtable_btn_view'])
        self._btnEdit = QPushButton()
        self._btnEdit.setProperty('role', 'endtable-edit')
        self._btnEdit.setFixedSize(btn_sz, btn_sz)
        self._btnEdit.setToolTip(S['endtable_btn_edit'])

        for btn, svg in [(self._btnView, SVG_VIEW), (self._btnEdit, SVG_EDIT)]:
            px = QPixmap()
            px.loadFromData(QByteArray(svg.encode()), 'SVG')
            if not px.isNull():
                btn.setIcon(QIcon(px.scaled(
                    icon_sz, icon_sz,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )))

        self._btnView.clicked.connect(self._openViewDialog)
        self._btnEdit.clicked.connect(self._openEditDialog)
        hl.addWidget(self._btnView)
        hl.addWidget(self._btnEdit)

        # Without checkbox: always visible. With checkbox: only when checked.
        if self._showCheckbox:
            self._btnView.setVisible(checked)
            self._btnEdit.setVisible(checked)

        outer.addWidget(header)

    def _onCheckChanged(self, checked: bool):
        if self._showCheckbox:
            self._btnView.setVisible(checked)
            self._btnEdit.setVisible(checked)

    def _openViewDialog(self):
        from .dialog import CustomDialog
        from PySide6.QtWidgets import QTextEdit as _QTE
        from strings import S
        dlg = CustomDialog(S.get('guarantees_view_title', 'Ver Garantías'), self)
        dlg.setMinimumSize(600, 400)
        dlg.setSizeGripEnabled(True)
        editor = _QTE()
        editor.setReadOnly(True)
        editor.setHtml(self._html or S.get('guarantees_empty_hint',
                                           '<i>Sin contenido</i>'))
        dlg.contentLayout().addWidget(editor)
        dlg.exec()

    def _openEditDialog(self):
        from .dialog import CustomDialog
        from PySide6.QtWidgets import QTextEdit as _QTE, QHBoxLayout as _QHL
        from PySide6.QtGui import QFont, QTextListFormat, QTextCharFormat
        from strings import S
        from theme import QSSA as _Q
        from svgs import (get_svg_bold, get_svg_italic, get_svg_underline,
                          get_svg_list_bullet, get_svg_clear_format)
        from PySide6.QtCore import QByteArray as _QBA

        dlg = CustomDialog(S.get('guarantees_edit_title', 'Editar Garantías'), self)
        dlg.setMinimumSize(640, 480)
        dlg.setSizeGripEnabled(True)
        cl = dlg.contentLayout()

        # Toolbar
        toolbarRow = _QHL()
        toolbarRow.setSpacing(_Q['spacing_annex_toolbar_items'])

        def _tbtn(svg_fn, tip, callback):
            ic = _Q.get('toolbar_button_text', '#4f5f6f')
            bw = int(_Q.get('toolbar_btn_width', '28'))
            bh = int(_Q.get('toolbar_btn_height', '28'))
            iz = int(_Q.get('toolbar_btn_icon_size', '14'))
            b = QPushButton()
            b.setObjectName('ToolbarButton')
            b.setToolTip(tip)
            b.setFixedSize(bw, bh)
            px = QPixmap()
            px.loadFromData(_QBA(svg_fn(ic).encode('utf-8')), 'SVG')
            if not px.isNull():
                b.setIcon(QIcon(px.scaled(iz, iz,
                    Qt.KeepAspectRatio, Qt.SmoothTransformation)))
            b.clicked.connect(callback)
            return b

        editor = _QTE()
        editor.setAcceptRichText(True)
        if self._html:
            editor.setHtml(self._html)

        def _bold():
            c = editor.textCursor()
            is_bold = c.charFormat().fontWeight() >= 600
            fmt = QTextCharFormat()
            fmt.setFontWeight(QFont.Weight.Normal if is_bold else QFont.Weight.Bold)
            if c.hasSelection():
                c.mergeCharFormat(fmt)
            else:
                editor.setFontWeight(
                    QFont.Weight.Normal if is_bold else QFont.Weight.Bold)
            editor.setFocus()

        def _italic():
            c = editor.textCursor()
            is_it = c.charFormat().fontItalic()
            fmt = QTextCharFormat()
            fmt.setFontItalic(not is_it)
            if c.hasSelection():
                c.mergeCharFormat(fmt)
            else:
                editor.setFontItalic(not is_it)
            editor.setFocus()

        def _underline():
            c = editor.textCursor()
            is_ul = c.charFormat().fontUnderline()
            fmt = QTextCharFormat()
            fmt.setFontUnderline(not is_ul)
            if c.hasSelection():
                c.mergeCharFormat(fmt)
            else:
                editor.setFontUnderline(not is_ul)
            editor.setFocus()

        def _bullet():
            c = editor.textCursor()
            fmt = QTextListFormat()
            fmt.setStyle(QTextListFormat.Style.ListDisc)
            fmt.setIndent(1)
            c.createList(fmt)
            editor.setFocus()

        def _clear():
            from PySide6.QtGui import QTextBlockFormat
            c = editor.textCursor()
            lst = c.block().textList()
            if lst:
                lst.remove(c.block())
            bf = QTextBlockFormat()
            bf.setIndent(0)
            bf.setTextIndent(0.0)
            c.setBlockFormat(bf)
            editor.setFocus()

        for svg_fn, tip, cb in [
            (get_svg_bold,         S['toolbar_bold_tip'],      _bold),
            (get_svg_italic,       S['toolbar_italic_tip'],    _italic),
            (get_svg_underline,    S['toolbar_underline_tip'], _underline),
            (get_svg_list_bullet,  S['toolbar_list_tip'],      _bullet),
            (get_svg_clear_format, S['toolbar_clear_tip'],     _clear),
        ]:
            toolbarRow.addWidget(_tbtn(svg_fn, tip, cb))
        toolbarRow.addStretch()
        cl.addLayout(toolbarRow)

        cl.addWidget(editor, 1)

        # Close button
        btnRow = _QHL()
        btnRow.addStretch()
        btnClose = QPushButton(S.get('endtable_btn_save', 'Guardar'))
        btnClose.setAutoDefault(False)
        btnClose.setDefault(False)
        btnClose.clicked.connect(dlg.accept)  # accept() saves and closes
        btnRow.addWidget(btnClose)
        cl.addLayout(btnRow)

        dlg.exec()
        # Save HTML back
        self._html = editor.toHtml()

    # ── Public API ────────────────────────────────────────────────────────────

    def isChecked(self) -> bool:
        if self._cb is None:
            return True  # single policy — always included
        return self._cb.isChecked()

    def setChecked(self, checked: bool):
        if self._cb is not None:
            self._cb.setChecked(checked)

    def getHtml(self) -> str:
        return self._html

    def setHtml(self, html: str):
        if html:
            self._html = html

    def isEmpty(self) -> bool:
        return not self._html.strip()

    @property
    def branchName(self) -> str:
        return self._branch

    @property
    def numero(self) -> str:
        return self._numero
