"""
Input Validators and Formatters
Reusable helpers applied to QLineEdit fields across all pages.
"""

from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui  import QRegularExpressionValidator, QFont
from PySide6.QtWidgets import QLineEdit, QLabel, QComboBox, QDateEdit


# ─────────────────────────────────────────────────────────────────────────────
# VALIDATOR FACTORIES
# Each function returns a QValidator ready to be assigned to a QLineEdit.
# ─────────────────────────────────────────────────────────────────────────────

def numbersOnlyValidator():
    """
    Allow only digit characters (0-9).
    Used for: Número de Carta.
    """
    return QRegularExpressionValidator(QRegularExpression(r'^\d*$'))


def lettersAmpersandValidator():
    """
    Allow letters (including accented), spaces, digits and the & symbol.
    Used for: Ramo field in PolicyWidget (e.g. "VIDA GRUPO 3", "RC3").
    """
    return QRegularExpressionValidator(
        QRegularExpression(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s&0-9]*$')
    )


def annexContentValidator():
    """
    Allow letters (including accented), spaces, &, period and comma.
    Used for: annex content input in pageConfig.
    """
    return QRegularExpressionValidator(
        QRegularExpression(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s&.,]*$')
    )


def currencyInputValidator():
    """
    Allow only digits, a single period (decimal separator) and commas
    (used as thousand separators during typing).
    Used for: Prima, Total in PolicyWidget and Prima de Cuota in FinancingTable.
    The actual formatting is applied on focus-out via formatCurrencyField().
    """
    return QRegularExpressionValidator(
        QRegularExpression(r'^[\d,]*\.?\d{0,2}$')
    )


# ─────────────────────────────────────────────────────────────────────────────
# CURRENCY FORMATTER
# Applied when a currency field loses focus (editingFinished / focusOut).
# ─────────────────────────────────────────────────────────────────────────────

def formatCurrencyValue(text):
    """
    Parse a raw currency string and return a formatted string with:
      - Comma thousand separators  (e.g. 1,234,567)
      - Always exactly 2 decimal places  (e.g. .00 appended if missing)
      - Period as decimal separator
    Returns '0.00' for empty or invalid input.
    Example: '1234567.5' → '1,234,567.50'
    """
    # Strip existing commas so we work with a clean number string
    clean = text.replace(',', '').strip()

    if not clean:
        return '0.00'

    try:
        value = float(clean)
    except ValueError:
        return '0.00'

    # Format with 2 decimal places and comma thousand separators
    return f'{value:,.2f}'


def applyCurrencyFormat(lineEdit):
    """
    Read the current text of a QLineEdit, format it as currency,
    and write the result back.
    Intended to be connected to editingFinished signal.
    """
    lineEdit.setText(formatCurrencyValue(lineEdit.text()))


# ─────────────────────────────────────────────────────────────────────────────
# STYLE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def setBold(widget):
    """
    Apply bold font to any widget via QFont — avoids setStyleSheet
    which would block QSS rules for child widgets.
    Works on QLabel and QLineEdit.
    """
    from PySide6.QtGui import QFont
    font = widget.font()
    font.setBold(True)
    widget.setFont(font)


class DropDownComboBox(QComboBox):
    """
    QComboBox that always opens its dropdown below the widget,
    regardless of selected item position or screen position.
    Replaces all QComboBox() instantiations in the app.

    Also enforces the theme min-height at the Python layout level so all
    instances are sized consistently regardless of container or layout type.
    setMinimumHeight mirrors the QSS min-height value from QSSD so the Qt
    layout engine and the style engine agree on the same minimum dimension.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        from theme import QSSA
        self.setMinimumHeight(int(QSSA['combobox_min_height']))
        self.setMinimumWidth(int(QSSA['combobox_min_width']))

    def showPopup(self):
        """Override to always open dropdown below the widget.
        Uses native Qt showPopup — preserves border and shadow.
        Positions popup directly below the combobox on Windows.
        """
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

# Keep for backwards compatibility
def applyComboBoxFix(comboBox):
    """Deprecated — use DropDownComboBox instead."""
    pass



class ThemedDateEdit(QDateEdit):
    """
    QDateEdit that enforces the theme min-height and min-width at the Python
    layout level, mirroring the QSS min-height/min-width values from QSSD.

    This ensures the Qt layout engine and the style engine agree on the same
    minimum dimensions, regardless of container type or layout policy.

    Use everywhere instead of plain QDateEdit() to get consistent sizing.
    The setFixedHeight() override for header-embedded date edits (if any)
    can still be applied after instantiation — it takes precedence.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        from theme import QSSA
        self.setMinimumHeight(int(QSSA['dateedit_min_height']))
        self.setMinimumWidth(int(QSSA['dateedit_min_width']))
