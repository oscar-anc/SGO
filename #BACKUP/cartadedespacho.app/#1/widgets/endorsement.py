# coding: utf-8
"""
widgets/endorsement.py — Cesiones de Derecho widget system.

EndorsementTableCard:    Card with checkbox, branch, count and action buttons.
_EndorsementViewDialog:  Read-only view of endorsement data in tabs.
_EndorsementEditDialog:  Full edit dialog with per-group editors and Excel import.
_GroupEditor:            Single endorsee group — name combo, columns, table.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QTabWidget, QFileDialog,
    QApplication, QSizePolicy, QLineEdit, QTextEdit, QComboBox,
    QScrollArea, QFrame,
)
from PySide6.QtCore import Qt, Signal, QByteArray, QTimer
from PySide6.QtGui import QIcon, QPixmap, QFont, QColor
from theme import QSSA
from strings import S
import json as _json
try:
    _DB = _json.load(open('db.json', encoding='utf-8'))
except Exception:
    _DB = {}
_ENDORSEE_TAB_NAMES = _DB.get('endorsee_tab_names', {})

def _normalize_currency_cols(cols, currency):
    """Replace any 'Monto Endosado ...' column with current currency suffix."""
    import re as _re
    return [
        _re.sub(r'^Monto Endosado.*', f'Monto Endosado {currency}', c)
        for c in cols
    ]
from svgs import SVG_VIEW, SVG_EDIT, SVG_EXCEL_IMPORT, get_svg_trash, SVG_TRASH
from .dialog import CustomDialog  # direct submodule import — avoids circular via __init__
import copy


def _makeSvgButton(svg_str, object_name='', size=32, icon_size=18,
                   tooltip='', role=''):
    """
    Build a square icon-only QPushButton from an inline SVG string.
    Color controlled via QSS role property (preferred) or objectName.
    """
    btn = QPushButton()
    if role:
        btn.setProperty('role', role)
        btn.style().unpolish(btn)
        btn.style().polish(btn)
    elif object_name:
        btn.setObjectName(object_name)
    btn.setFixedSize(size, size)
    btn.setToolTip(tooltip)
    px = QPixmap()
    px.loadFromData(QByteArray(svg_str.encode()), 'SVG')
    if not px.isNull():
        btn.setIcon(QIcon(px.scaled(
            icon_size, icon_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )))
    return btn


class EndorsementTableCard(QWidget):
    """
    Unified card for Cesiones de Derecho entries.
    Header: checkbox (when multiple policies) + ramo label + count + Ver/Editar/Import buttons.
    No body — all editing happens in dialogs.
    Schema dynamic: {'columns': [...], 'rows': [[...],...]} for standard ramos
                    {'groups': [{'name':..,'columns':[..],'rows':[[..]]}]} for TREC
    """

    def __init__(self, label='', isTrec=False, defaultColumns=None,
                 savedData=None, showCheckbox=True, currency='S/.', parent=None):
        super().__init__(parent)
        self._label        = label
        self._isTrec       = isTrec
        self._showCheckbox = showCheckbox
        self._endosatarios = []
        self._currency     = currency

        if savedData and ('rows' in savedData or 'groups' in savedData):
            self._data = copy.deepcopy(savedData)
        else:
            if isTrec:
                self._data = {'groups': []}
            else:
                cols = defaultColumns or [
                    'Detalle',
                    f'Monto Endosado {currency}',
                    'Endosatario'
                ]
                self._data = {'columns': list(cols), 'rows': []}

        self._buildLayout()

    def _buildLayout(self):

        outer = QVBoxLayout(self)
        outer.setContentsMargins(*QSSA['margins_zero'])
        outer.setSpacing(QSSA['spacing_zero'])

        self._header = QWidget()
        self._header.setObjectName('EndorsementCard')
        self._header.setAttribute(Qt.WA_StyledBackground, True)
        self._header.setMinimumHeight(QSSA['card_header_fixed_height'])

        hl = QHBoxLayout(self._header)
        hl.setContentsMargins(*QSSA['margins_endtable_header'])
        hl.setSpacing(QSSA['spacing_endtable_header'])

        if self._showCheckbox:
            self._cb = QCheckBox(self._label)
            self._cb.setObjectName('CardTitle')
            self._cb.toggled.connect(self._onCheckChanged)
            hl.addWidget(self._cb)
        else:
            lbl = QLabel(self._label)
            lbl.setObjectName('CardTitle')
            hl.addWidget(lbl)
            self._cb = None

        hl.addStretch()

        # Counter — positioned right side, before action buttons
        self._countLabel = QLabel('')
        self._countLabel.setObjectName('CardTitle')
        f = self._countLabel.font()
        f.setPointSize(max(f.pointSize() - 2, 7))
        f.setBold(False)
        self._countLabel.setFont(f)
        self._countLabel.setVisible(False)
        hl.addWidget(self._countLabel)

        def _hbtn(svg_str, role, tip, sz=22):
            b = QPushButton()
            b.setProperty('role', role)
            b.style().unpolish(b)
            b.style().polish(b)
            b.setFixedSize(sz, sz)
            b.setToolTip(tip)
            px = QPixmap()
            px.loadFromData(QByteArray(svg_str.encode()), 'SVG')
            if not px.isNull():
                b.setIcon(QIcon(px.scaled(
                    sz - 6, sz - 6,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )))
            return b

        self._btnView   = _hbtn(SVG_VIEW,         'endtable-view',   S['endtable_btn_view'])
        self._btnEdit   = _hbtn(SVG_EDIT,         'endtable-edit',   S['endtable_btn_edit'])
        self._btnImport = _hbtn(SVG_EXCEL_IMPORT, 'endtable-import', S['endtable_btn_import'])

        self._btnView.clicked.connect(self._openViewDialog)
        self._btnEdit.clicked.connect(self._openEditDialog)
        self._btnImport.clicked.connect(self._openImportDialog)

        for btn in (self._btnView, self._btnEdit, self._btnImport):
            hl.addWidget(btn)
            if self._showCheckbox:
                btn.setVisible(False)  # hidden until checked

        outer.addWidget(self._header)
        self._updateCountLabel()

        # Show buttons if already checked at init
        if self._showCheckbox and self._cb and self._cb.isChecked():
            for btn in (self._btnView, self._btnEdit, self._btnImport):
                btn.setVisible(True)

    def _onCheckChanged(self, checked):
        for btn in (self._btnView, self._btnEdit, self._btnImport):
            btn.setVisible(checked)
        self._updateCountLabel()

    def isChecked(self):
        return self._cb.isChecked() if self._cb else True

    def setChecked(self, val):
        if self._cb:
            self._cb.blockSignals(True)
            self._cb.setChecked(val)
            self._cb.blockSignals(False)
            self._onCheckChanged(val)

    def _rowCount(self):
        if self._isTrec:
            return sum(len(g.get('rows', [])) for g in self._data.get('groups', []))
        if self._data.get('mode') == 'by_endorsee':
            return sum(len(g.get('rows', [])) for g in self._data.get('groups', []))
        return len(self._data.get('rows', []))

    def _endorseeCount(self):
        """Return number of endorsee groups in Individual mode."""
        if self._data.get('mode') == 'by_endorsee':
            return len(self._data.get('groups', []))
        return 0

    def _updateCountLabel(self):
        if self._showCheckbox and self._cb and not self._cb.isChecked():
            self._countLabel.setVisible(False)
            return
        n = self._rowCount()
        if self._data.get('mode') == 'by_endorsee':
            e = self._endorseeCount()
            e_word = 'endosatario' if e == 1 else 'endosatarios'
            n_word = 'fila'        if n == 1 else 'filas'
            text = f'{e} {e_word} & {n} {n_word}'
        else:
            n_word = 'fila' if n == 1 else 'filas'
            text = f'{n} {n_word}'
        self._countLabel.setText(text)
        self._countLabel.setVisible(True)

    def _openViewDialog(self):
        dlg = _EndorsementViewDialog(
            self._data, self._isTrec, self._currency,
            title='',
            parent=self
        )
        dlg.exec()

    def _openEditDialog(self):
        dlg = _EndorsementEditDialog(
            self._data, self._isTrec, self._currency,
            self._endosatarios,
            title='Editar',
            parent=self
        )
        if dlg.exec():
            self._data = dlg.getData()
            self._updateCountLabel()

    def _openImportDialog(self):
        from .messagebox import CustomMessageBox
        path, _ = QFileDialog.getOpenFileName(
            QApplication.activeWindow(), S['endtable_btn_import'], '', 'Excel (*.xlsx *.xls)'
        )
        if not path:
            return
        try:
            wb = openpyxl.load_workbook(path, data_only=True)
            ws = wb.active
            rows_iter = list(ws.iter_rows(values_only=True))
            if not rows_iter:
                return
            excelCols = [str(c) if c is not None else '' for c in rows_iter[0]]
            excelRows = [[str(c) if c is not None else '' for c in row]
                         for row in rows_iter[1:] if any(c is not None for c in row)]

            if self._isTrec:
                self._importTrec(excelCols, excelRows)
            else:
                self._importStandard(excelCols, excelRows)

            self._updateCountLabel()
            CustomMessageBox.information(
                QApplication.activeWindow(), S['endtable_btn_import'],
                S['endtable_import_ok'].format(n=len(excelRows), g=1)
            )
        except Exception as e:
            CustomMessageBox.critical(
                QApplication.activeWindow(), S['endtable_btn_import'],
                S['endtable_import_err'].format(error=str(e))
            )

    def _askMergeOrReplace(self, currentCols, excelCols):
        from .dialog import CustomDialog
        dlg = CustomDialog(S['endtable_import_mismatch_title'], QApplication.activeWindow())
        dlg.setMinimumWidth(QSSA['policy_editor_min_width'])
        dlg.contentLayout().addWidget(QLabel(
            S['endtable_import_mismatch_body'].format(
                current=', '.join(currentCols), excel=', '.join(excelCols)
            )
        ))
        btnRow = QHBoxLayout()
        result = ['cancel']
        def _pick(val):
            result[0] = val
            dlg.accept()
        for lbl, val in [(S['endtable_import_replace'], 'replace'),
                         (S['endtable_import_merge'],   'merge'),
                         (S['endtable_import_cancel'],  'cancel')]:
            b = QPushButton(lbl)
            b.clicked.connect(lambda _=False, v=val: _pick(v))
            btnRow.addWidget(b)
        dlg.contentLayout().addLayout(btnRow)
        dlg.exec()
        return result[0]

    def _importStandard(self, excelCols, excelRows):
        currentCols = self._data.get('columns', [])
        if sorted(excelCols) != sorted(currentCols):
            action = self._askMergeOrReplace(currentCols, excelCols)
            if action == 'cancel':
                return
            if action == 'replace':
                self._data['columns'] = excelCols
                self._data['rows'] = []
            else:
                merged = list(currentCols)
                for c in excelCols:
                    if c not in merged:
                        merged.append(c)
                self._data['columns'] = merged
        finalCols = self._data['columns']
        for vals in excelRows:
            row = []
            for col in finalCols:
                idx = excelCols.index(col) if col in excelCols else -1
                row.append(vals[idx] if 0 <= idx < len(vals) else '')
            self._data['rows'].append(row)

    def _importTrec(self, excelCols, excelRows):
        dataStart = 1
        colNames  = list(excelCols[dataStart:])
        groups    = OrderedDict()
        for vals in excelRows:
            name = vals[0] if vals else ''
            rowData = list(vals[dataStart:])
            if name not in groups:
                groups[name] = {'name': name, 'columns': colNames, 'rows': []}
            groups[name]['rows'].append(rowData)
        existing = {g['name']: g for g in self._data.get('groups', [])}
        for name, gdata in groups.items():
            if name in existing:
                if gdata['columns'] != existing[name].get('columns', []):
                    action = self._askMergeOrReplace(existing[name]['columns'], gdata['columns'])
                    if action == 'cancel':
                        continue
                    if action == 'replace':
                        existing[name]['columns'] = gdata['columns']
                        existing[name]['rows'] = []
                    else:
                        merged = list(existing[name]['columns'])
                        for c in gdata['columns']:
                            if c not in merged:
                                merged.append(c)
                        existing[name]['columns'] = merged
                existing[name]['rows'].extend(gdata['rows'])
            else:
                self._data['groups'].append(gdata)
                existing[name] = gdata

    def getData(self):
        return copy.deepcopy(self._data)


# ─────────────────────────────────────────────────────────────────────────────
# ENDORSEMENT DIALOGS
# ─────────────────────────────────────────────────────────────────────────────

def _svg_to_qicon(svg_str: str, size: int = 16):
    """Convert an SVG string to a QIcon scaled to size×size pixels."""
    px = QPixmap()
    px.loadFromData(QByteArray(svg_str.encode()), 'SVG')
    if not px.isNull():
        return QIcon(px.scaled(
            size, size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
    return QIcon()


def _makeStyledTable():
    """Create a QTableWidget with app-styled headers and proportional columns."""
    tbl = QTableWidget()
    tbl.verticalHeader().setDefaultSectionSize(28)
    tbl.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    tbl.verticalHeader().setFixedWidth(QSSA['endtable_col_header_width'])
    tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    tbl.horizontalHeader().setStretchLastSection(True)
    tbl.setAlternatingRowColors(True)
    tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
    tbl.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    # Row highlight color set via QSS in theme
    return tbl
    t.setWordWrap(True)
    t.verticalHeader().setSectionResizeMode(
        t.verticalHeader().ResizeMode.ResizeToContents)



class _EndorsementViewDialog(CustomDialog):
    """Read-only view dialog for endorsement data."""

    def __init__(self, data, isTrec, currency, title='', parent=None):
        super().__init__(title, parent)
        self.setMinimumSize(*QSSA['endtable_dialog_min_size'])
        self.setSizeGripEnabled(True)
        self._data     = data
        self._isTrec   = isTrec
        self._currency = currency
        self._populate()

    def _populate(self):

        def _make_view_table(cols, rows):
            tbl = _makeStyledTable()
            tbl.setColumnCount(len(cols))
            tbl.setHorizontalHeaderLabels(cols)
            tbl.setRowCount(len(rows))
            tbl.setEditTriggers(tbl.EditTrigger.NoEditTriggers)
            tbl.setFrameShape(tbl.Shape.NoFrame)  # no double border inside tab
            tbl.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Interactive)
            tbl.horizontalHeader().setStretchLastSection(True)
            tbl.verticalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.ResizeToContents)
            for ri, row in enumerate(rows):
                for ci, val in enumerate(row):
                    item = QTableWidgetItem(str(val))
                    col_name = cols[ci].lower() if ci < len(cols) else ''
                    if any(k in col_name for k in
                           ('monto', 'amount', 'suma', 'importe', 'prima',
                            'endosatario', 'endorsee', 'beneficiario')):
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    tbl.setItem(ri, ci, item)
            tbl.resizeRowsToContents()
            return tbl

        use_tabs = self._isTrec or self._data.get('mode') == 'by_endorsee'
        if use_tabs:
            tabs = QTabWidget()
            for grp in self._data.get('groups', []):
                tbl = _make_view_table(
                    grp.get('columns', []), grp.get('rows', []))
                tabs.addTab(tbl, grp.get('name', '—'))
            self.contentLayout().addWidget(tabs, 1)
        else:
            tbl = _make_view_table(
                self._data.get('columns', []), self._data.get('rows', []))
            self.contentLayout().addWidget(tbl, 1)

        btnRow = QHBoxLayout()
        btnRow.addStretch()
        btnClose = QPushButton(S['btn_close'])
        btnClose.clicked.connect(self.reject)
        btnRow.addWidget(btnClose)
        self.contentLayout().addLayout(btnRow)



class _EndorsementEditDialog(CustomDialog):
    """Full edit dialog. Top bar: Agregar Endosatario | Importar Excel | Descargar Plantilla."""

    def __init__(self, data, isTrec, currency, endosatarios, title='', parent=None):
        super().__init__(title, parent)
        self._data         = copy.deepcopy(data)
        self._isTrec       = isTrec
        self._currency     = currency
        self._endosatarios = endosatarios
        self._groupWidgets = []
        self.setMinimumSize(*QSSA['endtable_view_min_size'])
        self.setSizeGripEnabled(True)
        self._populate()

    def _populate(self):
        cl = self.contentLayout()
        cl.setSpacing(QSSA['spacing_endtable_groups'])

        # Top action bar
        topBar = QHBoxLayout()
        topBar.setSpacing(QSSA['spacing_endtable_topbar2'])

        # Mode toggle (non-TREC only): Una tabla ↔ Por endosatario
        if not self._isTrec:
            self._modeBtn = QPushButton()
            self._modeBtn.setCheckable(True)
            self._modeBtn.setProperty('role', 'cesiones-neutral')
            self._modeBtn.style().unpolish(self._modeBtn)
            self._modeBtn.style().polish(self._modeBtn)
            # Checked = 'Por endosatario' (Flujo B), Unchecked = 'Una tabla' (Flujo A)
            hasGroups = bool(self._data.get('mode') == 'by_endorsee' or
                            len(self._data.get('groups', [])) > 0)
            self._modeBtn.setChecked(hasGroups)
            self._modeBtn.setText(
                S.get('endtable_mode_by_endorsee', 'Por endosatario') if hasGroups
                else S.get('endtable_mode_single', 'Una tabla')
            )
            self._modeBtn.setFixedHeight(QSSA['endtable_topbar_height'])
            self._modeBtn.setAutoDefault(False)
            self._modeBtn.setDefault(False)
            self._modeBtn.toggled.connect(self._onModeToggled)
            topBar.addWidget(self._modeBtn)
            topBar.addSpacing(12)
        else:
            self._modeBtn = None

        self._btnAddEndorsee = QPushButton(S['endtable_add_endorsee'])
        self._btnImportTop   = QPushButton(S['endtable_btn_import'])
        self._btnImportTop.setObjectName('BtnExcelImportText')
        self._btnDownload    = QPushButton(S['endtable_download_template'])
        self._btnDownload.setObjectName('BtnDownloadTemplate')
        self._btnAddEndorsee.clicked.connect(lambda: self._addGroup())
        self._btnImportTop.clicked.connect(self._importExcel)
        self._btnDownload.clicked.connect(self._downloadTemplate)
        # Gear for Agrupado mode — toggles config panel on the single GroupEditor
        if not self._isTrec:
            g_w, g_h = QSSA.get('group_editor_gear_size', (28, 28))
            from svgs import get_svg_gear
            self._topbarGearBtn = QPushButton()
            self._topbarGearBtn.setProperty('role', 'config-gear')
            self._topbarGearBtn.setCheckable(True)
            self._topbarGearBtn.setFixedSize(g_w, g_h)
            self._topbarGearBtn.setToolTip(S['endtable_gear_tip'])
            self._topbarGearBtn.setIcon(_svg_to_qicon(
                get_svg_gear(QSSA.get('card_header_toggle', '#9a9a9a')),
                QSSA['endtable_topbar_height'] - 8))
            # Override setFixedSize — use consistent topbar height
            self._topbarGearBtn.setFixedSize(QSSA['endtable_topbar_height'],
                                             QSSA['endtable_topbar_height'])
            self._topbarGearBtn.toggled.connect(
                lambda checked: self._groupWidgets[0].showConfigPanel(checked)
                if self._groupWidgets else None
            )
        else:
            self._topbarGearBtn = None
        # Uniform height
        for b in (self._btnAddEndorsee, self._btnImportTop, self._btnDownload):
            b.setFixedHeight(QSSA['endtable_topbar_height'])
        topBar.addStretch()
        if not self._isTrec and hasattr(self, '_topbarGearBtn') and self._topbarGearBtn:
            topBar.addWidget(self._topbarGearBtn)
        topBar.addWidget(self._btnAddEndorsee)
        topBar.addWidget(self._btnImportTop)
        topBar.addWidget(self._btnDownload)
        cl.addLayout(topBar)
        # Visibility after layout is set
        if not self._isTrec:
            self._btnAddEndorsee.setVisible(hasGroups)
            if self._topbarGearBtn is not None:
                self._topbarGearBtn.setVisible(not hasGroups)

        # Container: QTabWidget for Individual/TREC, QScrollArea for Agrupado
        # Determined after restore — we build both and show the right one
        self._tabWidget = QTabWidget()
        self._tabWidget.setTabsClosable(False)
        self._tabWidget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        container = QWidget()
        container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._groupsLayout = QVBoxLayout(container)
        self._groupsLayout.setSpacing(QSSA['spacing_endtable_groups'])
        scroll.setWidget(container)
        self._scroll = scroll

        # Both added to layout; visibility toggled by _updateContainerMode
        cl.addWidget(self._tabWidget, 1)
        cl.addWidget(scroll, 1)
        # Initial state determined after data restore
        self._tabWidget.setVisible(False)
        self._scroll.setVisible(True)

        # Set container mode BEFORE restoring groups so _addGroup routes correctly
        _byEndorsee_init = (not self._isTrec and
                            self._data.get('mode') == 'by_endorsee')
        # Sync modeBtn state so _addGroup reads correct mode via isChecked()
        if self._modeBtn is not None and not self._isTrec:
            self._modeBtn.blockSignals(True)
            self._modeBtn.setChecked(_byEndorsee_init)
            self._modeBtn.setText(
                S.get('endtable_mode_by_endorsee', 'Individual') if _byEndorsee_init
                else S.get('endtable_mode_single', 'Agrupado'))
            self._modeBtn.blockSignals(False)
        self._updateContainerMode(_byEndorsee_init)

        # Restore data — respect saved mode
        if self._isTrec:
            savedGroups = self._data.get('groups', [])
            if savedGroups:
                for grp in savedGroups:
                    self._addGroup(grp.get('name', ''), grp.get('columns'), grp.get('rows', []))
            else:
                self._addGroup()  # one empty TREC group as default
        else:
            savedMode = self._data.get('mode', 'single')
            if savedMode == 'by_endorsee':
                # Individual mode: restore each group as a card
                savedGroups = self._data.get('groups', [])
                if savedGroups:
                    for grp in savedGroups:
                        self._addGroup(grp.get('name', ''), grp.get('columns'), grp.get('rows', []))
                else:
                    self._addGroup()
            else:
                # Agrupado mode: single table with columns/rows at root level
                self._addGroup('', self._data.get('columns'), self._data.get('rows', []))

        # Ensure tab 0 is selected after restore
        if self._tabWidget.count() > 0:
            self._tabWidget.setCurrentIndex(0)

        # Single Close button — always saves on close
        btnRow = QHBoxLayout()
        btnRow.addStretch()
        btnClose = QPushButton(S.get('endtable_btn_save', 'Guardar'))
        btnClose.setAutoDefault(False)
        btnClose.setDefault(False)
        btnClose.clicked.connect(self.accept)  # accept() saves and closes
        btnRow.addWidget(btnClose)
        cl.addLayout(btnRow)

    def _addGroup(self, name='', columns=None, rows=None):
        if columns is None:
            if self._isTrec:
                columns = ['Equipo', 'Marca', 'Modelo', 'Serie', 'Placa', 'Año', 'Nro. Leasing', 'Suma Asegurada']
            else:
                # Agrupado = single table with Endosatario column
                # Individual = per-endorsee cards, Endosatario lives in combo header
                byEndorsee = self._modeBtn is not None and self._modeBtn.isChecked()
                if byEndorsee:
                    # Individual: no Endosatario column — it's in the card header combo
                    columns = ['Detalle', f'Monto Endosado {self._currency}']
                else:
                    # Agrupado: Endosatario is a column in the single table
                    columns = ['Detalle', f'Monto Endosado {self._currency}', 'Endosatario']
        # First group in non-TREC is not deletable; TREC groups always deletable
        canDelete = self._isTrec or len(self._groupWidgets) > 0
        # Individual mode = header shown; Agrupado = no header
        byEndorsee = self._modeBtn is not None and self._modeBtn.isChecked()
        grp = _GroupEditor(
            name=str(name) if name is not None else '',
            columns=list(columns),
            rows=list(rows or []),
            endosatarios=self._endosatarios,
            currency=self._currency,
            canDelete=canDelete,
            hasHeader=byEndorsee or self._isTrec,
        )
        grp.sigRemove.connect(lambda g=grp: self._removeGroup(g))
        self._groupWidgets.append(grp)
        use_tabs = self._isTrec or (self._modeBtn is not None and self._modeBtn.isChecked())
        if use_tabs:
            tab_num = self._tabWidget.count() + 1

            def _tab_label(text, num):
                """Use short name from db.json if available, else use text as-is."""
                if not text:
                    return f'Endosatario {num}'
                return _ENDORSEE_TAB_NAMES.get(text, text)

            tab_name = _tab_label(
                grp._nameCombo.currentText() if hasattr(grp, '_nameCombo') else '', tab_num)
            self._tabWidget.addTab(grp, tab_name)
            self._tabWidget.setCurrentIndex(self._tabWidget.count() - 1)
            # Sync tab title when name combo changes
            if hasattr(grp, '_nameCombo'):
                idx = self._tabWidget.count() - 1
                grp._nameCombo.currentTextChanged.connect(
                    lambda text, i=idx, n=tab_num: self._tabWidget.setTabText(
                        i, _tab_label(text, n))
                )
        else:
            self._groupsLayout.addWidget(grp)

    def _removeGroup(self, grp):
        if grp in self._groupWidgets:
            self._groupWidgets.remove(grp)
        grp.setParent(None)
        grp.deleteLater()

    def _clearGroups(self):
        # Clear tab widget
        while self._tabWidget.count():
            self._tabWidget.removeTab(0)
        for grp in list(self._groupWidgets):
            grp.setParent(None)
            grp.deleteLater()
        self._groupWidgets.clear()
        # Remove all spacers and widgets from scroll layout
        for i in range(self._groupsLayout.count() - 1, -1, -1):
            item = self._groupsLayout.itemAt(i)
            if item:
                if item.spacerItem():
                    self._groupsLayout.removeItem(item)
                elif item.widget():
                    item.widget().setParent(None)

    def _updateContainerMode(self, byEndorsee):
        """Switch visible container between QTabWidget (Individual) and QScrollArea (Agrupado)."""
        use_tabs = byEndorsee or self._isTrec
        self._tabWidget.setVisible(use_tabs)
        self._scroll.setVisible(not use_tabs)
        # Force geometry update so the visible container actually repaints
        if use_tabs:
            self._tabWidget.updateGeometry()
        else:
            self._scroll.updateGeometry()

    def _onModeToggled(self, checked: bool):
        """
        checked=True  → Individual (by endorsee, hasHeader=True)
        checked=False → Agrupado  (single table, hasHeader=False)

        Agrupado → Individual: split rows by Endosatario column if present.
        Individual → Agrupado: consolidate rows, add Endosatario column from group names.
        """
        from .messagebox import CustomMessageBox
        from PySide6.QtWidgets import QMessageBox
        self._modeBtn.setText(
            S.get('endtable_mode_by_endorsee', 'Individual') if checked
            else S.get('endtable_mode_single', 'Agrupado')
        )
        self._btnAddEndorsee.setVisible(checked)
        if self._topbarGearBtn:
            self._topbarGearBtn.setVisible(not checked)

        if checked:
            # ── Agrupado → Individual ────────────────────────────────────
            # Read Endosatario column from single table, split rows by endorsee
            # into separate cards. Endorsee value moves from column → combo header.
            if not self._groupWidgets:
                self._clearGroups()
                self._addGroup()
                return
            data = self._groupWidgets[0].getGroupData()
            cols = data.get('columns', [])
            rows = data.get('rows', [])
            # Find Endosatario column
            try:
                end_idx = next(i for i,c in enumerate(cols)
                               if c.lower() == 'endosatario')
            except StopIteration:
                end_idx = None
            # Body columns = all columns except Endosatario
            body_cols = _normalize_currency_cols(
                [c for i,c in enumerate(cols) if i != end_idx], self._currency)
            if end_idx is not None:
                # Group rows by Endosatario value → each becomes a card
                groups_dict = {}
                order = []  # preserve insertion order
                for row in rows:
                    endorsee = row[end_idx] if end_idx < len(row) else ''
                    body_row = [v for i,v in enumerate(row) if i != end_idx]
                    if endorsee not in groups_dict:
                        groups_dict[endorsee] = []
                        order.append(endorsee)
                    groups_dict[endorsee].append(body_row)
                self._clearGroups()
                self._updateContainerMode(True)
                for endorsee in order:
                    self._addGroup(endorsee, body_cols, groups_dict[endorsee])
                if not groups_dict:
                    self._addGroup('', body_cols, [])
            else:
                # No Endosatario column — wrap all rows in one unnamed card
                self._clearGroups()
                self._updateContainerMode(True)
                self._addGroup('', body_cols, rows)
        else:
            # ── Individual → Agrupado ────────────────────────────────────
            # Each card's combo (endorsee name) becomes a value in a new
            # Endosatario column. All rows are merged into a single table.
            all_data = [g.getGroupData() for g in self._groupWidgets]
            all_cols = [d.get('columns', []) for d in all_data]
            # Check column consistency across cards
            all_same = len(set(tuple(c) for c in all_cols)) <= 1
            if not all_same:
                reply = CustomMessageBox.question(
                    self,
                    S.get('endtable_mode_conflict_title', 'Columnas diferentes'),
                    S.get('endtable_mode_conflict_body',
                          'Los grupos tienen columnas diferentes. Al unificar se '
                          'perderán las columnas adicionales.\n\n¿Desea continuar?'),
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if reply == QMessageBox.No:
                    self._modeBtn.blockSignals(True)
                    self._modeBtn.setChecked(True)
                    self._modeBtn.blockSignals(False)
                    self._btnAddEndorsee.setVisible(True)
                    if self._topbarGearBtn:
                        self._topbarGearBtn.setVisible(False)
                    return
            # Merge: each card's rows get Endosatario column appended at end
            base_cols = all_cols[0] if all_cols else []
            merged_cols = _normalize_currency_cols(
                list(base_cols), self._currency) + ['Endosatario']
            merged_rows = []
            for d in all_data:
                endorsee = d.get('name', '')
                for row in d.get('rows', []):
                    merged_rows.append(list(row) + [endorsee])
            self._clearGroups()
            self._updateContainerMode(False)
            self._addGroup('', merged_cols, merged_rows)


    def _importExcel(self):
        from .messagebox import CustomMessageBox
        path, _ = QFileDialog.getOpenFileName(self, S['endtable_btn_import'], '', 'Excel (*.xlsx *.xls)')
        if not path:
            return
        try:
            wb = openpyxl.load_workbook(path, data_only=True)
            ws = wb.active
            rows_iter = list(ws.iter_rows(values_only=True))
            if not rows_iter:
                return
            excelCols = [str(c) if c is not None else '' for c in rows_iter[0]]
            excelRows = [[str(c) if c is not None else '' for c in row]
                         for row in rows_iter[1:] if any(c is not None for c in row)]
            if self._isTrec:
                dataStart = 1
                colNames  = list(excelCols[dataStart:])
                groups = OrderedDict()
                for vals in excelRows:
                    nm = vals[0] if vals else ''
                    if nm not in groups:
                        groups[nm] = {'name': nm, 'columns': colNames, 'rows': []}
                    groups[nm]['rows'].append(list(vals[dataStart:]))
                for nm, gd in groups.items():
                    self._addGroup(nm, gd['columns'], gd['rows'])
            else:
                if self._groupWidgets:
                    self._groupWidgets[0].appendRows(excelCols, excelRows)
            total = sum(len(g.get('rows',[])) for g in [gw.getGroupData() for gw in self._groupWidgets])
            CustomMessageBox.information(self, S['endtable_btn_import'],
                                         S['endtable_import_ok'].format(n=total, g=len(self._groupWidgets)))
        except Exception as e:
            CustomMessageBox.critical(self, S['endtable_btn_import'],
                                      S['endtable_import_err'].format(error=str(e)))

    def _downloadTemplate(self):
        from .messagebox import CustomMessageBox
        path, _ = QFileDialog.getSaveFileName(self, S['endtable_download_template'],
                                               'plantilla_cesiones.xlsx', 'Excel (*.xlsx)')
        if not path:
            return
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            if self._isTrec:
                baseHeaders = self._groupWidgets[0].getColumns() if self._groupWidgets else \
                    ['Equipo', 'Marca', 'Modelo', 'Serie', 'Placa', 'Año', 'Nro. Leasing', 'Suma Asegurada']
                headers = ['Endosatario'] + baseHeaders
            else:
                headers = self._groupWidgets[0].getColumns() if self._groupWidgets else []
            for ci, h in enumerate(headers, 1):
                cell = ws.cell(row=1, column=ci, value=h)
                cell.font      = Font(bold=True, color='FFFFFF')
                cell.fill      = PatternFill('solid', fgColor='217346')
                cell.alignment = Alignment(horizontal='center')
            wb.save(path)
            CustomMessageBox.information(self, S['endtable_download_template'],
                                         S['endtable_template_saved'].format(path=path))
        except Exception as e:
            CustomMessageBox.critical(self, S['endtable_download_template'],
                                      S['endtable_template_err'].format(error=str(e)))

    def getData(self):
        if self._isTrec:
            return {'groups': [gw.getGroupData() for gw in self._groupWidgets]}
        else:
            byEndorsee = self._modeBtn is not None and self._modeBtn.isChecked()
            if byEndorsee:
                groups = [gw.getGroupData() for gw in self._groupWidgets]
                return {'mode': 'by_endorsee', 'groups': groups}
            else:
                gd = self._groupWidgets[0].getGroupData() if self._groupWidgets else {'columns': [], 'rows': []}
                return {'mode': 'single', 'columns': gd['columns'], 'rows': gd['rows']}



class _GroupEditor(QWidget):
    """One endorsee group inside _EndorsementEditDialog."""

    from PySide6.QtCore import Signal as _Sig
    sigRemove = _Sig()

    def __init__(self, name='', columns=None, rows=None,
                 endosatarios=None, currency='S/.', canDelete=True,
                 hasHeader=True, parent=None):
        super().__init__(parent)
        self._columns      = list(columns or [])
        self._rows         = [list(r) for r in (rows or [])]
        self._endosatarios = endosatarios or []
        self._currency     = currency
        self._canDelete    = canDelete
        self._selectedCol  = -1
        self._hasHeader    = hasHeader  # True=Individual, False=Agrupado
        self._buildLayout(str(name) if name is not None else '')

    def _buildLayout(self, name):
        """Build layout. self._hasHeader controls whether header is shown (Individual mode)."""
        from svgs import (get_svg_gear, get_svg_col_add, get_svg_col_remove,
                          get_svg_col_rename, get_svg_chevron_down, get_svg_chevron_right)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(*QSSA['margins_group_editor'])
        outer.setSpacing(0)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # ── Header (Individual mode only) ─────────────────────────────────────
        hdr_h   = QSSA.get('group_editor_header_height', 36)
        btn_sz  = QSSA.get('group_editor_header_btn_size', (28, 28))[0]
        icon_sz = btn_sz - 8
        icon_color = QSSA.get('card_header_toggle', '#ffffff')

        if self._hasHeader:
            headerWidget = QWidget()
            headerWidget.setObjectName('CardHeader')
            headerWidget.setAttribute(Qt.WA_StyledBackground, True)
            headerWidget.setFixedHeight(hdr_h)
            hl = QHBoxLayout(headerWidget)
            hl.setContentsMargins(6, 0, 6, 0)
            hl.setSpacing(4)
            hl.setAlignment(Qt.AlignVCenter)

            # Accordion button — hidden in Individual mode (QTabWidget handles navigation)
            self._accordionBtn = QPushButton()
            self._accordionBtn.setProperty('role', 'accordion')
            self._accordionBtn.setCheckable(True)
            self._accordionBtn.setChecked(True)
            self._accordionBtn.setFixedSize(btn_sz, btn_sz)
            self._accordionBtn.setToolTip(S['endtable_accordion_tip'])
            self._accordionBtn.setIcon(_svg_to_qicon(get_svg_chevron_down(icon_color), icon_sz))
            self._accordionBtn.toggled.connect(self._onAccordionToggled)
            self._accordionBtn.setVisible(False)  # hidden — tab provides navigation
            hl.addWidget(self._accordionBtn)

            # Endorsee combo — fixed max width, not stretch
            self._nameCombo = QComboBox()
            self._nameCombo.setEditable(True)
            self._nameCombo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
            self._nameCombo.setPlaceholderText(S['endtable_endorsee_placeholder'])
            self._nameCombo.addItems(self._endosatarios)
            self._nameCombo.setMaximumWidth(QSSA.get('group_editor_combo_max_width', 400))
            self._nameCombo.setFixedHeight(hdr_h - 8)
            if name:
                self._nameCombo.setCurrentText(name)
            hl.addWidget(self._nameCombo)
            hl.addStretch()

            # Gear button
            self._gearBtn = QPushButton()
            self._gearBtn.setProperty('role', 'config-gear')
            self._gearBtn.setCheckable(True)
            self._gearBtn.setFixedSize(btn_sz, btn_sz)
            self._gearBtn.setToolTip(S['endtable_gear_tip'])
            self._gearBtn.setIcon(_svg_to_qicon(get_svg_gear(icon_color), icon_sz))
            self._gearBtn.toggled.connect(self._onGearToggled)
            hl.addWidget(self._gearBtn)

            # Trash button
            if self._canDelete:
                btnRm = _makeSvgButton(SVG_TRASH, size=btn_sz, icon_size=icon_sz, role='quitar')
                btnRm.clicked.connect(self.sigRemove.emit)
                hl.addWidget(btnRm)

            outer.addWidget(headerWidget)
        else:
            self._accordionBtn = None
            self._gearBtn      = None
            self._nameCombo    = None

        # ── Config panel (gear drawer, hidden by default) ─────────────────────
        self._configPanel = QWidget()
        self._configPanel.setObjectName('ConfigPanel')
        self._configPanel.setAttribute(Qt.WA_StyledBackground, True)
        configLayout = QHBoxLayout(self._configPanel)
        configLayout.setContentsMargins(*QSSA['group_editor_config_padding'])
        configLayout.setSpacing(QSSA['group_editor_config_spacing'])

        configLayout.addStretch()  # push everything to the right
        self._colNameEdit = QLineEdit()
        self._colNameEdit.setPlaceholderText(S['endtable_col_config_placeholder'])
        self._colNameEdit.setMaximumWidth(QSSA.get('group_editor_col_input_width2', 350))
        self._colNameEdit.setMinimumWidth(200)
        self._colNameEdit.setMinimumHeight(int(QSSA['lineedit_min_height']))
        configLayout.addWidget(self._colNameEdit)

        c_w, c_h = QSSA['group_editor_col_btn_size']
        icon_col      = QSSA.get('text_on_dark', '#FFFFFF')
        icon_col_danger = '#FFFFFF'  # always white on danger bg
        self._btnColAdd    = QPushButton()
        self._btnColRename = QPushButton()
        self._btnColRemove = QPushButton()
        for btn, svg_fn, role, tip_key in [
            (self._btnColAdd,    get_svg_col_add(icon_col),         'col-action',        'endtable_col_add_tip'),
            (self._btnColRename, get_svg_col_rename(icon_col),      'col-action',        'endtable_col_rename_tip'),
            (self._btnColRemove, get_svg_col_remove(icon_col_danger),'col-action-danger', 'endtable_col_remove_tip'),
        ]:
            btn.setProperty('role', role)
            btn.style().unpolish(btn); btn.style().polish(btn)
            btn.setFixedSize(c_w, c_h)
            btn.setToolTip(S[tip_key])
            btn.setIcon(_svg_to_qicon(svg_fn, c_h - 6))
            configLayout.addWidget(btn)

        self._configPanel.setVisible(False)  # hidden until gear pressed
        outer.addWidget(self._configPanel)

        # ── Body ──────────────────────────────────────────────────────────────
        self._body = QWidget()
        self._body.setObjectName('CardBody')
        self._body.setAttribute(Qt.WA_StyledBackground, True)
        bodyLayout = QVBoxLayout(self._body)
        bodyLayout.setContentsMargins(*QSSA['margins_card_body'])
        bodyLayout.setSpacing(QSSA['spacing_card_body'])

        # Input row (dynamic — rebuilt when columns change)
        self._inputContainer = QWidget()
        self._inputLayout    = QHBoxLayout(self._inputContainer)
        self._inputLayout.setContentsMargins(*QSSA['margins_group_editor_input'])
        self._inputLayout.setSpacing(QSSA['spacing_group_editor_input'])
        self._inputs = []
        self._rebuildInputs()
        bodyLayout.addWidget(self._inputContainer)

        # Action buttons
        btnRow = QHBoxLayout()
        self._btnAdd    = QPushButton(S['btn_add'].upper())
        self._btnUpdate = QPushButton(S['btn_update'].upper())
        self._btnDelete = QPushButton(S['btn_delete'].upper())
        self._btnAdd.setProperty('role', 'cesiones-neutral')
        self._btnUpdate.setProperty('role', 'cesiones-neutral')
        self._btnDelete.setProperty('role', 'cesiones-danger')
        for b in (self._btnAdd, self._btnUpdate, self._btnDelete):
            b.setFixedHeight(QSSA['group_editor_table_height'])
        self._btnAdd.clicked.connect(self._addRow)
        self._btnUpdate.clicked.connect(self._updateRow)
        self._btnDelete.clicked.connect(self._deleteRow)
        for b in (self._btnAdd, self._btnUpdate, self._btnDelete):
            btnRow.addWidget(b, 1)
        bodyLayout.addLayout(btnRow)

        # Table — expands to fill available dialog space
        self._table = _makeStyledTable()
        self._table.setColumnCount(len(self._columns))
        self._table.setHorizontalHeaderLabels(self._columns)
        self._table.horizontalHeader().setSectionsMovable(True)
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setMinimumHeight(QSSA.get('group_editor_table_min_h', 120))
        self._table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._table.itemSelectionChanged.connect(self._onSelectionChanged)
        self._table.horizontalHeader().sectionClicked.connect(
            self._onHeaderClicked)
        bodyLayout.addWidget(self._table, 1)
        outer.addWidget(self._body, 1)  # stretch so table fills dialog

        # Populate
        self._table.blockSignals(True)
        self._table.setRowCount(len(self._rows))
        for ri, row in enumerate(self._rows):
            for ci in range(min(len(row), len(self._columns))):
                item = QTableWidgetItem(str(row[ci]))
                # Center Monto and Endosatario columns
                col_name = self._columns[ci].lower() if ci < len(self._columns) else ''
                is_center = any(k in col_name for k in
                    ('monto', 'amount', 'suma', 'importe', 'prima',
                     'endosatario', 'endorsee', 'beneficiario'))
                if is_center:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter)
                self._table.setItem(ri, ci, item)
        self._table.blockSignals(False)
        # Resize all rows to show full content after populating
        self._table.resizeRowsToContents()

        # Header alignment
        for ci in range(len(self._columns)):
            self._table.model().setHeaderData(
                ci, Qt.Orientation.Horizontal,
                int(Qt.AlignmentFlag.AlignCenter),
                Qt.ItemDataRole.TextAlignmentRole
            )

        # Wire config panel buttons
        self._btnColAdd.clicked.connect(self._addColumn)
        self._btnColRemove.clicked.connect(self._deleteSelectedColumn)
        self._btnColRename.clicked.connect(self._renameSelectedColumn)

        # Non-header mode: gear button lives in dialog topbar (wired externally)
        if not self._hasHeader:
            self._gearBtn = None  # created externally for Agrupado mode


    def _onAccordionToggled(self, expanded: bool):
        """Show/hide body when accordion button toggled."""
        self._body.setVisible(expanded)
        self._configPanel.setVisible(expanded and self._gearBtn is not None
                                     and self._gearBtn.isChecked())
        from svgs import get_svg_chevron_down, get_svg_chevron_right
        icon_color = QSSA.get('card_header_toggle', '#ffffff')
        sz = QSSA['group_editor_accordion_size'][1] - 8
        svg = get_svg_chevron_down(icon_color) if expanded else get_svg_chevron_right(icon_color)
        self._accordionBtn.setIcon(_svg_to_qicon(svg, sz))
        # Collapse height to header only — prevents blank space between groups
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred if expanded
            else QSizePolicy.Policy.Maximum
        )
        self.updateGeometry()

    def _onGearToggled(self, checked: bool):
        """Show/hide config panel. Only visible when body is expanded."""
        visible = checked and self._body.isVisible()
        self._configPanel.setVisible(visible)
        if visible:
            self._colNameEdit.setFocus()

    def showConfigPanel(self, show: bool = True):
        """Called externally (Agrupado mode) to show/hide config panel."""
        self._configPanel.setVisible(show)
        if show:
            self._colNameEdit.setFocus()



    def _onHeaderClicked(self, logicalIndex):
        """Select column. If config panel is open, load column name into editor."""
        self._selectedCol = logicalIndex
        self._table.selectColumn(logicalIndex)
        # Load name into config panel if it's visible
        if self._configPanel.isVisible() and logicalIndex < len(self._columns):
            self._colNameEdit.setText(self._columns[logicalIndex])

    def _rebuildInputs(self):
        while self._inputLayout.count():
            item = self._inputLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._inputs = []
        for col in self._columns:
            col_lower = col.lower()
            is_detalle = col_lower in ('detalle', 'detail', 'descripción', 'descripcion')
            is_endosatario = col_lower in ('endosatario', 'endorsee', 'beneficiario')
            is_monto = any(kw in col_lower for kw in
                           ('monto', 'amount', 'suma', 'importe', 'prima'))
            if is_detalle:
                inp = QTextEdit()
                inp.setPlaceholderText(col)
                inp.setAcceptRichText(False)
                inp.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                inp.setTabChangesFocus(True)  # Tab moves to next input
            elif is_endosatario and not self._hasHeader:
                # Agrupado mode — QComboBox with db.json endorsees list
                inp = QComboBox()
                inp.setEditable(True)
                inp.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
                inp.setPlaceholderText(col)
                if self._endosatarios:
                    inp.addItems(self._endosatarios)
                inp.setCurrentIndex(-1)
                inp.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                inp.setMinimumHeight(int(QSSA['combobox_min_height']))
            else:
                inp = QLineEdit()
                inp.setPlaceholderText(col)
                inp.setMinimumHeight(int(QSSA['lineedit_min_height']))
                if is_monto:
                    from PySide6.QtGui import QDoubleValidator
                    v = QDoubleValidator(0.0, 999_999_999.99, 2)
                    v.setNotation(QDoubleValidator.Notation.StandardNotation)
                    inp.setValidator(v)
            self._inputs.append(inp)
            self._inputLayout.addWidget(inp, 1)

    def _addColumn(self):
        from .messagebox import CustomMessageBox
        name = self._colNameEdit.text().strip()
        if not name:
            CustomMessageBox.warning(self, S['endtable_add_column'],
                                     S.get('endtable_col_empty_name', 'Escribe el nombre de la columna.'))
            return
        self._columns.append(name)
        self._table.setColumnCount(len(self._columns))
        self._table.setHorizontalHeaderLabels(self._columns)
        self._table.horizontalHeader().setSectionResizeMode(
            len(self._columns) - 1, QHeaderView.ResizeMode.Stretch
        )
        self._table.horizontalHeader().setStretchLastSection(True)
        self._colNameEdit.clear()
        self._rebuildInputs()

    def _deleteSelectedColumn(self):
        from .messagebox import CustomMessageBox
        # Use last header-clicked column or current column
        col = self._selectedCol
        if col < 0:
            col = self._table.currentColumn()
        if col < 0:
            CustomMessageBox.warning(self, S['endtable_del_column'], S['endtable_no_col_selected'])
            return
        logicalCol = self._table.horizontalHeader().logicalIndex(
            self._table.horizontalHeader().visualIndex(col)
        )
        if 0 <= logicalCol < len(self._columns):
            self._columns.pop(logicalCol)
        self._table.removeColumn(logicalCol)
        self._selectedCol = -1
        self._colNameEdit.clear()
        self._rebuildInputs()

    def _renameSelectedColumn(self):
        """Rename selected column using text in config panel QLineEdit."""
        new_name = self._colNameEdit.text().strip()
        if not new_name:
            from .messagebox import CustomMessageBox
            CustomMessageBox.warning(self, 'Renombrar columna',
                                     'Escribe el nuevo nombre de la columna.')
            return
        if self._selectedCol < 0 or self._selectedCol >= len(self._columns):
            from .messagebox import CustomMessageBox
            CustomMessageBox.warning(self, 'Renombrar columna',
                                     'Selecciona una columna haciendo click en su encabezado.')
            return
        self._columns[self._selectedCol] = new_name
        self._table.setHorizontalHeaderLabels(self._columns)
        self._table.model().setHeaderData(
            self._selectedCol, Qt.Orientation.Horizontal,
            int(Qt.AlignmentFlag.AlignCenter),
            Qt.ItemDataRole.TextAlignmentRole
        )
        self._colNameEdit.clear()
        self._rebuildInputs()

    def appendRows(self, excelCols, excelRows):
        """Merge-import rows from Excel."""
        from .messagebox import CustomMessageBox
        currentCols = self._columns
        if sorted(excelCols) != sorted(currentCols):
            merged = list(currentCols)
            for c in excelCols:
                if c not in merged:
                    merged.append(c)
            self._columns = merged
            self._table.setColumnCount(len(self._columns))
            self._table.setHorizontalHeaderLabels(self._columns)
            self._rebuildInputs()
        for vals in excelRows:
            ri = self._table.rowCount()
            self._table.insertRow(ri)
            for ci, col in enumerate(self._columns):
                idx = excelCols.index(col) if col in excelCols else -1
                val = vals[idx] if 0 <= idx < len(vals) else ''
                self._table.setItem(ri, ci, QTableWidgetItem(str(val)))

    def _currentInputValues(self):
        vals = []
        for inp in self._inputs:
            if isinstance(inp, QTextEdit):
                vals.append(inp.toPlainText())
            elif isinstance(inp, QComboBox):
                vals.append(inp.currentText())
            else:
                vals.append(inp.text())
        return vals

    def _addRow(self):
        vals = self._currentInputValues()
        if not any(v.strip() for v in vals):
            return
        ri = self._table.rowCount()
        self._table.insertRow(ri)
        for ci, v in enumerate(vals):
            item = QTableWidgetItem(v)
            col_name = self._columns[ci].lower() if ci < len(self._columns) else ''
            is_center = any(k in col_name for k in
                ('monto', 'amount', 'suma', 'importe', 'prima',
                 'endosatario', 'endorsee', 'beneficiario'))
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter if is_center
                else Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            self._table.setItem(ri, ci, item)
        self._table.resizeRowToContents(ri)
        for inp in self._inputs:
            if isinstance(inp, QLineEdit):
                inp.clear()
            elif isinstance(inp, QTextEdit):
                inp.setPlainText('')
            elif isinstance(inp, QComboBox):
                inp.setCurrentIndex(-1)

    def _updateRow(self):
        ri = self._table.currentRow()
        if ri < 0:
            return
        for ci, v in enumerate(self._currentInputValues()):
            item = QTableWidgetItem(v)
            col_name = self._columns[ci].lower() if ci < len(self._columns) else ''
            is_center = any(k in col_name for k in
                ('monto', 'amount', 'suma', 'importe', 'prima',
                 'endosatario', 'endorsee', 'beneficiario'))
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter if is_center
                else Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            self._table.setItem(ri, ci, item)
        self._table.resizeRowToContents(ri)

    def _deleteRow(self):
        ri = self._table.currentRow()
        if ri < 0:
            return
        self._table.removeRow(ri)

    def _onSelectionChanged(self):
        # Only fill inputs if a row is selected (not a column)
        selected = self._table.selectedItems()
        if not selected:
            return
        ri = self._table.currentRow()
        if ri < 0:
            return
        hdr = self._table.horizontalHeader()
        for vi in range(self._table.columnCount()):
            li   = hdr.logicalIndex(vi)
            item = self._table.item(ri, li)
            if vi < len(self._inputs):
                val = item.text() if item else ''
                inp = self._inputs[vi]
                if isinstance(inp, QTextEdit):
                    inp.setPlainText(val)
                elif isinstance(inp, QComboBox):
                    idx = inp.findText(val)
                    inp.setCurrentIndex(idx) if idx >= 0 else inp.setEditText(val)
                else:
                    inp.setText(val)

    def getColumns(self):
        hdr = self._table.horizontalHeader()
        return [self._columns[hdr.logicalIndex(vi)]
                for vi in range(self._table.columnCount())
                if hdr.logicalIndex(vi) < len(self._columns)]

    def getGroupData(self):
        cols = self.getColumns()
        hdr  = self._table.horizontalHeader()
        rows = []
        for ri in range(self._table.rowCount()):
            row = []
            for vi in range(self._table.columnCount()):
                li   = hdr.logicalIndex(vi)
                item = self._table.item(ri, li)
                row.append(item.text() if item else '')
            rows.append(row)
        name = ''
        if self._nameCombo is not None:
            name = self._nameCombo.currentText().strip()
        return {'name': name, 'columns': cols, 'rows': rows}
