from strings import S
"""
Página 1: Configuración
Manages letter type, OPE data, client data, limit of liability and annexes.

Layout order (top to bottom):
  1. Datos del Cliente
  2. OPE
  3. Tipo de Carta  &  Importe LOL  (side by side, horizontal)
  4. Anexos
"""

from theme import QSSA
from PySide6.QtWidgets import *
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QByteArray, QSize, Signal, Qt
from widgets import NoNewlineLineEdit, CustomMessageBox, CardWidget, AutoTreeWidget

from svgs import get_svg_word, get_svg_pdf, get_svg_plus_separator
from validators import (
    numbersOnlyValidator,
    annexContentValidator,
)


class PageConfig(QWidget):
    """Configuration page — Page 1."""

    signalNext  = Signal()
    signalReset = Signal()   # triggers global app reset from app.py

    def __init__(self):
        super().__init__()
        self.buildUI()

    def buildUI(self):
        """Build the complete user interface."""
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        containerWidget = QWidget()
        mainLayout = QVBoxLayout(containerWidget)

        # ── 1. DATOS DEL CLIENTE + OPE (side by side) ───────────────────────
        topRow = QHBoxLayout()
        topRow.setSpacing(QSSA['spacing_config_top_row'])
        topRow.setContentsMargins(*QSSA['margins_config_top_row'])

        # Left — Datos del Cliente (labels above fields)
        groupClientData = CardWidget(S["card_client_data"])
        clientDataLayout = QVBoxLayout()
        clientDataLayout.setSpacing(QSSA['spacing_config_fields'])

        clientDataLayout.addWidget(QLabel(S["label_company_name"]))
        self.insuredCompany = NoNewlineLineEdit()
        clientDataLayout.addWidget(self.insuredCompany)

        clientDataLayout.addWidget(QLabel(S["label_address"]))
        self.insuredAddress = NoNewlineLineEdit()
        clientDataLayout.addWidget(self.insuredAddress)

        clientDataLayout.addWidget(QLabel(S["label_contact_name"]))
        self.insuredContactName = NoNewlineLineEdit()
        clientDataLayout.addWidget(self.insuredContactName)

        groupClientData.setLayout(clientDataLayout)
        groupClientData.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        topRow.addWidget(groupClientData, 1)

        # Right — OPE (labels above fields)
        groupOpe = CardWidget(S["card_ope"])
        opeLayout = QVBoxLayout()
        opeLayout.setSpacing(QSSA['spacing_config_fields'])

        opeLayout.addWidget(QLabel(S["label_ope_number"]))
        self.opeNumber = NoNewlineLineEdit()
        # Only digits allowed — letter number is always numeric
        self.opeNumber.setValidator(numbersOnlyValidator())
        opeLayout.addWidget(self.opeNumber)

        opeLayout.addWidget(QLabel(S["label_ope_barcode"]))
        self.opeBarcode = NoNewlineLineEdit()
        opeLayout.addWidget(self.opeBarcode)

        groupOpe.setLayout(opeLayout)
        groupOpe.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        topRow.addWidget(groupOpe, 1)

        mainLayout.addLayout(topRow)

        # ── 3. TIPO DE CARTA  &  IMPORTE LOL  (side by side) ─────────────────
        # Both cards share the row equally via stretch=1 on each widget.
        # Wrapped in a plain QWidget so the HBoxLayout fits into the main VBox.
        horizontalRow = QHBoxLayout()
        horizontalRow.setSpacing(QSSA['spacing_config_side_row'])
        horizontalRow.setContentsMargins(*QSSA['margins_config_side_row'])

        # Left — Tipo de Carta
        self.cardLetterType  = CardWidget(S["card_letter_type"])
        letterTypeLayout = QVBoxLayout()

        self.policyOperation = QButtonGroup()
        self.policyIssue     = QRadioButton(S["letter_type_issue"])
        self.policyRenewal   = QRadioButton(S["letter_type_renewal"])
        self.policyOperation.addButton(self.policyIssue)
        self.policyOperation.addButton(self.policyRenewal)
        letterTypeLayout.addWidget(self.policyIssue)
        letterTypeLayout.addWidget(self.policyRenewal)
        self.cardLetterType.setLayout(letterTypeLayout)
        self.cardLetterType.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Right — Importe LOL
        self.cardLol = CardWidget(S["card_lol"])
        lolLayout = QVBoxLayout()

        self.limitOfLiabilityGroup = QButtonGroup()
        self.limitUndefined        = QRadioButton(S["lol_undefined"])
        self.limitGeneric          = QRadioButton(S["lol_general"])
        self.limitFixedAmount      = QRadioButton(S["lol_fixed"])
        self.limitMultinacional    = QRadioButton(S["lol_multinacional"])
        self.limitOfLiabilityGroup.addButton(self.limitUndefined)
        self.limitOfLiabilityGroup.addButton(self.limitGeneric)
        self.limitOfLiabilityGroup.addButton(self.limitFixedAmount)
        self.limitOfLiabilityGroup.addButton(self.limitMultinacional)
        lolLayout.addWidget(self.limitUndefined)
        lolLayout.addWidget(self.limitGeneric)
        lolLayout.addWidget(self.limitFixedAmount)
        lolLayout.addWidget(self.limitMultinacional)

        # Fixed-amount input — only visible when "Importe Fijo" is selected
        self.liabilityLimit  = QWidget()
        lolFixedLayout       = QVBoxLayout(self.liabilityLimit)
        lolFixedLayout.setContentsMargins(*QSSA['margins_config_lol_fixed'])
        lolFixedLayout.addWidget(QLabel(S["lol_amount_label"]))
        self.limitAmount = NoNewlineLineEdit()
        self.limitAmount.setPlaceholderText(S["lol_amount_placeholder"])
        from validators import currencyInputValidator, applyCurrencyFormat
        self.limitAmount.setValidator(currencyInputValidator())
        self.limitAmount.editingFinished.connect(
            lambda: applyCurrencyFormat(self.limitAmount)
        )
        lolFixedLayout.addWidget(self.limitAmount)
        self.liabilityLimit.setVisible(False)
        lolLayout.addWidget(self.liabilityLimit)
        lolLayout.addStretch()

        self.limitFixedAmount.toggled.connect(self.liabilityLimit.setVisible)
        self.cardLol.setLayout(lolLayout)
        self.cardLol.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Add both cards with equal stretch so they share width 50/50
        horizontalRow.addWidget(self.cardLetterType, 1)
        horizontalRow.addWidget(self.cardLol, 1)

        horizontalContainer = QWidget()
        horizontalContainer.setLayout(horizontalRow)
        mainLayout.addWidget(horizontalContainer)

        # ── 4. ANEXOS ─────────────────────────────────────────────────────────
        groupAnnexes = CardWidget(S["card_annexes"])
        annexesLayout = QVBoxLayout()

        annexInputLayout = QHBoxLayout()
        self.annexContent = NoNewlineLineEdit()
        self.annexContent.setPlaceholderText(S["annex_placeholder"])
        # Only letters, &, period and comma allowed in annex descriptions
        self.annexContent.setValidator(annexContentValidator())
        annexInputLayout.addWidget(self.annexContent)
        annexesLayout.addLayout(annexInputLayout)

        annexButtonsLayout = QHBoxLayout()
        self.addAnnex    = QPushButton(S["btn_add"])
        self.updateAnnex = QPushButton(S["btn_update"])
        self.deleteAnnex = QPushButton(S["btn_delete"])
        self.addAnnex.clicked.connect(self.addRow)
        self.updateAnnex.clicked.connect(self.updateRow)
        self.deleteAnnex.clicked.connect(self.deleteRow)
        annexButtonsLayout.addWidget(self.addAnnex)
        annexButtonsLayout.addWidget(self.updateAnnex)
        annexButtonsLayout.addWidget(self.deleteAnnex)
        annexesLayout.addLayout(annexButtonsLayout)

        self.annexTable = AutoTreeWidget([0.25, 0.75], [S["tree_header_annex_code"], S["tree_header_annex_content"]])
        self.annexTable.itemSelectionChanged.connect(self.loadSelectedRow)
        annexesLayout.addWidget(self.annexTable)

        groupAnnexes.setLayout(annexesLayout)
        mainLayout.addWidget(groupAnnexes)

        # ── 5. FORMATO DE SALIDA ─────────────────────────────────────────────
        groupOutputFormat = CardWidget(S["card_output_format"])
        outputLayout = QVBoxLayout()
        outputLayout.setSpacing(QSSA['spacing_config_fields'])

        self.outputFormatGroup = QButtonGroup()
        self.outputFormatGroup.setExclusive(True)

        def _svg_pixmap(svg_fn):
            px = QPixmap()
            px.loadFromData(QByteArray(svg_fn().encode()), 'SVG')
            return px

        _icon_h    = int(QSSA.get('format_btn_icon_h', 22))
        _icon_gap  = int(QSSA.get('format_btn_icon_gap', 4))
        _txt_gap   = int(QSSA.get('format_btn_text_gap', 6))

        def _make_btn(label, id_, px1=None, px2=None):
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setProperty('role', 'format-selector')
            if px2 is not None and px1 is not None and not px1.isNull() and not px2.isNull():
                # Dual-icon: [Word][gap][+][gap][PDF], no text
                from PySide6.QtGui import QPainter as _QP
                from PySide6.QtCore import QByteArray as _BA
                s1 = px1.scaled(_icon_h, _icon_h, Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)
                s2 = px2.scaled(_icon_h, _icon_h, Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)
                _plus_sz = max(8, _icon_h // 2)
                _px_plus = QPixmap()
                _px_plus.loadFromData(_BA(
                    get_svg_plus_separator().encode()), 'SVG')
                splus = _px_plus.scaled(_plus_sz, _plus_sz,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation)
                cw = s1.width() + _icon_gap + splus.width() + _icon_gap + s2.width()
                ch = max(s1.height(), splus.height(), s2.height())
                combined = QPixmap(cw, ch)
                combined.fill(Qt.GlobalColor.transparent)
                p = _QP(combined)
                x = 0
                p.drawPixmap(x, (ch - s1.height()) // 2, s1)
                x += s1.width() + _icon_gap
                p.drawPixmap(x, (ch - splus.height()) // 2, splus)
                x += splus.width() + _icon_gap
                p.drawPixmap(x, (ch - s2.height()) // 2, s2)
                p.end()
                btn.setIcon(QIcon(combined))
                btn.setIconSize(QSize(cw, ch))
                btn.setText('')
            elif px1 is not None and not px1.isNull():
                s = px1.scaled(_icon_h, _icon_h, Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
                btn.setIcon(QIcon(s))
                btn.setIconSize(QSize(_icon_h, _icon_h))
                btn.setText(label)
            else:
                btn.setText(label)
            self.outputFormatGroup.addButton(btn, id_)
            return btn
        px_word = _svg_pixmap(get_svg_word)
        px_pdf  = _svg_pixmap(get_svg_pdf)
        self.outputWord = _make_btn(S['output_word'], 0, px1=px_word)
        self.outputPdf  = _make_btn(S['output_pdf'],  1, px1=px_pdf)
        self.outputBoth = _make_btn(S['output_both'], 2, px1=px_word, px2=px_pdf)
        self.outputWord.setChecked(True)

        btnRow = QHBoxLayout()
        btnRow.setSpacing(QSSA.get('format_btn_row_spacing', 12))
        btnRow.addWidget(self.outputWord)
        btnRow.addWidget(self.outputPdf)
        btnRow.addWidget(self.outputBoth)
        outputLayout.addLayout(btnRow)

        groupOutputFormat.setLayout(outputLayout)
        groupOutputFormat.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        mainLayout.addWidget(groupOutputFormat)

        mainLayout.addStretch()
        scrollArea.setWidget(containerWidget)

        # ── NAVIGATION — fixed outside scrollArea ─────────────────────────────
        nextButton = QPushButton(S["nav_next"])
        nextButton.clicked.connect(self.signalNext.emit)

        clearButton = QPushButton(S["nav_clear"])
        clearButton.clicked.connect(self._onClearAll)

        navWidget = QWidget()
        navWidget.setObjectName("NavBar")
        navLayout = QHBoxLayout(navWidget)
        navLayout.setContentsMargins(*QSSA['margins_nav'])
        navLayout.addStretch()
        navLayout.addWidget(clearButton)
        navLayout.addStretch()
        navLayout.addWidget(nextButton)

        pageLayout = QVBoxLayout(self)
        pageLayout.setContentsMargins(*QSSA['margins_zero'])
        pageLayout.setSpacing(QSSA['spacing_zero'])
        pageLayout.addWidget(scrollArea, 1)
        pageLayout.addWidget(navWidget)

        # Add three default annex rows that the user can delete if needed
        self._addDefaultAnnexRow("Manual de Procedimientos en Caso de Siniestros")
        self._addDefaultAnnexRow('Flyer "Portal de Siniestros"')
        self._addDefaultAnnexRow("Garantías Particulares")

    # ── Private helpers ────────────────────────────────────────────────────────

    def _addDefaultAnnexRow(self, content):
        """
        Insert a pre-filled annex row at build time.
        These rows behave exactly like user-added rows and can be deleted.
        """
        nextIndex = self.annexTable.topLevelItemCount()
        if nextIndex >= 26:
            return
        letter = chr(ord('A') + nextIndex)
        self.annexTable.addRow([letter, content])

    # ── Public slot methods ────────────────────────────────────────────────────

    def reindexRowLetters(self):
        """Re-assign annex letters consecutively (A, B, C...) after a deletion."""
        contents = []
        for row in range(self.annexTable.topLevelItemCount()):
            item = self.annexTable.topLevelItem(row)
            if item:
                contents.append(item.text(1))

        self.annexTable.clear()

        for index, content in enumerate(contents):
            letter = chr(ord('A') + index)
            self.annexTable.addRow([letter, content])

    def addRow(self):
        """Add a new annex row with the next consecutive letter."""
        content = self.annexContent.text().strip()
        if not content:
            CustomMessageBox.warning(self, S["msg_warning_title"], S["msg_annex_empty"])
            return

        nextIndex = self.annexTable.topLevelItemCount()
        if nextIndex >= 26:
            CustomMessageBox.warning(self, S["msg_warning_title"], S["msg_annex_max"])
            return

        letter = chr(ord('A') + nextIndex)
        self.annexTable.addRow([letter, content])
        self.annexContent.clear()

    def updateRow(self):
        """Update the content of the selected annex row."""
        currentItem = self.annexTable.currentItem()
        if not currentItem:
            CustomMessageBox.warning(self, S["msg_warning_title"], S["msg_annex_no_selection"])
            return

        content = self.annexContent.text().strip()
        if not content:
            CustomMessageBox.warning(self, S["msg_warning_title"], S["msg_annex_empty"])
            return

        row = self.annexTable.indexOfTopLevelItem(currentItem.parent() or currentItem)
        item = self.annexTable.topLevelItem(row)
        if item:
            item.setText(1, content)
            item.setTextAlignment(1, Qt.AlignCenter)
        self.annexContent.clear()

    def deleteRow(self):
        """Delete the selected annex row and reindex remaining letters."""
        currentItem = self.annexTable.currentItem()
        if not currentItem:
            CustomMessageBox.warning(self, S["msg_warning_title"], S["msg_annex_no_selection"])
            return

        row = self.annexTable.indexOfTopLevelItem(currentItem.parent() or currentItem)
        # Disconnect signal before removal to prevent autofill on next selection
        self.annexTable.itemSelectionChanged.disconnect(self.loadSelectedRow)
        self.annexTable.takeTopLevelItem(row)
        self.reindexRowLetters()
        # Clear input fields — deleted row should not populate the edit box
        self.annexContent.clear()
        self.annexTable.clearSelection()
        # Reconnect signal
        self.annexTable.itemSelectionChanged.connect(self.loadSelectedRow)

    def loadSelectedRow(self):
        """Load the selected row content into the input field for editing."""
        currentItem = self.annexTable.currentItem()
        if currentItem:
            row = self.annexTable.indexOfTopLevelItem(currentItem.parent() or currentItem)
            item = self.annexTable.topLevelItem(row)
            if item:
                self.annexContent.setText(item.text(1))

    def _onClearAll(self):
        """Global reset: clears this page and signals app.py to reset all other pages."""
        reply = CustomMessageBox.question(
            self,
            S["dlg_clear_all_title"],
            S["dlg_clear_all_body"],
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.No:
            return

        # Reset client data
        self.insuredCompany.clear()
        self.insuredAddress.clear()
        self.insuredContactName.clear()

        # Reset OPE
        self.opeNumber.clear()
        self.opeBarcode.clear()

        # Reset letter type
        self.policyOperation.setExclusive(False)
        self.policyIssue.setChecked(False)
        self.policyRenewal.setChecked(False)
        self.policyOperation.setExclusive(True)

        # Reset LOL
        self.limitOfLiabilityGroup.setExclusive(False)
        self.limitUndefined.setChecked(False)
        self.limitGeneric.setChecked(False)
        self.limitFixedAmount.setChecked(False)
        self.limitMultinacional.setChecked(False)
        self.limitOfLiabilityGroup.setExclusive(True)
        self.liabilityLimit.setVisible(False)
        self.limitAmount.clear()

        # Reset output format to default
        self.outputWord.setChecked(True)

        # Reset annexes to defaults
        self.annexTable.clear()
        self._addDefaultAnnexRow("Manual de Procedimientos en Caso de Siniestros")
        self._addDefaultAnnexRow('Flyer "Portal de Siniestros"')
        self._addDefaultAnnexRow("Garantías Particulares")
        self.annexContent.clear()

        # Signal app.py to reset all other pages
        self.signalReset.emit()

    def getData(self):
        """Collect and return all form data as a dict for document generation.""" 
        formData = {}

        if self.policyIssue.isChecked():
            formData['letterType'] = 'Emision'
        elif self.policyRenewal.isChecked():
            formData['letterType'] = 'Renovacion'
        else:
            formData['letterType'] = ''

        formData['letterNumber'] = self.opeNumber.text()
        formData['barcode']      = self.opeBarcode.text()

        formData['companyName']  = self.insuredCompany.text()
        formData['address']      = self.insuredAddress.text()
        formData['contactName']  = self.insuredContactName.text()

        if self.limitUndefined.isChecked():
            formData['lolAmountType']  = 'Sin Definir'
            formData['lolAmountValue'] = ''
        elif self.limitGeneric.isChecked():
            formData['lolAmountType']  = 'General'
            formData['lolAmountValue'] = ''
        elif self.limitFixedAmount.isChecked():
            formData['lolAmountType']  = 'Fijo'
            formData['lolAmountValue'] = self.limitAmount.text()
        elif self.limitMultinacional.isChecked():
            formData['lolAmountType']  = 'Multinacional'
            formData['lolAmountValue'] = ''
        else:
            formData['lolAmountType']  = ''
            formData['lolAmountValue'] = ''

        if self.outputWord.isChecked():
            formData['outputFormat'] = 'word'
        elif self.outputPdf.isChecked():
            formData['outputFormat'] = 'pdf'
        elif self.outputBoth.isChecked():
            formData['outputFormat'] = 'both'
        else:
            formData['outputFormat'] = 'word'

        annexList = []
        for row in range(self.annexTable.topLevelItemCount()):
            item = self.annexTable.topLevelItem(row)
            letter  = item.text(0) if item else ''
            content = item.text(1) if item else ''
            annexList.append({'anexo': letter, 'contenido': content})
        formData['attachments'] = annexList

        return formData
