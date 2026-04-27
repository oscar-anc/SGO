"""
Main Application
Manages page navigation and central form data state.
pageConfig: letter type, OPE, client data, LOL, annexes.
pagePolicies: quantity selectors, financing, currency, insured/policy data.
"""

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QStackedWidget, QMessageBox,
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
)  # QHBoxLayout/QVBoxLayout/QLabel/QPushButton used in CustomTitleBar
from PySide6.QtGui import QFontDatabase, QFont
from theme import QSSA, build_palette, build_qss
from framelesswindow import FramelessMainWindow, TitleBar
from PySide6.QtCore import Qt
from PySide6.QtGui  import QPixmap
from widgets import CustomMessageBox

from pageConfig   import PageConfig
from pageUnit     import PageUnit
from pagePolicies import PagePolicies
from pageFinance  import PageFinance
from pageAnnex    import PageAnnex
from strings import S
from helpers      import generateDocument, generateManualSiniestros, generateGuarantees, generateCesiones, resource_path




class CustomTitleBar(TitleBar):
    """
    Custom title bar using framelesswindow.TitleBar as base.
    Uses the library's native minBtn/maxBtn/closeBtn exactly as created —
    no setFixedSize/setFixedHeight on them so their QPainter icons stay
    centered and harmonious. Colors are applied via TitleBarButton API.
    Background applied via WA_StyledBackground + setStyleSheet.
    Drag, resize and double-click-maximize handled by TitleBarBase.

    To change button colors later, call these methods on minBtn/maxBtn/closeBtn:
        setNormalColor(QColor)          — icon color at rest
        setHoverColor(QColor)           — icon color on hover
        setNormalBackgroundColor(QColor)— background at rest
        setHoverBackgroundColor(QColor) — background on hover
        setPressedBackgroundColor(QColor)
    """

    def __init__(self, parent):
        super().__init__(parent)

        from PySide6.QtGui import QColor

        # ── Background ────────────────────────────────────────────────────────
        # WA_StyledBackground required so Qt applies the stylesheet to this
        # inherited QWidget — without it the background stays white.
        # setFixedHeight only on the TitleBar itself, NOT on the buttons,
        # so the native QPainter icons keep their correct internal geometry.
        self.setFixedHeight(QSSA['titlebar_fixed_height'])
        # Use QPalette for background — setStyleSheet on a parent widget
        # blocks QSS rules for all child widgets (QLineEdit, QComboBox etc.)
        from PySide6.QtGui import QColor
        from theme import QSSA as _T
        pal = self.palette()
        pal.setColor(pal.ColorRole.Window, QColor(_T['titlebar_bg']))
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        # ── Logo ──────────────────────────────────────────────────────────────
        # logo_path is stored in QSSA so the theme_editor can change it.
        # Falls back through common filenames if the stored path doesn't load.
        logoLabel = QLabel()
        logoLabel.setObjectName("AppLogo")
        logo_candidates = [
            _T.get('logo_path', 'imgs/logo_white.svg'),
            'imgs/logo_white.svg',
            'imgs/logo_white.png',
            'imgs/logo.png',
        ]
        for logo_path in logo_candidates:
            try:
                pix = QPixmap(resource_path(logo_path))
                if not pix.isNull():
                    logoLabel.setPixmap(
                        pix.scaled(80, 18, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    )
                    break
            except Exception:
                pass
        # Insert logo at start of the existing hBoxLayout — before stretch+buttons
        self.hBoxLayout.insertSpacing(0, 12)
        self.hBoxLayout.insertWidget(1, logoLabel, 0, Qt.AlignVCenter)

        # ── Color native buttons via API — reads from QSSA ───────────
        from theme import QSSA as _T
        btn_text     = QColor(_T.get('titlebar_btn_text',))
        btn_hover    = QColor(_T.get('titlebar_btn_hover_bg',))
        btn_pressed  = QColor(_T.get('titlebar_btn_pressed_bg',))
        close_hover  = QColor(_T.get('titlebar_close_hover_bg',))
        close_pressed= QColor(_T.get('titlebar_close_pressed_bg',))

        for btn in [self.minBtn, self.maxBtn]:
            btn.setNormalColor(btn_text)
            btn.setHoverColor(btn_text)
            btn.setPressedColor(btn_text)
            btn.setNormalBackgroundColor(QColor(0, 0, 0, 0))
            btn.setHoverBackgroundColor(btn_hover)
            btn.setPressedBackgroundColor(btn_pressed)

        # closeBtn: white icon, danger hover background
        self.closeBtn.setNormalColor(btn_text)
        self.closeBtn.setHoverColor(btn_text)
        self.closeBtn.setPressedColor(btn_text)
        self.closeBtn.setNormalBackgroundColor(QColor(0, 0, 0, 0))
        self.closeBtn.setHoverBackgroundColor(close_hover)
        self.closeBtn.setPressedBackgroundColor(close_pressed)


class MainApp(FramelessMainWindow):
    """Main application window - manages the 4-page stack."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle(S["app_title"])
        self.setGeometry(100, 50, 720, 955)
        self.setMinimumSize(QSSA['app_min_width'], QSSA['app_min_height'])
        self.loadStyles()

        # Build root widget with TitleBar on top + pageStack below.
        # This gives the TitleBar its own physical space in the layout so
        # content starts below it — not underneath it.
        # setTitleBar() registers the widget with the library for drag/resize.
        self._customTitleBar = CustomTitleBar(self)
        self.setTitleBar(self._customTitleBar)

        self.pageStack = QStackedWidget()

        rootWidget = QWidget()
        rootLayout = QVBoxLayout(rootWidget)
        rootLayout.setContentsMargins(*QSSA['margins_app_root'])
        rootLayout.setSpacing(QSSA['spacing_app_root'])
        rootLayout.addWidget(self._customTitleBar)
        rootLayout.addWidget(self.pageStack)
        self.setCentralWidget(rootWidget)

        self.pageConfig   = PageConfig()
        self.pageUnit     = PageUnit()
        self.pagePolicies = PagePolicies()
        self.pageFinance  = PageFinance()
        self.pageAnnex    = PageAnnex()

        self.pageStack.addWidget(self.pageConfig)    # index 0
        self.pageStack.addWidget(self.pageUnit)      # index 1
        self.pageStack.addWidget(self.pagePolicies)  # index 2
        self.pageStack.addWidget(self.pageFinance)   # index 3
        self.pageStack.addWidget(self.pageAnnex)     # index 4

        self.connectSignals()

        # Central form data dict shared across all pages
        self.formData = {}

        # Central persistence store for financing tables.
        # Keys are stable 8-char UUID fragments from InsuredWidget/PolicyWidget.widgetId,
        # immune to name changes by the user.
        # Key formats:
        #   Case 1:              '__single__'
        #   Case 2 Individual:   'insuredId::policyId'
        #   Case 2 Collective:   'insuredId'
        #   Case 3:              'insuredId'
        #   Case 4 Individual:   'insuredId::policyId'
        #   Case 4 Collective:   'insuredId'
        # Each value is a list of quota dicts: [{'nro', 'vencimiento', 'importe'}, ...]
        self.paymentData = {}

        # Persistence store for PageAnnex selections across navigations.
        # Survives back/forward navigation; wiped only on onResetPolicies().
        self.annexData      = {}
        self.endorsementData = {}
        # Give pagePolicies refs to live data dicts so reduction warnings
        # can report exactly what data will be lost. All three are dicts
        # passed by reference — updates in app.py are visible automatically.
        self.pagePolicies._endorsementDataRef = self.endorsementData
        self.pagePolicies._paymentDataRef     = self.paymentData
        self.pagePolicies._annexDataRef       = self.annexData

        # Track previous financing config to detect on/off changes
        self.previousFinancingConfig = None
        self.previousFinancingType   = None  # 'Individual' or 'Collective'

        # Track previous structural config (multiplePolicies + multipleClients).
        # When either of these changes, paymentData must be wiped entirely because
        # the key schema changes and any surviving entries become stale/orphaned.
        # This is the root cause of the bug where switching Varios→Uno→Varios
        # left quota data from the previous session attached to the wrong keys.
        self.previousStructuralConfig = None  # tuple: (multiplePolicies, multipleClients)

    def _toggleMaximize(self):
        """Toggle between maximized and normal window state."""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def loadStyles(self):
        """Apply QSS generated from QSSA to QApplication.
        Applying to QApplication (not self) preserves the QPalette
        set in main() — widget-level setStyleSheet resets the palette.
        """
        from PySide6.QtWidgets import QApplication
        QApplication.instance().setStyleSheet(build_qss(QSSA))

    def connectSignals(self):
        """Wire up all inter-page navigation signals."""
        self.pageConfig.signalNext.connect(self.goToUnit)
        self.pageConfig.signalReset.connect(self.onGlobalReset)
        self.pageUnit.signalBack.connect(lambda: self.pageStack.setCurrentIndex(0))
        self.pageUnit.signalNext.connect(self.goToPolicies)
        self.pagePolicies.signalBack.connect(lambda: self.pageStack.setCurrentIndex(1))
        self.pagePolicies.signalNext.connect(self.goToPayment)
        self.pagePolicies.signalGenerate.connect(self.onGeneratePressed)
        self.pageFinance.signalBack.connect(self.onPaymentBack)
        self.pageFinance.signalGenerate.connect(self.onGeneratePressed)
        self.pageFinance.signalWipePaymentData.connect(self._onWipePaymentData)
        self.pagePolicies.signalReset.connect(self.onResetPolicies)
        self.pagePolicies.signalCesionesReduce.connect(self._onCesionesReduce)
        self.pagePolicies.signalEndorsementCleared.connect(self._onEndorsementDetailedOff)
        self.pageAnnex.signalClearCesiones.connect(lambda: self.endorsementData.clear())
        self.pageAnnex.signalBack.connect(self.onAnnexBack)
        self.pageAnnex.signalGenerate.connect(self.onGenerateDocument)

    def goToUnit(self):
        """Collect page 1 data and navigate to page 2."""
        self._saveEndorsementIfNeeded()
        self.formData.update(self.pageConfig.getData())
        self.pageStack.setCurrentIndex(1)

    def goToPolicies(self):
        """
        Collect page 2 data and navigate to page 3.
        pagePolicies is fully self-managed: quantity, financing and currency
        all live there. Only pre-fill company name if not already set.
        """
        self.formData.update(self.pageUnit.getData())

        # Pre-fill main insured name from company name if not already set
        companyName = self.formData.get('companyName', '')
        if not self.pagePolicies.mainInsured.insuredName.text():
            self.pagePolicies.setMainInsuredName(companyName)

        self.pageStack.setCurrentIndex(2)

    def _buildExpectedKeys(self, pageConfig, financingType):
        """
        Build the list of expected paymentData keys based on current
        policies/insured configuration and financing type.

        Keys use stable widgetId values (8-char UUID fragments) so they
        remain valid even when the user edits insured or policy names.

        Key formats:
          Case 1:              ['__single__']
          Case 2 Individual:   ['insuredId::policyId', ...]
          Case 2 Collective:   ['insuredId']
          Case 3:              ['insuredId', ...]
          Case 4 Individual:   ['insuredId::policyId', ...]
          Case 4 Collective:   ['insuredId', ...]
        """
        multi   = pageConfig['multiplePolicies']
        insured = pageConfig['multipleClients']

        allInsured = [self.pagePolicies.mainInsured] + self.pagePolicies.additionalInsuredList

        keys = []

        if not multi and not insured:
            keys = ['__single__']

        elif multi and not insured:
            mainInsuredWidget = self.pagePolicies.mainInsured
            if financingType == 'Individual':
                for policy in mainInsuredWidget.policyList:
                    keys.append(f"{mainInsuredWidget.widgetId}::{policy.widgetId}")
            else:
                keys = [mainInsuredWidget.widgetId]

        elif not multi and insured:
            for widget in allInsured:
                keys.append(widget.widgetId)

        else:
            if financingType == 'Individual':
                for widget in allInsured:
                    for policy in widget.policyList:
                        keys.append(f"{widget.widgetId}::{policy.widgetId}")
            else:
                for widget in allInsured:
                    keys.append(widget.widgetId)

        return keys

    def _syncPaymentData(self, expectedKeys):
        """
        Synchronize self.paymentData against expectedKeys:
          - Add missing keys with empty quota list
          - Remove orphaned keys
          - Preserve existing keys with their quota data
        """
        orphaned = [k for k in self.paymentData if k not in expectedKeys]
        for key in orphaned:
            del self.paymentData[key]

        for key in expectedKeys:
            if key not in self.paymentData:
                self.paymentData[key] = {'cuotas': [], 'total': '0.00'}

        return self.paymentData

    def _structuralConfigChanged(self, currentMultiPolicies, currentMultiInsured):
        """
        Return True if the multiplePolicies or multipleClients selection has
        changed since the last time the user navigated to pageFinance.

        A structural change means the key schema of paymentData is no longer
        valid — any surviving entries refer to a different case layout and
        must be discarded entirely to avoid stale/orphaned data.

        Example of the bug this fixes:
          1. User sets Varias Polizas + Varios Asegurados → enters quotas
          2. User goes back, switches to Una Póliza → navigates to payment
          3. paymentData was partially wiped (only Case 3 key survived)
          4. User goes back again, switches to Varias Polizas → navigates to payment
          5. Without this check: the surviving Case 3 key is still in paymentData,
             loaded into the wrong table (mismatched key schema → ghost data)
          6. With this check: the structural change is detected → full wipe
        """
        currentConfig = (currentMultiPolicies, currentMultiInsured)
        if self.previousStructuralConfig is None:
            # First navigation to pageFinance — nothing to compare yet
            return False
        return self.previousStructuralConfig != currentConfig

    def goToPayment(self):
        """
        Collect page 3 data, sync paymentData store, and navigate to page 4.
        Reads quantity and financing config directly from pagePolicies.

        Wipe strategy (in priority order):
          1. Financing turned OFF (Si → No): full wipe — no data needed at all.
          2. Structural config changed (multi flags differ): full wipe — key
             schema changed so all existing keys are invalid for the new case.
          3. Neither: only orphaned keys removed, valid keys preserved.
        """
        self.formData.update(self.pagePolicies.getData())

        # hasPayment now comes from pagePolicies via getData()
        currentFinancingConfig = self.formData.get('hasPayment', 'No')

        quantityConfig = self.pagePolicies.getPolicyConfig()
        currentMultiPolicies = quantityConfig['multiplePolicies'] == 'Varias Polizas'
        currentMultiInsured  = quantityConfig['multipleClients']  == 'Si'

        pageConfig = {
            'multiplePolicies': currentMultiPolicies,
            'multipleClients':  currentMultiInsured,
        }

        currentFinancingType = self.pageFinance.getCurrentFinancingType()

        # --- Wipe rule 1: financing turned off ---------------------------------
        # If the user switched from Si to No, discard everything.
        if self.previousFinancingConfig == "Si" and currentFinancingConfig == "No":
            self.paymentData = {}

        # --- Wipe rule 2: structural config changed ----------------------------
        # If multiplePolicies or multipleClients changed, the key schema is
        # different — any surviving paymentData entries belong to the old case
        # and would be loaded into wrong tables (the ghost-data bug).
        # Full wipe ensures the user always starts with a clean slate that
        # matches the current insured/policy layout.
        elif self._structuralConfigChanged(currentMultiPolicies, currentMultiInsured):
            self.paymentData = {}

        # --- Update structural tracker before building expected keys -----------
        # Must be updated AFTER the change-detection check above, otherwise
        # the check always sees "no change" on the second navigation.
        self.previousStructuralConfig = (currentMultiPolicies, currentMultiInsured)

        expectedKeys = self._buildExpectedKeys(pageConfig, currentFinancingType)
        self._syncPaymentData(expectedKeys)

        self.pageFinance.setupPage(
            pageConfig=pageConfig,
            paymentData=self.paymentData,
            policiesPage=self.pagePolicies,
        )

        self.previousFinancingConfig = currentFinancingConfig
        self.previousFinancingType   = currentFinancingType
        self.pageStack.setCurrentIndex(3)

    def onPaymentBack(self):
        """Save current payment table data before navigating back to pagePolicies."""
        self.paymentData = self.pageFinance.collectPaymentData()
        self.pageStack.setCurrentIndex(2)

    def _onWipePaymentData(self):
        """
        Called when the user confirms a financing type change on pageFinance.
        Clears paymentData in app.py immediately so that if the user navigates
        back to pagePolicies and returns to pageFinance, setupPage() receives
        an empty dict and does not reload the stale quotas from the old type.
        """
        self.paymentData = {}

    def onResetPolicies(self):
        """
        Called when the user confirms the LIMPIAR action on pagePolicies.
        Wipes paymentData and all state trackers so the next navigation to
        pageFinance starts completely fresh — no orphaned keys possible.
        """
        # Full wipe of quota and annex data
        self.paymentData = {}
        self.annexData   = {}

        # Reset all state trackers to their initial values.
        # previousStructuralConfig=None makes goToPayment treat the next
        # visit as a first-time navigation (no change detection needed).
        self.previousFinancingConfig   = None
        self.previousFinancingType     = None
        self.previousStructuralConfig  = None

    def onGeneratePressed(self):
        """
        Called when GENERAR is pressed on pageFinance or pagePolicies.
        Collects current data then asks if the user wants annexes.
        'Sí' → navigate to PageAnnex.
        'No, solo la Carta de Despacho' → generate immediately.
        """
        # Collect fresh data from the current page before leaving
        if self.pageStack.currentWidget() == self.pageFinance:
            self.paymentData = self.pageFinance.collectPaymentData()
        self.formData.update(self.pagePolicies.getData())
        if self.pageStack.currentWidget() != self.pagePolicies:
            self.formData.update(self.pageStack.currentWidget().getData())
        self.formData['financiamiento'] = self.paymentData
        self._enrichFinanciamientoNames()

        # Determine origin for ATRAS on PageAnnex
        origin = ('finance' if self.pageStack.currentWidget() == self.pageFinance
                  else 'policies')

        from PySide6.QtWidgets import QMessageBox
        reply = CustomMessageBox.question(
            self,
            S["dlg_annex_question_title"],
            S["dlg_annex_question_body"],
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.goToAnnex(origin)
        else:
            self.onGenerateDocument()

    def goToAnnex(self, origin='finance'):
        """
        Navigate to PageAnnex.
        setupPage() is deferred via QTimer.singleShot(0) so it runs in the
        next event-loop cycle — this prevents a ghost overlay flash that occurs
        when goToAnnex() is called from inside QDialog.finished signal handling,
        before Qt has fully torn down the dialog and its overlay.
        """
        from PySide6.QtCore import QTimer
        _collected = self.pageAnnex.collectAnnexData()
        self.annexData = _collected
        # Merge collected cesiones into endorsementData — preserve keys not in current view
        _new_cesiones = _collected.get('cesiones', {})
        if _new_cesiones:
            self.endorsementData.update(_new_cesiones)
        elif not self.endorsementData:
            self.endorsementData = {}
        self.pageStack.setCurrentIndex(4)
        self._syncEndorsementData()
        QTimer.singleShot(0, lambda: self.pageAnnex.setupPage(
            self.pagePolicies, self.annexData,
            endorsementData=self.endorsementData, origin=origin
        ))

    def _saveEndorsementIfNeeded(self):
        """Save endorsementData from pageAnnex if it is the current page."""
        if self.pageStack.currentWidget() == self.pageAnnex:
            _c = self.pageAnnex.collectAnnexData()
            self.annexData = _c
            _ces = _c.get('cesiones', {})
            if _ces:
                self.endorsementData.update(_ces)

    def onAnnexBack(self, origin):
        """Save annex selections and navigate back to the origin page."""
        _collected  = self.pageAnnex.collectAnnexData()
        self.annexData = _collected
        _new_cesiones = _collected.get('cesiones', {})
        if _new_cesiones:
            self.endorsementData.update(_new_cesiones)
        if origin == 'finance':
            self.pageStack.setCurrentIndex(3)
        else:
            self.pageStack.setCurrentIndex(2)

    def onGenerateDocument(self):
        """
        Generate the Carta de Despacho and any selected annexes.
        Called from pageAnnex.signalGenerate or directly from onGeneratePressed
        when the user chooses 'No, solo la Carta de Despacho'.

        Flow when coming from PageAnnex:
          1. Collect annex selections.
          2. If Manual is Sí but no optional items → ask confirmation BEFORE saving.
             No  → return to pageAnnex, nothing is generated.
             Sí  → proceed with generation.
          3. Open save dialog for the Carta.
          4. Generate Manual and/or Garantías if selected.
          5. Show result summary.
        """
        import os
        from PySide6.QtWidgets import QMessageBox
        try:
            # Step 1: collect latest annex selections if coming from PageAnnex
            from_annex = self.pageStack.currentWidget() == self.pageAnnex
            if from_annex:
                self.annexData = self.pageAnnex.collectAnnexData()

            # Step 2: pre-flight check — Manual selected but no optional items
            # Must happen BEFORE the save dialog so the user can correct and retry
            # without any file having been created.
            manual_si   = self.annexData.get('manual_yes', False) and from_annex
            manualItems = self.pageAnnex.getManualItems() if (manual_si and from_annex) else []
            if manual_si and len(manualItems) <= 1:
                reply = CustomMessageBox.question(
                    self,
                    S["dlg_manual_no_items_title"],
                    S["dlg_manual_no_items_body"],
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    # Return to pageAnnex — nothing generated, user can correct
                    return
                # User confirmed — generate with Aspectos Generales only

            # Step 3: open save dialog for the Carta
            result = generateDocument(self.formData, self)

            if not result['success']:
                if result['error'] == 'Cancelado por usuario':
                    CustomMessageBox.warning(self, S["dlg_cancelled_title"],
                        S["dlg_cancelled_body"])
                else:
                    CustomMessageBox.critical(self, S["dlg_error_title"],
                        S["dlg_error_generate_body"].format(error=result['error']))
                return

            folder    = os.path.dirname(result['path'])
            _fmt = self.formData.get('outputFormat', 'word')
            _carta_key = (
                'doc_item_carta_pdf'  if _fmt == 'pdf'  else
                'doc_item_carta_both' if _fmt == 'both' else
                'doc_item_carta_docx'
            )
            generated = [S[_carta_key]]
            errors    = []

            # Step 4a: generate Manual if selected
            if manual_si and manualItems:
                manualPath   = os.path.join(folder, 'manual_siniestros.docx')
                manualResult = generateManualSiniestros(
                    self.formData, manualItems, manualPath
                )
                if manualResult['success']:
                    generated.append(S["doc_item_manual"])
                else:
                    errors.append(f"Manual: {manualResult['error']}")

            # Step 4b: generate Garantías if selected
            if self.annexData.get('guarantees_yes') and from_annex:
                guaranteesData = self.annexData.get('guarantees', {})
                if guaranteesData:
                    guaranteesPath   = os.path.join(folder, 'garantias_particulares.docx')
                    guaranteesResult = generateGuarantees(
                        self.formData, guaranteesData, guaranteesPath
                    )
                    if guaranteesResult['success']:
                        generated.append(S["doc_item_guarantees"])
                    else:
                        errors.append(f"Garantías: {guaranteesResult['error']}")

            # Step 4c: generate Cesiones de Derecho if endorsementType == Detallado
            if (self.formData.get('endorsementType') == 'Detallado'
                    and from_annex and self.endorsementData):
                cesionesPath   = os.path.join(folder, 'cesion_de_derechos.docx')
                cesionesResult = generateCesiones(
                    self.formData, self.endorsementData, cesionesPath
                )
                if cesionesResult['success']:
                    generated.append(S['doc_item_cesiones'])
                else:
                    errors.append(f"Cesiones: {cesionesResult['error']}")

            # Step 5: show result summary
            if errors:
                CustomMessageBox.warning(self, S['dlg_partial_title'],
                    S['dlg_partial_body'].format(
                        generated='\n'.join(generated),
                        errors='\n'.join(errors)))
            else:
                CustomMessageBox.information(self, S['dlg_success_title'],
                    S['dlg_success_body'].format(generated='\n'.join(generated)))

        except Exception as error:
            CustomMessageBox.critical(self, "Error", str(error))

    def _enrichFinanciamientoNames(self):
        """
        Add insuredName and policyBranch to each entry in formData['financiamiento'].

        Builds two lookup dicts from live pagePolicies widgets:
          insuredById  { widgetId: insuredName }
          policyById   { widgetId: policyBranch }

        Then walks formData['financiamiento'] and injects the resolved names.
        Keys follow the pattern set by pageFinance:
          'insuredId::policyId'  → Individual case (has both insured and policy)
          'insuredId'            → Collective/per-insured case (insured only)
        """
        financiamento = self.formData.get('financiamiento', {})
        if not financiamento:
            return

        # Build insured name lookup from all insured widgets
        insuredById = {}
        mainInsured = self.pagePolicies.mainInsured
        insuredById[mainInsured.widgetId] = mainInsured.insuredName.text()
        for insured in self.pagePolicies.additionalInsuredList:
            insuredById[insured.widgetId] = insured.insuredName.text()

        # Build policy branch lookup from all policy widgets
        policyById = {}
        for insured in [mainInsured] + self.pagePolicies.additionalInsuredList:
            for policy in insured.policyList:
                policyById[policy.widgetId] = policy.policyBranch.currentText()

        # Inject names into each financiamiento entry
        for key, entry in financiamento.items():
            if not isinstance(entry, dict):
                # entry is still a raw quota list from collectPaymentData —
                # wrap it so helpers.py can access cuotas and metadata
                entry = {'cuotas': entry, 'total': '0.00'}
                financiamento[key] = entry

            if '::' in key:
                # Individual case: key = insuredId::policyId
                insuredId, policyId = key.split('::', 1)
                entry['insuredName']  = insuredById.get(insuredId, '')
                entry['policyBranch'] = policyById.get(policyId,   '')
            else:
                # Collective / per-insured case: key = insuredId only
                entry['insuredName']  = insuredById.get(key, '')
                entry['policyBranch'] = ''




    def _syncEndorsementData(self):
        """
        Sync endorsementData against current pagePolicies widget keys.
        Preserves existing keys with data, adds empty dicts for new keys,
        removes orphaned keys. Same pattern as _syncPaymentData.
        """
        allInsured = [self.pagePolicies.mainInsured] + self.pagePolicies.additionalInsuredList
        expectedKeys = set()
        for insWidget in allInsured:
            for pol in insWidget.policyList:
                expectedKeys.add(f"{insWidget.widgetId}::{pol.widgetId}")

        # Remove orphaned keys
        for k in list(self.endorsementData.keys()):
            if k not in expectedKeys:
                del self.endorsementData[k]

        # Add missing keys with empty dict (no rows/groups yet)
        for k in expectedKeys:
            if k not in self.endorsementData:
                self.endorsementData[k] = {}

    def _onEndorsementDetailedOff(self):
        """Called when user switches away from Si(Detallado). If endorsementData has records, confirm."""
        hasRecords = any(
            v.get('rows') or v.get('groups')
            for v in self.endorsementData.values()
        )
        if not hasRecords:
            return
        from widgets import CustomMessageBox
        from PySide6.QtWidgets import QMessageBox
        reply = CustomMessageBox.question(
            self.mainWindow,
            S['dlg_detallado_clear_title'],
            S['dlg_detallado_clear_body'],
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.endorsementData = {}

    def _onCesionesReduce(self):
        """
        Called when user confirms a structure reduction (fewer policies/insured).
        Clears endorsementData entirely — orphaned keys from the old structure
        would cause stale data to appear in the new layout.
        The user confirmed the loss via the dialog in pagePolicies.
        """
        self.endorsementData = {}

    def onGlobalReset(self):
        """
        Global reset triggered by Limpiar on pageConfig.
        Resets all pages (except pageConfig, already reset by caller) and
        all central state. Navigates back to page 1.
        """
        from PySide6.QtCore import QDate
        from pagePolicies import InsuredWidget

        # ── pageUnit ──────────────────────────────────────────────────────────
        self.pageUnit.segmentGroup.setExclusive(False)
        for btn in self.pageUnit.segmentGroup.buttons():
            btn.setChecked(False)
        self.pageUnit.segmentGroup.setExclusive(True)
        self.pageUnit.units.clear()
        self.pageUnit.executives.clear()
        self.pageUnit.unitLeader.clear()
        self.pageUnit.executiveName.setText('-')
        self.pageUnit.executivePosition.setText('-')
        self.pageUnit.executiveEmail.setText('-')
        self.pageUnit.executiveMobile.setText('-')
        self.pageUnit.executivePhone.setText('-')
        self.pageUnit._currentExecutiveSignaturePath = ''
        self.pageUnit._currentLeaderSignaturePath    = ''
        self.pageUnit._currentLeaderEmail            = ''
        self.pageUnit._currentLeaderMobile           = ''
        self.pageUnit._loadSignatureIntoLabel('')

        # ── pagePolicies ──────────────────────────────────────────────────────
        pp = self.pagePolicies
        pp.blockSignalChanges = True
        for group in [pp.policyQuantity, pp.insuredQuantity,
                      pp.financingOptions, pp.currencyGroup]:
            group.setExclusive(False)
            for btn in group.buttons():
                btn.setChecked(False)
            group.setExclusive(True)
        pp.endorsement.setExclusive(False)
        pp.endorsementYes.setChecked(False)
        pp.endorsementDetailed.setChecked(False)
        pp.endorsementNo.setChecked(False)
        pp.endorsement.setExclusive(True)
        pp.endorsementData.setVisible(False)
        pp.endorsementBranch.clear()
        pp.endorsementBeneficiary.clear()
        pp.insurer.setCurrentIndex(0)
        pp.policyStartDate.setDate(QDate.currentDate())
        pp.policyEndDate.setDate(QDate.currentDate().addYears(1))
        pp.insuredArea.setVisible(False)
        pp.nextStep.setVisible(False)
        pp.generateDocument.setVisible(False)
        pp.addInsuredButton.setVisible(False)
        pp.clearAdditionalInsured()
        pp.pageConfig = {'allowMultipleInsured': False, 'allowMultiplePolicies': False}
        pp.mainInsured.deleteLater()
        pp.mainInsured = InsuredWidget(1, canDelete=False, allowMultiplePolicies=False)
        pp.insuredArea.layout().insertWidget(0, pp.mainInsured)
        pp.blockSignalChanges = False

        # ── pageFinance ───────────────────────────────────────────────────────
        self.pageFinance.clearContent()

        # ── pageAnnex ─────────────────────────────────────────────────────────
        # Rebuild with empty annexData so all selections are cleared
        self.annexData      = {}
        self.endorsementData = {}

        # ── Central state ─────────────────────────────────────────────────────
        self.formData                 = {}
        self.paymentData              = {}
        self.endorsementData          = {}
        self.previousFinancingConfig  = None
        self.previousFinancingType    = None
        self.previousStructuralConfig = None

        # Navigate to page 1
        self.pageStack.setCurrentIndex(0)


def main():
    """Application entry point."""
    # Show splash for at least 6 seconds, then close.
    # Works with both --onefile and --onedir PyInstaller builds.
    _splash_start = None
    try:
        import pyi_splash, time
        _splash_start = time.monotonic()
    except ImportError:
        pass

    app = QApplication(sys.argv)

    # Fusion style respects QSS 100% — windows11/windowsvista style overrides
    # many QSS rules for inputs, tables and buttons with its own renderer.
    app.setStyle("Fusion")

    # Apply theme palette — overrides OS dark/light mode so widgets
    # always render with the correct colors regardless of system settings.
    app.setPalette(build_palette(QSSA))

    # ── Load fonts dynamically from fonts/ folder ──────────────────────────────
    # All .ttf and .otf files found in fonts/ are registered automatically.
    # Qt groups them by family name — multiple weights of the same family
    # (e.g. Outfit-Regular.ttf, Outfit-Bold.ttf) are registered under one
    # family, making font-weight: 300/400/600/700 etc. resolve correctly in QSS.
    # To try a new font: drop its .ttf/.otf files into fonts/, update
    # QSSD['app_font_family'] to its exact registered name, restart the app.
    # The console output below shows the registered family name for each file.
    from pathlib import Path
    _fonts_dir = Path(resource_path("fonts"))
    _loaded_families = set()

    # ── Load all fonts and log registered family names ────────────────────────
    for _font_path in sorted(_fonts_dir.glob("*.ttf")) + sorted(_fonts_dir.glob("*.otf")):
        _fid = QFontDatabase.addApplicationFont(str(_font_path))
        if _fid >= 0:
            _families = QFontDatabase.applicationFontFamilies(_fid)
            _loaded_families.update(_families)
            print(f"  [font] {_font_path.name:<35} → {_families}")
        else:
            print(f"  [font] FAILED to load: {_font_path.name}")

    # ── Log all styles and weights per registered family ──────────────────────
    # For each family Qt registered, show every style it knows and the numeric
    # weight Qt assigned. Use this to decide:
    #   - If a weight appears under 'Poppins' → font-weight: 700 works in QSS
    #   - If it only appears under 'Poppins Medium' → use that name in font_family
    print()
    for _family in sorted(_loaded_families):
        print(f"  [font-db] '{_family}'")
        for _style in QFontDatabase.styles(_family):
            _weight = QFontDatabase.weight(_family, _style)
            _is_italic = QFontDatabase.italic(_family, _style)
            _italic_tag = " (italic)" if _is_italic else ""
            print(f"            style: {_style:<20} weight: {_weight}{_italic_tag}")
    print()

    # ── Apply global font + antialiasing ─────────────────────────────────────────
    # app_font_family in QSSD is the single source of truth for which typeface
    # the app uses. Changing it in QSSD updates both QSS (all widget selectors)
    # and this app.setFont() call on the next restart.
    # PreferAntialias: use antialiasing over speed.
    # PreferQuality:   allow hinting for better rendering at small sizes.
    #   (swap ForceOutline for PreferQuality if you see pixel artefacts)
    _app_font = QFont(QSSA['app_font_family'])
    _app_font.setStyleStrategy(
        QFont.StyleStrategy.PreferAntialias | QFont.StyleStrategy.PreferQuality
    )
    app.setFont(_app_font)

    window = MainApp()

    # Adaptive taskbar/window icon — selects based on Windows theme.
    # app_icon_dark.ico  → used when Windows is in Light theme (dark icon on light taskbar)
    # app_icon_light.ico → used when Windows is in Dark theme  (light icon on dark taskbar)
    # Falls back to app_icon_dark.ico if detection fails or files are missing.
    from PySide6.QtGui import QIcon
    import os as _os

    def _isWindowsDarkTheme():
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize'
            )
            val, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
            winreg.CloseKey(key)
            # AppsUseLightTheme == 0 → Dark mode; == 1 → Light mode
            return val == 0
        except Exception:
            return False

    _dark_theme = _isWindowsDarkTheme()
    _icon_name  = 'imgs/app_icon_light.ico' if _dark_theme else 'imgs/app_icon_dark.ico'
    _icon_path  = resource_path(_icon_name)
    if not _os.path.isfile(_icon_path):
        _icon_path = resource_path('imgs/app_icon_dark.ico')
    if _os.path.isfile(_icon_path):
        _appIcon = QIcon(_icon_path)
        app.setWindowIcon(_appIcon)
        window.setWindowIcon(_appIcon)
    # Close splash — enforce minimum 6-second display
    try:
        import pyi_splash, time
        if _splash_start is not None:
            elapsed = time.monotonic() - _splash_start
            remaining = 6.0 - elapsed
            if remaining > 0:
                time.sleep(remaining)
        pyi_splash.close()
    except Exception:
        pass

    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
