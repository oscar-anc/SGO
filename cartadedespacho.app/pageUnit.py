from strings import S
"""
Page 2: Unit Selection
Select business segment, unit and executive with complete information display.
Signature images are loaded from the path stored in db.json under 'firma'.
If the image file does not exist, the placeholder label 'Sin firma' is shown.
"""

from theme import QSSA
from validators import DropDownComboBox
from PySide6.QtWidgets import *
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap
from widgets import NoNewlineLineEdit, CardWidget
import json
import os
from helpers import resource_path


class PageUnit(QWidget):
    """Unit selection page - Page 2"""

    signalNext = Signal()
    signalBack = Signal()

    def __init__(self):
        super().__init__()
        self.database = self.loadDatabase()
        # Store the current executive's signature path so getData() can return it.
        # Updated each time onExecutiveInfoChange() fires.
        self._currentExecutiveSignaturePath = ''
        self._currentLeaderSignaturePath    = ''
        self._currentLeaderEmail            = ''   # correo_lider from db.json
        self._currentLeaderMobile           = ''   # celular_lider from db.json
        self._gerenteData                   = {}   # kept for schema safety only
        self.buildUI()

    def loadDatabase(self):
        """Load units and executives database from db.json."""
        try:
            with open(resource_path('db.json'), 'r', encoding='utf-8') as dbFile:
                return json.load(dbFile)
        except Exception:
            return {}

    def buildUI(self):
        """Build complete user interface."""
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        containerWidget = QWidget()
        mainLayout = QVBoxLayout(containerWidget)

        # ── SEGMENTO ──────────────────────────────────────────────────────────
        # Business segment the executive belongs to
        groupSegment = CardWidget(S["card_segment"])
        segmentLayout = QVBoxLayout()

        self.segmentGroup      = QButtonGroup()
        self.segmentRisk       = QRadioButton(S["segment_risk"])
        self.segmentCorporate  = QRadioButton(S["segment_corporate"])
        self.segmentCommercial = QRadioButton(S["segment_commercial"])
        self.segmentGroup.addButton(self.segmentRisk)
        self.segmentGroup.addButton(self.segmentCorporate)
        self.segmentGroup.addButton(self.segmentCommercial)
        segmentLayout.addWidget(self.segmentRisk)
        segmentLayout.addWidget(self.segmentCorporate)
        segmentLayout.addWidget(self.segmentCommercial)
        groupSegment.setLayout(segmentLayout)
        mainLayout.addWidget(groupSegment)

        # Refresh unit list whenever segment selection changes
        self.segmentRisk.toggled.connect(self.onSegmentChange)
        self.segmentCorporate.toggled.connect(self.onSegmentChange)
        self.segmentCommercial.toggled.connect(self.onSegmentChange)

        # ── UNIDAD ────────────────────────────────────────────────────────────
        groupUnit = CardWidget(S["card_unit"])
        unitLayout = QVBoxLayout()
        self.units = DropDownComboBox()
        self.units.setEditable(True)
        self.units.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.units.setEnabled(False)
        self.units.currentTextChanged.connect(self.onUnitLeaderChange)
        unitLayout.addWidget(self.units)
        groupUnit.setLayout(unitLayout)
        mainLayout.addWidget(groupUnit)

        # ── LIDER DE UNIDAD ───────────────────────────────────────────────────
        groupLeader = CardWidget(S["card_unit_leader"])
        leaderLayout = QVBoxLayout()
        self.unitLeader = NoNewlineLineEdit()
        self.unitLeader.setReadOnly(True)
        leaderLayout.addWidget(self.unitLeader)
        groupLeader.setLayout(leaderLayout)
        mainLayout.addWidget(groupLeader)

        # ── EJECUTIVO ─────────────────────────────────────────────────────────
        groupExecutive = CardWidget(S["card_executive"])
        executiveLayout = QVBoxLayout()
        self.executives = DropDownComboBox()
        self.executives.setEditable(True)
        self.executives.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.executives.setEnabled(False)
        self.executives.currentTextChanged.connect(self.onExecutiveInfoChange)
        executiveLayout.addWidget(self.executives)
        groupExecutive.setLayout(executiveLayout)
        mainLayout.addWidget(groupExecutive)

        # ── INFORMACIÓN DEL EJECUTIVO ─────────────────────────────────────────
        groupInfo = CardWidget(S["card_executive_info"])
        infoLayout = QHBoxLayout()

        # Signature image placeholder — replaced with actual image when available.
        # QPixmap loads from the path stored in db.json['firma'].
        # If the file does not exist or QPixmap.isNull() is True, the "Sin firma"
        # text is kept as a visual placeholder inside the styled QLabel.
        self.executiveSignature = QLabel()
        self.executiveSignature.setFixedSize(*QSSA['unit_logo_size'])
        self.executiveSignature.setAlignment(Qt.AlignCenter)
        # Style via #SignaturePlaceholder in build_qss()
        self.executiveSignature.setObjectName("SignaturePlaceholder")
        self.executiveSignature.setText(S["signature_none"])
        infoLayout.addWidget(self.executiveSignature)

        # Executive detail labels (read-only, populated from database)
        detailsLayout = QFormLayout()
        # Left padding so labels are not flush against the signature image
        detailsLayout.setContentsMargins(*QSSA['margins_unit_details'])
        self.executiveName     = QLabel(S["exec_field_empty"])
        self.executivePosition = QLabel(S["exec_field_empty"])
        self.executiveEmail    = QLabel(S["exec_field_empty"])
        self.executiveMobile   = QLabel(S["exec_field_empty"])
        self.executivePhone    = QLabel(S["exec_field_empty"])
        detailsLayout.addRow(S["exec_field_name"],     self.executiveName)
        detailsLayout.addRow(S["exec_field_position"], self.executivePosition)
        detailsLayout.addRow(S["exec_field_email"],    self.executiveEmail)
        detailsLayout.addRow(S["exec_field_mobile"],   self.executiveMobile)
        detailsLayout.addRow(S["exec_field_phone"],    self.executivePhone)
        infoLayout.addLayout(detailsLayout)
        infoLayout.addStretch()

        groupInfo.setLayout(infoLayout)
        mainLayout.addWidget(groupInfo)

        mainLayout.addStretch()
        scrollArea.setWidget(containerWidget)

        # ── NAVIGATION — fixed outside scrollArea ─────────────────────────────
        previousStep = QPushButton(S["nav_back"])
        previousStep.clicked.connect(self.signalBack.emit)
        clearButton = QPushButton(S["nav_clear"])
        clearButton.clicked.connect(self._onClearPage)
        nextStep = QPushButton(S["nav_next"])
        nextStep.clicked.connect(self.signalNext.emit)

        navWidget = QWidget()
        navWidget.setObjectName("NavBar")
        navLayout = QHBoxLayout(navWidget)
        navLayout.setContentsMargins(*QSSA['margins_nav'])
        navLayout.addWidget(previousStep)
        navLayout.addStretch()
        navLayout.addWidget(clearButton)
        navLayout.addStretch()
        navLayout.addWidget(nextStep)

        pageLayout = QVBoxLayout(self)
        pageLayout.setContentsMargins(*QSSA['margins_zero'])
        pageLayout.setSpacing(QSSA['spacing_zero'])
        pageLayout.addWidget(scrollArea, 1)
        pageLayout.addWidget(navWidget)

    # ── Private helpers ────────────────────────────────────────────────────────

    def _loadSignatureIntoLabel(self, path):
        """
        Attempt to load a signature image from the given file path into
        self.executiveSignature QLabel.

        If the file exists and QPixmap loads successfully, the image is scaled
        to fit within the fixed 150x100 label while preserving aspect ratio.
        If the file does not exist or the pixmap is null, restores the
        'Sin firma' placeholder text instead — never raises an exception.

        Args:
            path (str): Relative or absolute path to the signature image.
        """
        # Reset to placeholder state first so partial failures are always clean
        self.executiveSignature.clear()
        self.executiveSignature.setText(S["signature_none"])

        if not path:
            return

        try:
            resolved = resource_path(path)
            if os.path.isfile(resolved):
                pixmap = QPixmap(resolved)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(
                        150, 100,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.executiveSignature.setPixmap(scaled)
                    # Clear the placeholder text once a real image is displayed
                    self.executiveSignature.setText("")
        except Exception:
            # Any unexpected error falls back silently to the placeholder
            pass

    def _getUnitData(self):
        """
        Return the db.json dict for the currently selected segment + unit,
        or None if the selection is incomplete or missing from the database.
        """
        segment = self.getSegment()
        unit    = self.units.currentText()
        if not segment or not unit:
            return None
        return self.database.get(segment, {}).get(unit)

    # ── Signal handlers ────────────────────────────────────────────────────────

    def onSegmentChange(self):
        """Refresh the units dropdown when the selected segment changes."""
        segment = self.getSegment()
        self.units.clear()
        self.units.setEnabled(bool(segment))
        if segment and segment in self.database:
            self.units.addItems(list(self.database[segment].keys()))

    def onUnitLeaderChange(self):
        """
        Update the unit leader field and refresh executives when unit changes.
        Also reads and stores the unit leader's signature path (firma_lider)
        from db.json so getData() can include it without a second lookup.
        """
        unitData = self._getUnitData()
        self.executives.clear()
        self.executives.setEnabled(bool(unitData))

        if not unitData:
            self.unitLeader.clear()
            self.executives.clear()
            self._currentLeaderSignaturePath = ''
            self._currentLeaderEmail  = ''
            self._currentLeaderMobile = ''
            return

        self.unitLeader.setText(unitData.get('lider', ''))

        # Store leader contact details — used in getData() for the Word doc
        # and for the Manual de Siniestros context in helpers.py.
        self._currentLeaderSignaturePath = unitData.get('firma_lider',   '')
        self._currentLeaderEmail         = unitData.get('correo_lider',  '')
        self._currentLeaderMobile        = unitData.get('celular_lider', '')

        self.refreshExecutiveList()

    def refreshExecutiveList(self):
        """Populate the executives dropdown for the currently selected unit."""
        unitData = self._getUnitData()
        self.executives.clear()

        if not unitData:
            return

        if 'ejecutivos' in unitData and isinstance(unitData['ejecutivos'], dict):
            self.executives.addItems(list(unitData['ejecutivos'].keys()))

    def onExecutiveInfoChange(self):
        """
        Update all executive detail labels when the selected executive changes.
        Loads the executive's signature image from the path stored in db.json
        under the 'firma' key. If the file does not exist or 'firma' is absent,
        the 'Sin firma' placeholder is shown. The path is also stored in
        self._currentExecutiveSignaturePath for use in getData().
        """
        segment   = self.getSegment()
        unit      = self.units.currentText()
        executive = self.executives.currentText()

        # Reset all labels and the signature image to default state
        self.executiveName.setText("-")
        self.executivePosition.setText("-")
        self.executiveEmail.setText("-")
        self.executiveMobile.setText("-")
        self.executivePhone.setText("-")
        self._currentExecutiveSignaturePath = ''
        # Reset the signature widget to placeholder
        self._loadSignatureIntoLabel('')

        if not segment or not unit or not executive:
            return

        try:
            data = self.database[segment][unit]['ejecutivos'][executive]
            if isinstance(data, dict):
                self.executiveName.setText(data.get('nombre', executive))
                self.executivePosition.setText(data.get('puesto', '-'))
                self.executiveEmail.setText(data.get('correo', '-'))
                self.executiveMobile.setText(data.get('celular', '-'))
                self.executivePhone.setText(data.get('telefono', '-'))

                # Read and store the executive's signature path.
                # 'firma' key may be absent in older db.json versions; defaults to ''.
                firma_path = data.get('firma', '')
                self._currentExecutiveSignaturePath = firma_path

                # Attempt to load the signature image into the QLabel.
                # Falls back to 'Sin firma' placeholder if file does not exist.
                self._loadSignatureIntoLabel(firma_path)

        except Exception:
            # Any key error or unexpected issue — reset to default silently
            self._currentExecutiveSignaturePath = ''
            self._loadSignatureIntoLabel('')

    # ── Public interface ───────────────────────────────────────────────────────

    def _onClearPage(self):
        """Reset all fields on this page after user confirmation."""
        from widgets import NoNewlineLineEdit, CustomMessageBox
        from PySide6.QtWidgets import QMessageBox
        reply = CustomMessageBox.question(
            self,
            S["dlg_clear_page_title"],
            S["dlg_clear_unit_body"],
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.No:
            return
        self.segmentGroup.setExclusive(False)
        for btn in self.segmentGroup.buttons():
            btn.setChecked(False)
        self.segmentGroup.setExclusive(True)
        self.units.clear()
        self.executives.clear()
        self.unitLeader.clear()
        self.executiveName.setText('-')
        self.executivePosition.setText('-')
        self.executiveEmail.setText('-')
        self.executiveMobile.setText('-')
        self.executivePhone.setText('-')
        self._currentExecutiveSignaturePath = ''
        self._currentLeaderSignaturePath    = ''
        self._currentLeaderEmail            = ''
        self._currentLeaderMobile           = ''
        self._loadSignatureIntoLabel('')

    def getSegment(self):
        """Return the currently selected segment string or None."""
        if self.segmentRisk.isChecked():
            return "Risk"
        elif self.segmentCorporate.isChecked():
            return "Corporate"
        elif self.segmentCommercial.isChecked():
            return "Commercial"
        return None

    def getData(self):
        """
        Collect and return all unit/executive form data.

        The firma table in the Word document always shows the Líder de Unidad
        alongside the Executive. Variables unitLeader and unitLeaderSignature
        are used directly in the template — no conditional selection needed.
        """
        return {
            'segment':                  self.getSegment() or '',
            'unit':                     self.units.currentText(),
            'unitLeader':               self.unitLeader.text(),
            'leaderEmail':              self._currentLeaderEmail,
            'leaderMobile':             self._currentLeaderMobile,
            'executive':                self.executives.currentText(),
            'executiveName':            self.executiveName.text(),
            'executivePosition':        self.executivePosition.text(),
            'executiveEmail':           self.executiveEmail.text(),
            'executiveMobile':          self.executiveMobile.text(),
            'executivePhone':           self.executivePhone.text(),
            # Signature file paths — helpers.py loads these as InlineImage objects
            'executiveSignature':       self._currentExecutiveSignaturePath,
            'unitLeaderSignature':      self._currentLeaderSignaturePath,
        }
