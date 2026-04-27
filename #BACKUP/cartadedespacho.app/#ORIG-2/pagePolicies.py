from strings import S
from theme import QSSA
"""
Página 3: Pólizas
Structure (top to bottom):
  1. Cantidad de Pólizas  &  Cantidad de Asegurados  (side by side)
  2. Datos de la Póliza
  3. Financiamiento  &  Cesiones de Derecho  (side by side)
  4. Asegurado/s  — always stacked vertically
       4.1 Pólizas  — QGridLayout, groups of POLICY_MAX_COLS columns, rebuilt on add/remove only
       4.2 Botón Agregar/Quitar Póliza (if applicable)
       4.3 Botón Quitar Asegurado (if applicable)
  5. Botón Agregar Asegurado (if applicable)

Policy grid layout rules (POLICY_MAX_COLS = 3 columns per row):
  n=1  → [p1 full width]
  n=2  → [p1 half][p2 half]
  n=3  → [p1 third][p2 third][p3 third]
  n=4  → [p1][p2][p3] / [p4 full width]
  n=5  → [p1][p2][p3] / [p4 half][p5 half]
  n=6  → [p1][p2][p3] / [p4][p5][p6]
  ...and so on. Maximum = POLICY_MAX (12).

Partial-row layout is handled by placing remainder cards into a QHBoxLayout
wrapped in a single grid cell spanning all columns. This avoids colspan integer
division bugs (e.g. 3//2=1 leaving a phantom column) and is simpler to reason about.

KEY SAFETY RULE — no setParent(None) in _rebuildPolicyGrid():
  removeWidget() detaches the layout item but keeps Qt ownership with policyContainer.
  Python references in policyList remain valid. Rebuild triggers only on add/delete,
  never on resizeEvent. This is what prevents the cascade-crash.
"""

from theme import QSSA
from PySide6.QtWidgets import (
    QCompleter,
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QScrollArea, QLabel, QLineEdit, QPushButton,
    QRadioButton, QButtonGroup, QComboBox, QSizePolicy, QMessageBox,
)
from PySide6.QtCore import Signal, QDate, Qt
from widgets import NoNewlineLineEdit, CustomMessageBox, CardWidget
    from validators import ThemedDateEdit
import json
import uuid
from helpers import resource_path

from validators import (
    DropDownComboBox,
    lettersAmpersandValidator,
    currencyInputValidator,
    applyCurrencyFormat,
)

# ── Policy grid constants ──────────────────────────────────────────────────────
# Max columns per full row. Change to 2 to switch to 2-column groups everywhere.
POLICY_MAX_COLS = 3

# Max policies per insured. Should be a multiple of POLICY_MAX_COLS.
POLICY_MAX = 12

def _loadDbList(key, fallback):
    """Load a list from db.json by key, returning fallback if unavailable."""
    try:
        with open(resource_path('db.json'), 'r', encoding='utf-8') as _f:
            return json.load(_f).get(key, fallback)
    except Exception:
        return fallback

# Loaded from db.json — edit db.json to update these lists
INSURANCE_COMPANIES = _loadDbList('aseguradoras', [
    "RIMAC SEGUROS Y REASEGUROS",
    "PACIFICO SEGUROS",
    "MAPFRE PERU",
    "LA POSITIVA SEGUROS",
    "CHUBB SEGUROS",
    "LIBERTY SEGUROS",
    "AVLA PERU COMPAÑIA DE SEGUROS",
])

POLICY_BRANCHES = _loadDbList('ramos', [])


