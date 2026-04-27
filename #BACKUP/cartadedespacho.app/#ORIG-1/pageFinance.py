from strings import S
"""
Página 4: Financiamiento

Key fix vs previous version:
  _allContainers list replaces the single _activeContainer reference.
  Every FinancingGridContainer created in any case builder is appended to
  _allContainers. collectPaymentData() iterates the full list, so quotas
  from ALL asegurados and ALL tables are collected on ATRAS and GENERAR.
  Previously only the first container was saved — causing data loss for
  Cases 3 and 4 on navigation back.

FinancingTable compact mode:
  compact=True stacks inputs/buttons vertically so tables fit at ~270px wide
  (two tables side by side at 620px window width).

FinancingGridContainer:
  Uses removeWidget() only, never setParent(None) on data widgets.
  Partial rows handled by QHBoxLayout wrappers spanning all columns.
"""

from theme import QSSA
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea,
    QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup, QDateEdit,
    QSizePolicy, QMessageBox,
)
from PySide6.QtCore import Signal, QDate, Qt
from widgets import NoNewlineLineEdit, CustomMessageBox, CardWidget, AutoTreeWidget

from validators import (
    currencyInputValidator,
    applyCurrencyFormat,
    setBold,
)

PAYMENT_MAX_COLS = 2


