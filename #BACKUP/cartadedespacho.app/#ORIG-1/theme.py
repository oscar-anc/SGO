# coding: utf-8
"""
theme.py — Central theme and color management.

SVG icons in imgs/ have their stroke color hardcoded in the file.
To change icon colors, edit the SVG files in imgs/ directly.
No files are generated at runtime — SVGs ship as static assets.

Bold flags (5 only):
  text_primary_bold       — general app text (QLabel, etc.)
  card_header_text_bold   — CardWidget header title
  table_header_text_bold  — QTreeWidget / table header
  msg_titlebar_text_bold  — CustomMessageBox title bar
  msg_text_bold           — CustomMessageBox body text
All QPushButton variants are always bold — hardcoded in QSS, no flag needed.
"""

from PySide6.QtGui import QPalette, QColor

QSSD = {
    # =========================================================================
    # COLOUR VARIABLES
    # These map directly to CSS color values in build_qss().
    # Change a color here → every QSS rule that references it updates instantly.
    # =========================================================================

    # ── App background ────────────────────────────────────────────────────────
    # Used by: QWidget (global reset), NavBar, QScrollArea viewport
    'app_bg':                   '#f0f3f6',

    # ── Text ──────────────────────────────────────────────────────────────────
    # text_primary    → QLabel, QLineEdit, QComboBox, QCheckBox, QDateEdit (all pages)
    # text_on_dark    → labels on dark/navy backgrounds (card headers, titlebar)
    # text_disabled   → any widget with setEnabled(False)
    # input_placeholder → placeholder text in QLineEdit / QComboBox (all inputs)
    'text_primary':             '#4f5f6f',
    'text_on_dark':             '#FFFFFF',
    'text_disabled':            '#a1b1c2',
    'input_placeholder':        '#a1b1c2',
    'text_on_accent':           '#FFFFFF',   # text on accent-colored backgrounds (checked buttons)

    # ── Surfaces ──────────────────────────────────────────────────────────────
    # surface     → normal input/widget background (QLineEdit, QComboBox, QDateEdit)
    # surface_alt → read-only inputs, alternating table rows, calendar off-days
    'surface':                  '#FFFFFF',
    'surface_alt':              '#e1ecf7',

    # ── CSS keyword constants — all 'none', 'transparent', keyword values ────
    # These look fixed but ARE personalizable (e.g. change 'none' to a border).
    # Having them as variables means any QSS rule can be changed without
    # touching the template — only the QSSD needs updating.
    'css_none':                 'none',          # generic none value
    'css_transparent':          'transparent',   # transparent background/border
    'css_solid':                'solid',         # border-style solid
    'css_zero':                 '0',             # zero value (margin/padding/height/width)
    'css_outline_none':         'none',          # outline: none (focus ring removal)
    'css_image_none':           'none',          # image: none (remove arrow image)

    # ── Text alignment constants ──────────────────────────────────────────────
    'align_left':               'left',          # text-align: left
    'align_center':             'center',        # text-align: center
    'align_right':              'right',         # text-align: right

    # ── Font weight constants ─────────────────────────────────────────────────
    'fw_bold':                  'bold',          # font-weight: bold
    'fw_normal':                'normal',        # font-weight: normal

    # ── Specific border-side constants ────────────────────────────────────────
    # 'none' borders for sides that intentionally have no border
    'border_top_none':          'none',          # border-top: none (e.g. QTabWidget::pane)
    'border_bottom_none':       'none',          # border-bottom: none (e.g. active tab)
    'border_left_none':         'none',          # border-left: none
    'border_right_none':        'none',          # border-right: none

    # ── Structural zero values ────────────────────────────────────────────────
    'margin_zero':              '0',             # margin: 0
    'tab_pane_top':             '-1px',          # QTabWidget::pane top offset (overlap fix)

    # ── Aliases & convenience keys ────────────────────────────────────────────
    # These are aliases used in QSS rules — set them to match their source value
    'card_bg':                  '#FFFFFF',   # CardWidget body/content background → matches card_body_bg
    'border_color':             '#C8D0D8',   # Generic border color → matches border_input
    'text_muted':               '#888888',   # Muted text (gray) — manual-fixed buttons, hints
    'card_header_min_height':   '36',        # #CardHeader QSS min-height (px string)

    # ── Input borders ─────────────────────────────────────────────────────────
    # border_input       → QLineEdit, QComboBox, QDateEdit at rest
    # border_input_hover → same widgets on mouse hover
    # border_input_focus → same widgets when focused (clicked / keyboard)
    # border_strong      → #CardBody border, strong horizontal dividers
    # border_abstractitemview → left/right border of QComboBox popup list
    'border_input':             '#C8D0D8',
    'border_input_hover':       '#33536d',
    'border_input_focus':       '#33536d',
    'border_strong':            '#475564',
    'border_abstractitemview':  '#96989a',

    # ── Title bar — main window ────────────────────────────────────────────────
    # titlebar_bg             → CustomTitleBar background (app.py)
    # titlebar_btn_text       → icon color for Min/Max/Close at rest
    # titlebar_btn_hover_bg   → Min/Max button hover background
    # titlebar_btn_pressed_bg → Min/Max button pressed background
    # titlebar_close_hover_bg / pressed_bg → Close button (red family)
    'titlebar_bg':              '#4f5f6f',
    'titlebar_btn_text':        '#FFFFFF',
    'titlebar_btn_hover_bg':    '#59c2e6',
    'titlebar_btn_pressed_bg':  '#3aaac8',
    'titlebar_close_hover_bg':  '#fc4c7a',
    'titlebar_close_pressed_bg':'#d93060',

    # ── CardWidget ────────────────────────────────────────────────────────────
    # card_header_bg     → #CardHeader background (navy bar at top of every card)
    #                      Used in: pagePolicies, pageFinance, pageAnnex, Dialogs
    # card_header_text   → title text inside the navy header
    # card_header_toggle → chevron/accordion icon color in header
    # card_body_bg       → #CardBody background (white content area)
    # card_body_border   → #CardBody border (all 4 sides, matches header for unity)
    # insured_group_text → InsuredGroupCard header text (inverted — dark on light)
    'card_header_bg':           '#4f5f6f',
    'card_header_text':         '#FFFFFF',
    'card_header_toggle':       '#FFFFFF',

    # ── Accordion button states (on navy CardWidget header) ──────────────────
    # QPushButton[role='accordion'] — collapse/expand toggle in all card headers
    'accordion_normal_border':  'rgba(255,255,255,60)',   # border at rest
    'accordion_hover_bg':       'rgba(255,255,255,40)',   # background on hover
    'accordion_hover_border':   'rgba(255,255,255,120)',  # border on hover (more opaque)
    'accordion_border_css':     '1px solid rgba(255,255,255,60)',  # full border shorthand
    'card_body_bg':             '#FFFFFF',
    'card_body_border':         '#4f5f6f',
    'card_body_border_top':     'none',
    'insured_group_text':       '#4f5f6f',

    # ── Card header inputs (QLineEdit / QComboBox embedded in navy header) ────
    # These override the standard input styles for widgets that live inside
    # the navy CardWidget header — e.g. insuredName in pagePolicies headers,
    # policyBranch QComboBox in policy card headers, endorsee combo in
    # GroupEditor (Cesiones dialog).
    #
    # bg           → transparent so the navy header shows through
    # text         → white to contrast against navy
    # placeholder  → semi-transparent white
    # border       → none (no box around the input in the header)
    # font_size    → CSS font-size for the embedded input text
    # padding      → CSS padding inside the embedded input
    # min_height   → px integer — overrides standard input_min_height
    'card_header_input_bg':          'transparent',
    'card_header_input_text':        '#FFFFFF',
    'card_header_input_placeholder': 'rgba(255,255,255,140)',
    'card_header_input_border':      'none',
    'card_header_input_font_size':   '9pt',
    'card_header_input_padding':     '2px 4px',
    'card_header_input_min_height':  '24',        # px integer string

    # ── RadioButton ───────────────────────────────────────────────────────────
    # Used by: pageConfig (letter type), pagePolicies (currency), pageFinance (type selector)
    'radio_bg':                 '#FFFFFF',
    'radio_border':             '#33536d',
    'radio_hover':              '#59c2e6',
    'radio_checked':            '#59c2e6',

    # ── Accent ────────────────────────────────────────────────────────────────
    # accent      → primary brand color: checked state, hover highlights, badges
    # accent_dark → darker variant used on hover/pressed over accent bg
    # accent_light → very light tint for hover on white backgrounds
    'accent':                   '#59c2e6',
    'accent_dark':              '#3aaac8',
    'accent_light':             '#e8f4fd',

    # ── Button — Primary (generic navy) ───────────────────────────────────────
    # Used by: any QPushButton without a specific role
    'btn_primary_bg':           '#4f5f6f',
    'btn_primary_hover':        '#59c2e6',
    'btn_primary_text':         '#FFFFFF',

    # ── Button — SIGUIENTE (next page navigation) ──────────────────────────────
    # Located in NavBar at the bottom of every page
    'btn_next_bg':              '#4f5f6f',
    'btn_next_hover':           '#3aaac8',
    'btn_next_text':            '#FFFFFF',

    # ── Button — GENERAR (generate Word/PDF document) ─────────────────────────
    # Located in NavBar of pageAnnex (final step)
    'btn_generar_bg':           '#59c2e6',
    'btn_generar_hover':        '#3aaac8',
    'btn_generar_text':         '#FFFFFF',

    # ── Button — AGREGAR (add quota row, add annex item) ──────────────────────
    # Used in pageFinance (add quota), pageAnnex (add item)
    'btn_agregar_bg':           '#59c2e6',
    'btn_agregar_hover':        '#3aaac8',
    'btn_agregar_text':         '#FFFFFF',

    # ── Button — Action (generic accent — backward compat alias) ──────────────
    'btn_action_bg':            '#59c2e6',
    'btn_action_hover':         '#3aaac8',
    'btn_action_text':          '#FFFFFF',

    # ── Button — ATRAS (back navigation) ──────────────────────────────────────
    # Located in NavBar on all pages except pageConfig
    'btn_back_bg':              '#bacada',
    'btn_back_hover':           '#a1b1c2',
    'btn_back_text':            '#4f5f6f',

    # ── Button — Excel import ─────────────────────────────────────────────────
    # Used in: Cesiones dialog (import endorsements from Excel)
    'btn_excel_bg':             '#4caf7d',
    'btn_excel_border':         '#217346',
    'btn_excel_text':           '#FFFFFF',
    'btn_excel_hover_bg':       '#217346',
    'btn_excel_hover_text':     '#FFFFFF',

    # ── Button — Danger (LIMPIAR, ELIMINAR, QUITAR) ────────────────────────────
    # Outline danger style — used for destructive actions in all pages
    'btn_danger_bg':            'transparent',
    'btn_danger_border':        '#fc4c7a',
    'btn_danger_text':          '#fc4c7a',
    'btn_danger_hover_bg':      '#fc4c7a',
    'btn_danger_hover_text':    '#FFFFFF',

    # ── Button — AGREGAR PÓLIZA / ASEGURADO ───────────────────────────────────
    # Used in pagePolicies: add another policy or insured
    'btn_add_sub_bg':           '#4f5f6f',
    'btn_add_sub_hover':        '#59c2e6',
    'btn_add_sub_text':         '#FFFFFF',

    # ── Button — QUITAR (icon trash button in card headers) ───────────────────
    # btn_quitar_svg_*  → icon-only trash button (red pill style, pagePolicies headers)
    # btn_quitar_*      → text danger button (outline style, card bodies)
    'btn_quitar_svg_bg':        '#e05570',
    'btn_quitar_svg_hover_bg':  '#c0304a',
    'btn_quitar_bg':            'transparent',
    'btn_quitar_border':        '#fc4c7a',
    'btn_quitar_text':          '#fc4c7a',
    'btn_quitar_hover_bg':      '#fc4c7a',
    'btn_quitar_hover_text':    '#FFFFFF',

    # ── QTreeWidget / QTableWidget header ─────────────────────────────────────
    # Used in: pageUnit (tree), Cesiones view dialog (table), GroupEditor (table)
    'tree_header_bg':           '#4f5f6f',
    'tree_header_text':         '#FFFFFF',
    'table_header_bg':          '#4f5f6f',
    'table_header_text':        '#FFFFFF',

    # ── Table rows & selection ─────────────────────────────────────────────────
    # Used in: QTreeWidget (pageUnit), QTableWidget (GroupEditor, Cesiones view)
    'table_border':             '#C8D0D8',
    'table_row_bg':             '#FFFFFF',
    'table_row_alt':            '#f8fafc',
    'table_row_hover':          '#e1ecf7',
    'table_row_selected_bg':    '#59c2e6',
    'table_row_selected_text':  '#FFFFFF',
    'tree_selected_bg':         '#59c2e6',
    'tree_selected_text':       '#FFFFFF',
    'table_row_selected':       '#59c2e6',
    'border_table':             '#C8D0D8',
    'table_bg':                 '#FFFFFF',

    # ── QComboBox popup dropdown ───────────────────────────────────────────────
    # Affects the floating list that appears when a QComboBox is opened
    'combo_dropdown_bg':        '#FFFFFF',
    'combo_dropdown_border':    '#96989a',
    'combo_item_hover_bg':      '#59c2e6',
    'combo_item_hover_text':    '#FFFFFF',
    'combo_item_selected_bg':   '#4f5f6f',
    'combo_item_selected_text': '#FFFFFF',

    # ── Scrollbar ─────────────────────────────────────────────────────────────
    # Global QScrollBar style — applies to all scroll areas in the app
    'scrollbar_track':          '#f0f3f6',
    'scrollbar_handle':         '#ced6dc',
    'scrollbar_hover':          '#959fa9',
    'scrollbar_pressed':        '#4f5f6f',

    # ── QCalendarWidget ───────────────────────────────────────────────────────
    # Used in: pageConfig (date fields)
    'cal_nav_bg':               '#4f5f6f',   # month/year navigation bar
    'cal_nav_text':             '#FFFFFF',
    'cal_nav_arrow_hover_bg':  '#3aaac8',   # calendar nav arrow hover bg
    'cal_nav_arrow_hover':      '#3aaac8',

    'cal_subheader_bg':         '#59c2e6',   # weekday labels row (Mon-Sun)
    'cal_day_bg':               '#FFFFFF',
    'cal_day_alt_bg':           '#e1ecf7',
    'cal_day_text':             '#4f5f6f',
    'cal_other_month_text':     '#a1b1c2',   # days outside current month
    'cal_hover_border':         '#4f5f6f',
    'cal_hover_bg':             '#e8f0f8',
    'cal_selected_bg':          '#59c2e6',
    'cal_selected_text':        '#FFFFFF',
    'cal_grid':                 '#dce6f0',   # grid lines between day cells
    'cal_min_height':           '220',       # QCalendarWidget minimum height (px)
    'cal_arrow_size':           '16',        # calendar icon width/height (px)

    # ── CustomMessageBox ──────────────────────────────────────────────────────
    # msg_titlebar_* → colored header bar at top of message dialog
    # msg_body_*     → white content area
    # msg_btn_*      → confirm/cancel buttons inside the dialog
    'msg_titlebar_bg':          '#4f5f6f',
    'msg_titlebar_text':        '#FFFFFF',
    'msg_close_hover':          '#fc4c7a',
    'msg_body_bg':              '#FFFFFF',
    'msg_frame_bg':             '#FFFFFF',
    'msg_frame_border':         '#dce6f0',
    'msg_border':               '#475564',
    'msg_text':                 '#4f5f6f',
    'msg_btn_primary_bg':       '#59c2e6',
    'msg_btn_primary_hover':    '#3aaac8',
    'msg_btn_primary_text':     '#FFFFFF',
    'msg_btn_secondary_bg':     'transparent',
    'msg_btn_secondary_border': '#475564',
    'msg_btn_secondary_text':   '#4f5f6f',
    'msg_btn_secondary_hover':  '#e1ecf7',

    # ── CustomMessageBox — variant accent colors ───────────────────────────────
    # Each variant changes the titlebar bg and the left border of MsgFrame
    # warning  → amber (non-critical alerts)
    # error    → red (failures, data loss warnings)
    # info     → blue (informational dialogs)
    # question → neutral navy (confirmations, yes/no questions)
    'msg_header_warning':       '#e07b00',
    'msg_border_warning':       '#e07b00',
    'msg_header_error':         '#c0293e',
    'msg_border_error':         '#c0293e',
    'msg_header_info':          '#2c7da0',
    'msg_border_info':          '#2c7da0',
    'msg_header_question':      '#4f5f6f',
    'msg_border_question':      '#475564',

    # ── Dim overlay ───────────────────────────────────────────────────────────
    # Semi-transparent layer shown over the app when a CustomMessageBox is open
    # overlay_opacity → 0 (transparent) to 255 (opaque), stored as string
    'overlay_color':            '#000000',
    'overlay_opacity':          '120',

    # ── QCheckBox indicator ───────────────────────────────────────────────────
    # Used on all pages where QCheckBox appears (pagePolicies, pageAnnex, etc.)
    'checkbox_border':          '#33536d',
    'checkbox_disabled_border': '#a1b1c2',
    'checkbox_bg':              '#FFFFFF',
    'checkbox_checked_bg':      '#59c2e6',
    'checkbox_checked_border':  '#3aaac8',
    'checkbox_hover_border':    '#59c2e6',
    'checkbox_disabled_bg':     '#e0e8f0',

    # ── Toolbar buttons (Garantías editor: Bold/Italic/Underline/List/Clear) ──
    # Used in: GuaranteesCard body (pageAnnex) and GuaranteesTableCard edit dialog
    'toolbar_button_bg':        '#e1ecf7',
    'toolbar_button_text':      '#4f5f6f',   # icon color — passed to SVG functions
    'toolbar_button_hover':     '#c8d8e8',
    'toolbar_button_border':    '#C8D0D8',
    'toolbar_btn_width':        '28',        # button width (integer string, no px)
    'toolbar_btn_height':       '28',        # button height (integer string, no px)
    'toolbar_btn_icon_size':    '14',        # SVG icon size (integer string, no px)

    # ── Format selector buttons (pageConfig: Word / PDF / Both) ───────────────
    # Used in the output format section of pageConfig
    # format_btn_icon_h   → SVG icon height inside each button
    # format_btn_icon_gap → gap between the two icons in the "Both" button
    # format_btn_text_gap → gap between icons and label text
    # format_btn_row_spacing → spacing between the three buttons
    'format_btn_icon_h':         22,
    'format_btn_icon_gap':       4,
    'format_btn_text_gap':       6,
    'format_btn_row_spacing':    12,
    'format_btn_min_width':      '110',      # CSS min-width value
    'format_btn_padding':        '6px 14px', # CSS padding

    # ── QTabWidget (Cesiones dialog — Individual mode) ─────────────────────────
    # Tabs appear above each endorsee's GroupEditor
    # tab_header_height  → height of each tab pill
    # tab_border_radius  → top corners of each tab
    # tab_content_margins → pane content margins (tuple, used in Python)
    'tab_header_height':         32,
    'tab_border_radius':         '4px 4px 0 0',
    'tab_content_margins':       (0, 0, 0, 0),

    # ── NavBar ────────────────────────────────────────────────────────────────
    # Horizontal bar at bottom of every page (ATRAS / SIGUIENTE / GENERAR / LIMPIAR)
    'nav_bg':                   '#f0f3f6',
    'nav_height':               '56',        # px integer string
    'nav_border_width':         '1px',
    'nav_border_color':         '#dce6f0',
    'selection_bg':             '#59c2e6',

    # ── Logo path ─────────────────────────────────────────────────────────────
    # Relative path to the SVG/PNG logo shown in the main titlebar
    # Change to 'imgs/logo_midnight.svg' for dark logos
    'logo_path':                'imgs/logo_white.svg',

    # ── Instruction / hint text ───────────────────────────────────────────────
    # #InstructionLabel — small muted labels (e.g. "Paste here", copy hints)
    'instruction_text':         '#8a9bae',
    'text_instruction':         '#6b7c8d',
    'cal_icon_size':            '16',        # calendar arrow icon size (px, str)
    'nav_btn_icon_size':        '30',        # NavBar button icon area (px, str)
    'tab_margin_right':         '2px',       # QTabBar tab right margin
    'tab_inactive_margin_top':  '2px',       # QTabBar inactive tab top offset
    'margin_groupbox_title':    '14px',      # QGroupBox title bar top margin-top
    'groupbox_padding_top':     '3px',       # QGroupBox top padding
    'groupbox_label_left':      '12px',      # QGroupBox title left offset
    'groupbox_label_top':       '-1px',      # QGroupBox title top offset
    'msg_box_min_height':       '36',        # #MsgBtnPrimary/#MsgBtnSecondary min-height

    # =========================================================================
    # TYPOGRAPHY VARIABLES (QSS)
    # =========================================================================

    # ── Font family & size ────────────────────────────────────────────────────
    # font_family    → applied globally to QWidget — single name, no fallback list
    # font_size_base → inherited by all widgets unless overridden below
    'font_family':              'Open Sans',
    'font_size_base':           '10pt',
    'font_size_button':         '9pt',   # QPushButton label
    'font_size_small':          '9pt',   # tree headers, calendar header, tooltip
    'font_size_instruction':    '8pt',   # #InstructionLabel hints
    'font_size_large':          '11pt',  # Large text — msg titlebar, section headers
    'font_size_nav':            '12px',  # NavBar button font size

    # ── Font weight flags ─────────────────────────────────────────────────────
    # Use 'bold' or 'normal'. Controls font-weight in generated QSS.
    'text_primary_bold':        'normal',  # general app labels
    'card_header_text_bold':    'bold',    # CardWidget header title
    'table_header_text_bold':   'bold',    # QTreeWidget / QTableWidget header
    'msg_titlebar_text_bold':   'bold',    # CustomMessageBox titlebar
    'msg_text_bold':            'normal',  # CustomMessageBox body text
    'btn_primary_font_weight':  'bold',    # all QPushButton variants
    'cal_tool_font_weight':     'bold',    # QCalendarWidget tool buttons
    'cal_header_font_weight':   'bold',    # QCalendarWidget weekday header
    'toolbar_btn_font_weight':  'normal',  # B/I/U/List/Clear toolbar buttons
    'msg_btn_font_weight':      'bold',    # #MsgBtnPrimary / Secondary
    'groupbox_font_weight':     'bold',    # QGroupBox title

    # =========================================================================
    # BORDER VARIABLES (QSS)
    # All values are CSS strings: '1px', '2px', '0px', etc.
    # =========================================================================

    # ── Border widths ─────────────────────────────────────────────────────────
    # Each key targets a specific widget family in build_qss()
    'border_width_input':       '1px',   # QLineEdit — all pages
    'border_width_combo':       '1px',   # QComboBox main box — all pages
    'border_width_combo_dropdown': '1px',# QComboBox popup side borders
    'border_width_date':        '1px',   # QDateEdit — pageConfig
    'border_width_card':        '1px',   # #CardBody and QGroupBox borders
    'border_width_table':       '1px',   # QTreeWidget row & header borders
    'border_width_radio':       '1px',   # QRadioButton::indicator
    'border_width_checkbox':    '1px',   # QCheckBox::indicator
    'border_width_toolbar':     '1px',   # #ToolbarButton (Garantías editor)
    'border_width_msg':         '1px',   # #MsgFrame, #MsgBtnSecondary
    'border_width_msg_variant': '2px',   # warning/error/info left accent border
    'border_width_calendar':    '1px',   # QCalendarWidget outer border

    # ── Border radius ─────────────────────────────────────────────────────────
    # CSS shorthand supported: '4px', '4px 4px 0 0', etc.
    'radius_input':             '2px',   # QLineEdit
    'radius_combo':             '2px',   # QComboBox
    'radius_date':              '2px',   # QDateEdit
    'radius_button':            '2px',   # QPushButton (all variants)
    'radius_btn':               '4px',   # QPushButton generic (newer alias)
    'radius_card':              '0px',   # QGroupBox, #CardBody
    'radius_checkbox':          '1px',   # QCheckBox::indicator
    'radius_msg':               '0px',   # #MsgFrame, #MsgBtnPrimary/Secondary
    'radius_toolbar':           '2px',   # #ToolbarButton
    'radius_textedit':          '2px',   # QTextEdit (Garantías editor)
    'radius_msg_frame':         '0px',   # #MsgFrame outer border
    'radius_msg_titlebar':      '0px',   # #MsgTitleBar corners
    'radius_msg_body':          '0px',   # #MsgBody corners
    'radius_msg_btn':           '0px',   # #MsgBtnPrimary / Secondary
    'radius_table':             '0px',   # QTreeWidget outer border

    # ── Padding (QSS) ─────────────────────────────────────────────────────────
    # CSS shorthand: '7px 10px' = top/bottom 7, left/right 10
    'padding_input':            '7px 10px',   # QLineEdit / QComboBox / QDateEdit
    'padding_button':           '7px 16px',   # QPushButton (generic)
    'padding_msg_btn':          '7px 20px',   # CustomMessageBox buttons
    'padding_toolbar_btn':      '3px 10px',   # B/I/U/List/Clear toolbar buttons
    'padding_card_body':        '12px',       # #CardBody inner padding
    'padding_nav_btn':          '0 12px',     # NavBar button (SIGUIENTE/ATRAS/etc) padding
    'padding_endtable_btn':     '0px 12px',   # EndorsementTableCard action button padding
    'padding_combo_header':     '0px 8px',
    'padding_header_vert':      '0px 1px',   # QHeaderView vertical section padding
    'padding_zero_h':           '0px',       # Zero padding (intentional — buttons/icons)    # QComboBox in card header (no top/bottom)
    'padding_tab':              '4px 14px',   # QTabBar::tab padding
    'padding_header_sec':       '4px 8px',    # QHeaderView section (normal columns)
    'padding_header_section':   '4px 6px',    # QHeaderView section (last/only column)
    'padding_tree_cell':        '2px 4px',    # QTreeWidget::item cell padding
    'padding_card_header_h':    '6px',        # CardHeader horizontal padding between elements
    'padding_groupbox':         '14px 12px 12px 12px',  # QGroupBox body content padding
    'padding_groupbox_top':     '3px',        # QGroupBox title label padding
    'padding_tree_item':        '5px 8px',    # QTreeWidget::item row
    'padding_tree_header':      '7px 10px',   # QTreeWidget header section
    'padding_msg_body':         '16px',       # CustomMessageBox body outer padding
    'padding_btn':              '4px 12px',   # alternate button padding
    'padding_combo':            '4px 8px',    # alternate combo padding

    # =========================================================================
    # SIZING VARIABLES (QSS)
    # Integer-string values (e.g. '28') used in QSS min-height / min-width.
    # No 'px' suffix in the value — added in the QSS template as needed.
    # =========================================================================

    # ── Input sizing ──────────────────────────────────────────────────────────
    # Applies to: QLineEdit, QComboBox, QDateEdit across all pages
    'input_min_height':         '28',    # min-height for standard inputs
    'input_height':             '20',    # fixed height (legacy — some inputs use this)
    'combo_min_height':         '28',    # QComboBox min-height
    'combo_arrow_width':        '24',    # width of the dropdown arrow area
    'combo_item_height':        '28',    # height of each item in the dropdown
    'combo_arrow_size':         '14',    # QComboBox dropdown arrow width/height (px)
    'combo_popup_padding':      '2px',   # QComboBox popup item padding
    'scrollbar_margin':         '1px',   # QScrollBar handle margin (separation from track)
    'radius_zero':              '0px',   # Zero border-radius (sharp corners)
    'radius_tab_inactive':      '2px',   # QTabBar inactive tab border-radius (bottom corners visible)
    'combo_popup_padding_item': '2px 8px',  # QComboBox popup QListView item padding

    # ── Button sizing ──────────────────────────────────────────────────────────
    'btn_min_height':           '30',    # QPushButton min-height (all variants)
    'btn_min_width':            '76',    # QPushButton min-width
    'msg_btn_min_height':       '34',    # CustomMessageBox button min-height
    'btn_border_width':         '1px',   # button border width
    'btn_danger_min_width':     '70',    # danger/quitar button min-width
    'card_header_sel_bg':       'rgba(255,255,255,80)', # card header input selection bg
    'radius_table_header':      '2px',   # QTabBar tab border-radius (inactive)
    'min_width_dialog_btn':     '100px', # dialog close/save/confirm button min-width
    'cesiones_btn_height':      '26',    # action buttons inside Cesiones tables
    'btn_endtable_size':        '22',    # EndorsementTableCard header icon buttons
    'btn_quitar_size':          '26',    # BtnQuitar trash icon button
    'btn_dialog_topbar_height': '30',    # Cesiones dialog top bar buttons

    # ── QTextEdit (Garantías editor) ───────────────────────────────────────────
    'textedit_bg':              '#FFFFFF',
    'textedit_border':          '#C8D0D8',

    # ── Misc QSS ──────────────────────────────────────────────────────────────
    'titlebar_height':          '32',    # legacy QSS value (CustomDialog)
    'titlebar_btn_width':       '32',    # legacy QSS value
    'titlebar_text':            '#FFFFFF',

    # ── Radio button QSS sizing ────────────────────────────────────────────────
    'radio_spacing':            '12',
    'radio_border_width':       '2',
    'radio_checked_bg':         '#4f5f6f',
    'radio_checked_border':     '#4f5f6f',
    'radio_hover_border':       '#59c2e6',

    # ── Checkbox QSS sizing ───────────────────────────────────────────────────
    'checkbox_spacing':         '8',
    'checkbox_border_width':    '2',
    'checkbox_radius':          '3',

    # ── Table QSS sizing ──────────────────────────────────────────────────────
    'table_row_height':         '28',
    'table_header_height':      '28',
    'table_header_divider':     '#475564',
    'table_vertical_header_width': '28',

    # ── Widget QSS sizes ──────────────────────────────────────────────────────
    'checkbox_size':            '15',    # QCheckBox::indicator size
    'radio_size':               '16',    # QRadioButton::indicator size
    'radio_radius':             '8px',   # QRadioButton::indicator border-radius (half of radio_size)
    'scrollbar_width':          '10',    # QScrollBar width/height
    'scrollbar_handle_radius':  '5px',   # QScrollBar handle border-radius
    'scrollbar_handle_hover':   '#959fa9',  # handle hover color (= scrollbar_hover)
    'margin_scrollbar':         '1px',      # handle margin from track
    'scrollbar_handle_min':     '30',    # QScrollBar handle min-height/width (px)
    'card_header_height':       '36',    # #CardHeader min+max height
    'msg_titlebar_height':      '40',    # #MsgTitleBar min+max height

    # ── CustomMessageBox radius (per-component free CSS) ──────────────────────
    # Supports full CSS shorthand: '10px', '10px 10px 0 0', etc.

    # =========================================================================
    # LAYOUT & SIZE VARIABLES (Python)
    # Used directly in Python layouts — NOT in build_qss().
    # Tuples → unpack with *QSSA['key']
    # Integers → use directly as px values
    # =========================================================================

    # ── Zero-margin/spacing wrappers ──────────────────────────────────────────
    # Use for structural containers that should have no visual padding
    'margins_zero':             (0, 0, 0, 0),
    'spacing_zero':             0,

    # ── NavBar layout (bottom of every page) ──────────────────────────────────
    'margins_nav':              (16, 8, 16, 8),
    'spacing_nav':              8,

    # ── CardWidget header layout ───────────────────────────────────────────────
    # Controls the QHBoxLayout inside every #CardHeader bar
    'margins_card_header':      (12, 6, 10, 6),
    'spacing_card_header':      6,

    # ── CardWidget body layout ─────────────────────────────────────────────────
    'margins_card_body':        (10, 10, 10, 10),
    'spacing_card_body':        8,

    # ── Inline rows (date+currency, qty rows) ─────────────────────────────────
    'margins_inline_row':       (0, 0, 0, 0),
    'spacing_inline_row':       8,

    # ── App window ────────────────────────────────────────────────────────────
    'app_min_width':            700,
    'app_min_height':           500,
    'margins_app_root':         (0, 0, 0, 0),
    'spacing_app_root':         0,

    # ── CustomTitleBar (main window) ──────────────────────────────────────────
    # titlebar_logo_size   → (width, height) of the logo QLabel in the titlebar
    # titlebar_fixed_height → height of the entire titlebar bar (px)
    # dialog_titlebar_height → height for CustomDialog and messagebox titlebars
    'titlebar_logo_size':       (28, 28),
    'titlebar_fixed_height':    40,
    'dialog_titlebar_height':   30,
    'margins_titlebar_outer':   (0, 0, 0, 0),
    'margins_titlebar_inner':   (0, 0, 0, 0),
    'spacing_titlebar':         0,

    # ── CustomMessageBox layout ───────────────────────────────────────────────
    'msg_box_min_width':        380,
    'margins_msg_titlebar':     (16, 8, 12, 8),
    'msg_close_btn_size':       (24, 24),
    'margins_msg_body':         (24, 20, 24, 8),
    'spacing_msg_body':         20,
    'margins_msg_buttons':      (0, 0, 0, 0),
    'spacing_msg_buttons':      8,
    'msg_body_gap':             4,

    # ── CardWidget base layout ─────────────────────────────────────────────────
    # card_header_fixed_height → Python setMinimumHeight / setFixedHeight for #CardHeader
    # card_toggle_fixed_size   → (w, h) for the accordion QPushButton
    'card_header_fixed_height': 32,
    'card_toggle_fixed_size':   (26, 26),
    'card_toggle_size_px':      '26px',  # accordion button size for QSS (card_toggle_fixed_size[0])
    'card_body_min_height':     174,
    'spacing_card_header_base': 6,
    'spacing_card_body_base':   8,

    # ── EndorsementTableCard (Cesiones card in pageAnnex) ─────────────────────
    # Header bar in each cesiones card. Action buttons (Ver/Editar/Import)
    # are sized by endtable_btn_fixed_size.
    'endtable_header_height':   32,
    'endtable_btn_fixed_size':  (26, 26),
    'endtable_dialog_min_size': (760, 500),   # edit dialog min size
    'endtable_view_min_size':   (920, 620),   # view dialog min size
    'endtable_topbar_height':   30,
    'endtable_col_header_width':28,
    'margins_endtable_header':  (12, 4, 8, 4),
    'spacing_endtable_header':  8,
    'spacing_endtable_groups':  8,
    'spacing_endtable_topbar':  8,
    'spacing_endtable_topbar2': 6,

    # ── GroupEditor (Cesiones edit dialog inner editor) ────────────────────────
    # The _GroupEditor widget inside the Cesiones edit dialog.
    # Each "tab" in Individual mode or single editor in Agrupado mode.
    # group_editor_accordion_size → chevron button in GroupEditor header
    # group_editor_header_height  → GroupEditor header bar height
    # group_editor_combo_max_width → endorsee name combo max width
    # group_editor_table_height   → row height in the data table
    # group_editor_table_min_h    → minimum height of the data table
    'group_editor_accordion_size':  (28, 28),
    'group_editor_header_btn_size': (28, 28),
    'group_editor_header_height':   36,
    'group_editor_combo_max_width': 400,
    'group_editor_col_input_width': 350,
    'group_editor_col_input_width2':350,
    'group_editor_gear_size':       (28, 28),
    'group_editor_col_btn_size':    (22, 22),
    'group_editor_config_padding':  (6, 6, 6, 6),
    'group_editor_config_spacing':  6,
    'group_editor_btn_height':      26,
    'group_editor_table_height':    34,
    'group_editor_table_min_h':     220,
    'margins_group_editor':         (0, 0, 0, 8),
    'spacing_group_editor':         6,
    'margins_group_editor_input':   (0, 0, 0, 0),
    'spacing_group_editor_input':   4,
    'spacing_group_editor_row5':    4,
    'spacing_group_editor_inner':   6,

    # ── CustomDialog (dialog with custom titlebar) ────────────────────────────
    'margins_dialog_titlebar':  (12, 0, 0, 0),
    'spacing_dialog_titlebar':  0,
    'margins_dialog_body':      (14, 14, 14, 14),
    'spacing_dialog_body':      8,

    # ── InsuredGroupCard / EndorsementPolicyCard (pagePolicies) ───────────────
    # Cards that hold insured party info with collapsible policy grids
    'insured_group_header_h':   32,
    'insured_toggle_size':      (26, 26),
    'policy_card_topbar_h':     32,
    'policy_card_topbar2_h':    32,
    'policy_editor_min_width':  480,
    'policy_editor_min_height': 200,
    'margins_policy_card_body': (8, 8, 8, 8),
    'spacing_policy_card_body': 6,

    # ── PageConfig ─────────────────────────────────────────────────────────────
    # spacing_config_fields → vertical gap between label and input in each field group
    'margins_config_top_row':   (0, 0, 0, 0),
    'spacing_config_top_row':   8,
    'spacing_config_fields':    4,
    'spacing_config_side_row':  8,
    'margins_config_side_row':  (0, 0, 0, 0),
    'margins_config_lol_fixed': (20, 10, 0, 0),

    # ── PagePolicies ──────────────────────────────────────────────────────────
    # Controls the layout of the insured/policy card grid
    'spacing_policies_main':    6,
    'margins_policies_grid':    (0, 0, 0, 0),
    'spacing_policies_grid':    8,
    'margins_policies_wrapper': (0, 0, 0, 0),
    'spacing_policies_wrapper': 8,
    'spacing_policies_qty_row': 8,
    'margins_policies_qty_row': (0, 0, 0, 0),
    'margins_policies_currency':(0, 0, 0, 0),
    'spacing_policies_currency':20,
    'margins_policies_finces':  (0, 0, 0, 0),
    'spacing_policies_finces':  8,
    'margins_policies_ed':      (0, 4, 0, 0),
    'margins_policies_insured': (0, 0, 0, 0),
    'margins_policies_clients': (0, 0, 0, 0),

    # ── PageUnit ───────────────────────────────────────────────────────────────
    'unit_logo_size':           (150, 100),
    'margins_unit_details':     (12, 0, 0, 0),

    # ── PageFinance ────────────────────────────────────────────────────────────
    'finance_label_width':      150,
    'margins_finance_recibo':   (0, 0, 0, 0),
    'margins_finance_grid':     (0, 0, 0, 0),
    'spacing_finance_grid':     8,
    'margins_finance_wrapper':  (0, 0, 0, 0),
    'spacing_finance_wrapper':  8,

    # ── PageAnnex ──────────────────────────────────────────────────────────────
    # Toolbar = B/I/U/List/Clear buttons above the Garantías rich-text editor
    # Editor  = QTextEdit for Garantías Particulares free text
    'annex_toolbar_min_height': 32,
    'annex_toolbar_btn_size':   (26, 26),
    'annex_editor_min_height':  180,
    'annex_sig_preview_height': 96,
    'annex_sig_dialog_min_h':   120,
    'annex_tab_editor_min_h':   140,
    'margins_annex_toolbar_outer':(0, 0, 0, 4),
    'spacing_annex_toolbar_outer':0,
    'margins_annex_toolbar_inner':(12, 6, 10, 6),
    'margins_annex_body':       (10, 8, 10, 10),
    'spacing_annex_body':       6,
    'spacing_annex_toolbar_items':4,
    'spacing_annex_radio_row':  24,
    'spacing_annex_check_area': 4,
    'margins_annex_check_area': (0, 8, 0, 0),
    'spacing_annex_g_area':     8,
    'margins_annex_g_area':     (0, 8, 0, 0),
    'margins_annex_ces_row':    (0, 0, 0, 0),
    'spacing_annex_ces_row':    4,
    'margins_annex_ces_card':   (0, 4, 0, 4),
    'spacing_annex_ces_card':   6,
    'spacing_annex_group_inner':6,
    'spacing_annex_row5':       4,
    'margins_annex_edit_outer': (0, 0, 0, 0),
    'spacing_annex_edit_outer': 4,
    'margins_annex_edit_toprow':(0, 0, 0, 0),
    'spacing_annex_edit_toprow':6,
    'margins_annex_groups_list':(0, 0, 0, 0),
    'spacing_annex_groups_list':8,
    'groupbox_title_origin':    'margin',
    'groupbox_title_position':  'top left',
}

