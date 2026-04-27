# coding: utf-8
"""
widgets/tree.py — AutoTreeWidget

QTreeWidget subclass with alternating row colors, auto-resize columns and
header styling. Used in pagePolicies and pageFinance for tabular data.
"""

from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView, QAbstractItemView
from PySide6.QtCore import Qt
from theme import QSSA

class AutoTreeWidget(QTreeWidget):
    """
    QTreeWidget that automatically distributes column widths by ratio.
    Pass ratios as a list that sums to 1.0, e.g. [0.25, 0.75].
    Columns resize proportionally when the widget is resized.
    Used in pageConfig (annexes) and pagePayment (quotas).
    """

    def __init__(self, ratios, headers, height=None):
        super().__init__()
        self._ratios = ratios
        self.setRootIsDecorated(False)
        self.setColumnCount(len(ratios))
        self.setHeaderLabels(headers)
        # Center header labels
        for col in range(len(headers)):
            self.headerItem().setTextAlignment(col, Qt.AlignCenter)
        self.header().setStretchLastSection(False)
        for col in range(len(ratios)):
            self.header().setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
        self.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectRows)
        self.setEditTriggers(QTreeWidget.EditTrigger.NoEditTriggers)
        self.setVerticalScrollMode(QTreeWidget.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QTreeWidget.ScrollMode.ScrollPerPixel)
        # Minimum height = header (34px) + 5 rows × 28px = 174px
        self.setMinimumHeight(QSSA['card_body_min_height'])
        if height:
            self.setFixedHeight(height)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w    = self.viewport().width()
        used = 0
        # All columns except the last use int(w * ratio).
        # The last column takes the remaining pixels to eliminate the
        # 1px phantom gap caused by rounding when ratios don't sum to
        # an exact integer at the current viewport width.
        for col, ratio in enumerate(self._ratios[:-1]):
            width = int(w * ratio)
            self.setColumnWidth(col, width)
            used += width
        self.setColumnWidth(len(self._ratios) - 1, w - used)

    def mousePressEvent(self, event):
        """
        Deselect any selected row when the user clicks on an empty area of the
        tree viewport — the area below the last row or between rows.
        Standard Qt QTreeWidget keeps the selection active even when clicking
        outside any item; this override clears it for better UX.
        """
        item = self.itemAt(event.pos())
        if item is None:
            self.clearSelection()
            self.setCurrentItem(None)
        super().mousePressEvent(event)

    def addRow(self, values, alignment=Qt.AlignCenter):
        """Add a row with centered text. Returns the QTreeWidgetItem."""
        item = QTreeWidgetItem([str(v) for v in values])
        for col in range(len(values)):
            item.setTextAlignment(col, alignment)
        self.addTopLevelItem(item)
        return item

    def rowCount(self):
        """Compatibility method — same as topLevelItemCount()."""
        return self.topLevelItemCount()

    def getRow(self, row):
        """Return values of a row as a list of strings."""
        item = self.topLevelItem(row)
        if not item:
            return []
        return [item.text(col) for col in range(self.columnCount())]

    def clearRows(self):
        """Remove all data rows."""
        self.clear()