class PolicyWidget(CardWidget):
    """
    Single policy entry widget.
    Labels above each QLineEdit for readability in narrow grid columns.
    widgetId is a stable UUID fragment used as the paymentData key in app.py —
    it never changes even if branch/number fields are edited by the user.
    """

    signalDelete = Signal(object)

    def __init__(self, policyNumber, canDelete=False):
        super().__init__(
            '',  # branch shown in header via combo
            collapsible=True, bold_title=True
        )
        self.canDelete    = canDelete
        self.policyNumber = policyNumber
        self.widgetId     = str(uuid.uuid4())[:8]
        self.buildUI()

    def buildUI(self):
        """Build policy — branch in header, other fields in collapsible body."""
        # ── Header: [▼] [policyBranch···] [🗑] ──────────────────────────
        from PySide6.QtCore import QByteArray
        from PySide6.QtGui import QIcon, QPixmap
        from svgs import get_svg_trash
        hl = self._header.layout()
        btn_sz = QSSA.get('card_toggle_fixed_size', (18, 18))[0]

        # Clear existing header and rebuild in correct order
        while hl.count():
            item = hl.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        # [▼] accordion toggle
        if hasattr(self, '_toggleBtn'):
            hl.addWidget(self._toggleBtn, 0, Qt.AlignVCenter)

        # [policyBranch···] with stretch
        self.policyBranch = DropDownComboBox()
        self.policyBranch.setEditable(True)
        self.policyBranch.setInsertPolicy(DropDownComboBox.NoInsert)
        self.policyBranch.addItems(POLICY_BRANCHES)
        self.policyBranch.setCurrentIndex(-1)
        self.policyBranch.lineEdit().setPlaceholderText(S["policy_branch_placeholder"])
        self.policyBranch.setObjectName('CardTitle')
        _completer = QCompleter(POLICY_BRANCHES, self.policyBranch)
        _completer.setCaseSensitivity(Qt.CaseInsensitive)
        _completer.setFilterMode(Qt.MatchContains)
        self.policyBranch.setCompleter(_completer)
        hl.addWidget(self.policyBranch, 1)

        # [🗑] trash at far right
        if self.canDelete:
            trashBtn = QPushButton()
            trashBtn.setProperty('role', 'endtable-danger')
            trashBtn.setFixedSize(btn_sz + 8, btn_sz + 8)
            px = QPixmap()
            px.loadFromData(QByteArray(get_svg_trash('#ffffff').encode()), 'SVG')
            if not px.isNull():
                trashBtn.setIcon(QIcon(px))
            trashBtn.clicked.connect(lambda: self.signalDelete.emit(self))
            hl.addWidget(trashBtn, 0, Qt.AlignVCenter)

        # ── Body — remaining fields ────────────────────────────────────────
        mainLayout = QVBoxLayout()
        mainLayout.setSpacing(QSSA['spacing_policies_main'])

        mainLayout.addWidget(QLabel(S["policy_label_number"]))
        self.policyNum = NoNewlineLineEdit()
        mainLayout.addWidget(self.policyNum)

        mainLayout.addWidget(QLabel(S["policy_label_receipt"]))
        self.policyReceipt = NoNewlineLineEdit()
        mainLayout.addWidget(self.policyReceipt)

        mainLayout.addWidget(QLabel(S["policy_label_premium"]))
        self.policyPremium = NoNewlineLineEdit()
        self.policyPremium.setPlaceholderText(S["policy_placeholder_premium"])
        self.policyPremium.setValidator(currencyInputValidator())
        self.policyPremium.editingFinished.connect(
            lambda: applyCurrencyFormat(self.policyPremium)
        )
        mainLayout.addWidget(self.policyPremium)

        mainLayout.addWidget(QLabel(S["policy_label_premium_total"]))
        self.policyPremiumTotal = NoNewlineLineEdit()
        self.policyPremiumTotal.setPlaceholderText(S["policy_placeholder_premium"])
        self.policyPremiumTotal.setValidator(currencyInputValidator())
        self.policyPremiumTotal.editingFinished.connect(
            lambda: applyCurrencyFormat(self.policyPremiumTotal)
        )
        mainLayout.addWidget(self.policyPremiumTotal)

        mainLayout.addStretch()
        self.setLayout(mainLayout)

    def renumber(self, newNumber):
        """Update placeholder when cards are reordered after a deletion."""
        self.policyNumber = newNumber
        self.policyBranch.lineEdit().setPlaceholderText(
            f"{S['policy_branch_placeholder']} #{newNumber}"
            if newNumber > 1 else S['policy_branch_placeholder'])

    def getData(self):
        """Return policy field values as a dict."""
        return {
            'POLIZA_RAMO':        self.policyBranch.currentText(),
            'POLIZA_NUMERO':      self.policyNum.text(),
            'POLIZA_RECIBO':      self.policyReceipt.text(),
            'POLIZA_PRIMA':       self.policyPremium.text(),
            'POLIZA_PRIMA_TOTAL': self.policyPremiumTotal.text(),
        }