def build_palette(theme):
    """Build a QPalette from theme colours so OS dark/light mode is overridden."""
    from PySide6.QtGui import QPalette, QColor
    c = theme
    p = QPalette()
    base   = QColor(c.get('surface',   '#FFFFFF'))
    window = QColor(c.get('app_bg',    '#f0f3f6'))
    text   = QColor(c.get('text_primary', '#4f5f6f'))
    hi     = QColor(c.get('selection_bg', '#59c2e6'))
    hi_txt = QColor(c.get('text_on_dark', '#FFFFFF'))
    dis    = QColor(c.get('text_disabled','#a1b1c2'))
    p.setColor(QPalette.Window,          window)
    p.setColor(QPalette.WindowText,      text)
    p.setColor(QPalette.Base,            base)
    p.setColor(QPalette.AlternateBase,   QColor(c.get('surface_alt', '#e1ecf7')))
    p.setColor(QPalette.Text,            text)
    p.setColor(QPalette.Button,          window)
    p.setColor(QPalette.ButtonText,      text)
    p.setColor(QPalette.Highlight,       hi)
    p.setColor(QPalette.HighlightedText, hi_txt)
    p.setColor(QPalette.Disabled, QPalette.Text,       dis)
    p.setColor(QPalette.Disabled, QPalette.ButtonText, dis)
    return p


