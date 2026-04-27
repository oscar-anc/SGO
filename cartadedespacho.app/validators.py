"""
Input Validators and Formatters
Reusable helpers applied to QLineEdit fields across all pages.
"""

from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui  import QRegularExpressionValidator, QFont
from PySide6.QtWidgets import QLineEdit, QLabel, QComboBox, QDateEdit


def numbersOnlyValidator():
    return QRegularExpressionValidator(QRegularExpression(r'^\d*$'))


def lettersAmpersandValidator():
    return QRegularExpressionValidator(
        QRegularExpression(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s&0-9]*$')
    )


def annexContentValidator():
    return QRegularExpressionValidator(
        QRegularExpression(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s&.,]*$')
    )


def currencyInputValidator():
    return QRegularExpressionValidator(
        QRegularExpression(r'^[\d,]*\.?\d{0,2}$')
    )


def formatCurrencyValue(text):
    clean = text.replace(',', '').strip()
    if not clean:
        return '0.00'
    try:
        value = float(clean)
    except ValueError:
        return '0.00'
    return f'{value:,.2f}'


def applyCurrencyFormat(lineEdit):
    lineEdit.setText(formatCurrencyValue(lineEdit.text()))


def setBold(widget):
    from PySide6.QtGui import QFont
    font = widget.font()
    font.setBold(True)
    widget.setFont(font)


def install_completer(combo, items):
    """
    Install a MatchContains + CaseInsensitive QCompleter on any QComboBox.

    Used for plain QComboBox instances in pageAnnex.py and endorsement.py
    that are not subclasses of DropDownComboBox. Call once after addItems().

    Args:
        combo:  Any editable QComboBox instance.
        items:  List of strings to populate the completer with.
    """
    from PySide6.QtWidgets import QCompleter
    if not items:
        return
    completer = QCompleter(items, combo)
    completer.setCaseSensitivity(Qt.CaseInsensitive)
    completer.setFilterMode(Qt.MatchContains)
    completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
    combo.setCompleter(completer)


class DropDownComboBox(QComboBox):
    """
    QComboBox that always opens its dropdown below the widget,
    regardless of selected item position or screen position.

    Auto-completer: when the combo is editable, a QCompleter with
    MatchContains + CaseInsensitive is installed automatically and refreshed
    on every addItems() / addItem() call. No manual completer setup needed
    at call sites — just call setEditable(True) then addItems() as normal.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        from theme import QSSA
        self.setMinimumHeight(int(QSSA['combobox_min_height']))
        self.setMinimumWidth(int(QSSA['combobox_min_width']))
        self._autoCompleter = None

    def setEditable(self, editable):
        super().setEditable(editable)
        if editable:
            self.autoCompleter()

    def autoCompleter(self):
        from PySide6.QtWidgets import QCompleter
        items = [self.itemText(i) for i in range(self.count())]
        self._autoCompleter = QCompleter(items, self)
        self._autoCompleter.setCaseSensitivity(Qt.CaseInsensitive)
        self._autoCompleter.setFilterMode(Qt.MatchContains)
        self._autoCompleter.setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion
        )
        self.setCompleter(self._autoCompleter)

    def addItems(self, texts):
        super().addItems(texts)
        if self.isEditable():
            self.autoCompleter()

    def addItem(self, text, userData=None):
        if userData is not None:
            super().addItem(text, userData)
        else:
            super().addItem(text)
        if self.isEditable():
            self.autoCompleter()

    def showPopup(self):
        from PySide6.QtCore import QPoint, QTimer
        super().showPopup()

        def _forceBelow():
            popup = self.view().window()
            if not popup.isVisible():
                return
            target = self.mapToGlobal(QPoint(0, self.height()))
            from PySide6.QtWidgets import QApplication
            screen = QApplication.screenAt(self.mapToGlobal(QPoint(0, 0)))
            if screen:
                avail = screen.availableGeometry()
                if target.y() + popup.height() <= avail.bottom():
                    popup.move(target.x(), target.y())

        QTimer.singleShot(0, _forceBelow)


def applyComboBoxFix(comboBox):
    """Deprecated — use DropDownComboBox instead."""
    pass


class ThemedDateEdit(QDateEdit):
    """
    QDateEdit that enforces the theme min-height and min-width at the Python
    layout level, mirroring the QSS min-height/min-width values from QSSD.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        from theme import QSSA
        self.setMinimumHeight(int(QSSA['dateedit_min_height']))
        self.setMinimumWidth(int(QSSA['dateedit_min_width']))