class InsuredWidget(CardWidget):
    """
    Single insured party widget.
    Manages a list of PolicyWidget instances in a QGridLayout with groups of
    POLICY_MAX_COLS columns per row.

    Partial-row handling: remainder cards are placed inside a QHBoxLayout
    wrapper that spans all grid columns. This avoids colspan integer-division
    bugs and produces correct 50/50 or full-width layouts for any remainder.

    Grid safety: _rebuildPolicyGrid() uses only removeWidget() — no setParent(None).
    Rebuild is triggered only on add/delete, never on resizeEvent.
    """

    signalDelete = Signal(object)

    def __init__(self, insuredNumber, canDelete=False, allowMultiplePolicies=False):
        super().__init__(
            '',  # title set dynamically via insuredName
            collapsible=True, bold_title=True
        )
        self.insuredNumber         = insuredNumber
        self.canDelete             = canDelete
        self.allowMultiplePolicies = allowMultiplePolicies
        self.policyList            = []
        self.widgetId              = str(uuid.uuid4())[:8]
        self._lastRowWrapper       = None
        self.buildUI()

    def buildUI(self):
        """Build insured entry — name field in header, policies in body."""
        # ── Header: [▼] [insuredName···] [🗑] ────────────────────────────
        from PySide6.QtCore import QByteArray
        from PySide6.QtGui import QIcon, QPixmap
        from svgs import get_svg_trash
        hl = self._header.layout()
        btn_sz = QSSA.get('card_toggle_fixed_size', (18, 18))[0]

        # Clear existing header widgets and rebuild in correct order
        while hl.count():
            item = hl.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        # [▼] accordion toggle
        if hasattr(self, '_toggleBtn'):
            hl.addWidget(self._toggleBtn, 0, Qt.AlignVCenter)

        # [insuredName···] with stretch
        self.insuredName = NoNewlineLineEdit()
        self.insuredName.setPlaceholderText(
            f"{S['insured_label_name']} #{self.insuredNumber}"
            if self.insuredNumber > 1 else S['insured_label_name'])
        self.insuredName.setObjectName('CardTitle')
        self.insuredName.setFrame(False)
        self.insuredName.setStyleSheet('background: transparent;')
        hl.addWidget(self.insuredName, 1)

        # [🗑] trash at far right
        if self.canDelete:
            trashBtn = QPushButton()
            trashBtn.setProperty('role', 'endtable-danger')
            trashBtn.setFixedSize(btn_sz + 8, btn_sz + 8)
            px = QPixmap()
            px.loadFromData(QByteArray(get_svg_trash('#ffffff').encode()), 'SVG')
            if not px.isNull():
                trashBtn.setIcon(QIcon(px))
            trashBtn.clicked.connect(lambda: self.signalDelete.emit(self))
            hl.addWidget(trashBtn, 0, Qt.AlignVCenter)

        # ── Body — policy grid ─────────────────────────────────────────────
        mainLayout = QVBoxLayout()
        self.policyContainer = QWidget()
        self.policyGrid      = QGridLayout(self.policyContainer)
        self.policyGrid.setContentsMargins(*QSSA['margins_policies_grid'])
        self.policyGrid.setSpacing(QSSA['spacing_policies_grid'])
        mainLayout.addWidget(self.policyContainer)

        if self.allowMultiplePolicies:
            self.addPolicyBtn = QPushButton(S["btn_add_policy"])
            self.addPolicyBtn.clicked.connect(self.addPolicyRow)
            mainLayout.addWidget(self.addPolicyBtn)

        self.setLayout(mainLayout)

        firstPolicy = PolicyWidget(1, canDelete=False)
        firstPolicy.setParent(self.policyContainer)
        self.policyList.append(firstPolicy)
        self._rebuildPolicyGrid()

    def _rebuildPolicyGrid(self):
        """
        Reposition all policy widgets according to POLICY_MAX_COLS rules.

        Full rows: each row holds exactly POLICY_MAX_COLS widgets, one per column.
        Partial row (remainder > 0): a QHBoxLayout wrapper widget spans all columns,
          containing the remainder cards with equal stretch. This avoids the
          colspan division bug and correctly produces 50/50 for remainder=2,
          full-width for remainder=1, etc.

        All widgets are detached with removeWidget() before repositioning.
        removeWidget() does not call setParent() — Qt ownership stays with
        policyContainer throughout the operation.
        """
        n    = len(self.policyList)
        cols = POLICY_MAX_COLS

        # Detach all current items — removeWidget keeps ownership with policyContainer
        for policy in self.policyList:
            self.policyGrid.removeWidget(policy)

        # Remove the previous partial-row wrapper if it exists.
        # setParent(None) is SAFE here: _lastRowWrapper is a throwaway QWidget container
        # that has no Python references. The PolicyWidgets inside it are only referenced
        # via policyList — they are owned by policyContainer, not by this wrapper.
        # Destroying the wrapper does NOT invalidate any PolicyWidget pointer.
        if self._lastRowWrapper is not None:
            self.policyGrid.removeWidget(self._lastRowWrapper)
            self._lastRowWrapper.setParent(None)
            self._lastRowWrapper.deleteLater()
            self._lastRowWrapper = None

        # Reset column stretch values from the previous layout
        for c in range(cols):
            self.policyGrid.setColumnStretch(c, 0)

        full_rows = n // cols
        remainder = n % cols

        # Place full-row widgets: row i, col 0..cols-1
        for idx in range(full_rows * cols):
            row = idx // cols
            col = idx % cols
            self.policyGrid.addWidget(self.policyList[idx], row, col)

        # Place partial-row widgets in a QHBoxLayout wrapper spanning all columns.
        # This produces correct equal-width sharing regardless of remainder count:
        #   remainder=1 → full width,  remainder=2 → 50/50,  remainder=3 → 33/33/33
        if remainder > 0:
            wrapper = QWidget(self.policyContainer)
            wrapperLayout = QHBoxLayout(wrapper)
            wrapperLayout.setContentsMargins(*QSSA['margins_policies_wrapper'])
            wrapperLayout.setSpacing(QSSA['spacing_policies_wrapper'])
            for i in range(remainder):
                policy = self.policyList[full_rows * cols + i]
                wrapperLayout.addWidget(policy, 1)   # stretch=1 → equal share
            self.policyGrid.addWidget(wrapper, full_rows, 0, 1, cols)
            self._lastRowWrapper = wrapper

        # Equal column stretch on full rows so all columns share width evenly
        for c in range(cols):
            self.policyGrid.setColumnStretch(c, 1)

        # Renumber all policy cards so titles/buttons stay consistent after deletions
        for i, policy in enumerate(self.policyList):
            policy.renumber(i + 1)

        # Ensure all widgets are visible (Qt may hide them after removeWidget)
        for policy in self.policyList:
            policy.show()

    def addPolicyRow(self):
        """Add a new deletable policy card and rebuild the grid."""
        if len(self.policyList) >= POLICY_MAX:
            CustomMessageBox.warning(
                self, "Límite alcanzado",
                f"Máximo {POLICY_MAX} pólizas por asegurado."
            )
            return
        policyNumber = len(self.policyList) + 1
        newPolicy    = PolicyWidget(policyNumber, canDelete=True)
        newPolicy.setParent(self.policyContainer)
        newPolicy.signalDelete.connect(self.deletePolicyRow)
        self.policyList.append(newPolicy)
        self._rebuildPolicyGrid()

    def deletePolicyRow(self, widgetToDelete):
        """
        Remove a policy card and rebuild the grid.
        deleteLater() schedules destruction after all pending signals are processed,
        preventing use-after-free on the clicked signal that fired this method.
        """
        if widgetToDelete in self.policyList:
            self.policyList.remove(widgetToDelete)
        self.policyGrid.removeWidget(widgetToDelete)
        widgetToDelete.hide()
        widgetToDelete.deleteLater()
        self._rebuildPolicyGrid()

    def getData(self):
        """Return insured name and all associated policy data."""
        data = {'POLIZA_ASEGURADO': self.insuredName.text()}
        if self.policyList:
            data.update(self.policyList[0].getData())
            data['polizas'] = [p.getData() for p in self.policyList[1:]]
        return data