QSSA = QSSD


def build_qss(theme):
    """
    Generate the full application QSS from the theme dictionary.
    Every value comes from QSSD — no hardcoded values in the template.
    Edit values in QSSD (ACTIVE_THEME), not in this function.
    """
    c = theme

    def bw(key):
        """Return 'bold' if QSSD[key] == 'bold', else 'normal'."""
        return 'bold' if c.get(key, 'normal') == 'bold' else 'normal'

    qss = f"""
    
    /* ===========================================================================
       S1  GLOBAL RESET & BASE WIDGET
       =========================================================================== */
    
    QWidget {{
        font-family:    {c['font_family']};
        font-size:      {c['font_size_base']};
        color:          {c['text_primary']};
        outline: {c['css_outline_none']};
    }}
    /* App background - only on top-level containers, not all widgets */
    QMainWindow {{ background-color: {c['app_bg']}; }}
    QDialog {{ background-color: {c['app_bg']}; }}
    QStackedWidget > QWidget {{ background-color: {c['app_bg']}; }}
    
    /* ===========================================================================
       S2  SCROLLBARS
       =========================================================================== */
    
    QScrollBar:vertical {{
        border: {c['css_none']};
        background-color: {c['scrollbar_track']};
        width:  {c['scrollbar_width']}px;
        margin: {c['margin_zero']};
    }}
    QScrollBar:horizontal {{
        border: {c['css_none']};
        background-color: {c['scrollbar_track']};
        height: {c['scrollbar_width']}px;
        margin: {c['margin_zero']};
    }}
    QScrollBar::handle:vertical {{
        background-color: {c['scrollbar_handle']};
        border-radius: {c['scrollbar_handle_radius']};
        min-height: {c['scrollbar_handle_min']}px;
        margin: {c['scrollbar_margin']};
    }}
    QScrollBar::handle:horizontal {{
        background-color: {c['scrollbar_handle']};
        border-radius: {c['scrollbar_handle_radius']};
        min-width: {c['scrollbar_handle_min']}px;
        margin: {c['scrollbar_margin']};
    }}
    QScrollBar::handle:vertical:hover,
    QScrollBar::handle:horizontal:hover {{
        background-color: {c['scrollbar_handle_hover']};
    }}
    QScrollBar::handle:vertical:pressed,
    QScrollBar::handle:horizontal:pressed {{
        background-color: {c['scrollbar_pressed']};
    }}
    QScrollBar::add-line, QScrollBar::sub-line,
    QScrollBar::add-page, QScrollBar::sub-page {{
        background: none; border: {c['css_none']}; height: 0; width: 0;
    }}
    
    /* QTreeWidget gets its own scrollbar scope */
    QTreeWidget QScrollBar:vertical   {{ border: {c['css_none']}; background-color: {c['scrollbar_track']}; width: {c['scrollbar_width']}px; margin: {c['margin_zero']}; }}
    QTreeWidget QScrollBar:horizontal {{ border: {c['css_none']}; background-color: {c['scrollbar_track']}; height: {c['scrollbar_width']}px; margin: {c['margin_zero']}; }}
    QTreeWidget QScrollBar::handle:vertical   {{ background-color: {c['scrollbar_handle']}; border-radius: {c['scrollbar_handle_radius']}; min-height: {c['scrollbar_handle_min']}px; margin: {c['margin_scrollbar']}; }}
    QTreeWidget QScrollBar::handle:horizontal {{ background-color: {c['scrollbar_handle']}; border-radius: {c['scrollbar_handle_radius']}; min-width: {c['scrollbar_handle_min']}px; margin: {c['margin_scrollbar']}; }}
    QTreeWidget QScrollBar::handle:vertical:hover,
    QTreeWidget QScrollBar::handle:horizontal:hover   {{ background-color: {c['scrollbar_handle_hover']}; }}
    QTreeWidget QScrollBar::handle:vertical:pressed,
    QTreeWidget QScrollBar::handle:horizontal:pressed {{ background-color: {c['scrollbar_pressed']}; }}
    QTreeWidget QScrollBar::add-line, QTreeWidget QScrollBar::sub-line,
    QTreeWidget QScrollBar::add-page, QTreeWidget QScrollBar::sub-page {{ background: none; border: {c['css_none']}; height: 0; width: 0; }}
    
    /* ===========================================================================
       S3  QSCROLLAREA
       =========================================================================== */
    
    QScrollArea,
    QScrollArea > QWidget,
    QScrollArea > QWidget > QWidget {{
        background-color: {c['app_bg']};
        border: {c['css_none']};
    }}
    
    /* ===========================================================================
       S4  QLABEL & QRADIOBUTTON
       =========================================================================== */
    
    QLabel {{
        color:            {c['text_primary']};
        font-weight:      {bw('text_primary_bold')};
        background-color: {c['css_transparent']};
        border: {c['css_none']};
        outline: {c['css_outline_none']};
    }}
    
    QRadioButton {{
        spacing:          {c['radio_spacing']}px;
        color:            {c['text_primary']};
        background-color: {c['css_transparent']};
        border: {c['css_none']};
        outline: {c['css_outline_none']};
    }}
    QRadioButton::indicator {{
        width:        {c['radio_size']}px;
        height:       {c['radio_size']}px;
        border:       {c['border_width_radio']} solid {c['radio_border']};
        border-radius:{c['radio_radius']};
        background-color: {c['radio_bg']};
    }}
    QRadioButton::indicator:hover {{
        border: {c['border_width_radio']} solid {c['radio_hover_border']};
    }}
    QRadioButton::indicator:checked {{
        border: {c['border_width_radio']} solid {c['border_input_hover']};
        background-color: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 {c['border_input_hover']}, stop:0.4 {c['border_input_hover']}, stop:0.45 {c['radio_bg']}, stop:1 {c['radio_bg']});
    }}
    
    /* ===========================================================================
       S5  QLINEEDIT
       =========================================================================== */
    
    QLineEdit {{
        background-color: {c['surface']};
        color:            {c['text_primary']};
        border:           {c['border_width_input']} solid {c['border_input']};
        border-radius:    {c['radius_input']};
        padding:          {c['padding_input']};
        min-height:       {c['input_min_height']}px;
        selection-background-color: {c['selection_bg']};
    }}
    QLineEdit:hover {{
        border: {c['border_width_input']} solid {c['border_input_hover']};
        border-radius: {c['radius_input']};
    }}
    QLineEdit:focus {{
        border: {c['border_width_input']} solid {c['border_input_focus']};
        border-radius: {c['radius_input']};
        outline: {c['css_outline_none']};
        background-color: {c['surface']};
    }}
    QLineEdit:read-only {{
        background-color: {c['surface_alt']};
        color:            {c['text_primary']};
        border: {c['border_width_input']} solid {c['border_input']};
    }}
    QLineEdit:disabled {{
        background-color: {c['surface_alt']};
        color:            {c['text_disabled']};
    }}
    
    /* ===========================================================================
       S6  QCOMBOBOX & DROPDOWN
       =========================================================================== */
    
    QComboBox {{
        background-color: {c['surface']};
        color:            {c['text_primary']};
        border:           {c['border_width_combo']} solid {c['border_input']};
        border-radius:    {c['radius_combo']};
        padding:          {c['padding_combo']};
        min-height:       {c['combo_min_height']}px;
        selection-background-color: {c['selection_bg']};
    }}
    QComboBox:hover {{
        border: {c['border_width_combo']} solid {c['border_input_hover']};
        border-radius: {c['radius_combo']};
    }}
    QComboBox:focus {{
        border: {c['border_width_combo']} solid {c['border_input_focus']};
        border-radius: {c['radius_combo']};
        outline: {c['css_outline_none']};
    }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: {c['combo_arrow_width']}px;
        border: {c['css_none']};
    }}
    QComboBox::down-arrow       {{ image: url(imgs/arrow_down.svg); width: {c['combo_arrow_size']}px; height: {c['combo_arrow_size']}px; }}
    QComboBox::down-arrow:on    {{ image: url(imgs/arrow_up.svg); width: {c['combo_arrow_size']}px; height: {c['combo_arrow_size']}px; }}
    QComboBox QAbstractItemView {{
        background-color: {c['surface']};
        color:            {c['text_primary']};
        border:           {c['border_width_combo_dropdown']} solid {c['border_input']};
        border-radius:    {c['radius_combo']};
        selection-background-color: {c['selection_bg']};
        outline: {c['css_outline_none']};
        padding: {c['combo_popup_padding']};
    }}
    QComboBox QAbstractItemView::item {{
        min-height: {c['combo_item_height']}px;
        padding: {c['combo_popup_padding_item']};
        border-radius: {c['radius_combo']};
    }}
    QComboBox QAbstractItemView::item:hover {{
        background-color: {c['combo_item_hover_bg']};
        color: {c['text_primary']};
    }}
    QComboBox QAbstractItemView::item:selected {{
        background-color: {c['combo_item_selected_bg']};
        color: {c['combo_item_selected_text']};
    }}
    
    /* ===========================================================================
       S7  QDATEEDIT & QCALENDARWIDGET
       =========================================================================== */
    
    QDateEdit {{
        background-color: {c['surface']};
        color:            {c['text_primary']};
        border:           {c['border_width_date']} solid {c['border_input']};
        border-radius:    {c['radius_date']};
        padding:          {c['padding_input']};
        min-height:       {c['input_min_height']}px;
    }}
    QDateEdit:hover {{
        border: {c['border_width_date']} solid {c['border_input_hover']};
        border-radius: {c['radius_date']};
    }}
    QDateEdit:focus {{
        border: {c['border_width_date']} solid {c['border_input_focus']};
        border-radius: {c['radius_date']};
        outline: {c['css_outline_none']};
    }}
    QDateEdit::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: {c['combo_arrow_width']}px;
        border: {c['css_none']};
    }}
    QDateEdit::down-arrow {{ image: url(imgs/calendar.svg); width: {c['cal_icon_size']}px; height: {c['cal_icon_size']}px; }}
    
    QCalendarWidget {{
        background-color: {c['surface']};
        border: {c['border_width_calendar']} solid {c['border_strong']};
        min-height: {c['cal_min_height']}px;
    }}
    QCalendarWidget QAbstractItemView {{
        background-color: {c['surface']};
        color:            {c['text_primary']};
        selection-background-color: {c['cal_selected_bg']};
        selection-color:            {c['cal_selected_text']};
        gridline-color: {c['cal_grid']};
        outline: {c['css_outline_none']};
    }}
    QCalendarWidget QAbstractItemView:disabled {{ color: {c['cal_other_month_text']}; }}
    QCalendarWidget QAbstractItemView::item:hover {{
        background-color: {c['cal_hover_bg']};
        color: {c['text_primary']};
        border-radius: {c['radius_input']};
    }}
    QCalendarWidget QAbstractItemView::item:selected {{
        background-color: {c['cal_selected_bg']};
        color: {c['cal_selected_text']};
        border-radius: {c['radius_input']};
    }}
    QCalendarWidget QWidget#qt_calendar_navigationbar {{
        background-color: {c['cal_nav_bg']};
        padding: {c['groupbox_padding_top']};
        min-height: {c['card_header_min_height']}px;
    }}
    QCalendarWidget QToolButton {{
        background-color: {c['css_transparent']};
        color: {c['cal_nav_text']};
        border: {c['css_none']};
        border-radius: {c['radius_zero']};
        padding: {c['groupbox_padding_top']} 8px;
        font-weight: {bw('cal_tool_font_weight')};
    }}
    QCalendarWidget QToolButton:hover {{ background-color: {c['cal_nav_arrow_hover_bg']}; border-radius: {c['radius_zero']}; }}
    QCalendarWidget QToolButton::menu-indicator {{ image: {c['css_image_none']}; }}
    QCalendarWidget QToolButton#qt_calendar_prevmonth {{ qproperty-icon: url(imgs/arrow_left.svg); icon-size: {c['cal_icon_size']}px; }}
    QCalendarWidget QToolButton#qt_calendar_nextmonth {{ qproperty-icon: url(imgs/arrow_right.svg); icon-size: {c['cal_icon_size']}px; }}
    QCalendarWidget QSpinBox {{
        background-color: {c['css_transparent']};
        color: {c['cal_nav_text']};
        border: {c['css_none']};
        selection-background-color: {c['cal_selected_bg']};
    }}
    QCalendarWidget QSpinBox::up-button,
    QCalendarWidget QSpinBox::down-button {{ width: {c['css_zero']}; }}
    QCalendarWidget QHeaderView::section {{
        background-color: {c['cal_nav_bg']};
        color: {c['cal_nav_text']};
        border: {c['css_none']};
        font-weight: {c['fw_bold']};
    }}
    
    /* ===========================================================================
       S8  QCHECKBOX
       =========================================================================== */
    
    QCheckBox {{
        spacing:          {c['checkbox_spacing']}px;
        color:            {c['text_primary']};
        background-color: {c['css_transparent']};
        border: {c['css_none']};
        outline: {c['css_outline_none']};
    }}
    QCheckBox::indicator {{
        width:         {c['checkbox_size']}px;
        height:        {c['checkbox_size']}px;
        border:        {c['border_width_checkbox']} solid {c['checkbox_border']};
        border-radius: {c['checkbox_radius']}px;
        background-color: {c['checkbox_bg']};
    }}
    QCheckBox::indicator:hover {{
        border: {c['border_width_checkbox']} solid {c['checkbox_hover_border']};
    }}
    QCheckBox::indicator:checked {{
        background-color: {c['checkbox_checked_bg']};
        border:           {c['border_width_checkbox']} solid {c['checkbox_checked_border']};
        image: url(imgs/check.svg);
    }}
    QCheckBox::indicator:indeterminate {{
        background-color: {c['checkbox_checked_bg']};
        border:           {c['border_width_checkbox']} solid {c['checkbox_checked_border']};
        image: url(imgs/check_indeterminate.svg);
    }}
    QCheckBox::indicator:disabled {{
        background-color: {c['checkbox_disabled_bg']};
        border:           {c['border_width_checkbox']} solid {c['text_disabled']};
        image: url(imgs/check_disabled.svg);
    }}
    
    /* ===========================================================================
       S9  QGROUPBOX
       =========================================================================== */
    
    QGroupBox {{
        background-color: {c['card_body_bg']};
        border: {c['border_width_card']} solid {c['border_strong']};
        border-radius: {c['radius_card']};
        margin-top: {c['margin_groupbox_title']};
        padding: {c['padding_groupbox']};
        font-weight: {bw('groupbox_font_weight')};
        font-size: {c['font_size_base']};
        color: {c['text_primary']};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: {c['groupbox_title_position']};
        left: {c['groupbox_label_left']};
        top: {c['groupbox_label_top']};
        padding: 0 {c['padding_groupbox_top']};
        color: {c['text_primary']};
        background-color: {c['app_bg']};
    }}
    
    /* ===========================================================================
       S10  QPUSHBUTTON - BASE (all buttons inherit these defaults)
       =========================================================================== */
    
    QPushButton {{
        background-color: {c['btn_primary_bg']};
        color:            {c['btn_primary_text']};
        border:           {c['btn_border_width']} solid {c['btn_primary_bg']};
        border-radius:    {c['radius_btn']};
        padding:          {c['padding_btn']};
        min-height:       {c['btn_min_height']}px;
        min-width:        {c['btn_min_width']}px;
        font-weight:      {c['fw_bold']};
    }}
    QPushButton:hover   {{
        background-color: {c['btn_primary_hover']};
        color: {c['btn_primary_text']};
    }}
    QPushButton:pressed {{
        background-color: {c['accent_dark']};
        color: {c['btn_primary_text']};
    }}
    QPushButton:disabled {{
        background-color: {c['text_disabled']};
        color: {c['text_on_dark']};
    }}
    
    /* ===========================================================================
       S11  QPUSHBUTTON - NAMED ACTION BUTTONS (text + role selectors)
            Format: QPushButton[text="LABEL"][role="ROLE"]
            Roles: danger | neutral | excel | download | quitar | endtable-view |
                   endtable-edit | endtable-import
       =========================================================================== */
    
    /* -- Danger buttons (LIMPIAR, ELIMINAR) -- */
    QPushButton[text="LIMPIAR"],
    QPushButton[text="ELIMINAR"],
    QPushButton[role="danger"] {{
        background-color: {c['btn_danger_bg']};
        color:            {c['btn_danger_text']};
        border:           {c['border_width_msg']} solid {c['btn_danger_border']};
        border-radius:    {c['radius_btn']};
        padding:          {c['padding_btn']};
        min-height:       {c['btn_min_height']}px;
        min-width:        {c['btn_danger_min_width']}px;
    }}
    QPushButton[text="LIMPIAR"]:hover,
    QPushButton[text="ELIMINAR"]:hover,
    QPushButton[role="danger"]:hover {{
        background-color: {c['btn_danger_hover_bg']};
        color:            {c['btn_danger_hover_text']};
        border: {c['css_none']};
    }}
    
    /* -- Danger controlled-height (Cesiones action: ELIMINAR in tables) -- */
    QPushButton[role="cesiones-danger"] {{
        background-color: {c['btn_danger_bg']};
        color:            {c['btn_danger_text']};
        border:           {c['border_width_msg']} solid {c['btn_danger_border']};
        border-radius:    {c['radius_btn']};
        padding:          {c['padding_combo_header']};
        min-height:       {c['cesiones_btn_height']}px;
        max-height:       {c['cesiones_btn_height']}px;
    }}
    QPushButton[role="cesiones-danger"]:hover {{
        background-color: {c['btn_danger_hover_bg']};
        color:            {c['btn_danger_hover_text']};
        border: {c['css_none']};
    }}
    
    /* -- Neutral controlled-height (Cesiones neutral: AGREGAR/ACTUALIZAR in tables) -- */
    QPushButton[role="cesiones-neutral"] {{
        background-color: {c['btn_primary_bg']};
        color:            {c['btn_primary_text']};
        border:           {c['btn_border_width']} solid {c['btn_primary_bg']};
        border-radius:    {c['radius_btn']};
        padding:          {c['padding_combo_header']};
        min-height:       {c['cesiones_btn_height']}px;
        max-height:       {c['cesiones_btn_height']}px;
    }}
    QPushButton[role="cesiones-neutral"]:hover {{
        background-color: {c['btn_primary_hover']};
    }}
    
    /* -- Quitar (trash icon button - TREC group remove) -- */
    QPushButton[role="quitar"] {{
        background-color: {c['btn_quitar_svg_bg']};
        border:           {c['css_none']};
        border-radius:    {c['radius_btn']};
        padding:          {c['padding_groupbox_top']};
        min-width:        {c['btn_quitar_size']}px;
        max-width:        {c['btn_quitar_size']}px;
        min-height:       {c['btn_quitar_size']}px;
        max-height:       {c['btn_quitar_size']}px;
    }}
    QPushButton[role="quitar"]:hover {{
        background-color: {c['btn_quitar_svg_hover_bg']};
    }}
    
    /* -- Excel Import - icon-only (Row5 in _GroupEditor) -- */
    QPushButton[role="excel-icon"] {{
        background-color: {c['btn_excel_bg']};
        border:           {c['css_none']};
        border-radius:    {c['radius_btn']};
        padding:          {c['combo_popup_padding']};
        min-width:        {c['btn_endtable_size']}px;
        max-width:        {c['btn_endtable_size']}px;
        min-height:       {c['btn_endtable_size']}px;
        max-height:       {c['btn_endtable_size']}px;
    }}
    QPushButton[role="excel-icon"]:hover {{
        background-color: {c['btn_excel_hover_bg']};
    }}
    
    /* -- Excel Import - text button (TopRow in dialog) -- */
    QPushButton[role="excel-text"] {{
        background-color: {c['btn_excel_bg']};
        color:            {c['btn_excel_text']};
        border:           {c['css_none']};
        border-radius:    {c['radius_btn']};
        padding:          {c['padding_endtable_btn']};
        min-height:       {c['btn_dialog_topbar_height']}px;
    }}
    QPushButton[role="excel-text"]:hover {{
        background-color: {c['btn_excel_hover_bg']};
    }}
    
    /* -- Download Template button -- */
    QPushButton[role="download"] {{
        background-color: {c['css_transparent']};
        color:            {c['btn_excel_hover_bg']};
        border:           {c['border_width_msg']} solid {c['btn_excel_hover_bg']};
        border-radius:    {c['radius_btn']};
        padding:          {c['padding_endtable_btn']};
        min-height:       {c['btn_dialog_topbar_height']}px;
    }}
    QPushButton[role="download"]:hover {{
        background-color: {c['btn_excel_hover_bg']};
        color:            {c['btn_excel_hover_text']};
        border: {c['css_none']};
    }}
    
    /* -- EndorsementTableCard header: Ver (view) -- */
    QPushButton[role="endtable-view"] {{
        background-color: {c['card_body_bg']};
        color:            {c['card_header_bg']};
        border:           {c['border_width_input']} solid {c['border_input']};
        border-radius:    {c['radius_btn']};
        padding:          {c['combo_popup_padding']};
        min-width:        {c['btn_endtable_size']}px;
        max-width:        {c['btn_endtable_size']}px;
        min-height:       {c['btn_endtable_size']}px;
        max-height:       {c['btn_endtable_size']}px;
    }}
    QPushButton[role="endtable-view"]:hover {{ background-color: {c['surface_alt']}; }}
    
    /* -- EndorsementTableCard header: Editar (edit) -- */
    QPushButton[role="endtable-edit"] {{
        background-color: {c['card_body_bg']};
        color:            {c['card_header_bg']};
        border:           {c['border_width_input']} solid {c['border_input']};
        border-radius:    {c['radius_btn']};
        padding:          {c['combo_popup_padding']};
        min-width:        {c['btn_endtable_size']}px;
        max-width:        {c['btn_endtable_size']}px;
        min-height:       {c['btn_endtable_size']}px;
        max-height:       {c['btn_endtable_size']}px;
    }}
    QPushButton[role="endtable-edit"]:hover {{ background-color: {c['surface_alt']}; }}
    
    /* -- EndorsementTableCard header: Import Excel -- */
    QPushButton[role="endtable-import"] {{
        background-color: {c['btn_excel_bg']};
        border:           {c['css_none']};
        border-radius:    {c['radius_btn']};
        padding:          {c['combo_popup_padding']};
        min-width:        {c['btn_endtable_size']}px;
        max-width:        {c['btn_endtable_size']}px;
        min-height:       {c['btn_endtable_size']}px;
        max-height:       {c['btn_endtable_size']}px;
    }}
    QPushButton[role="endtable-import"]:hover {{
        background-color: {c['btn_excel_hover_bg']};
    }}
    
    /* -- QUITAR POLIZA / QUITAR ASEGURADO (text buttons in pagePolicies) -- */
    QPushButton[text^="QUITAR POLIZA"],
    QPushButton[text^="QUITAR ASEGURADO"] {{
        background-color: {c['btn_quitar_bg']};
        color:            {c['btn_quitar_text']};
        border:           {c['border_width_msg']} solid {c['btn_quitar_border']};
        border-radius:    {c['radius_btn']};
        padding:          {c['padding_btn']};
        min-width:        {c['min_width_dialog_btn']};
        min-height:       {c['btn_min_height']}px;
    }}
    QPushButton[text^="QUITAR POLIZA"]:hover,
    QPushButton[text^="QUITAR ASEGURADO"]:hover {{
        background-color: {c['btn_quitar_hover_bg']};
        color:            {c['btn_quitar_hover_text']};
        border: {c['css_none']};
    }}
    
    /* ===========================================================================
       S12  QTREEWIDGET (table views - pagePolicies, pageFinance, pageAnnex)
       =========================================================================== */
    
    QTreeWidget {{
        background-color:     {c['table_bg']};
        alternate-background-color: {c['table_row_alt']};
        color:                {c['text_primary']};
        border:               {c['border_width_table']} solid {c['border_table']};
        border-radius:        {c['radius_table']};
        gridline-color:       {c['table_border']};
        outline: {c['css_outline_none']};
    }}
    QTreeWidget::item {{
        min-height:           {c['table_row_height']}px;
        padding:              {c['padding_tree_cell']};
        border-bottom:        {c['border_width_table']} solid {c['table_border']};
    }}
    QTreeWidget::item:!selected {{ border-bottom: {c['border_width_table']} solid {c['table_border']}; }}
    QTreeWidget::item:hover     {{ background-color: {c['table_row_hover']}; color: {c['text_primary']}; }}
    QTreeWidget::item:selected  {{
        background-color: {c['table_row_selected']};
        color:            {c['table_row_selected_text']};
    }}
    QTreeWidget QHeaderView {{ border: {c['css_none']}; }}
    QTreeWidget QHeaderView::section {{
        background-color: {c['table_header_bg']};
        color:            {c['table_header_text']};
        font-weight:      {bw('table_header_text_bold')};
        border:           {c['css_none']};
        border-right:     {c['border_width_table']} solid {c['table_header_divider']};
        padding:          {c['padding_header_sec']};
        min-height:       {c['table_header_height']}px;
    }}
    QTreeWidget QHeaderView::section:last,
    QTreeWidget QHeaderView::section:last-child,
    QTreeWidget QHeaderView::section:only-child {{ border-right: {c['border_right_none']}; }}
    
    /* QTableWidget headers - EndorsementEditDialog */
    QTableWidget QHeaderView::section:horizontal {{
        background-color: {c['card_header_bg']};
        color:            {c['card_header_text']};
        font-weight:      {c['fw_bold']};
        padding:          {c['padding_header_section']};
        border:           {c['css_none']};
        border-right:     1px solid {c['border_input']};
    }}
    QTableWidget QHeaderView::section:vertical {{
        background-color: {c['card_header_bg']};
        color:            {c['card_header_text']};
        padding:          {c['padding_header_vert']};
        border:           {c['css_none']};
        border-bottom:    1px solid {c['border_input']};
        min-width:        {c['table_vertical_header_width']}px;
        max-width:        {c['table_vertical_header_width']}px;
    }}
    
    /* ===========================================================================
       S13  NAVBAR (bottom navigation bar on each page)
       =========================================================================== */
    
    #NavBar {{
        background-color: {c['nav_bg']};
        border-top:       {c['nav_border_width']} solid {c['nav_border_color']};
        min-height:       {c['nav_height']}px;
        max-height:       {c['nav_height']}px;
    }}
    
    /* ===========================================================================
       S14  CARDWIDGET (collapsible card used throughout the app)
       =========================================================================== */
    
    #CardHeader {{
        background-color: {c['card_header_bg']};
        min-height:       {c['card_header_height']}px;
        max-height:       {c['card_header_height']}px;
        padding:          {c['padding_nav_btn']};
        border-radius:    {c['radius_zero']};
    }}
    #CardTitle {{
        color:            {c['card_header_text']};
        font-weight:      {bw('card_header_text_bold')};
        font-size:        {c['font_size_base']};
        background-color: {c['css_transparent']};
    }}
    #CardToggle {{
        color:            {c['card_header_toggle']};
        background-color: {c['css_transparent']};
    }}
    #CardBody {{
        background-color: {c['card_body_bg']};
        border-width:     {c['border_width_card']};
        border-style:     {c['css_solid']};
        border-color:     {c['card_body_border']};
        border-top:       {c['border_width_card']} solid {c['card_body_border']};
        border-radius:    {c['radius_card']};
        padding:          {c['padding_card_body']};
    }}
    #CardBody QLineEdit  {{ border: {c['border_width_input']} solid {c['border_input']};  border-radius: {c['radius_input']};  background-color: {c['surface']}; outline: {c['css_outline_none']}; }}
    #CardBody QComboBox  {{ border: {c['border_width_combo']} solid {c['border_input']};  border-radius: {c['radius_combo']};  background-color: {c['surface']}; outline: {c['css_outline_none']}; }}
    #CardBody QDateEdit  {{ border: {c['border_width_date']}  solid {c['border_input']};  border-radius: {c['radius_date']};   background-color: {c['surface']}; outline: {c['css_outline_none']}; }}
    #CardBody QLineEdit:hover,  #CardBody QLineEdit:focus  {{ border: {c['border_width_input']} solid {c['border_input_focus']}; border-radius: {c['radius_input']}; outline: {c['css_outline_none']}; }}
    #CardBody QComboBox:hover,  #CardBody QComboBox:focus  {{ border: {c['border_width_combo']} solid {c['border_input_focus']}; border-radius: {c['radius_combo']}; outline: {c['css_outline_none']}; }}
    #CardBody QDateEdit:hover,  #CardBody QDateEdit:focus  {{ border: {c['border_width_date']}  solid {c['border_input_focus']}; border-radius: {c['radius_date']};  outline: {c['css_outline_none']}; }}
    
    /* ===========================================================================
       S15  CUSTOMMESSAGEBOX
       =========================================================================== */
    
    #MsgFrame {{
        background-color: {c['msg_frame_bg']};
        border:           {c['border_width_msg']} solid {c['msg_frame_border']};
        border-radius:    {c['radius_msg_frame']};
    }}
    #MsgTitleBar {{
        background-color: {c['msg_titlebar_bg']};
        border-radius:    {c['radius_msg_titlebar']};
        min-height:       {c['msg_titlebar_height']}px;
        max-height:       {c['msg_titlebar_height']}px;
    }}
    #MsgTitle {{
        color:       {c['msg_titlebar_text']};
        font-weight: {bw('msg_titlebar_text_bold')};
        font-size:   {c['font_size_large']};
        background-color: {c['css_transparent']};
    }}
    #MsgBody {{
        background-color: {c['msg_body_bg']};
        border-radius:    {c['radius_msg_body']};
        padding:          {c['padding_msg_body']};
    }}
    #MsgText {{
        color:       {c['msg_text']};
        font-weight: {bw('msg_text_bold')};
        font-size:   {c['font_size_base']};
        background-color: {c['css_transparent']};
    }}
    #MsgBtnPrimary {{
        background-color: {c['msg_btn_primary_bg']};
        color:            {c['msg_btn_primary_text']};
        font-weight:      {bw('msg_btn_font_weight')};
        border:           {c['border_width_msg']} solid {c['msg_btn_primary_bg']};
        border-radius:    {c['radius_msg_btn']};
        padding:          {c['padding_msg_btn']};
        min-width:        {c['btn_min_width']}px;
        min-height:       {c['msg_btn_min_height']}px;
    }}
    #MsgBtnPrimary:hover {{
        background-color: {c['msg_btn_primary_hover']};
    }}
    #MsgBtnSecondary {{
        background-color: {c['msg_btn_secondary_bg']};
        color:            {c['msg_btn_secondary_text']};
        font-weight:      {bw('msg_btn_font_weight')};
        border:           {c['border_width_msg']} solid {c['msg_btn_secondary_border']};
        border-radius:    {c['radius_msg_btn']};
        padding:          {c['padding_msg_btn']};
        min-width:        {c['btn_min_width']}px;
        min-height:       {c['msg_btn_min_height']}px;
    }}
    #MsgBtnSecondary:hover {{
        background-color: {c['msg_btn_secondary_hover']};
    }}
    
    /* ===========================================================================
       S16  CESIONES / ENDORSEMENTTABLECARD
       =========================================================================== */
    
    /* EndorsementTableCard header - transparent (child card) */
    #EndorsementCard {{
        background-color: {c['css_transparent']};
        border:           {c['border_width_input']} solid {c['border_input']};
        border-radius:    {c['radius_zero']};
    }}
    #EndorsementCard QLabel {{
        color:            {c['text_primary']};
        background:       {c['css_transparent']};
    }}
    #EndorsementCard QCheckBox {{
        color:            {c['text_primary']};
        background:       {c['css_transparent']};
    }}
    
    /* InsuredGroupCard - navy header (inverted from original) */
    #InsuredGroupHeader {{
        background-color: {c['card_header_bg']};
        border:           {c['border_width_input']} solid {c['card_header_bg']};
        border-radius:    {c['radius_zero']};
    }}
    #InsuredGroupHeader QLabel {{
        color:            {c['card_header_text']};
        font-weight:      {c['fw_bold']};
        background:       {c['css_transparent']};
    }}
    #InsuredGroupHeader #CardToggle {{
        color: {c['card_header_toggle']};
    }}
    #InsuredGroupBody {{
        background-color: {c['card_body_bg']};
        border:           {c['border_width_card']} solid {c['card_body_border']};
        border-top:       {c['border_top_none']};
        padding:          {c['padding_card_header_h']};
    }}
    
    /* ── Output format selector buttons ── */
    QPushButton[role="format-selector"] {{
        background-color: {c['card_bg']};
        border:           1px solid {c['border_color']};
        border-radius:    {c['radius_btn']};
        padding:          {c['format_btn_padding']};
        min-width:        {c['format_btn_min_width']}px;
        color:            {c['text_primary']};
        font-weight:      {c['fw_normal']};
        icon-size:        {c['format_btn_icon_h']}px;
        text-align:       {c['align_center']};
    }}
    QPushButton[role="format-selector"]:hover {{
        background-color: {c['accent_light']};
        border-color:     {c['accent']};
    }}
    QPushButton[role="format-selector"]:checked {{
        background-color: {c['accent']};
        border-color:     {c['accent_dark']};
        color:            {c['text_on_accent']};
        font-weight:      {c['fw_bold']};
    }}
    QPushButton[role="format-selector"]:checked:hover {{
        background-color: {c['accent_dark']};
    }}
    
    /* ── Manual procedure item buttons ── */
    QPushButton[role="manual-item"] {{
        background-color: {c['card_bg']};
        border:           1px solid {c['border_color']};
        border-radius:    {c['radius_btn']};
        padding:          {c['padding_tree_item']};
        color:            {c['text_primary']};
        text-align:       {c['align_left']};
        min-height:       {c['input_min_height']}px;
    }}
    QPushButton[role="manual-item"]:hover {{
        background-color: {c['accent_light']};
        border-color:     {c['accent']};
    }}
    QPushButton[role="manual-item"]:checked {{
        background-color: {c['accent_light']};
        border-color:     {c['accent']};
        color:            {c['accent_dark']};
        font-weight:      {c['fw_bold']};
    }}
    QPushButton[role="manual-item"]:disabled {{
        background-color: {c['card_bg']};
        border-color:     {c['border_color']};
        color:            {c['text_primary']};
        font-weight:      {c['fw_normal']};
    }}
    
    /* ── Manual procedure fixed item (Aspectos Generales) ── */
    QPushButton[role="manual-fixed"] {{
        background-color: {c['card_bg']};
        border:           1px solid {c['accent']};
        border-radius:    {c['radius_btn']};
        padding:          {c['padding_tree_item']};
        color:            {c['text_muted']};
        font-weight:      {c['fw_bold']};
        text-align:       {c['align_left']};
        min-height:       {c['input_min_height']}px;
    }}
    QPushButton[role="manual-fixed"]:disabled {{
        background-color: {c['card_bg']};
        border:           1px solid {c['accent']};
        color:            {c['text_muted']};
        font-weight:      {c['fw_bold']};
    }}
    
    /* ── Accordion QPushButton - all card accordions across the app ── */
    QPushButton[role="accordion"] {{
        background-color: {c['css_transparent']};
        border:           {c['accordion_border_css']};
        border-radius:    {c['radius_btn']};
        padding:          {c['padding_zero_h']};
        icon-size:        {c['card_toggle_size_px']};
        color:            {c['card_header_toggle']};
        min-width:        {c['card_toggle_size_px']};
        min-height:       {c['card_toggle_size_px']};
    }}
    QPushButton[role="accordion"]:hover {{
        background-color: {c['accordion_hover_bg']};
        border-color:     {c['accordion_hover_border']};
    }}
    QPushButton[role="accordion"]:checked {{
        background-color: {c['css_transparent']};
        border-color:     {c['accordion_normal_border']};
    }}
    QPushButton[role="accordion"]:checked:hover {{
        background-color: {c['accordion_hover_bg']};
        border-color:     {c['accordion_hover_border']};
    }}
    
    /* ── CardTitle QComboBox in navy header ── */
    QComboBox#CardTitle {{
        background-color: {c['css_transparent']};
        border:           {c['css_none']};
        color:            {c['card_header_toggle']};
        font-weight:      {c['fw_bold']};
    }}
    QComboBox#CardTitle QLineEdit {{
        background-color: {c['css_transparent']};
        color:            {c['card_header_toggle']};
        border:           {c['css_none']};
    }}
    QComboBox#CardTitle::drop-down {{
        border:           {c['css_none']};
    }}
    QComboBox#CardTitle::down-arrow {{
        width:  {c['padding_zero_h']}; height: {c['padding_zero_h']};
    }}
    
    /* ── GroupEditor gear button ── */
    QPushButton[role="config-gear"] {{
        background-color: {c['css_transparent']};
        border:           {c['css_none']};
        border-radius:    {c['radius_btn']};
        padding:          {c['combo_popup_padding']};
    }}
    QPushButton[role="config-gear"]:hover {{
        background-color: {c['titlebar_btn_hover_bg']};
    }}
    QPushButton[role="config-gear"]:checked {{
        background-color: {c['accent']};
    }}
    
    /* ── GroupEditor config panel ── */
    #ConfigPanel {{
        background-color: {c['card_body_bg']};
        border:           {c['border_width_input']} solid {c['border_input']};
        border-top:       {c['border_top_none']};
    }}
    
    /* ── Column action buttons (add/remove/rename) ── */
    QPushButton[role="col-action"] {{
        background-color: {c['btn_primary_bg']};
        border:           {c['css_none']};
        border-radius:    {c['radius_btn']};
        padding:          {c['combo_popup_padding']};
    }}
    QPushButton[role="col-action"]:hover {{
        background-color: {c['btn_primary_hover']};
    }}
    QPushButton[role="col-action-danger"] {{
        background-color: {c['btn_danger_bg']};
        border:           1px solid {c['btn_danger_bg']};
        border-radius:    {c['radius_btn']};
        padding:          {c['combo_popup_padding']};
        color:            {c['combo_item_hover_text']};
    }}
    QPushButton[role="col-action-danger"]:hover {{
        background-color: {c['btn_danger_hover_bg']};
        border-color:     {c['btn_danger_hover_bg']};
    }}
    
    
    /* ===========================================================================
       S17  APPTITLEBAR (CustomDialog frameless titlebar)
       =========================================================================== */
    
    #AppTitleBar {{
        background-color: {c['titlebar_bg']};
        min-height:       {c['titlebar_height']}px;
        max-height:       {c['titlebar_height']}px;
    }}
    #AppTitleLabel {{
        color:            {c['titlebar_text']};
        font-weight:      {c['fw_bold']};
        font-size:        {c['font_size_base']};
        background-color: {c['css_transparent']};
    }}
    QPushButton[role="titlebar-min"],
    QPushButton[role="titlebar-max"] {{
        background-color: {c['css_transparent']};
        color:            {c['titlebar_btn_text']};
        border:           {c['css_none']};
        font-size:        {c['font_size_nav']};
        min-width:        {c['titlebar_btn_width']}px;
        max-width:        {c['titlebar_btn_width']}px;
        min-height:       {c['titlebar_height']}px;
        max-height:       {c['titlebar_height']}px;
        border-radius:    {c['radius_zero']};
        padding:          {c['padding_zero_h']};
    }}
    QPushButton[role="titlebar-min"]:hover,
    QPushButton[role="titlebar-max"]:hover {{
        background-color: {c['titlebar_btn_hover_bg']};
    }}
    QPushButton[role="titlebar-close"] {{
        background-color: {c['css_transparent']};
        color:            {c['titlebar_btn_text']};
        border:           {c['css_none']};
        font-size:        {c['font_size_nav']};
        min-width:        {c['titlebar_btn_width']}px;
        max-width:        {c['titlebar_btn_width']}px;
        min-height:       {c['titlebar_height']}px;
        max-height:       {c['titlebar_height']}px;
        border-radius:    {c['radius_zero']};
        padding:          {c['padding_zero_h']};
    }}
    QPushButton[role="titlebar-close"]:hover {{
        background-color: {c['titlebar_close_hover_bg']};
    }}
    QPushButton[role="titlebar-close"]:pressed {{
        background-color: {c['titlebar_close_pressed_bg']};
    }}
    
    /* ===========================================================================
       S18  MISCELLANEOUS / PAGE-SPECIFIC
       =========================================================================== */
    
    #InstructionLabel {{
        color:       {c['text_instruction']};
        font-size:   {c['font_size_small']};
        font-weight: {c['fw_normal']};
    }}
    
    
    /* ── QTabWidget - Cesiones Individual mode ── */
    QTabWidget::pane {{
        border:        1px solid {c['card_header_bg']};
        border-top:    {c['border_top_none']};
        margin:        {c['padding_zero_h']};
        padding:       {c['padding_zero_h']};
        background:    {c['card_bg']};
        top:           {c['tab_pane_top']};
    }}
    QTabWidget {{
        margin:  {c['padding_zero_h']};
        padding: {c['padding_zero_h']};
    }}
    QTabBar::tab {{
        background-color: {c['card_bg']};
        color:            {c['card_header_bg']};
        border:           1px solid {c['card_header_bg']};
        border-bottom:    {c['border_bottom_none']};
        border-top-left-radius:  {c['radius_btn']};
        border-top-right-radius: {c['radius_btn']};
        padding:          {c['padding_tab']};
        min-height:       {c['tab_header_height']}px;
        margin-right:     {c['tab_margin_right']};
    }}
    QTabBar::tab:selected {{
        background-color: {c['card_header_bg']};
        color:            {c['card_header_toggle']};
        font-weight:      {c['fw_bold']};
    }}
    QTabBar::tab:!selected {{
        background-color: {c['card_bg']};
        color:            {c['card_header_bg']};
        margin-top:       {c['tab_inactive_margin_top']};
    }}
    QTabBar::tab:hover:!selected {{
        background-color: {c['card_header_bg']};
        color:            {c['card_header_toggle']};
    }}
    
    /* ── QLineEdit / QComboBox embedded in navy CardWidget header ── */
    /* Used in: pagePolicies insuredName, policyBranch; GroupEditor endorsee combo */
    QLineEdit#CardTitle {{
        background-color: {c['card_header_input_bg']};
        color:            {c['card_header_input_text']};
        border:           {c['card_header_input_border']};
        border-radius:    {c['radius_tab_inactive']};
        font-size:        {c['card_header_input_font_size']};
        padding:          {c['card_header_input_padding']};
        min-height:       {c['card_header_input_min_height']}px;
        selection-background-color: {c['card_header_sel_bg']};
    }}
    QLineEdit#CardTitle::placeholder {{
        color: {c['card_header_input_placeholder']};
    }}
    QComboBox#CardTitle {{
        background-color: {c['card_header_input_bg']};
        color:            {c['card_header_input_text']};
        border:           {c['card_header_input_border']};
        font-size:        {c['card_header_input_font_size']};
        padding:          {c['card_header_input_padding']};
        min-height:       {c['card_header_input_min_height']}px;
    }}
    QComboBox#CardTitle QLineEdit {{
        background-color: {c['css_transparent']};
        color:            {c['card_header_input_text']};
        border:           {c['css_none']};
        padding:          {c['card_header_input_padding']};
        font-size:        {c['card_header_input_font_size']};
    }}
    QComboBox#CardTitle::drop-down {{
        border: {c['css_none']};
    }}
    QComboBox#CardTitle::down-arrow {{
        width: {c['padding_zero_h']}; height: {c['padding_zero_h']};
    }}
    
    /* ── CardWidget inside QTabWidget - no borders in Individual mode ── */
    QTabWidget QWidget#CardBody {{
        border-left:   {c['border_left_none']};
        border-right:  {c['border_right_none']};
        border-bottom: {c['border_bottom_none']};
    }}
    QTabWidget QWidget#CardHeader {{
        border-radius: {c['radius_zero']};
    }}
    
    """



    # Convert url() to absolute paths when running from PyInstaller bundle
    try:
        import re as _re, os as _os
        from helpers import resource_path as _rp
        def _abs_url(m):
            rel = m.group(1)
            try:
                # Qt QSS url() requires forward slashes — replace backslashes
                abs_path = _rp(rel).replace('\\', '/')
                return f'url({abs_path})'
            except Exception:
                return m.group(0)
        qss = _re.sub(r'url\((imgs/[^)]+)\)', _abs_url, qss)
    except Exception:
        pass
    return qss