class FinancingTable(CardWidget):
    """
    Reusable installment table widget.
    compact=False: inputs and buttons horizontal (full-width single table).
    compact=True:  inputs and buttons vertical (narrow column, ~270px).

    Supports three display modes set externally via applyMode(mode):
      'cuota'  — original behavior: auto-numbered Cuota column (3 cols).
      'recibo' — manual Nro. de Recibo field per row (3 cols, col 0 = recibo).
      'ambos'  — 4 columns: Cuota | Nro. Recibo | Vencimiento | Importe.
                 receiptInput is visible so the user enters the recibo per row.
                 Two AutoTreeWidget instances coexist; only one is visible at a time.
                 Data is migrated between them when the mode switches.
    """

    def __init__(self, title="FINANCIAMIENTO", collapsible=False,
                 bold_title=False, compact=False):
        super().__init__(title, collapsible=collapsible, bold_title=bold_title)
        self._compact    = compact
        self._quoteMode  = 'cuota'   # current mode — set externally by applyMode()
        self.buildUI()

    def buildUI(self):
        mainLayout = QVBoxLayout()

        if self._compact:
            # ── Compact (vertical) layout ─────────────────────────────────────
            # Used when two tables share row width side by side (~270px each).

            # Número de Recibo field — hidden in 'cuota' mode, visible in 'recibo'/'ambos'
            self._receiptLabel = QLabel(S["finance_label_receipt"])
            self.receiptInput  = NoNewlineLineEdit()
            mainLayout.addWidget(self._receiptLabel)
            mainLayout.addWidget(self.receiptInput)

            mainLayout.addWidget(QLabel(S["finance_label_premium"]))
            self.quotaPremium = NoNewlineLineEdit()
            self.quotaPremium.setPlaceholderText(S["finance_placeholder_amount"])
            self.quotaPremium.setValidator(currencyInputValidator())
            self.quotaPremium.editingFinished.connect(
                lambda: applyCurrencyFormat(self.quotaPremium))
            mainLayout.addWidget(self.quotaPremium)

            mainLayout.addWidget(QLabel(S["finance_label_due_date"]))
            self.quotaDueDate = QDateEdit()
            self.quotaDueDate.setCalendarPopup(True)
            self.quotaDueDate.setDate(QDate.currentDate())
            mainLayout.addWidget(self.quotaDueDate)

            self.addQuota    = QPushButton(S["btn_add_quota"])
            self.updateQuota = QPushButton(S["btn_update_quota"])
            self.deleteQuota = QPushButton(S["btn_delete_quota"])
            self.addQuota.clicked.connect(self.addRow)
            self.updateQuota.clicked.connect(self.updateRow)
            self.deleteQuota.clicked.connect(self.deleteRow)
            mainLayout.addWidget(self.addQuota)
            mainLayout.addWidget(self.updateQuota)
            mainLayout.addWidget(self.deleteQuota)

        else:
            # ── Full-width (horizontal) layout ────────────────────────────────
            # Used when a single table occupies the full page width.

            inputsLayout = QHBoxLayout()

            # Número de Recibo group — hidden in 'cuota' mode
            self._receiptGroup = QWidget()
            reciboGroupLayout = QVBoxLayout(self._receiptGroup)
            reciboGroupLayout.setContentsMargins(*QSSA['margins_finance_recibo'])
            self._receiptLabel = QLabel(S["finance_label_receipt"])
            self.receiptInput  = NoNewlineLineEdit()
            reciboGroupLayout.addWidget(self._receiptLabel)
            reciboGroupLayout.addWidget(self.receiptInput)
            inputsLayout.addWidget(self._receiptGroup)

            premiumLayout = QVBoxLayout()
            premiumLayout.addWidget(QLabel(S["finance_label_premium"]))
            self.quotaPremium = NoNewlineLineEdit()
            self.quotaPremium.setPlaceholderText(S["finance_placeholder_amount"])
            self.quotaPremium.setValidator(currencyInputValidator())
            self.quotaPremium.editingFinished.connect(
                lambda: applyCurrencyFormat(self.quotaPremium))
            premiumLayout.addWidget(self.quotaPremium)
            inputsLayout.addLayout(premiumLayout)

            dueDateLayout = QVBoxLayout()
            dueDateLayout.addWidget(QLabel(S["finance_label_due_date"]))
            self.quotaDueDate = QDateEdit()
            self.quotaDueDate.setCalendarPopup(True)
            self.quotaDueDate.setDate(QDate.currentDate())
            dueDateLayout.addWidget(self.quotaDueDate)
            inputsLayout.addLayout(dueDateLayout)

            mainLayout.addLayout(inputsLayout)

            buttonsLayout = QHBoxLayout()
            self.addQuota    = QPushButton(S["btn_add_quota"])
            self.updateQuota = QPushButton(S["btn_update_quota"])
            self.deleteQuota = QPushButton(S["btn_delete_quota"])
            self.addQuota.clicked.connect(self.addRow)
            self.updateQuota.clicked.connect(self.updateRow)
            self.deleteQuota.clicked.connect(self.deleteRow)
            buttonsLayout.addWidget(self.addQuota)
            buttonsLayout.addWidget(self.updateQuota)
            buttonsLayout.addWidget(self.deleteQuota)
            mainLayout.addLayout(buttonsLayout)

        # ── 3-column table: Cuota/Recibo | Vencimiento | Importe ─────────────
        # Used in modes 'cuota' and 'recibo'. Col 0 header changes per mode.
        # Ratios sum to 1.0: 0.33 + 0.33 + 0.34 = 1.00
        self.quotasTable = AutoTreeWidget(
            [0.33, 0.33, 0.34],
            [S["tree_header_quota"], S["tree_header_due_date"], S["tree_header_amount"]]
        )
        self.quotasTable.itemSelectionChanged.connect(self.loadSelectedQuota)
        mainLayout.addWidget(self.quotasTable)

        # ── 4-column table: Cuota | Nro. Recibo | Vencimiento | Importe ──────────
        # Used in mode 'ambos' only. Hidden by default (mode starts as 'cuota').
        # Column order matches user spec: Cuota(0) | Nro.Recibo(1) | Vencimiento(2) | Importe(3)
        # Ratios sum to 1.0: 0.18 + 0.27 + 0.27 + 0.28 = 1.00
        self.quotasTableBoth = AutoTreeWidget(
            [0.18, 0.27, 0.27, 0.28],
            [S["tree_header_quota"], S["tree_header_receipt"], S["tree_header_due_date"], S["tree_header_amount"]]
        )
        self.quotasTableBoth.itemSelectionChanged.connect(self._loadSelectedQuotaBoth)
        self.quotasTableBoth.setVisible(False)   # hidden until mode == 'ambos'
        mainLayout.addWidget(self.quotasTableBoth)

        # ── Running total (read-only) — shared across all modes ───────────────
        totalLayout = QHBoxLayout()
        totalLayout.addStretch()
        totalLabel = QLabel(S["finance_total_label"])
        setBold(totalLabel)
        totalLayout.addWidget(totalLabel)
        self.quotaPremiumTotal = NoNewlineLineEdit()
        self.quotaPremiumTotal.setReadOnly(True)
        self.quotaPremiumTotal.setFixedWidth(QSSA['finance_label_width'])
        self.quotaPremiumTotal.setPlaceholderText(S["finance_placeholder_amount"])
        setBold(self.quotaPremiumTotal)
        totalLayout.addWidget(self.quotaPremiumTotal)
        mainLayout.addLayout(totalLayout)

        self.setLayout(mainLayout)

        # Hide recibo widgets on initial build — visible only in 'recibo'/'ambos'
        self._setReciboVisible(False)

    # ── Private helpers ────────────────────────────────────────────────────────

    def _setReciboVisible(self, visible):
        """
        Show or hide the Nro. de Recibo input.
        Compact layout hides the label + QLineEdit directly.
        Full-width layout hides the containing _receiptGroup widget.
        """
        if self._compact:
            self._receiptLabel.setVisible(visible)
            self.receiptInput.setVisible(visible)
        else:
            # In full-width mode the label is inside _receiptGroup
            self._receiptGroup.setVisible(visible)

    def _activeTable(self):
        """
        Return the currently visible AutoTreeWidget.
        In 'ambos' mode returns quotasTableBoth (4 cols).
        In 'cuota' or 'recibo' mode returns quotasTable (3 cols).
        This keeps all CRUD operations pointing to the right table transparently.
        """
        if self._quoteMode == 'ambos':
            return self.quotasTableBoth
        return self.quotasTable

    def _updatePremiumTotal(self):
        """
        Recompute the TOTAL field by summing the Importe column of the active table.
        Column index for Importe:
          3-col table (cuota/recibo): col 2
          4-col table (ambos):        col 3  (Cuota | Nro.Recibo | Vencimiento | Importe)
        """
        table     = self._activeTable()
        importe_col = 3 if self._quoteMode == 'ambos' else 2
        total = 0.0
        for row in range(table.topLevelItemCount()):
            item = table.topLevelItem(row)
            if item and item.text(importe_col):
                try:
                    total += float(item.text(importe_col).replace(',', ''))
                except ValueError:
                    pass
        from validators import formatCurrencyValue
        self.quotaPremiumTotal.setText(formatCurrencyValue(str(total)))

    def _reindexRows(self):
        """
        Re-number col 0 after a delete in 'cuota' mode.
        In 'recibo' mode col 0 holds the user-entered recibo number, so we
        do NOT overwrite it — each row keeps its original manual identifier.
        In 'ambos' mode the Cuota column (col 0) is auto-numbered; the
        Nro. Recibo column (col 1) holds the manual identifier and is preserved.
        """
        table = self._activeTable()
        if self._quoteMode == 'recibo':
            # Recibo mode: col 0 is manual — do not touch it
            return
        # cuota or ambos: col 0 is the auto-counter
        for row in range(table.topLevelItemCount()):
            item = table.topLevelItem(row)
            if item:
                item.setText(0, str(row + 1))
                item.setTextAlignment(0, Qt.AlignCenter)

    def _advanceDate(self):
        """Advance the due-date picker by one month after each row addition."""
        self.quotaDueDate.setDate(self.quotaDueDate.date().addMonths(1))

    def _migrateToBothMode(self, previous_mode):
        """
        Copy data from the 3-column table (quotasTable) into the 4-column
        table (quotasTableBoth) when switching TO 'ambos' mode.

        4-col order: Cuota(0) | Nro.Recibo(1) | Vencimiento(2) | Importe(3)

        previous_mode is passed explicitly because by the time this method is
        called, self._quoteMode has already been updated to 'ambos'. Reading
        self._quoteMode here would always return 'ambos' and the coming_from_recibo
        check would never fire — causing recibo values to be silently discarded.

        Column mapping  3-col → 4-col:
          col 0  nro/recibo  → col 0  Cuota (auto counter 1, 2, 3…)
          col 0  recibo val  → col 1  Nro. Recibo (preserved if previous_mode == 'recibo')
          col 1  vencimiento → col 2  Vencimiento
          col 2  importe     → col 3  Importe
        """
        coming_from_recibo = (previous_mode == 'recibo')
        self.quotasTableBoth.clear()
        for row in range(self.quotasTable.topLevelItemCount()):
            item = self.quotasTable.topLevelItem(row)
            if item:
                recibo_val = item.text(0) if coming_from_recibo else ''
                self.quotasTableBoth.addRow([
                    str(row + 1),      # col 0: auto counter (always re-numbered)
                    recibo_val,        # col 1: Nro. Recibo — preserved from recibo mode
                    item.text(1),      # col 2: Vencimiento
                    item.text(2),      # col 3: Importe
                ])

    def _migrateFromBothMode(self, destination_mode):
        """
        Copy data from the 4-column table (quotasTableBoth) back into the
        3-column table (quotasTable) when switching AWAY from 'ambos' mode.

        4-col order: Cuota(0) | Nro.Recibo(1) | Vencimiento(2) | Importe(3)

        Column mapping  4-col → 3-col:
          col 0  Cuota        → col 0  auto-counter (always re-numbered)
          col 1  Nro. Recibo  → col 0  when destination is 'recibo' (preserves recibo val)
          col 2  Vencimiento  → col 1  Vencimiento
          col 3  Importe      → col 2  Importe

        If destination is 'recibo', col 1 of the 4-col table (Nro. Recibo) is
        moved into col 0 of the 3-col table so the user sees their recibo values.
        If destination is 'cuota', col 0 becomes a plain auto-counter.
        """
        going_to_recibo = (destination_mode == 'recibo')
        self.quotasTable.clear()
        for row in range(self.quotasTableBoth.topLevelItemCount()):
            item = self.quotasTableBoth.topLevelItem(row)
            if item:
                # col 0: use recibo value if going to recibo mode, otherwise auto-counter
                col0 = item.text(1) if going_to_recibo else str(row + 1)
                self.quotasTable.addRow([
                    col0,            # col 0: recibo or counter
                    item.text(2),    # col 1: Vencimiento
                    item.text(3),    # col 2: Importe
                ])

    def _clearInputs(self):
        """
        Reset all input fields to their default empty state.
        Called after deleteRow and when switching modes to avoid stale values
        auto-loading into fields via itemSelectionChanged signals.
        """
        self.quotaPremium.clear()
        self.receiptInput.clear()
        self.quotaDueDate.setDate(QDate.currentDate())

    def applyMode(self, mode):
        """
        Apply a new display mode to this table.
        Called externally by PageFinance._onQuoteModeChanged() on every table,
        and by setupPage() after building all tables to restore persisted mode.

        Mode transitions:
          * → 'cuota':  hide receiptInput, 3-col table, col 0 header = 'Cuota'.
                        If coming from 'ambos', migrate data back preserving nothing in col 0.
          * → 'recibo': show receiptInput, 3-col table, col 0 header = 'Nro. Recibo'.
                        If coming from 'ambos', migrate back preserving col 1 → col 0.
          * → 'ambos':  show receiptInput (for entering recibo per row), 4-col table.
                        If coming from recibo, preserves recibo values into col 1.

        Inputs are cleared on every mode switch to prevent stale values from
        auto-filling via the itemSelectionChanged signal during the table swap.
        """
        previous = self._quoteMode
        self._quoteMode = mode

        # Disconnect selection signals during mode switch to prevent auto-fill
        # from firing while rows are being migrated between tables.
        try:
            self.quotasTable.itemSelectionChanged.disconnect(self.loadSelectedQuota)
        except RuntimeError:
            pass
        try:
            self.quotasTableBoth.itemSelectionChanged.disconnect(self._loadSelectedQuotaBoth)
        except RuntimeError:
            pass

        if mode == 'cuota':
            if previous == 'ambos':
                self._migrateFromBothMode(destination_mode='cuota')
            self.quotasTable.setVisible(True)
            self.quotasTableBoth.setVisible(False)
            self.quotasTable.setHeaderLabels([S["tree_header_quota"], S["tree_header_due_date"], S["tree_header_amount"]])
            self._setReciboVisible(False)
            self._updatePremiumTotal()

        elif mode == 'recibo':
            if previous == 'ambos':
                self._migrateFromBothMode(destination_mode='recibo')
            self.quotasTable.setVisible(True)
            self.quotasTableBoth.setVisible(False)
            self.quotasTable.setHeaderLabels([S["tree_header_receipt"], S["tree_header_due_date"], S["tree_header_amount"]])
            self._setReciboVisible(True)
            self._updatePremiumTotal()

        elif mode == 'ambos':
            if previous != 'ambos':
                self._migrateToBothMode(previous_mode=previous)
            self.quotasTable.setVisible(False)
            self.quotasTableBoth.setVisible(True)
            # receiptInput stays visible in ambos — user enters the recibo per row
            # before clicking AGREGAR, same as recibo mode
            self._setReciboVisible(True)
            self._updatePremiumTotal()

        # Clear all inputs after any mode switch — prevents stale values from
        # showing in fields after migration and avoids the auto-fill side-effect.
        self._clearInputs()

        # Reconnect selection signals now that migration is complete
        self.quotasTable.itemSelectionChanged.connect(self.loadSelectedQuota)
        self.quotasTableBoth.itemSelectionChanged.connect(self._loadSelectedQuotaBoth)

    # ── Data load / save ───────────────────────────────────────────────────────

    def loadQuotas(self, quotaList):
        """
        Populate the table(s) from a list of quota dicts (from persisted data).

        If the current mode is 'ambos', data is loaded directly into quotasTableBoth
        using the 'recibo' key so Nro. Recibo values survive navigation (C10 fix).
        In all other modes data is loaded into quotasTable (3-col).

        This is called by FinancingGridContainer._loadTable() before applyMode()
        runs on the freshly built table. In 'ambos' mode we skip the 3-col table
        entirely — no migration needed because the data lands in the right place.
        In 'cuota'/'recibo' modes applyMode() is a no-op regarding migration since
        the table is already in the correct visual state after this load.
        """
        if self._quoteMode == 'ambos':
            # Load directly into the 4-col table — preserves recibo values
            # 4-col order: Cuota(0) | Nro.Recibo(1) | Vencimiento(2) | Importe(3)
            self.quotasTableBoth.clear()
            for quota in quotaList:
                row = self.quotasTableBoth.topLevelItemCount()
                self.quotasTableBoth.addRow([
                    quota.get('nro',         str(row + 1)),
                    quota.get('recibo',      ''),
                    quota.get('vencimiento', ''),
                    quota.get('importe',     ''),
                ])
            self._updatePremiumTotal()
            if quotaList:
                last_venc = quotaList[-1].get('vencimiento', '')
                lastDate  = QDate.fromString(last_venc, 'dd/MM/yyyy')
                if lastDate.isValid():
                    self.quotaDueDate.setDate(lastDate.addMonths(1))
        else:
            # Load into the 3-col table (cuota or recibo mode)
            self.quotasTable.clear()
            for quota in quotaList:
                row = self.quotasTable.topLevelItemCount()
                self.quotasTable.addRow([
                    quota.get('nro', str(row + 1)),
                    quota.get('vencimiento', ''),
                    quota.get('importe', '')
                ])
            self._updatePremiumTotal()
            if quotaList:
                lastDate = QDate.fromString(quotaList[-1].get('vencimiento', ''), 'dd/MM/yyyy')
                if lastDate.isValid():
                    self.quotaDueDate.setDate(lastDate.addMonths(1))

    def collectQuotas(self):
        """
        Collect quota data from whichever table is currently active.

        'cuota' / 'recibo' modes → read from 3-col quotasTable.
          col 0 = nro (auto-counter or recibo number)
          col 1 = vencimiento
          col 2 = importe

        'ambos' mode → read from 4-col quotasTableBoth.
          col 0 = Cuota (counter)
          col 1 = Nro. Recibo
          col 2 = Importe
          col 3 = Vencimiento
        Data is normalized to the same dict shape so helpers.py is unchanged.
        """
        quotas = []
        if self._quoteMode == 'ambos':
            # 4-col order: Cuota(0) | Nro.Recibo(1) | Vencimiento(2) | Importe(3)
            for row in range(self.quotasTableBoth.topLevelItemCount()):
                item = self.quotasTableBoth.topLevelItem(row)
                quotas.append({
                    'nro':         item.text(0) if item else '',
                    'recibo':      item.text(1) if item else '',
                    'vencimiento': item.text(2) if item else '',
                    'importe':     item.text(3) if item else '',
                })
        else:
            for row in range(self.quotasTable.topLevelItemCount()):
                item = self.quotasTable.topLevelItem(row)
                quotas.append({
                    'nro':         item.text(0) if item else '',
                    'vencimiento': item.text(1) if item else '',
                    'importe':     item.text(2) if item else '',
                })
        return quotas

    # ── Public slot methods ────────────────────────────────────────────────────

    def addRow(self):
        """
        Add a new row to the active table.

        'cuota' mode:  col 0 = auto-number, col 1 = date, col 2 = premium.
        'recibo' mode: col 0 = receiptInput (manual, required), col 1 = date, col 2 = premium.
        'ambos' mode:  col 0 = auto-number, col 1 = receiptInput (manual, required),
                       col 2 = date, col 3 = premium. Uses 4-col table.
                       (Order: Cuota | Recibo | Vencimiento | Importe)

        When both Número de Recibo and Prima de Cuota are missing, a single combined
        warning lists both fields. When only one is missing, the specific field is named.
        """
        premium = self.quotaPremium.text().strip()
        date    = self.quotaDueDate.date().toString("dd/MM/yyyy")

        if self._quoteMode in ('recibo', 'ambos'):
            recibo = self.receiptInput.text().strip()
            # Build a combined warning if both required fields are empty
            missing = []
            if not recibo:
                missing.append("• Número de Recibo")
            if not premium:
                missing.append("• Prima de Cuota")
            if missing:
                CustomMessageBox.warning(
                    self, "Advertencia",
                    "Debe ingresar:\n\n" + "\n".join(missing)
                )
                return

            from validators import formatCurrencyValue
            if self._quoteMode == 'recibo':
                # col 0 = recibo number (no auto-counter in this mode)
                self.quotasTable.addRow([recibo, date, formatCurrencyValue(premium)])
            else:
                # 4-col order: Cuota(auto) | Recibo | Vencimiento | Importe
                row = self.quotasTableBoth.topLevelItemCount()
                self.quotasTableBoth.addRow([
                    str(row + 1),
                    recibo,
                    date,
                    formatCurrencyValue(premium),
                ])
            self.receiptInput.clear()

        else:
            # 'cuota' mode — only premium required, recibo not applicable
            if not premium:
                CustomMessageBox.warning(self, "Advertencia", "Ingrese el importe de la cuota.")
                return
            from validators import formatCurrencyValue
            row = self.quotasTable.topLevelItemCount()
            self.quotasTable.addRow([str(row + 1), date, formatCurrencyValue(premium)])

        self._advanceDate()
        self.quotaPremium.clear()
        self._updatePremiumTotal()

    def updateRow(self):
        """
        Update the selected row's fields.

        'cuota' mode:  updates col 1 (date) and col 2 (premium). Col 0 unchanged.
        'recibo' mode: updates col 0 (recibo from receiptInput), col 1 (date), col 2 (premium).
        'ambos' mode:  updates col 1 (recibo from receiptInput), col 2 (date), col 3 (premium).
                       4-col order: Cuota(0) | Nro.Recibo(1) | Vencimiento(2) | Importe(3)
        """
        table = self._activeTable()
        currentItem = table.currentItem()
        if not currentItem:
            CustomMessageBox.warning(self, S["msg_warning_title"], S["msg_quota_no_selection"])
            return
        premium = self.quotaPremium.text().strip()
        if not premium:
            CustomMessageBox.warning(self, "Advertencia", "Ingrese el importe de la cuota.")
            return
        from validators import formatCurrencyValue
        date       = self.quotaDueDate.date().toString("dd/MM/yyyy")
        currentRow = table.indexOfTopLevelItem(currentItem.parent() or currentItem)
        item       = table.topLevelItem(currentRow)
        if item:
            if self._quoteMode == 'recibo':
                # Update recibo number too when in recibo mode
                recibo = self.receiptInput.text().strip()
                if recibo:
                    item.setText(0, recibo)
                    item.setTextAlignment(0, Qt.AlignCenter)
                item.setText(1, date)
                item.setText(2, formatCurrencyValue(premium))
                item.setTextAlignment(1, Qt.AlignCenter)
                item.setTextAlignment(2, Qt.AlignCenter)
            elif self._quoteMode == 'ambos':
                # 4-col order: Cuota(0) | Nro.Recibo(1) | Vencimiento(2) | Importe(3)
                recibo = self.receiptInput.text().strip()
                if recibo:
                    item.setText(1, recibo)
                    item.setTextAlignment(1, Qt.AlignCenter)
                item.setText(2, date)
                item.setText(3, formatCurrencyValue(premium))
                item.setTextAlignment(2, Qt.AlignCenter)
                item.setTextAlignment(3, Qt.AlignCenter)
            else:
                # 'cuota' mode: date = col 1, premium = col 2
                item.setText(1, date)
                item.setText(2, formatCurrencyValue(premium))
                item.setTextAlignment(1, Qt.AlignCenter)
                item.setTextAlignment(2, Qt.AlignCenter)
        self.quotaPremium.clear()
        self.receiptInput.clear()   # clear recibo field after update — mirrors addRow behavior
        self._updatePremiumTotal()

    def deleteRow(self):
        """
        Remove the selected row and re-index remaining rows.
        After deletion all input fields are cleared — this prevents stale values
        from remaining in the fields when the last row is deleted (B7 fix).
        """
        table = self._activeTable()
        currentItem = table.currentItem()
        if not currentItem:
            CustomMessageBox.warning(self, S["msg_warning_title"], S["msg_quota_no_selection"])
            return
        currentRow = table.indexOfTopLevelItem(currentItem.parent() or currentItem)
        table.takeTopLevelItem(currentRow)
        self._reindexRows()
        self._updatePremiumTotal()
        # Clear inputs so no stale values remain after the row is removed
        self._clearInputs()

    def loadSelectedQuota(self):
        """
        Load a selected row from the 3-col table into the input fields.
        Called automatically when the user clicks a row in quotasTable.

        'cuota' mode: populates quotaDueDate and quotaPremium.
        'recibo' mode: also populates receiptInput with col 0 value.
        """
        currentItem = self.quotasTable.currentItem()
        if currentItem:
            row  = self.quotasTable.indexOfTopLevelItem(currentItem.parent() or currentItem)
            item = self.quotasTable.topLevelItem(row)
            if item:
                date = QDate.fromString(item.text(1), "dd/MM/yyyy")
                if date.isValid():
                    self.quotaDueDate.setDate(date)
                self.quotaPremium.setText(item.text(2))
                # In recibo mode, also restore the recibo number into receiptInput
                if self._quoteMode == 'recibo':
                    self.receiptInput.setText(item.text(0))

    def _loadSelectedQuotaBoth(self):
        """
        Load a selected row from the 4-col table into the input fields.
        Called automatically when the user clicks a row in quotasTableBoth.

        4-col order: Cuota(0) | Nro.Recibo(1) | Vencimiento(2) | Importe(3)
        Populates receiptInput (col 1), quotaDueDate (col 2), quotaPremium (col 3).
        """
        currentItem = self.quotasTableBoth.currentItem()
        if currentItem:
            row  = self.quotasTableBoth.indexOfTopLevelItem(currentItem.parent() or currentItem)
            item = self.quotasTableBoth.topLevelItem(row)
            if item:
                # col 1 = Nro. Recibo — load into receiptInput
                self.receiptInput.setText(item.text(1))
                # col 2 = Vencimiento
                date = QDate.fromString(item.text(2), "dd/MM/yyyy")
                if date.isValid():
                    self.quotaDueDate.setDate(date)
                # col 3 = Importe
                self.quotaPremium.setText(item.text(3))

    def getData(self):
        return {
            'cuotas': self.collectQuotas(),
            'total':  self.quotaPremiumTotal.text() or '0.00',
        }