class PagePolicies(QWidget):
    """
    Página 3: Pólizas (dinámica).
    Quantity selectors, financing and currency live here.
    The insured/policy area is hidden until both quantity selectors have a value.
    """

    signalNext     = Signal()
    signalGenerate = Signal()
    signalBack     = Signal()
    signalReset         = Signal()
    signalCesionesReduce    = Signal()   # emitted when user confirms structure reduction
    signalEndorsementCleared = Signal()  # emitted when Si(Detallado) is turned off with data

    def __init__(self):
        super().__init__()

        self.pageConfig = {
            'allowMultipleInsured':  False,
            'allowMultiplePolicies': False,
        }

        self.additionalInsuredList = []
        self._prefillName          = ""
        self.blockSignalChanges    = False
        self._endorsementDataRef   = {}  # reference to app.py endorsementData
        self._paymentDataRef       = {}  # reference to app.py paymentData
        self._annexDataRef         = {}  # reference to app.py annexData

        self.buildUI()

    def buildUI(self):
        """Build the full page layout."""
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        containerWidget = QWidget()
        self.mainLayout = QVBoxLayout(containerWidget)

        # ── 1. CANTIDAD DE PÓLIZAS  &  CANTIDAD DE ASEGURADOS  (side by side) ─
        quantityRow = QHBoxLayout()
        quantityRow.setSpacing(QSSA['spacing_policies_qty_row'])
        quantityRow.setContentsMargins(*QSSA['margins_policies_qty_row'])

        groupPolicyQty  = CardWidget(S["card_policy_qty"])
        policyQtyLayout = QVBoxLayout()
        self.policyQuantity   = QButtonGroup()
        self.singlePolicy     = QRadioButton(S["policy_qty_single"])
        self.multiplePolicies = QRadioButton(S["policy_qty_multiple"])
        self.policyQuantity.addButton(self.singlePolicy)
        self.policyQuantity.addButton(self.multiplePolicies)
        policyQtyLayout.addWidget(self.singlePolicy)
        policyQtyLayout.addWidget(self.multiplePolicies)
        groupPolicyQty.setLayout(policyQtyLayout)
        # Collapse card to its content height — no extra space below radio buttons
        groupPolicyQty.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        groupInsuredQty  = CardWidget(S["card_insured_qty"])
        insuredQtyLayout = QVBoxLayout()
        self.insuredQuantity  = QButtonGroup()
        self.singleInsured    = QRadioButton(S["insured_qty_single"])
        self.multipleInsured  = QRadioButton(S["insured_qty_multiple"])
        self.insuredQuantity.addButton(self.singleInsured)
        self.insuredQuantity.addButton(self.multipleInsured)
        insuredQtyLayout.addWidget(self.singleInsured)
        insuredQtyLayout.addWidget(self.multipleInsured)
        groupInsuredQty.setLayout(insuredQtyLayout)
        groupInsuredQty.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        quantityRow.addWidget(groupPolicyQty, 1)
        quantityRow.addWidget(groupInsuredQty, 1)
        quantityContainer = QWidget()
        quantityContainer.setLayout(quantityRow)
        self.mainLayout.addWidget(quantityContainer)

        self.singlePolicy.toggled.connect(
            lambda checked: self._onQuantityChanged() if checked else None)
        self.multiplePolicies.toggled.connect(
            lambda checked: self._onQuantityChanged() if checked else None)
        self.singleInsured.toggled.connect(
            lambda checked: self._onQuantityChanged() if checked else None)
        self.multipleInsured.toggled.connect(
            lambda checked: self._onQuantityChanged() if checked else None)

        # ── 2. DATOS DE LA PÓLIZA ─────────────────────────────────────────────
        groupPolicyData  = CardWidget(S["card_policy_data"])
        policyDataLayout = QFormLayout()

        self.insurer = DropDownComboBox()
        self.insurer.setEditable(True)
        self.insurer.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.insurer.addItems(INSURANCE_COMPANIES)
        self.insurer.setCurrentIndex(-1)
        self.insurer.lineEdit().setPlaceholderText(
            S.get('policy_data_insurer_placeholder', 'Seleccione o escriba...'))
        self.insurer.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        policyDataLayout.addRow(S["policy_data_insurer"], self.insurer)

        datesWidget = QWidget()
        datesRow    = QHBoxLayout(datesWidget)
        datesRow.setContentsMargins(*QSSA['margins_inline_row'])
        self.policyStartDate = ThemedDateEdit()
        self.policyStartDate.setCalendarPopup(True)
        self.policyStartDate.setDate(QDate.currentDate())
        datesRow.addWidget(self.policyStartDate)
        datesRow.addWidget(QLabel(S["policy_data_validity_to"]))
        self.policyEndDate = ThemedDateEdit()
        self.policyEndDate.setCalendarPopup(True)
        self.policyEndDate.setDate(QDate.currentDate().addDays(365))
        datesRow.addWidget(self.policyEndDate)
        # Auto-set end date to +365 days when start date changes
        self.policyStartDate.dateChanged.connect(
            lambda d: self.policyEndDate.setDate(d.addDays(365))
        )
        datesRow.addStretch()
        policyDataLayout.addRow(S["policy_data_validity"], datesWidget)

        currencyWidget = QWidget()
        currencyRow    = QHBoxLayout(currencyWidget)
        currencyRow.setContentsMargins(*QSSA['margins_policies_currency'])
        currencyRow.setSpacing(QSSA['spacing_policies_currency'])
        self.currencyGroup = QButtonGroup()
        self.currencyPE    = QRadioButton(S["currency_soles"])
        self.currencyUS    = QRadioButton(S["currency_dollars"])
        self.currencyGroup.addButton(self.currencyPE)
        self.currencyGroup.addButton(self.currencyUS)
        currencyRow.addWidget(self.currencyPE)
        currencyRow.addWidget(self.currencyUS)
        currencyRow.addStretch()
        policyDataLayout.addRow(S["policy_data_currency"], currencyWidget)

        groupPolicyData.setLayout(policyDataLayout)
        self.mainLayout.addWidget(groupPolicyData)

        # ── 3. FINANCIAMIENTO  &  CESIONES DE DERECHO  (side by side) ────────
        finCesRow = QHBoxLayout()
        finCesRow.setSpacing(QSSA['spacing_policies_finces'])
        finCesRow.setContentsMargins(*QSSA['margins_policies_finces'])

        self.cardFinancing  = CardWidget(S["card_financing"])
        financingLayout = QVBoxLayout()
        self.financingOptions = QButtonGroup()
        self.financingYes     = QRadioButton(S["yes"])
        self.financingNo      = QRadioButton(S["no"])
        self.financingOptions.addButton(self.financingYes)
        self.financingOptions.addButton(self.financingNo)
        financingLayout.addWidget(self.financingYes)
        financingLayout.addWidget(self.financingNo)
        self.cardFinancing.setLayout(financingLayout)
        self.cardFinancing.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Cesiones de Derecho — radio buttons vertical (not horizontal)
        self.cardEndorsement  = CardWidget(S["card_endorsement"])
        endorsementLayout = QVBoxLayout()
        self.endorsement         = QButtonGroup()
        self.endorsementYes      = QRadioButton(S["endorsement_simple"])
        self.endorsementDetailed = QRadioButton(S["endorsement_detailed"])
        self.endorsementNo       = QRadioButton(S["no"])
        self.endorsement.addButton(self.endorsementYes)
        self.endorsement.addButton(self.endorsementDetailed)
        self.endorsement.addButton(self.endorsementNo)
        endorsementLayout.addWidget(self.endorsementYes)
        endorsementLayout.addWidget(self.endorsementDetailed)
        endorsementLayout.addWidget(self.endorsementNo)

        self.endorsementData = QWidget()
        edLayout             = QVBoxLayout(self.endorsementData)
        edLayout.setContentsMargins(*QSSA['margins_policies_ed'])
        edLayout.addWidget(QLabel(S["endorsement_label_branch"]))
        self.endorsementBranch = NoNewlineLineEdit()
        edLayout.addWidget(self.endorsementBranch)
        edLayout.addWidget(QLabel(S["endorsement_label_beneficiary"]))
        self.endorsementBeneficiary = NoNewlineLineEdit()
        edLayout.addWidget(self.endorsementBeneficiary)
        self.endorsementData.setVisible(False)
        endorsementLayout.addWidget(self.endorsementData)

        # Show line edits only for Simple — Detallado uses PageAnnex card
        self.endorsementYes.toggled.connect(self.endorsementData.setVisible)
        self.cardEndorsement.setLayout(endorsementLayout)
        self.cardEndorsement.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        finCesRow.addWidget(self.cardFinancing, 1)
        finCesRow.addWidget(self.cardEndorsement, 1)
        finCesContainer = QWidget()
        finCesContainer.setLayout(finCesRow)
        self.mainLayout.addWidget(finCesContainer)

        self.financingYes.toggled.connect(
            lambda checked: self._onFinancingChanged() if checked else None)
        self.financingNo.toggled.connect(
            lambda checked: self._onFinancingChanged() if checked else None)

        # ── 4. INSURED / POLICY AREA ──────────────────────────────────────────
        self.insuredArea = QWidget()
        self.insuredArea.setVisible(False)
        insuredAreaLayout = QVBoxLayout(self.insuredArea)
        insuredAreaLayout.setContentsMargins(*QSSA['margins_policies_insured'])

        self.mainInsured = InsuredWidget(1, canDelete=False, allowMultiplePolicies=False)
        insuredAreaLayout.addWidget(self.mainInsured)

        self.containerClients = QWidget()
        self.layoutClients    = QVBoxLayout(self.containerClients)
        self.layoutClients.setContentsMargins(*QSSA['margins_policies_clients'])
        insuredAreaLayout.addWidget(self.containerClients)

        self.addInsuredButton = QPushButton(S["btn_add_insured"])
        self.addInsuredButton.clicked.connect(self.addInsured)
        self.addInsuredButton.setVisible(False)
        insuredAreaLayout.addWidget(self.addInsuredButton)

        self.mainLayout.addWidget(self.insuredArea)

        # ── NAVIGATION — fixed outside scrollArea ─────────────────────────────
        previousStep = QPushButton(S["nav_back"])
        previousStep.clicked.connect(self.signalBack.emit)

        self.clearButton = QPushButton(S["nav_clear"])
        self.clearButton.clicked.connect(self._onClearClicked)

        self.nextStep = QPushButton(S["nav_next"])
        self.nextStep.clicked.connect(self.signalNext.emit)
        self.nextStep.setVisible(False)

        self.generateDocument = QPushButton(S["nav_generate"])
        self.generateDocument.clicked.connect(self.signalGenerate.emit)
        self.generateDocument.setVisible(False)

        self.mainLayout.addStretch()
        scrollArea.setWidget(containerWidget)

        navWidget = QWidget()
        navWidget.setObjectName("NavBar")
        navRow = QHBoxLayout(navWidget)
        navRow.setContentsMargins(*QSSA['margins_nav'])
        navRow.addWidget(previousStep)
        navRow.addStretch()
        navRow.addWidget(self.clearButton)
        navRow.addStretch()
        navRow.addWidget(self.nextStep)
        navRow.addWidget(self.generateDocument)

        pageLayout = QVBoxLayout(self)
        pageLayout.setContentsMargins(*QSSA['margins_zero'])
        pageLayout.setSpacing(QSSA['spacing_zero'])
        pageLayout.addWidget(scrollArea, 1)
        pageLayout.addWidget(navWidget)

    # ── Quantity / financing handlers ──────────────────────────────────────────

    def _bothQuantitiesSelected(self):
        return (
            (self.singlePolicy.isChecked() or self.multiplePolicies.isChecked()) and
            (self.singleInsured.isChecked() or self.multipleInsured.isChecked())
        )

    def _hasInsuredData(self):
        """Return True if any data exists in the insured/policy area."""
        if self.mainInsured.insuredName.text().strip():
            return True
        for policy in self.mainInsured.policyList:
            if any([policy.policyBranch.currentText().strip(),
                    policy.policyNum.text().strip(),
                    policy.policyReceipt.text().strip(),
                    policy.policyPremium.text().strip(),
                    policy.policyPremiumTotal.text().strip()]):
                return True
        return bool(self.additionalInsuredList)

    def _onQuantityChanged(self):
        """
        Rebuilds the insured/policy area when quantity selectors change.
        Shows a confirmation dialog only when reducing (data could be lost).
        blockSignalChanges suppresses the dialog during programmatic reverts.
        """
        if not self._bothQuantitiesSelected():
            self.insuredArea.setVisible(False)
            return

        self.insuredArea.setVisible(True)

        allowMultiplePolicies = self.multiplePolicies.isChecked()
        allowMultipleInsured  = self.multipleInsured.isChecked()
        prevMultiPolicies     = self.pageConfig['allowMultiplePolicies']
        prevMultiInsured      = self.pageConfig['allowMultipleInsured']
        reducingPolicies      = prevMultiPolicies and not allowMultiplePolicies
        reducingInsured       = prevMultiInsured  and not allowMultipleInsured

        if (not self.blockSignalChanges
                and (reducingPolicies or reducingInsured)
                and self._hasInsuredData()):
            from strings import S as _S
            # Build dynamic message — only mention data types that actually exist
            # in the policies/insured that will be removed
            _lost_keys = self._getLosingKeys(
                reducingPolicies, reducingInsured
            )
            _body = self._buildReductionMessage(_S, _lost_keys)
            reply = CustomMessageBox.question(
                self,
                _S["dlg_cesiones_reduce_title"],
                _body,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                self.blockSignalChanges = True
                (self.multiplePolicies if prevMultiPolicies else self.singlePolicy).setChecked(True)
                (self.multipleInsured  if prevMultiInsured  else self.singleInsured).setChecked(True)
                self.blockSignalChanges = False
                return

        # Notify app.py to wipe orphaned endorsementData keys
        if reducingPolicies or reducingInsured:
            self.signalCesionesReduce.emit()

        if reducingPolicies and reducingInsured:
            restoreMode = '_restoreFirstInsuredPolicy'
        elif reducingPolicies:
            restoreMode = '_restoreFirstPolicy'
        elif reducingInsured:
            restoreMode = '_restoreFirstInsured'
        else:
            restoreMode = 'full'

        self._rebuildInsuredArea(
            allowMultiplePolicies=allowMultiplePolicies,
            allowMultipleInsured=allowMultipleInsured,
            preserveData=True,
            restoreMode=restoreMode
        )

        if (not self.mainInsured.insuredName.text().strip()
                and getattr(self, '_prefillName', '')):
            self.mainInsured.insuredName.setText(self._prefillName)

    def _onFinancingChanged(self):
        """Show SIGUIENTE (payment page) or GENERAR based on financing selection."""
        if self.financingYes.isChecked():
            self.nextStep.setVisible(True)
            self.generateDocument.setVisible(False)
        elif self.financingNo.isChecked():
            self.nextStep.setVisible(False)
            self.generateDocument.setVisible(True)

    def _getLosingKeys(self, reducingPolicies, reducingInsured):
        """
        Return the set of 'insuredId::policyId' keys that will be lost
        after applying the reduction.
        """
        allInsured = [self.mainInsured] + self.additionalInsuredList
        # Determine which insured survive
        if reducingInsured:
            survivingInsured = [self.mainInsured]
        else:
            survivingInsured = allInsured
        # Determine which policies survive per insured
        survivingKeys = set()
        for ins in survivingInsured:
            policies = ins.policyList
            if reducingPolicies:
                policies = policies[:1]
            for pol in policies:
                survivingKeys.add(f"{ins.widgetId}::{pol.widgetId}")
        # All current keys
        allKeys = set()
        for ins in allInsured:
            for pol in ins.policyList:
                allKeys.add(f"{ins.widgetId}::{pol.widgetId}")
        return allKeys - survivingKeys

    def _buildReductionMessage(self, S, lostKeys):
        """
        Build a human-readable warning listing only the data types
        that will actually be lost for the given set of keys.
        """
        lines = []
        # Póliza data (branch/number fields have content)
        allInsured = [self.mainInsured] + self.additionalInsuredList
        hasPolicyData = False
        for ins in allInsured:
            for pol in ins.policyList:
                key = f"{ins.widgetId}::{pol.widgetId}"
                if key in lostKeys:
                    if pol.policyBranch.currentText().strip() or pol.policyNum.text().strip():
                        hasPolicyData = True
                        break
        if hasPolicyData:
            lines.append(S.get('reduce_data_policies', '• Datos de pólizas'))
        # Financiamiento
        hasPayment = any(
            bool(self._paymentDataRef.get(k, {}).get('cuotas'))
            for k in lostKeys
        )
        if hasPayment:
            lines.append(S.get('reduce_data_payment', '• Cuotas de financiamiento'))
        # Cesiones de Derecho
        hasCesiones = (
            hasattr(self, 'endorsementDetailed') and
            self.endorsementDetailed.isChecked() and
            any(
                bool(self._endorsementDataRef.get(k, {}).get('rows') or
                     self._endorsementDataRef.get(k, {}).get('groups'))
                for k in lostKeys
            )
        )
        if hasCesiones:
            lines.append(S.get('reduce_data_cesiones', '• Cesiones de Derecho'))
        # Garantías Particulares
        guarantees = self._annexDataRef.get('guarantees', {})
        hasGarantias = any(k in guarantees for k in lostKeys)
        if hasGarantias:
            lines.append(S.get('reduce_data_garantias', '• Garantías Particulares'))
        # Build final message
        intro = S.get('reduce_intro',
                      'Ha reducido la cantidad de pólizas o asegurados.')
        if lines:
            detail = S.get('reduce_will_lose',
                           'Se perderá la siguiente información:')
            body = f"{intro}\n\n{detail}\n" + "\n".join(lines)
        else:
            body = intro
        return body + "\n\n" + S.get('reduce_confirm', '¿Desea continuar?')

    def _rebuildInsuredArea(self, allowMultiplePolicies, allowMultipleInsured,
                            preserveData=True, restoreMode='full'):
        """Saves data, recreates mainInsured with new config, clears additional insured, restores data."""
        self.blockSignalChanges = True
        saved = self.saveData() if preserveData else None

        self.pageConfig = {
            'allowMultipleInsured':  allowMultipleInsured,
            'allowMultiplePolicies': allowMultiplePolicies,
        }

        oldWidgetId     = self.mainInsured.widgetId
        oldPolicyIds    = [p.widgetId for p in self.mainInsured.policyList]
        self.mainInsured.deleteLater()
        self.mainInsured = InsuredWidget(
            insuredNumber=1,
            canDelete=False,
            allowMultiplePolicies=allowMultiplePolicies
        )
        self.mainInsured.widgetId = oldWidgetId
        # Restore policy widgetIds so endorsementData/paymentData keys stay valid
        for i, pol in enumerate(self.mainInsured.policyList):
            if i < len(oldPolicyIds):
                pol.widgetId = oldPolicyIds[i]
        self.insuredArea.layout().insertWidget(0, self.mainInsured)

        self.addInsuredButton.setVisible(allowMultipleInsured)
        self.clearAdditionalInsured()

        if preserveData and saved:
            self.restoreData(saved, mode=restoreMode)

        self.blockSignalChanges = False

        if not self.currencyPE.isChecked() and not self.currencyUS.isChecked():
            self.currencyUS.setChecked(True)

    # ── Data save / restore ────────────────────────────────────────────────────

    def saveData(self):
        """Capture all current widget values before any reconstruction."""
        saved = {
            'insurer':       self.insurer.currentText(),
            'startDate':     self.policyStartDate.date(),
            'endDate':       self.policyEndDate.date(),
            'currencyPE':    self.currencyPE.isChecked(),
            'mainName':      self.mainInsured.insuredName.text(),
            'mainPolicies':  [],
            'extraInsured':  [],
            'endorseYes':    self.endorsementYes.isChecked(),
            'endorseDetailed': self.endorsementDetailed.isChecked(),
            'endorseNo':     self.endorsementNo.isChecked(),
            'endorseBranch': self.endorsementBranch.text(),
            'endorseBenef':  self.endorsementBeneficiary.text(),
        }
        # Save widgetId per policy so endorsementData keys survive rebuild
        saved['mainInsuredId'] = self.mainInsured.widgetId
        for p in self.mainInsured.policyList:
            saved['mainPolicies'].append({
                'widgetId': p.widgetId,
                'branch':  p.policyBranch.currentText(),
                'number':  p.policyNum.text(),
                'receipt': p.policyReceipt.text(),
                'premium': p.policyPremium.text(),
                'total':   p.policyPremiumTotal.text(),
            })
        for ins in self.additionalInsuredList:
            iData = {
                'widgetId': ins.widgetId,
                'name': ins.insuredName.text(),
                'policies': []
            }
            for p in ins.policyList:
                iData['policies'].append({
                    'widgetId': p.widgetId,
                    'branch':  p.policyBranch.currentText(),
                    'number':  p.policyNum.text(),
                    'receipt': p.policyReceipt.text(),
                    'premium': p.policyPremium.text(),
                    'total':   p.policyPremiumTotal.text(),
                })
            saved['extraInsured'].append(iData)
        return saved

    def restoreData(self, saved, mode='full'):
        """Restore previously saved data. mode controls how much is restored."""
        if not saved:
            return
        saved_insurer = saved.get('insurer', '')
        idx = self.insurer.findText(saved_insurer)
        if idx >= 0:
            self.insurer.setCurrentIndex(idx)
        elif saved_insurer:
            self.insurer.setEditText(saved_insurer)
        self.policyStartDate.setDate(saved['startDate'])
        self.policyEndDate.setDate(saved['endDate'])
        (self.currencyPE if saved.get('currencyPE', True) else self.currencyUS).setChecked(True)
        if saved['endorseYes']:
            self.endorsementYes.setChecked(True)
        elif saved.get('endorseDetailed'):
            self.endorsementDetailed.setChecked(True)
        elif saved['endorseNo']:
            self.endorsementNo.setChecked(True)
        self.endorsementBranch.setText(saved['endorseBranch'])
        self.endorsementBeneficiary.setText(saved['endorseBenef'])
        dispatch = {
            'full':                       self._restoreFull,
            '_restoreFirstPolicy':        self._restoreFirstPolicy,
            '_restoreFirstInsured':       self._restoreFirstInsured,
            '_restoreFirstInsuredPolicy': self._restoreFirstInsuredPolicy,
        }
        dispatch.get(mode, self._restoreFull)(saved)

    def _applyPoliciesToInsured(self, widget, policies, onlyFirst=False):
        """Write a list of policy dicts into an InsuredWidget.
        Restores widgetId per policy so endorsementData/paymentData keys
        remain valid across insured area rebuilds.
        """
        if not policies:
            return
        p0 = policies[0]
        if 'widgetId' in p0:
            widget.policyList[0].widgetId = p0['widgetId']
        widget.policyList[0].policyBranch.setCurrentText(p0['branch'])
        widget.policyList[0].policyNum.setText(p0['number'])
        widget.policyList[0].policyReceipt.setText(p0['receipt'])
        widget.policyList[0].policyPremium.setText(p0['premium'])
        widget.policyList[0].policyPremiumTotal.setText(p0['total'])
        if not onlyFirst:
            for pData in policies[1:]:
                widget.addPolicyRow()
                last = widget.policyList[-1]
                if 'widgetId' in pData:
                    last.widgetId = pData['widgetId']
                last.policyBranch.setCurrentText(pData['branch'])
                last.policyNum.setText(pData['number'])
                last.policyReceipt.setText(pData['receipt'])
                last.policyPremium.setText(pData['premium'])
                last.policyPremiumTotal.setText(pData['total'])

    def _restoreFull(self, saved):
        self.mainInsured.insuredName.setText(saved['mainName'])
        if 'mainInsuredId' in saved:
            self.mainInsured.widgetId = saved['mainInsuredId']
        self._applyPoliciesToInsured(self.mainInsured, saved['mainPolicies'])
        for iData in saved['extraInsured']:
            self.addInsured()
            last = self.additionalInsuredList[-1]
            if 'widgetId' in iData:
                last.widgetId = iData['widgetId']
            last.insuredName.setText(iData['name'])
            self._applyPoliciesToInsured(last, iData['policies'])

    def _restoreFirstPolicy(self, saved):
        self.mainInsured.insuredName.setText(saved['mainName'])
        if 'mainInsuredId' in saved:
            self.mainInsured.widgetId = saved['mainInsuredId']
        self._applyPoliciesToInsured(self.mainInsured, saved['mainPolicies'], onlyFirst=True)
        for iData in saved['extraInsured']:
            self.addInsured()
            last = self.additionalInsuredList[-1]
            if 'widgetId' in iData:
                last.widgetId = iData['widgetId']
            last.insuredName.setText(iData['name'])
            self._applyPoliciesToInsured(last, iData['policies'], onlyFirst=True)

    def _restoreFirstInsured(self, saved):
        self.mainInsured.insuredName.setText(saved['mainName'])
        self._applyPoliciesToInsured(self.mainInsured, saved['mainPolicies'])

    def _restoreFirstInsuredPolicy(self, saved):
        self.mainInsured.insuredName.setText(saved['mainName'])
        self._applyPoliciesToInsured(self.mainInsured, saved['mainPolicies'], onlyFirst=True)

    # ── Public interface called by app.py ──────────────────────────────────────

    def setMainInsuredName(self, name):
        """Pre-fill the main insured name from pageConfig company name."""
        self._prefillName = name
        if hasattr(self, 'mainInsured') and self.mainInsured:
            self.mainInsured.insuredName.setText(name)

    def addInsured(self):
        """Add a new additional insured widget."""
        number     = len(self.additionalInsuredList) + 2
        newInsured = InsuredWidget(
            insuredNumber=number,
            canDelete=True,
            allowMultiplePolicies=self.pageConfig['allowMultiplePolicies']
        )
        newInsured.signalDelete.connect(self.deleteInsured)
        self.additionalInsuredList.append(newInsured)
        self.layoutClients.addWidget(newInsured)

    def deleteInsured(self, widgetToDelete):
        """Remove an additional insured widget."""
        if widgetToDelete in self.additionalInsuredList:
            self.additionalInsuredList.remove(widgetToDelete)
        widgetToDelete.deleteLater()

    def clearAdditionalInsured(self):
        """Remove all additional insured widgets."""
        for ins in self.additionalInsuredList:
            ins.deleteLater()
        self.additionalInsuredList.clear()

    def getPolicyConfig(self):
        """Return current quantity selection as a dict for app.py."""
        return {
            'multiplePolicies': 'Varias Polizas' if self.multiplePolicies.isChecked() else 'Una Poliza',
            'multipleClients':  'Si' if self.multipleInsured.isChecked() else 'No',
        }

    def _onDetailedToggled(self, checked):
        """If user turns off Si(Detallado) and there are cesiones records, confirm and clear."""
        if checked:
            return   # turning ON — no action needed
        # Emit signal to app.py which will check if endorsementData has rows
        self.signalEndorsementCleared.emit()

    def _onClearClicked(self):
        """Reset all fields of this page after user confirmation. Emits signalReset for app.py."""
        reply = CustomMessageBox.question(
            self,
            S["dlg_clear_page_title"],
            S["dlg_clear_policies_body"],
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.No:
            return

        self.blockSignalChanges = True

        for group in [self.policyQuantity, self.insuredQuantity,
                      self.financingOptions, self.currencyGroup]:
            group.setExclusive(False)
            for btn in group.buttons():
                btn.setChecked(False)
            group.setExclusive(True)

        self.endorsement.setExclusive(False)
        self.endorsementYes.setChecked(False)
        self.endorsementDetailed.setChecked(False)
        self.endorsementNo.setChecked(False)
        self.endorsement.setExclusive(True)
        self.endorsementData.setVisible(False)
        self.endorsementBranch.clear()
        self.endorsementBeneficiary.clear()

        self.insurer.setCurrentIndex(0)
        self.policyStartDate.setDate(QDate.currentDate())
        self.policyEndDate.setDate(QDate.currentDate().addYears(1))

        self.insuredArea.setVisible(False)
        self.nextStep.setVisible(False)
        self.generateDocument.setVisible(False)
        self.addInsuredButton.setVisible(False)

        self.clearAdditionalInsured()
        self.pageConfig = {'allowMultipleInsured': False, 'allowMultiplePolicies': False}

        self.mainInsured.deleteLater()
        self.mainInsured = InsuredWidget(1, canDelete=False, allowMultiplePolicies=False)
        self.insuredArea.layout().insertWidget(0, self.mainInsured)

        self.blockSignalChanges = False
        self.signalReset.emit()

    def getData(self):
        """Collect and return all policy page data for document generation."""
        qc   = self.getPolicyConfig()
        data = {
            'multiplePolicies':   qc['multiplePolicies'],
            'multipleClients':    qc['multipleClients'],
            'hasPayment':         'Si' if self.financingYes.isChecked() else 'No',
            'currency':           'S/.' if self.currencyPE.isChecked() else 'US$',
            'POLIZA_ASEGURADORA': self.insurer.currentText(),
            'POLIZA_INICIO':      self.policyStartDate.date().toString('dd/MM/yyyy'),
            'POLIZA_FIN':         self.policyEndDate.date().toString('dd/MM/yyyy'),
            'endorsementType':   (
                'Simple'   if self.endorsementYes.isChecked() else
                'Detallado' if self.endorsementDetailed.isChecked() else
                'No'
            ),
        }
        data.update(self.mainInsured.getData())
        data['ASEGURADOS_ADICIONALES'] = (
            [ins.getData() for ins in self.additionalInsuredList]
            if self.additionalInsuredList else []
        )
        if self.endorsementYes.isChecked():
            data['ENDOSO_RAMO']         = self.endorsementBranch.text()
            data['ENDOSO_BENEFICIARIO'] = self.endorsementBeneficiary.text()
        elif self.endorsementDetailed.isChecked():
            data['ENDOSO_RAMO']         = ''
            data['ENDOSO_BENEFICIARIO'] = ''
        return data