class FinancingGridContainer(QWidget):
    """
    Arranges FinancingTable widgets in a grid of PAYMENT_MAX_COLS columns.
    Partial rows use QHBoxLayout wrappers — no setParent(None) on data widgets.
    Stores all tables in self.tableMap { key: FinancingTable }.
    collectPaymentData() returns { key: {'cuotas': [...], 'total': str} }.

    quoteMode is injected at construction time so each FinancingTable has the
    correct _quoteMode BEFORE loadQuotas() is called. Without this, loadQuotas()
    always sees _quoteMode='cuota' (the constructor default) and loads into the
    3-col table even when the user is in 'ambos' mode — causing recibo values to
    be silently discarded on every navigation back.
    """

    def __init__(self, tableSpecs, paymentData, quoteMode='cuota', parent=None):
        """
        tableSpecs: list of (title, key) tuples.
        paymentData: dict { key: {'cuotas': [...], 'total': str} } from app.py.
        quoteMode:  current mode from PageFinance._quoteMode — injected so tables
                    know which internal table to load data into before applyMode().
        """
        super().__init__(parent)
        self.tableMap     = {}
        self._lastWrapper = None
        self._quoteMode   = quoteMode

        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(*QSSA['margins_finance_grid'])
        self._grid.setSpacing(QSSA['spacing_finance_grid'])

        self._buildGrid(tableSpecs, paymentData)

    def _buildGrid(self, tableSpecs, paymentData):
        """
        Place tables in rows of PAYMENT_MAX_COLS.
        Full rows: compact=True (side by side).
        Partial row: QHBoxLayout wrapper spanning all columns.
          - remainder=1: compact=False (full width, readable layout).
          - remainder=2: compact=True (side by side, narrow layout).
        """
        n         = len(tableSpecs)
        cols      = PAYMENT_MAX_COLS
        full_rows = n // cols
        remainder = n % cols

        for c in range(cols):
            self._grid.setColumnStretch(c, 1)

        # Full rows — compact=True because two tables share the row width
        for idx in range(full_rows * cols):
            title, key     = tableSpecs[idx]
            table = FinancingTable(title, collapsible=True,
                                   bold_title=True, compact=True)
            self._loadTable(table, key, paymentData)
            self.tableMap[key] = table
            self._grid.addWidget(table, idx // cols, idx % cols)

        # Partial row — wrapper spans all columns
        if remainder > 0:
            use_compact   = remainder > 1    # 2+ tables sharing row → compact
            wrapper       = QWidget(self)
            wrapperLayout = QHBoxLayout(wrapper)
            wrapperLayout.setContentsMargins(*QSSA['margins_finance_wrapper'])
            wrapperLayout.setSpacing(QSSA['spacing_finance_wrapper'])
            for i in range(remainder):
                title, key     = tableSpecs[full_rows * cols + i]
                table = FinancingTable(title, collapsible=True,
                                       bold_title=True, compact=use_compact)
                self._loadTable(table, key, paymentData)
                self.tableMap[key] = table
                wrapperLayout.addWidget(table, 1)
            self._grid.addWidget(wrapper, full_rows, 0, 1, cols)
            self._lastWrapper = wrapper

    def _loadTable(self, table, key, paymentData):
        """
        Set the correct quoteMode on the table FIRST, then load persisted quota data.

        Order matters: table._quoteMode must reflect the current global mode before
        loadQuotas() is called, because loadQuotas() routes data to quotasTable or
        quotasTableBoth based on _quoteMode. If we set it after loading, the data
        always lands in quotasTable (3-col) regardless of mode — this is the root
        cause of recibo values being lost on navigation back in 'ambos' mode (C10).
        """
        table._quoteMode = self._quoteMode   # inject mode before any data load

        entry = paymentData.get(key)
        if isinstance(entry, dict):
            quotas = entry.get('cuotas', [])
        elif isinstance(entry, list):
            quotas = entry
        else:
            quotas = []
        if quotas:
            table.loadQuotas(quotas)

    def collectPaymentData(self):
        """Return { key: {'cuotas': [...], 'total': str} } for all tables."""
        return {key: table.getData() for key, table in self.tableMap.items()}


class PageFinance(QWidget):
    """
    Página 4: Financiamiento.

    _allContainers: list of ALL FinancingGridContainer instances created by the
    current setupPage() call. collectPaymentData() iterates this list to collect
    from every container — not just the first one. This is the key fix that
    prevents quota data loss for Cases 3 and 4 on navigation back.
    """

    signalGenerate       = Signal()
    signalBack           = Signal()
    # Emitted when the user confirms a financing type change (Individual↔Colectivo).
    # app.py connects this to wipe self.paymentData so stale quotas don't reload
    # on the next setupPage() call after the user navigates back and returns.
    signalWipePaymentData = Signal()

    def __init__(self):
        super().__init__()

        self.pageConfig = {
            'multiplePolicies': False,
            'multipleClients':  False,
        }

        self.hasTypeWidgets       = False
        self.currentFinancingType = 'Individual'
        self.blockSignalChanges   = False
        self._quoteMode           = 'cuota'   # 'cuota' | 'recibo' | 'ambos'

        # ALL containers created in the current page layout.
        # Replaces the previous single _activeContainer reference.
        self._allContainers = []

        self.buildUI()

    def buildUI(self):
        """Build the permanent scaffold. Dynamic content inserted by setupPage()."""
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)

        self.containerWidget = QWidget()
        self.mainLayout      = QVBoxLayout(self.containerWidget)

        previousStep     = QPushButton(S["nav_back"])
        clearButton      = QPushButton(S["nav_clear"])
        generateDocument = QPushButton(S["nav_generate"])
        previousStep.clicked.connect(self.signalBack.emit)
        clearButton.clicked.connect(self._onClearPage)
        generateDocument.clicked.connect(self.signalGenerate.emit)

        # Nav is outside scrollArea — fixed at bottom regardless of content height.
        # clearContent() now keeps only stretch (last 1 item) not stretch + nav.
        self.mainLayout.addStretch()

        scrollArea.setWidget(self.containerWidget)

        navWidget = QWidget()
        navWidget.setObjectName("NavBar")
        navLayout = QHBoxLayout(navWidget)
        navLayout.setContentsMargins(*QSSA['margins_nav'])
        navLayout.addWidget(previousStep)
        navLayout.addStretch()
        navLayout.addWidget(clearButton)
        navLayout.addStretch()
        navLayout.addWidget(generateDocument)

        pageLayout = QVBoxLayout(self)
        pageLayout.setContentsMargins(*QSSA['margins_zero'])
        pageLayout.setSpacing(QSSA['spacing_zero'])
        pageLayout.addWidget(scrollArea, 1)
        pageLayout.addWidget(navWidget)

    def _onClearPage(self):
        """Reset all financing data on this page after user confirmation."""
        from PySide6.QtWidgets import QMessageBox
        reply = CustomMessageBox.question(
            self,
            S["dlg_clear_page_title"],
            S["dlg_clear_finance_body"],
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.No:
            return
        self.clearContent()
        self.signalWipePaymentData.emit()

    def clearContent(self):
        """Remove all dynamic widgets, reset container list, keep only the stretch (last 1 item).
        Navigation bar is now outside the scrollArea so it is no longer part of mainLayout."""
        self.hasTypeWidgets = False
        self._allContainers = []

        self.financingIndividual = None
        self.financingCollective = None

        # Remove all items from the top until only the stretch remains (last 1).
        while self.mainLayout.count() > 1:
            item = self.mainLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clearLayout(item.layout())

    def _clearLayout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clearLayout(item.layout())

    def getCurrentFinancingType(self):
        if self.hasTypeWidgets:
            try:
                if self.financingIndividual and self.financingIndividual.isChecked():
                    return 'Individual'
                if self.financingCollective and self.financingCollective.isChecked():
                    return 'Collective'
            except RuntimeError:
                # C++ object already deleted — fall through to stored type
                pass
        return self.currentFinancingType

    def setupPage(self, pageConfig, paymentData, policiesPage):
        """Rebuild the dynamic section. Called by app.py on every navigation to page 4."""
        self.pageConfig = pageConfig
        previousType    = self.getCurrentFinancingType()

        self.blockSignalChanges = True
        self.clearContent()

        multi   = pageConfig['multiplePolicies']
        insured = pageConfig['multipleClients']

        # Global TIPO DE CUOTA card — always at position 0, all cases
        self._quoteModeCard = self._buildQuotaModeCard()
        self._insertWidget(self._quoteModeCard, 0)

        if not multi and not insured:
            self._buildCase1(paymentData)
        elif multi and not insured:
            self._buildCase2(paymentData, policiesPage, previousType)
        elif not multi and insured:
            self._buildCase3(paymentData, policiesPage)
        else:
            self._buildCase4(paymentData, policiesPage, previousType)

        # Apply the persisted quote mode to all freshly created tables.
        # This ensures the correct visual state is restored on every navigation.
        for container in self._allContainers:
            for table in container.tableMap.values():
                table.applyMode(self._quoteMode)

        self.blockSignalChanges = False

    def _registerContainer(self, container):
        """
        Add a FinancingGridContainer to _allContainers.
        Called by every case builder whenever a container is created.
        This is what ensures collectPaymentData() sees ALL tables.
        """
        self._allContainers.append(container)

    def _insertWidget(self, widget, pos=0):
        """Insert a widget at pos in mainLayout (before the permanent nav+stretch)."""
        self.mainLayout.insertWidget(pos, widget)

    # ── Case builders ──────────────────────────────────────────────────────────

    def _buildCase1(self, paymentData):
        """Case 1: Single policy, single insured — one full-width table."""
        container = FinancingGridContainer(
            [("FINANCIAMIENTO", '__single__')], paymentData,
            quoteMode=self._quoteMode
        )
        self._registerContainer(container)
        self._insertWidget(container, 1)  # pos 1: after TIPO DE CUOTA
        self.hasTypeWidgets = False

    def _buildCase2(self, paymentData, policiesPage, previousType):
        """
        Case 2: Multiple policies, single insured.
        Type selector + grid of per-policy tables (Individual) or one collective table.
        """
        groupType = self._makeTypeCard()
        self._insertWidget(groupType, 1)  # pos 1: after TIPO DE CUOTA
        self.hasTypeWidgets = True

        tipo = 'Collective' if previousType == 'Collective' else 'Individual'
        (self.financingCollective if tipo == 'Collective' else self.financingIndividual).setChecked(True)

        self._rebuildCase2Tables(tipo, paymentData, policiesPage)

        # Type-change handlers do NOT capture paymentData.
        # On a confirmed type switch the user accepts data loss — we always
        # rebuild with an empty dict. Capturing paymentData here would hold
        # a stale reference to the old dict after app.py replaces it.
        self.financingIndividual.toggled.connect(
            lambda checked: self._onCase2TypeChange('Individual', policiesPage) if checked else None)
        self.financingCollective.toggled.connect(
            lambda checked: self._onCase2TypeChange('Collective', policiesPage) if checked else None)

    def _rebuildCase2Tables(self, tipo, paymentData, policiesPage):
        """Remove the current Case 2 container and rebuild for the new type."""
        # Remove container at index 2 if present
        # Layout: [quoteCard(0), typeCard(1), container(2)?, stretch]
        # Nav is outside scrollArea — minimum is 3 items (quoteCard + typeCard + stretch)
        while self.mainLayout.count() > 3:
            item = self.mainLayout.takeAt(2)
            if item.widget():
                item.widget().deleteLater()

        self._allContainers = []   # reset before rebuilding
        self.currentFinancingType = tipo
        mainInsured = policiesPage.mainInsured

        if tipo == 'Individual':
            specs = [
                (S["finance_card_policy_prefix"].format(branch=p.policyBranch.currentText() or S["finance_card_policy_fallback"]),
                 f"{mainInsured.widgetId}::{p.widgetId}")
                for p in mainInsured.policyList
            ]
        else:
            specs = [(
                S["finance_card_collective_prefix"].format(name=mainInsured.insuredName.text() or S["finance_card_insured_fallback"]),
                mainInsured.widgetId
            )]

        container = FinancingGridContainer(specs, paymentData, quoteMode=self._quoteMode)
        self._registerContainer(container)
        self.mainLayout.insertWidget(2, container)  # pos 2: after quote card + type card

        # Apply the current quote mode to the freshly created tables so the
        # visual state (receiptInput visibility, col headers) is consistent
        # after a financing type change (Individual ↔ Colectivo).
        for table in container.tableMap.values():
            table.applyMode(self._quoteMode)

    def _onCase2TypeChange(self, tipo, policiesPage):
        """
        Handle user-driven type change for Case 2.
        paymentData is intentionally NOT a parameter here — capturing it in the
        lambda would hold a stale reference after app.py replaces its dict.
        On a confirmed change the user accepts data loss so we always rebuild
        with {} and emit signalWipePaymentData to clear app.py's dict too.
        """
        if self.blockSignalChanges:
            return
        if self._hasQuotaData():
            if not self._confirmTypeChange(tipo):
                self._revertType()
                return
            self.signalWipePaymentData.emit()
        self._rebuildCase2Tables(tipo, {}, policiesPage)

    def _buildCase3(self, paymentData, policiesPage):
        """
        Case 3: Single policy, multiple insured.
        One FinancingGridContainer per insured, stacked vertically.
        All containers registered in _allContainers.
        """
        allInsured = [policiesPage.mainInsured] + policiesPage.additionalInsuredList
        for i, widget in enumerate(allInsured):
            key   = widget.widgetId
            title = widget.insuredName.text()
            container = FinancingGridContainer(
                [(S["finance_card_insured_prefix"].format(name=title), key)], paymentData,
                quoteMode=self._quoteMode
            )
            self._registerContainer(container)   # <— registers ALL, not just first
            self._insertWidget(container, 1 + i)  # pos 1+: after TIPO DE CUOTA
        self.hasTypeWidgets = False

    def _buildCase4(self, paymentData, policiesPage, previousType):
        """
        Case 4: Multiple policies, multiple insured.
        Type selector + per-insured CardWidget each containing a FinancingGridContainer.
        All containers registered in _allContainers.
        """
        groupType = self._makeTypeCard(
            individual_label=S["finance_individual_case2"],
            collective_label=S["finance_collective_case2"]
        )
        self._insertWidget(groupType, 1)  # pos 1: after TIPO DE CUOTA
        self.hasTypeWidgets = True

        tipo = 'Collective' if previousType == 'Collective' else 'Individual'
        (self.financingCollective if tipo == 'Collective' else self.financingIndividual).setChecked(True)

        self._rebuildCase4Tables(tipo, paymentData, policiesPage)

        # Same reasoning as Case 2 — no paymentData capture in lambdas.
        self.financingIndividual.toggled.connect(
            lambda checked: self._onCase4TypeChange('Individual', policiesPage) if checked else None)
        self.financingCollective.toggled.connect(
            lambda checked: self._onCase4TypeChange('Collective', policiesPage) if checked else None)

    def _rebuildCase4Tables(self, tipo, paymentData, policiesPage):
        """Remove all Case 4 insured-group cards and rebuild for the new type."""
        # Layout: [quoteCard(0), typeCard(1), group0(2), group1(3), ..., stretch]
        # Nav is outside scrollArea — minimum is 3 items (quoteCard + typeCard + stretch)
        while self.mainLayout.count() > 3:
            item = self.mainLayout.takeAt(2)
            if item.widget():
                item.widget().deleteLater()

        self._allContainers = []   # reset before rebuilding
        self.currentFinancingType = tipo
        allInsured = [policiesPage.mainInsured] + policiesPage.additionalInsuredList

        for i, widget in enumerate(allInsured):
            insuredTitle  = widget.insuredName.text()
            groupInsured  = CardWidget(S["finance_card_insured_prefix"].format(name=insuredTitle), collapsible=True, bold_title=True)
            insuredLayout = QVBoxLayout()

            if tipo == 'Individual':
                specs = [
                    (S["finance_card_policy_prefix"].format(branch=p.policyBranch.currentText() or S["finance_card_policy_fallback"]),
                     f"{widget.widgetId}::{p.widgetId}")
                    for p in widget.policyList
                ]
            else:
                specs = [(
                    S.get('finance_card_collective', 'FINANCIAMIENTO AGRUPADO'),
                    widget.widgetId
                )]

            container = FinancingGridContainer(specs, paymentData, quoteMode=self._quoteMode)
            self._registerContainer(container)   # <— registers ALL
            insuredLayout.addWidget(container)
            groupInsured.setLayout(insuredLayout)
            self.mainLayout.insertWidget(2 + i, groupInsured)  # pos 2+: after quote+type cards

            # Apply the current quote mode to each freshly created table so
            # receiptInput visibility and col headers survive a type change.
            for table in container.tableMap.values():
                table.applyMode(self._quoteMode)

    def _onCase4TypeChange(self, tipo, policiesPage):
        """Same rationale as _onCase2TypeChange — no paymentData parameter."""
        if self.blockSignalChanges:
            return
        if self._hasQuotaData():
            if not self._confirmTypeChange(tipo):
                self._revertType()
                return
            self.signalWipePaymentData.emit()
        self._rebuildCase4Tables(tipo, {}, policiesPage)

    # ── Type selector card factory ─────────────────────────────────────────────

    def _buildQuotaModeCard(self):
        """
        Build the global TIPO DE CUOTA selector CardWidget.
        Inserted at position 0 in setupPage() for all cases.
        Selection is stored in self._quoteMode and persists across navigation.
        """
        groupQuote  = CardWidget(S["card_quote_type"])
        quoteLayout = QVBoxLayout()

        self._quoteModeGroup  = QButtonGroup(self)
        self._qModeCuota  = QRadioButton("Cuota")
        self._qModeRecibo = QRadioButton("Número de Recibo")
        self._qModeAmbos  = QRadioButton("Ambos")


        self._quoteModeGroup.addButton(self._qModeCuota)
        self._quoteModeGroup.addButton(self._qModeRecibo)
        self._quoteModeGroup.addButton(self._qModeAmbos)

        quoteLayout.addWidget(self._qModeCuota)
        quoteLayout.addWidget(self._qModeRecibo)
        quoteLayout.addWidget(self._qModeAmbos)

        groupQuote.setLayout(quoteLayout)
        groupQuote.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Restore previously selected mode
        if self._quoteMode == 'recibo':
            self._qModeRecibo.setChecked(True)
        elif self._quoteMode == 'ambos':
            self._qModeAmbos.setChecked(True)
        else:
            self._qModeCuota.setChecked(True)

        # Connect signals — blockSignalChanges guards against spurious fires on rebuild
        self._qModeCuota.toggled.connect(
            lambda checked: self._onQuoteModeChanged('cuota')  if checked else None)
        self._qModeRecibo.toggled.connect(
            lambda checked: self._onQuoteModeChanged('recibo') if checked else None)
        self._qModeAmbos.toggled.connect(
            lambda checked: self._onQuoteModeChanged('ambos')  if checked else None)

        return groupQuote

    def _onQuoteModeChanged(self, mode):
        """
        Propagate the new mode to ALL financing tables across ALL containers.
        Each FinancingTable.applyMode(mode) handles its own visual update:
          - show/hide receiptInput
          - change col 0 header
          - switch between 3-col and 4-col AutoTreeWidget
          - migrate data between tables if needed
        blockSignalChanges guard prevents spurious calls during page rebuild.
        """
        if self.blockSignalChanges:
            return
        self._quoteMode = mode
        for container in self._allContainers:
            for table in container.tableMap.values():
                table.applyMode(mode)

    def _makeTypeCard(self,
                      individual_label=S["finance_individual_case4"],
                      collective_label=S["finance_collective_case4"]):
        """Build the financing type selector CardWidget."""
        groupType  = CardWidget(S["card_financing_type"])
        typeLayout = QVBoxLayout()

        self.financingType       = QButtonGroup()
        self.financingIndividual = QRadioButton(individual_label)
        self.financingCollective = QRadioButton(collective_label)
        self.financingType.addButton(self.financingIndividual)
        self.financingType.addButton(self.financingCollective)
        typeLayout.addWidget(self.financingIndividual)
        typeLayout.addWidget(self.financingCollective)
        groupType.setLayout(typeLayout)
        groupType.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        return groupType

    # ── Guard helpers ──────────────────────────────────────────────────────────

    def _hasQuotaData(self):
        """Return True if any table in any container has quota rows."""
        for container in self._allContainers:
            for table in container.tableMap.values():
                if table.quotasTable.topLevelItemCount() > 0:
                    return True
        return False

    def _confirmTypeChange(self, tipo):
        tipoLabel = "Colectivo" if tipo == "Collective" else "Individual"
        reply = CustomMessageBox.question(
            self,
            "Cambio de Tipo de Financiamiento",
            f"Al cambiar a {tipoLabel} se perderán las cuotas ingresadas.\n\n"
            "¿Desea continuar?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes

    def _revertType(self):
        """Revert the radio button to currentFinancingType without firing the handler."""
        self.blockSignalChanges = True
        if self.currentFinancingType == 'Individual':
            self.financingIndividual.setChecked(True)
        else:
            self.financingCollective.setChecked(True)
        self.blockSignalChanges = False

    # ── Persistence called by app.py ───────────────────────────────────────────

    def collectPaymentData(self):
        """
        Collect quota data from ALL containers in _allContainers.
        Returns { key: {'cuotas': [...], 'total': str} }.

        Previously only _activeContainer (the first one) was read — this caused
        data loss for Cases 3 and 4 where multiple containers exist.
        Now every container created by any case builder is in _allContainers,
        so all quotas are collected regardless of case.
        """
        result = {}
        for container in self._allContainers:
            result.update(container.collectPaymentData())
        return result

    def getData(self):
        """Return financing type metadata for document generation."""
        data    = {}
        multi   = self.pageConfig['multiplePolicies']
        insured = self.pageConfig['multipleClients']

        if self.hasTypeWidgets and hasattr(self, 'financingIndividual'):
            data['tipoFinanciamiento'] = (
                'Individual' if self.financingIndividual.isChecked() else 'Colectivo'
            )
        elif not multi and insured:
            data['tipoFinanciamiento'] = 'PorAsegurado'

        data['modoRecibo'] = self._quoteMode   # global mode for document generation

        return data
