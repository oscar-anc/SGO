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
    # S0  QWIDGET GLOBAL RESET  +  QPALETTE
    #
    # Variables consumed by two mechanisms:
    #   1. build_qss()     → QWidget {{ }} rule (font, color, background, outline)
    #   2. build_palette() → QPalette roles that override OS light/dark mode
    #
    # QPalette role mapping:
    #   app_bg        → Window, Button
    #   text_primary  → WindowText, Text, ButtonText
    #   surface       → Base
    #   surface_alt   → AlternateBase
    #   selection_bg  → Highlight
    #   text_on_dark  → HighlightedText
    #   text_disabled → Disabled/Text, Disabled/ButtonText
    # =========================================================================

    # ── App / window background ───────────────────────────────────────────────
    'app_bg':                       '#191A1B',   # QPalette.Window + QPalette.Button

    # ── Text ──────────────────────────────────────────────────────────────────
    'text_primary':                 '#4f5f6f',   # QPalette.WindowText / .Text / .ButtonText
    'text_on_dark':                 '#FFFFFF',   # QPalette.HighlightedText
    'text_disabled':                '#a1b1c2',   # QPalette.Disabled Text + ButtonText

    # ── Surfaces ──────────────────────────────────────────────────────────────
    'surface':                      '#FFFFFF',   # QPalette.Base (input background)
    'surface_alt':                  '#e1ecf7',   # QPalette.AlternateBase (alt rows)

    # ── Selection ─────────────────────────────────────────────────────────────
    'selection_bg':                 '#59c2e6',   # QPalette.Highlight

    # ── QWidget global outline (focus ring suppression for ALL widgets) ────────
    # Drives: QWidget { outline: <value> }
    # Setting to 'none' removes the dotted focus rectangle Qt draws by default.
    'qwidget_focus_outline':        'none',

    # ── App-level font family ─────────────────────────────────────────────────
    # app_font_family: the font family passed to app.setFont() at startup.
    # Controls both the antialiasing strategy applied globally and serves as the
    # canonical font name for Qt's font database lookup.
    # Must match the family name Qt registers when loading the .ttf/.otf files
    # from the fonts/ folder (logged to console at startup).
    # All widget_font_family values in QSSD should point to this same string
    # unless you intentionally want a different typeface per widget.
    'app_font_family':              'Ancizar Sans',

    # ── Typography ────────────────────────────────────────────────────────────

    # ── Logo ──────────────────────────────────────────────────────────────────
    # logo_path: relative path string from project root, e.g. 'imgs/logo_white.svg'
    'logo_path':                    'imgs/logo_white.svg',

    # ── Dim overlay (Python-only — not used in QSS) ───────────────────────────
    # overlay_color: CSS hex color string for the semi-transparent dim layer
    # overlay_opacity: integer string '0'–'255' (Qt alpha channel, not CSS 0–1)
    'overlay_color':                '#000000',
    'overlay_opacity':              '120',

    # =========================================================================
    # S1  GLOBAL RESET / QWIDGET
    # =========================================================================
    # Uses: app_bg, text_primary, qwidget_focus_outline

    # =========================================================================
    # S2  SCROLLBAR
    # =========================================================================

    'scrollbar_track_bg':           '#2e2f37',
    'scrollbar_border':             'none',
    'scrollbar_width':              '10',
    'scrollbar_margin':             '0',
    'scrollbar_handle_bg':          '#a6abb3',
    'scrollbar_handle_radius':      '5px',
    'scrollbar_handle_min':         '30',
    'scrollbar_handle_margin':      '1px',
    'scrollbar_handle_bg_hover':    '#d3d9e3',
    'scrollbar_handle_bg_pressed':  '#d3d9e3',
    # add-line / sub-line / add-page / sub-page suppression
    'scrollbar_line_bg':            'none',
    'scrollbar_line_border':        'none',
    'scrollbar_line_height':        '0',
    'scrollbar_line_width':         '0',

    # =========================================================================
    # S3  QSCROLLAREA
    # =========================================================================

    'scrollarea_bg':                '#191A1B',
    'scrollarea_border':            'none',

    # =========================================================================
    # S4a  QLABEL
    # =========================================================================

    'label_color':                  '#ededed', 
    'label_bg':                     'transparent',
    'label_border':                 'none',
    'label_outline':                'none',
    # typography
    'label_font_family':            'Ancizar Sans',
    'label_font_size':              '10.5pt',
    'label_font_weight':            '400',
    # font-weight flag: 'bold' or 'normal'

    # =========================================================================
    # S4b  QRADIOBUTTON
    # =========================================================================

    'radio_widget_color':           '#ededed',
    'radio_widget_bg':              'transparent',
    'radio_widget_border':          'none',
    'radio_widget_outline':         'none',
    # typography
    'radio_font_family':            'Ancizar Sans',
    'radio_font_size':              '10.5pt',
    'radio_font_weight':            '400',
    'radio_spacing':                '8',
    # indicator
    'radio_indicator_size':         '16',
    'radio_indicator_radius':       '10px',
    'radio_indicator_bg':           '#242526',
    # indicator border sides (all equal at rest)
    'radio_border_top':             '2px solid #333536',
    'radio_border_right':           '2px solid #333536',
    'radio_border_bottom':          '2px solid #333536',
    'radio_border_left':            '2px solid #333536',
    # hover
    'radio_border_top_hover':       '2px solid #3994BC',
    'radio_border_right_hover':     '2px solid #3994BC',
    'radio_border_bottom_hover':    '2px solid #3994BC',
    'radio_border_left_hover':      '2px solid #3994BC',
    # checked — gradient encodes all stop values as a single CSS string
    'radio_checked':                'url(imgs/radio_checked.svg)',
    'radio_border_top_checked':     '2px solid #3994BC',
    'radio_border_right_checked':   '2px solid #3994BC',
    'radio_border_bottom_checked':  '2px solid #3994BC',
    'radio_border_left_checked':    '2px solid #3994BC',

    # =========================================================================
    # S5  QLINEEDIT
    # =========================================================================

    'lineedit_bg':                  '#191A1B',
    'lineedit_color':               '#858889',
    'lineedit_padding':             '3px 3px',
    'lineedit_min_height':          '20',
    'lineedit_min_width':           '60',
    'lineedit_selection_bg':        'rgba(39, 103, 130, 0.87)',
    'lineedit_outline':             'none',
    'lineedit_bg_hover':            'rgba(255, 255, 255, 0.06)',
    'lineedit_bg_focus':            'rgba(255, 255, 255, 0.06)',
    # typography
    'lineedit_font_family':         'Ancizar Sans',
    'lineedit_font_size':           '10.5pt',
    'lineedit_font_weight':         '400',
    'lineedit_radius':              '2px',
    # border sides — rest
    'lineedit_border_top':          '1px solid #2A2B2C',
    'lineedit_border_right':        '1px solid #2A2B2C',
    'lineedit_border_bottom':       '1px solid #2A2B2C',
    'lineedit_border_left':         '1px solid #2A2B2C',
    # border sides — hover
    'lineedit_border_top_hover':    '1px solid #3994BC',
    'lineedit_border_right_hover':  '1px solid #3994BC',
    'lineedit_border_bottom_hover': '1px solid #3994BC',
    'lineedit_border_left_hover':   '1px solid #3994BC',
    # border sides — focus
    'lineedit_border_top_focus':    '1px solid #3994BC',
    'lineedit_border_right_focus':  '1px solid #3994BC',
    'lineedit_border_bottom_focus': '1px solid #3994BC',
    'lineedit_border_left_focus':   '1px solid #3994BC',
    'lineedit_color_focus':         '#bfbfbf',
    # border sides — read-only / disabled (same as rest)
    'lineedit_border_top_ro':       '1px solid #333536',
    'lineedit_border_right_ro':     '1px solid #333536',
    'lineedit_border_bottom_ro':    '1px solid #333536',
    'lineedit_border_left_ro':      '1px solid #333536',
    # states
    'lineedit_bg_readonly':         '#191A1B',
    'lineedit_bg_disabled':         '#191A1B',
    'lineedit_color_disabled':      '#555555',
    # ── CardWidget Header sub-section (QLineEdit#CardTitle) ──────────────────
    'lineedit_card_header_bg':              'transparent',
    'lineedit_card_header_color':           '#ededed',
    'lineedit_card_header_placeholder':     'rgba(255,255,255,140)',
    'lineedit_card_header_border_top':      'none',
    'lineedit_card_header_border_right':    'none',
    'lineedit_card_header_border_bottom':   'none',
    'lineedit_card_header_border_left':     'none',
    'lineedit_card_header_radius':          'none',
    'lineedit_card_header_font_size':       '10.5pt',
    'lineedit_card_header_padding':         '3px 3px',
    'lineedit_card_header_min_height':      '20',
    'lineedit_card_header_selection_bg':    'rgba(255,255,255,80)',
    # typography
    'lineedit_card_header_font_family': 'Ancizar Sans',
    'lineedit_card_header_font_weight': '400',

    # =========================================================================
    # S6  QCOMBOBOX
    # =========================================================================

    'combobox_bg':                  '#191A1B',
    'combobox_color':               '#858889',
    'combobox_padding':             '3px 4px',
    'combobox_min_height':          '20',
    'combobox_min_width':           '60',
    'combobox_selection_bg':        'rgba(39, 103, 130, 0.87)',
    'combobox_outline':             'none',
    'combobox_bg_hover':            'rgba(255, 255, 255, 0.06)',
    'combobox_bg_focus':            'rgba(255, 255, 255, 0.06)',
    # typography
    'combobox_font_family':         'Ancizar Sans',
    'combobox_font_size':           '10.5pt',
    'combobox_font_weight':         '400',
    'combobox_radius':              '2px',
    # border sides — rest
    'combobox_border_top':          '1px solid #2A2B2C',
    'combobox_border_right':        '1px solid #2A2B2C',
    'combobox_border_bottom':       '1px solid #2A2B2C',
    'combobox_border_left':         '1px solid #2A2B2C',
    # border sides — hover
    'combobox_border_top_hover':    '1px solid #3994BC',
    'combobox_border_right_hover':  '1px solid #3994BC',
    'combobox_border_bottom_hover': '1px solid #3994BC',
    'combobox_border_left_hover':   '1px solid #3994BC',
    # border sides — focus
    'combobox_border_top_focus':    '1px solid #3994BC',
    'combobox_border_right_focus':  '1px solid #3994BC',
    'combobox_border_bottom_focus': '1px solid #3994BC',
    'combobox_border_left_focus':   '1px solid #3994BC',
    # drop-down arrow area
    'combobox_arrow_area_width':    '24',
    'combobox_arrow_area_border':   '1px solid #2A2B2C',
    'combobox_arrow_size':          '13',
    'combobox_arrow_down_img':      'url(imgs/arrow_down.svg)',
    'combobox_arrow_up_img':        'url(imgs/arrow_up.svg)',
    # drop-down arrow area  — hover
    'combobox_arrow_area_border_hover': '1px solid #3994BC',
    # drop-down arrow area  — focus
    'combobox_arrow_area_border_focus': '1px solid #3994BC',
    # popup / QAbstractItemView
    'combobox_popup_bg':            '#191A1B',
    'combobox_popup_color':         '#bfbfbf',
    'combobox_popup_border_top':    '1px solid #3994BC',
    'combobox_popup_border_right':  '1px solid #3994BC',
    'combobox_popup_border_bottom': '1px solid #3994BC',
    'combobox_popup_border_left':   '1px solid #3994BC',
    'combobox_popup_radius':        '0px',
    'combobox_popup_outline':       'none',
    'combobox_popup_padding':       '2px',
    # typography — popup list and items
    'combobox_popup_font_family':       'Ancizar Sans',
    'combobox_popup_font_size':         '10.5pt',
    'combobox_popup_font_weight':       '400',
    'combobox_item_font_family':        'Ancizar Sans',
    'combobox_item_font_size':          '10.5pt',
    'combobox_item_font_weight':        '400',
    'combobox_popup_selection_bg':      '#262728',
    # popup item
    'combobox_item_min_height':     '28',
    'combobox_item_padding':        '2px 8px',
    'combobox_item_radius':         '2px',
    'combobox_item_bg_hover':       'rgba(57, 148, 188, 0.15)',
    'combobox_item_color_hover':    '#ededed',
    'combobox_item_bg_selected':    'rgba(57, 148, 188, 0.15)',
    'combobox_item_color_selected': '#FFFFFF',
    # ── CardWidget Header sub-section (QComboBox#CardTitle) ──────────────────
    'combobox_card_header_bg':              'transparent',
    'combobox_card_header_color':           '#FFFFFF',
    'combobox_card_header_border_top':      'none',
    'combobox_card_header_border_right':    'none',
    'combobox_card_header_border_bottom':   'none',
    'combobox_card_header_border_left':     'none',
    'combobox_card_header_font_family':     'Ancizar Sans',
    'combobox_card_header_font_size':       '10.5pt',
    'combobox_card_header_font_weight':     '600',
    'combobox_card_header_padding':         '3px 3px',
    'combobox_card_header_min_height':      '20',
    # embedded QLineEdit inside card-header combo
    'combobox_card_header_edit_bg':         'transparent',
    'combobox_card_header_edit_color':      '#FFFFFF',
    'combobox_card_header_edit_border_top': 'none',
    'combobox_card_header_edit_border_right':'none',
    'combobox_card_header_edit_border_bottom':'none',
    'combobox_card_header_edit_border_left':'none',
    # drop-down / arrow in card header (hidden)
    'combobox_card_header_dd_border':       'none',
    'combobox_card_header_arrow_width':     '0px',
    'combobox_card_header_arrow_height':    '0px',

    # =========================================================================
    # S7a  QDATEEDIT
    # =========================================================================

    'dateedit_bg':                  '#191A1B',
    'dateedit_color':               '#858889',
    'dateedit_padding':             '2px 5px',
    'dateedit_min_height':          '19',
    'dateedit_min_width':           '75',
    'dateedit_outline':             'none',
    'dateedit_selection_bg':        'rgba(39, 103, 130, 0.87)',
    # typography
    'dateedit_font_family':         'Ancizar Sans',
    'dateedit_font_size':           '10.5pt',
    'dateedit_font_weight':         '400',
    'dateedit_radius':              '2px',
    # border sides — rest
    'dateedit_border_top':          '1px solid #2A2B2C',
    'dateedit_border_right':        '1px solid #2A2B2C',
    'dateedit_border_bottom':       '1px solid #2A2B2C',
    'dateedit_border_left':         '1px solid #2A2B2C',
    # border sides — hover
    'dateedit_border_top_hover':    '1px solid #3994BC',
    'dateedit_border_right_hover':  '1px solid #3994BC',
    'dateedit_border_bottom_hover': '1px solid #3994BC',
    'dateedit_border_left_hover':   '1px solid #3994BC',
    'dateedit_bg_hover':            'rgba(255, 255, 255, 0.06)',
    # border sides — focus
    'dateedit_border_top_focus':    '1px solid #3994BC',
    'dateedit_border_right_focus':  '1px solid #3994BC',
    'dateedit_border_bottom_focus': '1px solid #3994BC',
    'dateedit_border_left_focus':   '1px solid #3994BC',
    'dateedit_color_focus':         '#bfbfbf',
    'dateedit_bg_focus':            'rgba(255, 255, 255, 0.06)',
    # drop-down arrow area
    'dateedit_arrow_area_width':    '0',
    'dateedit_arrow_area_border':   'none',
    'dateedit_arrow_size':          '0',

    # =========================================================================
    # S8  QCHECKBOX
    # =========================================================================

    'checkbox_widget_color':        '#ededed',
    'checkbox_widget_bg':           'transparent',
    'checkbox_widget_border':       'none',
    'checkbox_widget_outline':      'none',
    # typography
    'checkbox_font_family':         'Ancizar Sans',
    'checkbox_font_size':           '10.5pt',
    'checkbox_font_weight':         '400',
    'checkbox_spacing':             '8',
    # indicator
    'checkbox_indicator_size':      '16',
    'checkbox_indicator_bg':        '#242526',
    'checkbox_indicator_radius':    '3px',
    'checkbox_indicator_border_top':    '2px solid #333536',
    'checkbox_indicator_border_right':  '2px solid #333536',
    'checkbox_indicator_border_bottom': '2px solid #333536',
    'checkbox_indicator_border_left':   '2px solid #333536',
    # hover
    'checkbox_indicator_border_top_hover':    '2px solid #3994BC',
    'checkbox_indicator_border_right_hover':  '2px solid #3994BC',
    'checkbox_indicator_border_bottom_hover': '2px solid #3994BC',
    'checkbox_indicator_border_left_hover':   '2px solid #3994BC',
    # checked
    'checkbox_indicator_bg_checked':    '#3994BC',
    'checkbox_indicator_border_top_checked':    '2px solid #3994BC',
    'checkbox_indicator_border_right_checked':  '2px solid #3994BC',
    'checkbox_indicator_border_bottom_checked': '2px solid #3994BC',
    'checkbox_indicator_border_left_checked':   '2px solid #3994BC',
    'checkbox_indicator_img_checked':   'url(imgs/check.svg)',
    # indeterminate
    'checkbox_indicator_bg_indeterminate':  '#3994BC',
    'checkbox_indicator_border_top_indeterminate':    '2px solid #3994BC',
    'checkbox_indicator_border_right_indeterminate':  '2px solid #3994BC',
    'checkbox_indicator_border_bottom_indeterminate': '2px solid #3994BC',
    'checkbox_indicator_border_left_indeterminate':   '2px solid #3994BC',
    'checkbox_indicator_img_indeterminate': 'url(imgs/check_indeterminate.svg)',

    # =========================================================================
    # S9  QGROUPBOX
    # =========================================================================

    'groupbox_bg':                  '#FFFFFF',
    'groupbox_color':               '#4f5f6f',
    'groupbox_font_size':           '10pt',
    # font-weight flag: 'bold' or 'normal'
    'groupbox_font_weight':         'bold',
    # typography
    'groupbox_font_family':             'Ancizar Sans',
    'groupbox_title_font_family':       'Ancizar Sans',
    'groupbox_title_font_size':         '10pt',
    'groupbox_title_font_weight':       '700',
    'groupbox_margin_top':          '14px',
    'groupbox_padding':             '14px 12px 12px 12px',
    'groupbox_radius':              '0px',
    # border sides — all equal
    'groupbox_border_top':          '1px solid #475564',
    'groupbox_border_right':        '1px solid #475564',
    'groupbox_border_bottom':       '1px solid #475564',
    'groupbox_border_left':         '1px solid #475564',
    # title
    'groupbox_title_subcontrol_origin': 'margin',
    'groupbox_title_subcontrol_pos':    'top left',
    'groupbox_title_left':          '12px',
    'groupbox_title_top':           '-1px',
    'groupbox_title_padding':       '0 3px',
    'groupbox_title_color':         '#4f5f6f',
    'groupbox_title_bg':            '#f0f3f6',

    # =========================================================================
    # S10  QPUSHBUTTON — BASE (generic navy, unlabeled buttons)
    # =========================================================================

    'btn_bg':                       '#4f5f6f',
    'btn_color':                    '#FFFFFF',
    'btn_border_top':               '1px solid #4f5f6f',
    'btn_border_right':             '1px solid #4f5f6f',
    'btn_border_bottom':            '1px solid #4f5f6f',
    'btn_border_left':              '1px solid #4f5f6f',
    'btn_radius':                   '4px',
    'btn_padding':                  '4px 12px',
    'btn_min_height':               '30',
    'btn_min_width':                '76',
    # typography
    'btn_font_family':              'Ancizar Sans',
    'btn_font_size':                '10pt',
    'btn_font_weight':              '700',
    'btn_bg_hover':                 '#59c2e6',
    'btn_color_hover':              '#FFFFFF',
    'btn_bg_pressed':               '#3aaac8',
    'btn_color_pressed':            '#FFFFFF',
    'btn_bg_disabled':              '#a1b1c2',
    'btn_color_disabled':           '#FFFFFF',

    # =========================================================================
    # S11  QPUSHBUTTON — NAMED ACTION BUTTONS
    # =========================================================================


    'btn_danger_bg':                'transparent',
    'btn_danger_color':             '#fc4c7a',
    'btn_danger_border_top':        '1px solid #fc4c7a',
    'btn_danger_border_right':      '1px solid #fc4c7a',
    'btn_danger_border_bottom':     '1px solid #fc4c7a',
    'btn_danger_border_left':       '1px solid #fc4c7a',
    'btn_danger_radius':            '4px',
    'btn_danger_padding':           '4px 12px',
    'btn_danger_min_height':        '30',
    'btn_danger_min_width':         '70',
    'btn_danger_bg_hover':          '#fc4c7a',
    'btn_danger_color_hover':       '#FFFFFF',
    'btn_danger_border_top_hover':  'none',
    'btn_danger_border_right_hover':'none',
    'btn_danger_border_bottom_hover':'none',
    'btn_danger_border_left_hover': 'none',

    # ── role="danger" (generic danger role) ────────────────────────────────────
    # Shares values with NavBar danger — separate variables for independence
    'btn_role_danger_bg':               'transparent',
    'btn_role_danger_color':            '#fc4c7a',
    'btn_role_danger_border_top':       '1px solid #fc4c7a',
    'btn_role_danger_border_right':     '1px solid #fc4c7a',
    'btn_role_danger_border_bottom':    '1px solid #fc4c7a',
    'btn_role_danger_border_left':      '1px solid #fc4c7a',
    'btn_role_danger_radius':           '4px',
    'btn_role_danger_padding':          '4px 12px',
    'btn_role_danger_min_height':       '30',
    'btn_role_danger_min_width':        '70',
    'btn_role_danger_bg_hover':         '#fc4c7a',
    'btn_role_danger_color_hover':      '#FFFFFF',
    'btn_role_danger_border_top_hover': 'none',
    'btn_role_danger_border_right_hover':'none',
    'btn_role_danger_border_bottom_hover':'none',
    'btn_role_danger_border_left_hover':'none',

    # ── Cesiones danger (role="cesiones-danger") ─────────────────────────────
    'btn_ces_danger_bg':                'transparent',
    'btn_ces_danger_color':             '#fc4c7a',
    'btn_ces_danger_border_top':        '1px solid #fc4c7a',
    'btn_ces_danger_border_right':      '1px solid #fc4c7a',
    'btn_ces_danger_border_bottom':     '1px solid #fc4c7a',
    'btn_ces_danger_border_left':       '1px solid #fc4c7a',
    'btn_ces_danger_radius':            '4px',
    'btn_ces_danger_padding':           '0px 8px',
    'btn_ces_danger_height':            '26',
    'btn_ces_danger_bg_hover':          '#fc4c7a',
    'btn_ces_danger_color_hover':       '#FFFFFF',
    'btn_ces_danger_border_top_hover':  'none',
    'btn_ces_danger_border_right_hover':'none',
    'btn_ces_danger_border_bottom_hover':'none',
    'btn_ces_danger_border_left_hover': 'none',

    # ── Cesiones neutral (role="cesiones-neutral") ────────────────────────────
    'btn_ces_neutral_bg':               '#4f5f6f',
    'btn_ces_neutral_color':            '#FFFFFF',
    'btn_ces_neutral_border_top':       '1px solid #4f5f6f',
    'btn_ces_neutral_border_right':     '1px solid #4f5f6f',
    'btn_ces_neutral_border_bottom':    '1px solid #4f5f6f',
    'btn_ces_neutral_border_left':      '1px solid #4f5f6f',
    'btn_ces_neutral_radius':           '4px',
    'btn_ces_neutral_padding':          '0px 8px',
    'btn_ces_neutral_height':           '26',
    'btn_ces_neutral_bg_hover':         '#59c2e6',


    # ── pagePolicies: QUITAR PÓLIZA / QUITAR ASEGURADO (text) ─────────────────
    'btn_quitar_text_bg':               'transparent',
    'btn_quitar_text_color':            '#fc4c7a',
    'btn_quitar_text_border_top':       '1px solid #fc4c7a',
    'btn_quitar_text_border_right':     '1px solid #fc4c7a',
    'btn_quitar_text_border_bottom':    '1px solid #fc4c7a',
    'btn_quitar_text_border_left':      '1px solid #fc4c7a',
    'btn_quitar_text_radius':           '4px',
    'btn_quitar_text_padding':          '4px 12px',
    'btn_quitar_text_min_height':       '30',
    'btn_quitar_text_min_width':        '100px',
    'btn_quitar_text_bg_hover':         '#fc4c7a',
    'btn_quitar_text_color_hover':      '#FFFFFF',
    'btn_quitar_text_border_top_hover': 'none',
    'btn_quitar_text_border_right_hover':'none',
    'btn_quitar_text_border_bottom_hover':'none',
    'btn_quitar_text_border_left_hover':'none',

    # ── Card header: role="quitar" (icon-only trash pill) ─────────────────────
    'btn_quitar_icon_bg':           '#e05570',
    'btn_quitar_icon_border_top':   'none',
    'btn_quitar_icon_border_right': 'none',
    'btn_quitar_icon_border_bottom':'none',
    'btn_quitar_icon_border_left':  'none',
    'btn_quitar_icon_radius':       '4px',
    'btn_quitar_icon_padding':      '3px',
    'btn_quitar_icon_size':         '26',
    'btn_quitar_icon_bg_hover':     '#c0304a',

    # ── Excel icon-only (role="excel-icon") ───────────────────────────────────
    'btn_excel_icon_bg':            'none',
    'btn_excel_icon_border_top':    'none',
    'btn_excel_icon_border_right':  'none',
    'btn_excel_icon_border_bottom': 'none',
    'btn_excel_icon_border_left':   'none',
    'btn_excel_icon_radius':        '4px',
    'btn_excel_icon_padding':       '2px',
    'btn_excel_icon_size':          '20',
    'btn_excel_icon_bg_hover':      '#2A8A55',

    # ── Excel text (role="excel-text") ────────────────────────────────────────
    'btn_excel_text_bg':            'none',
    'btn_excel_text_color':         '#FFFFFF',
    'btn_excel_text_border_top':    'none',
    'btn_excel_text_border_right':  'none',
    'btn_excel_text_border_bottom': 'none',
    'btn_excel_text_border_left':   'none',
    'btn_excel_text_radius':        '4px',
    'btn_excel_text_padding':       '0px 12px',
    'btn_excel_text_height':        '30',
    # typography
    'btn_excel_text_font_family':       'Ancizar Sans',
    'btn_excel_text_font_size':         '10pt',
    'btn_excel_text_font_weight':       '700',
    'btn_excel_text_bg_hover':      '#217346',

    # ── Download template (role="download") ───────────────────────────────────
    'btn_download_bg':              'transparent',
    'btn_download_color':           'none',
    'btn_download_border_top':      'none',
    'btn_download_border_right':    'none',
    'btn_download_border_bottom':   'none',
    'btn_download_border_left':     'none',
    'btn_download_radius':          '4px',
    'btn_download_padding':         '0px 12px',
    'btn_download_height':          '30',
    # typography
    'btn_download_font_family':         'Ancizar Sans',
    'btn_download_font_size':           '10pt',
    'btn_download_font_weight':         '400',
    'btn_download_bg_hover':        '#217346',
    'btn_download_color_hover':     '#FFFFFF',
    'btn_download_border_top_hover': 'none',
    'btn_download_border_right_hover':'none',
    'btn_download_border_bottom_hover':'none',
    'btn_download_border_left_hover':'none',

    # ── EndorsementTableCard header: Ver (role="endtable-view") ──────────────
    'btn_endtable_view_bg':             'none',
    'btn_endtable_view_border_top':     'none',
    'btn_endtable_view_border_right':   'none',
    'btn_endtable_view_border_bottom':  'none',
    'btn_endtable_view_border_left':    'none',
    'btn_endtable_view_radius':         '4px',
    'btn_endtable_view_padding':        '2px',
    'btn_endtable_view_size':           '20',
    'btn_endtable_view_bg_hover':       '#242526',

    # ── EndorsementTableCard header: Editar (role="endtable-edit") ───────────
    'btn_endtable_edit_bg':             'none',
    'btn_endtable_edit_border_top':     'none',
    'btn_endtable_edit_border_right':   'none',
    'btn_endtable_edit_border_bottom':  'none',
    'btn_endtable_edit_border_left':    'none',
    'btn_endtable_edit_radius':         '4px',
    'btn_endtable_edit_padding':        '2px',
    'btn_endtable_edit_size':           '20',
    'btn_endtable_edit_bg_hover':       '#242526',

    # ── EndorsementTableCard header: Import Excel (role="endtable-import") ───
    'btn_endtable_import_bg':               'none',
    'btn_endtable_import_border_top':       'none',
    'btn_endtable_import_border_right':     'none',
    'btn_endtable_import_border_bottom':    'none',
    'btn_endtable_import_border_left':      'none',
    'btn_endtable_import_radius':           '2px',
    'btn_endtable_import_padding':          '2px',
    'btn_endtable_import_size':             '18',
    'btn_endtable_import_bg_hover':         '#254A3A',

    # ── Accordion toggle (role="accordion") ───────────────────────────────────
    'btn_accordion_bg':                     'none',
    'btn_accordion_border_top':             'none',
    'btn_accordion_border_right':           'none',
    'btn_accordion_border_bottom':          'none',
    'btn_accordion_border_left':            'none',
    'btn_accordion_radius':                 '4px',
    'btn_accordion_padding':                '2px',
    'btn_accordion_size':                   '18px',
    'btn_accordion_color':                  '#858889',
    'btn_accordion_bg_hover':               '#242526',
    'btn_accordion_border_color_hover':     'none',
    'btn_accordion_bg_checked':             '#242526',
    'btn_accordion_border_color_checked':   'none',

    # ── Format selector (role="format-selector") — pageConfig ─────────────────
    'btn_format_bg':                '#FFFFFF',
    'btn_format_color':             '#4f5f6f',
    'btn_format_border_top':        '1px solid #C8D0D8',
    'btn_format_border_right':      '1px solid #C8D0D8',
    'btn_format_border_bottom':     '1px solid #C8D0D8',
    'btn_format_border_left':       '1px solid #C8D0D8',
    'btn_format_radius':            '4px',
    'btn_format_padding':           '6px 14px',
    'btn_format_min_width':         '110',
    'btn_format_icon_size':         '22',
    # typography
    'btn_format_font_family':           'Ancizar Sans',
    'btn_format_font_size':             '10pt',
    'btn_format_font_weight':       'normal',
    'btn_format_text_align':        'center',
    'btn_format_bg_hover':          '#e8f4fd',
    'btn_format_border_color_hover':'#59c2e6',
    'btn_format_bg_checked':        '#59c2e6',
    'btn_format_border_color_checked':'#3aaac8',
    'btn_format_color_checked':     '#FFFFFF',
    'btn_format_font_weight_checked':'bold',
    'btn_format_bg_checked_hover':  '#3aaac8',
    # Python-only layout values
    'format_btn_icon_h':            22,
    'format_btn_icon_gap':          4,
    'format_btn_text_gap':          6,
    'format_btn_row_spacing':       12,

    # ── Manual item (role="manual-item") — pageAnnex procedure list ───────────
    'btn_manual_bg':                '#191A1B',
    'btn_manual_color':             '#858889',
    'btn_manual_border_top':        '1px solid #2A2B2C',
    'btn_manual_border_right':      '1px solid #2A2B2C',
    'btn_manual_border_bottom':     '1px solid #2A2B2C',
    'btn_manual_border_left':       '1px solid #2A2B2C',
    'btn_manual_radius':            '4px',
    'btn_manual_padding':           '4px 6px',
    'btn_manual_min_height':        '26',
    'btn_manual_text_align':        'left',
    # typography
    'btn_manual_font_family':             'Ancizar Sans',
    'btn_manual_font_size':               '10pt',
    'btn_manual_font_weight':             '400',
    'btn_manual_bg_hover':              'rgba(255, 255, 255, 0.06)',
    'btn_manual_border_color_hover':    '#3994BC',
    'btn_manual_bg_checked':            'rgba(255, 255, 255, 0.06)',
    'btn_manual_border_color_checked':  '#3994BC',
    'btn_manual_color_checked':         '#bfbfbf',
    'btn_manual_font_weight_checked':     'bold',

    'btn_manual_bg_disabled':           '#191A1B',
    'btn_manual_border_color_disabled': '#333536',
    'btn_manual_color_disabled':        '#555555',
    'btn_manual_font_weight_disabled':    'normal',

    # ── Manual fixed (role="manual-fixed") — Aspectos Generales ──────────────
    'btn_manual_fixed_bg':            '#191A1B',
    'btn_manual_fixed_color':         '#555555',
    'btn_manual_fixed_border_top':      '1px solid #333536',
    'btn_manual_fixed_border_right':    '1px solid #333536',
    'btn_manual_fixed_border_bottom':   '1px solid #333536',
    'btn_manual_fixed_border_left':     '1px solid #333536',
    'btn_manual_fixed_radius':          '4px',
    'btn_manual_fixed_padding':         '2px 6px',
    'btn_manual_fixed_min_height':      '26',
    'btn_manual_fixed_text_align':      'center',
    # typography
    'btn_manual_fixed_font_family':     'Ancizar Sans',
    'btn_manual_fixed_font_size':       '10pt',
    'btn_manual_fixed_font_weight':     'bold',
    # disabled same as normal (intentional locked state)
    'btn_manual_fixed_bg_disabled':           '#191A1B',
    'btn_manual_fixed_color_disabled':        '#555555',
    'btn_manual_fixed_border_top_disabled':     '1px solid #333536',
    'btn_manual_fixed_border_right_disabled':   '1px solid #333536',
    'btn_manual_fixed_border_bottom_disabled':  '1px solid #333536',
    'btn_manual_fixed_border_left_disabled':    '1px solid #333536',
    'btn_manual_fixed_font_weight_disabled':    'bold',

    # ── Config gear (role="config-gear") — GroupEditor settings toggle ────────
    'btn_gear_bg':                  'transparent',
    'btn_gear_border_top':          'none',
    'btn_gear_border_right':        'none',
    'btn_gear_border_bottom':       'none',
    'btn_gear_border_left':         'none',
    'btn_gear_radius':              '4px',
    'btn_gear_padding':             '2px',
    'btn_gear_bg_hover':            '#59c2e6',
    'btn_gear_bg_checked':          '#59c2e6',

    # ── Column action (role="col-action") — GroupEditor column management ──────
    'btn_col_action_bg':            '#4f5f6f',
    'btn_col_action_border_top':    'none',
    'btn_col_action_border_right':  'none',
    'btn_col_action_border_bottom': 'none',
    'btn_col_action_border_left':   'none',
    'btn_col_action_radius':        '4px',
    'btn_col_action_padding':       '2px',
    'btn_col_action_bg_hover':      '#59c2e6',
    # danger variant
    'btn_col_danger_bg':            'transparent',
    'btn_col_danger_color':         '#FFFFFF',
    'btn_col_danger_border_top':    '1px solid transparent',
    'btn_col_danger_border_right':  '1px solid transparent',
    'btn_col_danger_border_bottom': '1px solid transparent',
    'btn_col_danger_border_left':   '1px solid transparent',
    'btn_col_danger_radius':        '4px',
    'btn_col_danger_padding':       '2px',
    'btn_col_danger_bg_hover':      '#fc4c7a',
    'btn_col_danger_border_color_hover': '#fc4c7a',

    # ── AppTitleBar: titlebar-min / titlebar-max ───────────────────────────────
    'btn_titlebar_bg':              'transparent',
    'btn_titlebar_color':           '#FFFFFF',
    'btn_titlebar_border_top':      'none',
    'btn_titlebar_border_right':    'none',
    'btn_titlebar_border_bottom':   'none',
    'btn_titlebar_border_left':     'none',
    'btn_titlebar_radius':          '0px',
    'btn_titlebar_padding':         '0px',
    'btn_titlebar_font_size':       '12px',
    'btn_titlebar_bg_hover':        '#59c2e6',

    # ── AppTitleBar: titlebar-close ────────────────────────────────────────────
    'btn_titlebar_close_bg':        'transparent',
    'btn_titlebar_close_color':     '#FFFFFF',
    'btn_titlebar_close_border_top':    'none',
    'btn_titlebar_close_border_right':  'none',
    'btn_titlebar_close_border_bottom': 'none',
    'btn_titlebar_close_border_left':   'none',
    'btn_titlebar_close_radius':    '0px',
    'btn_titlebar_close_padding':   '0px',
    'btn_titlebar_close_font_size': '12px',
    'btn_titlebar_close_bg_hover':  '#fc4c7a',
    'btn_titlebar_close_bg_pressed':'#d93060',

    # =========================================================================
    # S12  QTREEWIDGET
    # =========================================================================

    'tree_bg':                      '#FFFFFF',
    'tree_alt_row_bg':              '#f8fafc',
    'tree_color':                   '#4f5f6f',
    'tree_outline':                 'none',
    'tree_gridline':                '#C8D0D8',
    'tree_border_top':              '1px solid #C8D0D8',
    'tree_border_right':            '1px solid #C8D0D8',
    'tree_border_bottom':           '1px solid #C8D0D8',
    'tree_border_left':             '1px solid #C8D0D8',
    'tree_radius':                  '0px',
    # item
    'tree_item_min_height':         '28',
    'tree_item_padding':            '2px 4px',
    'tree_item_border_top':         'none',
    'tree_item_border_right':       'none',
    'tree_item_border_bottom':      '1px solid #C8D0D8',
    # typography
    'tree_font_family':                 'Ancizar Sans',
    'tree_font_size':                   '10pt',
    'tree_font_weight':                 '400',
    'tree_item_font_family':            'Ancizar Sans',
    'tree_item_font_size':              '10pt',
    'tree_item_font_weight':            '400',
    'tree_item_border_left':        'none',
    'tree_item_bg_hover':           '#e1ecf7',
    'tree_item_color_hover':        '#4f5f6f',
    'tree_item_bg_selected':        '#59c2e6',
    'tree_item_color_selected':     '#FFFFFF',
    # header
    'tree_header_border':           'none',
    'tree_header_section_bg':       '#191A1B',
    'tree_header_section_color':    '#FFFFFF',
    # font-weight flag for QTreeWidget + QTableWidget headers: 'bold' or 'normal'
    # typography
    'tree_header_font_family':          'Ancizar Sans',
    'tree_header_font_size':            '10pt',
    'tree_header_font_weight':          '700',
    'table_hdr_hz_font_family':         'Ancizar Sans',
    'table_hdr_hz_font_size':           '10pt',
    'table_hdr_vt_font_family':         'Ancizar Sans',
    'table_hdr_vt_font_size':           '10pt',
    'table_hdr_vt_font_weight':         '400',
    'tree_header_section_border_top':    'none',
    'tree_header_section_border_right':  '1px solid #475564',
    'tree_header_section_border_bottom': 'none',
    'tree_header_section_border_left':   'none',
    'tree_header_section_padding':  '4px 8px',
    'tree_header_section_min_height':'28',
    'tree_header_last_border_right':'none',
    # QTableWidget headers (EndorsementEditDialog)
    'table_hdr_hz_bg':              '#4f5f6f',
    'table_hdr_hz_color':           '#FFFFFF',
    'table_hdr_hz_font_weight':     'bold',
    'table_hdr_hz_padding':         '4px 6px',
    'table_hdr_hz_border_top':      'none',
    'table_hdr_hz_border_right':    '1px solid #C8D0D8',
    'table_hdr_hz_border_bottom':   'none',
    'table_hdr_hz_border_left':     'none',
    'table_hdr_vt_bg':              '#4f5f6f',
    'table_hdr_vt_color':           '#FFFFFF',
    'table_hdr_vt_padding':         '0px 1px',
    'table_hdr_vt_border_top':      'none',
    'table_hdr_vt_border_right':    'none',
    'table_hdr_vt_border_bottom':   '1px solid #C8D0D8',
    'table_hdr_vt_border_left':     'none',
    'table_vertical_header_width':  '28',

    # =========================================================================
    # S13  NAVBAR
    # =========================================================================

    'navbar_bg':                    '#191A1B',
    'navbar_min_height':            '50',
    'navbar_max_height':            '50',
    'navbar_border_top':            '1px solid #2A2B2C',
    'navbar_border_right':          'none',
    'navbar_border_bottom':         'none',
    'navbar_border_left':           'none',

    # =========================================================================
    # S14  CARDWIDGET
    # =========================================================================

    # #CardHeader
    'card_header_bg':               '#121314',
    'card_header_min_height':       '33',
    'card_header_max_height':       '33',
    'card_header_padding':          '0px 0px 0px 0px',
    'card_header_radius':           '0px',
    'card_header_border_top':       '1px solid #3a94bc',
    'card_header_border_right':     '1px solid #2A2B2C',
    'card_header_border_bottom':    '1px solid #2A2B2C',
    'card_header_border_left':      '1px solid #2A2B2C',
    # #CardTitle (QLabel in header)
    'card_title_color':             '#ededed',
    'card_title_bg':                'transparent',
    # font-weight flag for CardTitle label: 'bold' or 'normal'
    # typography
    'card_title_font_family':           'Ancizar Sans',
    'card_title_font_size':             '12pt',
    'card_title_font_weight':           '700',
    'card_toggle_font_family':          'Ancizar Sans',
    'card_toggle_font_size':            '12pt',
    'card_toggle_font_weight':          '700',
    # #CardToggle (chevron label)
    'card_toggle_color':            '#858889',
    'card_toggle_bg':               'transparent',
    'card_toggle_bg_hover':         '#242526',
    # Python-accessed SVG color (cards.py, pageAnnex.py, endorsement.py paint accordion chevrons)
    'card_header_toggle':           '#858889',
    # #CardBody
    'card_body_bg':                 '#121314',
    'card_body_padding':            '0px 0px 0px 0px',
    'card_body_radius':             '0px',
    'card_body_border_top':       'none',
    'card_body_border_right':     '1px solid #2A2B2C',
    'card_body_border_bottom':    '1px solid #2A2B2C',
    'card_body_border_left':      '1px solid #2A2B2C',
    # ── CardBody sub-section: QLineEdit inside #CardBody ─────────────────────
    # ── CardBody sub-section: QComboBox inside #CardBody ─────────────────────
    # ── CardBody sub-section: QDateEdit inside #CardBody ─────────────────────
    # card header input variants (for Python layout use)

    # =========================================================================
    # S15  CUSTOMMESSAGEBOX
    # =========================================================================

    # #MsgFrame
    'msg_frame_bg':                 '#FFFFFF',
    'msg_frame_border_top':         '1px solid #dce6f0',
    'msg_frame_border_right':       '1px solid #dce6f0',
    'msg_frame_border_bottom':      '1px solid #dce6f0',
    'msg_frame_border_left':        '1px solid #dce6f0',
    'msg_frame_radius':             '0px',
    # #MsgTitleBar
    'msg_titlebar_bg':              '#4f5f6f',
    'msg_titlebar_radius':          '0px',
    'msg_titlebar_min_height':      '40',
    'msg_titlebar_max_height':      '40',
    # #MsgTitle
    'msg_title_color':              '#FFFFFF',
    'msg_title_bg':                 'transparent',
    # font-weight flag: 'bold' or 'normal'
    # typography
    'msg_title_font_family':        'Ancizar Sans',
    'msg_title_font_size':          '11pt',
    'msg_title_font_weight':        '700',
    # #MsgBody
    'msg_body_bg':                  '#FFFFFF',
    'msg_body_radius':              '0px',
    'msg_body_padding':             '16px',
    # #MsgText
    'msg_text_color':               '#4f5f6f',
    'msg_text_bg':                  'transparent',
    # font-weight flag: 'bold' or 'normal'
    # typography
    'msg_text_font_family':         'Ancizar Sans',
    'msg_text_font_size':           '10pt',
    'msg_text_font_weight':         '400',
    # #MsgBtnPrimary
    'msg_btn_primary_bg':           '#59c2e6',
    'msg_btn_primary_color':        '#FFFFFF',
    # font-weight flag shared by MsgBtnPrimary and MsgBtnSecondary: 'bold' or 'normal'
    'msg_btn_font_weight':          'bold',
    # typography
    'msg_btn_primary_font_family':      'Ancizar Sans',
    'msg_btn_primary_font_size':        '10pt',
    'msg_btn_primary_font_weight':      '700',
    'msg_btn_secondary_font_family':    'Ancizar Sans',
    'msg_btn_secondary_font_size':      '10pt',
    'msg_btn_secondary_font_weight':    '700',
    'msg_btn_primary_border_top':       '1px solid #59c2e6',
    'msg_btn_primary_border_right':     '1px solid #59c2e6',
    'msg_btn_primary_border_bottom':    '1px solid #59c2e6',
    'msg_btn_primary_border_left':      '1px solid #59c2e6',
    'msg_btn_primary_radius':           '0px',
    'msg_btn_primary_padding':          '7px 20px',
    'msg_btn_primary_min_width':        '76',
    'msg_btn_primary_min_height':       '34',
    'msg_btn_primary_bg_hover':         '#3aaac8',
    # #MsgBtnSecondary
    'msg_btn_secondary_bg':             'transparent',
    'msg_btn_secondary_color':          '#4f5f6f',
    'msg_btn_secondary_border_top':     '1px solid #475564',
    'msg_btn_secondary_border_right':   '1px solid #475564',
    'msg_btn_secondary_border_bottom':  '1px solid #475564',
    'msg_btn_secondary_border_left':    '1px solid #475564',
    'msg_btn_secondary_radius':         '0px',
    'msg_btn_secondary_padding':        '7px 20px',
    'msg_btn_secondary_min_width':      '76',
    'msg_btn_secondary_min_height':     '34',
    'msg_btn_secondary_bg_hover':       '#e1ecf7',
    # close button hover
    # Variant accent colors

    # =========================================================================
    # S16  CESIONES / ENDORSEMENTTABLECARD
    # =========================================================================

    # #EndorsementCard
    'endcard_bg':                   'transparent',
    'endcard_border_top':           'none',
    'endcard_border_right':         'none',
    'endcard_border_bottom':        'none',
    'endcard_border_left':          'none',
    'endcard_radius':               '0px',
    'endcard_label_color':          '#bfbfbf',
    # typography
    'endcard_label_font_family':    'Ancizar Sans',
    'endcard_label_font_size':      '10pt',
    'endcard_label_font_weight':    '400',
    'endcard_label_bg':             'transparent',
    'endcard_checkbox_color':       '#bfbfbf',
    'endcard_checkbox_bg':          'transparent',
    # #InsuredGroupHeader
    'insured_hdr_bg':               'transparent',
    'insured_hdr_border_top':       '1px solid #2A2B2C',
    'insured_hdr_border_right':     '1px solid #2A2B2C',
    'insured_hdr_border_bottom':    '1px solid #2A2B2C',
    'insured_hdr_border_left':      '1px solid #2A2B2C',
    'insured_hdr_radius':           '0px',
    'insured_hdr_label_color':      '#ededed',
    'insured_hdr_label_bg':         'transparent',
    'insured_hdr_label_fw':         'bold',
    # typography
    'insured_hdr_label_font_family':    'Ancizar Sans',
    'insured_hdr_label_font_size':      '11pt',
    'insured_hdr_label_font_weight':    '700',
    'insured_hdr_toggle_color':       '#FFFFFF',
    # #InsuredGroupBody
    'insured_body_bg':              'transparent',
    'insured_body_border_top':      'none',
    'insured_body_border_right':    '1px solid #2A2B2C',
    'insured_body_border_bottom':   '1px solid #2A2B2C',
    'insured_body_border_left':     '1px solid #2A2B2C',
    'insured_body_padding':         '0px',
    # format-selector (pageConfig output buttons) — see S11
    # #ConfigPanel
    'config_panel_bg':              '#FFFFFF',
    'config_panel_border_top':      'none',
    'config_panel_border_right':    '1px solid #C8D0D8',
    'config_panel_border_bottom':   '1px solid #C8D0D8',
    'config_panel_border_left':     '1px solid #C8D0D8',

    # =========================================================================
    # S17  APPTITLEBAR (CustomDialog frameless titlebar)
    # =========================================================================

    # Python-accessed color keys (app.py, dialog.py use these to paint SVG icon colors)
    'titlebar_btn_text':            '#8C8C8C',        # icon color for min/max/close buttons
    'titlebar_btn_hover_bg':        '#383939',        # min/max hover background
    'titlebar_btn_pressed_bg':      '#555556',        # min/max pressed background
    'titlebar_close_hover_bg':      '#e81123',        # close button hover background
    'titlebar_close_pressed_bg':    '#941520',        # close button pressed background
    'titlebar_bg':                  '#191a1b',
    'titlebar_min_height':          '35',
    'titlebar_max_height':          '35',
    # #AppTitleLabel
    'titlebar_label_color':         '#FFFFFF',
    'titlebar_label_bg':            'transparent',
    'titlebar_label_font_weight':   'bold',
    # typography
    'titlebar_label_font_family':   'Ancizar Sans',
    'titlebar_label_font_size':     '10pt',
    'titlebar_label_font_size':     '10pt',
    # button sizes (shared between min/max/close for consistent bar)
    'titlebar_btn_width':           '45',
    'titlebar_btn_height':          '35',

    # =========================================================================
    # S18  MISCELLANEOUS / PAGE-SPECIFIC
    # =========================================================================

    # #InstructionLabel
    'instruction_label_color':        '#6b7c8d',
    'instruction_label_font_size':      '9pt',
    'instruction_label_font_weight':    'normal',
    # typography
    'instruction_label_font_family':    'Ancizar Sans',
    'instruction_label_font_size':      '9pt',

    # QTabWidget (Cesiones Individual mode)
    'tab_pane_bg':                  '#FFFFFF',
    'tab_pane_top_offset':          '-1px',
    'tab_pane_margin':              '0px',
    'tab_pane_padding':             '0px',
    'tab_pane_border_top':          'none',
    'tab_pane_border_right':        '1px solid #4f5f6f',
    'tab_pane_border_bottom':       '1px solid #4f5f6f',
    'tab_pane_border_left':         '1px solid #4f5f6f',
    'tab_widget_margin':            '0px',
    'tab_widget_padding':           '0px',
    # QTabBar::tab
    'tab_bg':                       '#FFFFFF',
    'tab_color':                    '#4f5f6f',
    'tab_border_top':               '1px solid #4f5f6f',
    'tab_border_right':             '1px solid #4f5f6f',
    'tab_border_bottom':            'none',
    'tab_border_left':              '1px solid #4f5f6f',
    'tab_radius_tl':                '4px',
    'tab_radius_tr':                '4px',
    'tab_padding':                  '4px 14px',
    'tab_min_height':               '32',
    'tab_margin_right':             '2px',
    'tab_selected_bg':              '#4f5f6f',
    'tab_selected_color':           '#FFFFFF',
    'tab_selected_font_weight':     'bold',
    'tab_inactive_bg':              '#FFFFFF',
    'tab_inactive_color':           '#4f5f6f',
    'tab_inactive_top_margin':      '2px',
    'tab_inactive_hover_bg':        '#4f5f6f',
    'tab_inactive_hover_color':     '#FFFFFF',
    # typography
    'tab_font_family':               'Ancizar Sans',
    'tab_font_size':                 '10pt',
    'tab_font_weight':               '400',
    'tab_selected_font_family':      'Ancizar Sans',
    'tab_selected_font_size':        '10pt',
    # CardWidget inside QTabWidget — suppress side borders
    'tab_cardbody_border_top':      'none',
    'tab_cardbody_border_right':    'none',
    'tab_cardbody_border_bottom':   'none',
    'tab_cardbody_border_left':     'none',
    'tab_cardheader_radius':        '0px',
    # QLineEdit#CardTitle (S18 duplicate rule — same as S5 sub-section)
    # QComboBox#CardTitle (S18 duplicate rule — same as S6 sub-section)

    # Toolbar buttons (Garantías editor: B/I/U/List/Clear)
    'toolbar_btn_bg':               '#e1ecf7',
    'toolbar_btn_color':            '#4f5f6f',
    # Python-accessed SVG color key (cards.py, pageAnnex.py paint B/I/U/List/Clear icons)
    'toolbar_button_text':          '#4f5f6f',
    'toolbar_btn_bg_hover':         '#c8d8e8',
    'toolbar_btn_border_top':       '1px solid #C8D0D8',
    'toolbar_btn_border_right':     '1px solid #C8D0D8',
    'toolbar_btn_border_bottom':    '1px solid #C8D0D8',
    'toolbar_btn_border_left':      '1px solid #C8D0D8',
    'toolbar_btn_radius':           '2px',
    'toolbar_btn_padding':          '3px 10px',
    'toolbar_btn_width':            '28',
    'toolbar_btn_height':           '28',
    'toolbar_btn_icon_size':        '14',
    # font-weight flag: 'bold' or 'normal'
    'toolbar_btn_font_weight':      'normal',
    # typography
    'toolbar_btn_font_family':       'Ancizar Sans',
    'toolbar_btn_font_size':         '10pt',

    # QTextEdit (Garantías rich-text editor)
    'textedit_bg':                  '#FFFFFF',
    'textedit_color':               '#4f5f6f',
    'textedit_border_top':          '1px solid #C8D0D8',
    'textedit_border_right':        '1px solid #C8D0D8',
    'textedit_border_bottom':       '1px solid #C8D0D8',
    'textedit_border_left':         '1px solid #C8D0D8',
    'textedit_radius':              '2px',
    # typography
    'textedit_font_family':         'Ancizar Sans',
    'textedit_font_size':           '10pt',
    'textedit_font_weight':         '400',

    # =========================================================================
    # LAYOUT & SIZE VARIABLES (Python — NOT used in build_qss)
    # =========================================================================

    # ── Zero-margin/spacing wrappers ──────────────────────────────────────────
    'margins_zero':                 (0, 0, 0, 0),
    'spacing_zero':                 0,

    # ── NavBar layout ─────────────────────────────────────────────────────────
    'margins_nav':                  (12, 0, 12, 0),

    # ── CardWidget header layout ───────────────────────────────────────────────
    'margins_card_header':          (10, 6, 10, 6),
    'spacing_card_header':          20,

    # ── CardWidget body layout ─────────────────────────────────────────────────
    'margins_card_body':            (10, 0, 10, 0),
    'spacing_card_body':            0,

    # ── Inline rows ───────────────────────────────────────────────────────────
    'margins_inline_row':           (0, 0, 0, 0),

    # ── App window ────────────────────────────────────────────────────────────
    'app_min_width':                700,
    'app_min_height':               500,
    'margins_app_root':             (0, 0, 0, 0),
    'spacing_app_root':             0,

    # ── CustomTitleBar ────────────────────────────────────────────────────────
    'titlebar_fixed_height':        35,
    'dialog_titlebar_height':       30,

    # ── CustomMessageBox layout ───────────────────────────────────────────────
    'msg_box_min_width':            380,
    'margins_msg_body':             (24, 20, 24, 8),
    'spacing_msg_body':             20,
    'margins_msg_buttons':          (0, 0, 0, 0),
    'spacing_msg_buttons':          8,
    'msg_body_gap':                 4,

    # ── CardWidget base layout ─────────────────────────────────────────────────
    'card_header_fixed_height':     25,
    'card_toggle_fixed_size':       (22, 22),
    'card_body_min_height':         175,

    # ── EndorsementTableCard ──────────────────────────────────────────────────
    'endtable_header_height':       25,
    # Python-accessed size (cards.py uses this for endtable icon button fixed size)
    'btn_endtable_size':            25,
    'endtable_dialog_min_size':     (760, 500),
    'endtable_view_min_size':       (920, 620),
    'endtable_topbar_height':       30,
    'endtable_col_header_width':    28,
    'margins_endtable_header':      (8, 4, 6, 4),
    'spacing_endtable_header':      5,
    'spacing_endtable_groups':      8,
    'spacing_endtable_topbar2':     6,

    # ── GroupEditor ───────────────────────────────────────────────────────────
    'group_editor_accordion_size':  (28, 28),
    'group_editor_header_btn_size': (28, 28),
    'group_editor_header_height':   36,
    'group_editor_combo_max_width': 400,
    'group_editor_col_input_width2':350,
    'group_editor_gear_size':       (28, 28),
    'group_editor_col_btn_size':    (22, 22),
    'group_editor_config_padding':  (6, 6, 6, 6),
    'group_editor_config_spacing':  6,
    'group_editor_table_height':    34,
    'group_editor_table_min_h':     220,
    'margins_group_editor':         (0, 0, 0, 8),
    'margins_group_editor_input':   (0, 0, 0, 0),
    'spacing_group_editor_input':   4,

    # ── CustomDialog ──────────────────────────────────────────────────────────
    'margins_dialog_body':          (14, 14, 14, 14),
    'spacing_dialog_body':          8,

    # ── InsuredGroupCard / EndorsementPolicyCard ───────────────────────────────
    'policy_card_topbar_h':         32,
    'policy_editor_min_width':      480,
    'policy_editor_min_height':     200,
    'margins_policy_card_body':     (8, 8, 8, 8),
    'spacing_policy_card_body':     6,

    # ── PageConfig ─────────────────────────────────────────────────────────────
    'margins_config_top_row':       (0, 0, 0, 0),
    'spacing_config_top_row':       8,
    'spacing_config_fields':        4,
    'spacing_config_side_row':      8,
    'margins_config_side_row':      (0, 0, 0, 0),
    'margins_config_lol_fixed':     (20, 10, 0, 0),

    # ── PagePolicies ──────────────────────────────────────────────────────────
    'spacing_policies_main':        6,
    'margins_policies_grid':        (0, 0, 0, 0),
    'spacing_policies_grid':        8,
    'margins_policies_wrapper':     (0, 0, 0, 0),
    'spacing_policies_wrapper':     8,
    'spacing_policies_qty_row':     8,
    'margins_policies_qty_row':     (0, 0, 0, 0),
    'margins_policies_currency':    (0, 0, 0, 0),
    'spacing_policies_currency':    20,
    'margins_policies_finces':      (0, 0, 0, 0),
    'spacing_policies_finces':      8,
    'margins_policies_ed':          (0, 4, 0, 0),
    'margins_policies_insured':     (0, 0, 0, 0),
    'margins_policies_clients':     (0, 0, 0, 0),

    # ── PageUnit ───────────────────────────────────────────────────────────────
    'unit_logo_size':               (150, 100),
    'margins_unit_details':         (12, 0, 0, 0),

    # ── PageFinance ────────────────────────────────────────────────────────────
    'finance_label_width':          150,
    'margins_finance_recibo':       (0, 0, 0, 0),
    'margins_finance_grid':         (0, 0, 0, 0),
    'spacing_finance_grid':         8,
    'margins_finance_wrapper':      (0, 0, 0, 0),
    'spacing_finance_wrapper':      8,

    # ── PageAnnex ──────────────────────────────────────────────────────────────
    'annex_toolbar_min_height':     32,
    'annex_toolbar_btn_size':       (26, 26),
    'annex_editor_min_height':      180,
    'annex_sig_preview_height':     96,
    'annex_sig_dialog_min_h':       120,
    'annex_tab_editor_min_h':       140,
    'margins_annex_toolbar_outer':  (0, 0, 0, 4),
    'spacing_annex_toolbar_outer':  0,
    'margins_annex_toolbar_inner':  (12, 6, 10, 6),
    'margins_annex_body':           (10, 8, 10, 10),
    'spacing_annex_body':           6,
    'spacing_annex_toolbar_items':  4,
    'spacing_annex_radio_row':      24,
    'spacing_annex_check_area':     4,
    'margins_annex_check_area':     (0, 8, 0, 0),
    'spacing_annex_g_area':         8,
    'margins_annex_g_area':         (0, 8, 0, 0),
    'spacing_annex_ces_row':        4,
    'margins_annex_ces_card':       (0, 4, 0, 4),
    'spacing_annex_ces_card':       6,
    'spacing_annex_group_inner':    6,
    'spacing_annex_row5':           4,
    'margins_annex_edit_outer':     (0, 0, 0, 0),
    'spacing_annex_edit_outer':     4,
    'margins_annex_edit_toprow':    (0, 0, 0, 0),
    'spacing_annex_edit_toprow':    6,
    'spacing_annex_groups_list':    8,

    # ── QTabWidget (Python) ───────────────────────────────────────────────────

    # ── Scrollbar Python-accessed sizes ───────────────────────────────────────

    # ── GroupBox Python ────────────────────────────────────────────────────────
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


QSSA = QSSD

def build_qss(theme):
    """
    Generate the full application QSS from the theme dictionary.
    Every value comes from QSSD — no hardcoded literals in this template.
    Edit values in QSSD (ACTIVE_THEME), not in this function.
    """
    c = theme

    qss = f"""

    /* ===========================================================================
       S1  GLOBAL RESET & BASE WIDGET
       =========================================================================== */

    QWidget {{
        color:   {c['text_primary']};
        outline: {c['qwidget_focus_outline']};
    }}
    QMainWindow       {{ background-color: {c['app_bg']}; }}
    QDialog           {{ background-color: {c['app_bg']}; }}
    QStackedWidget > QWidget {{ background-color: {c['app_bg']}; }}

    /* ===========================================================================
       S2  SCROLLBARS
       =========================================================================== */

    QScrollBar:vertical {{
        border:           {c['scrollbar_border']};
        background-color: {c['scrollbar_track_bg']};
        width:            {c['scrollbar_width']}px;
        margin:           {c['scrollbar_margin']};
    }}
    QScrollBar:horizontal {{
        border:           {c['scrollbar_border']};
        background-color: {c['scrollbar_track_bg']};
        height:           {c['scrollbar_width']}px;
        margin:           {c['scrollbar_margin']};
    }}
    QScrollBar::handle:vertical {{
        background-color: {c['scrollbar_handle_bg']};
        border-radius:    {c['scrollbar_handle_radius']};
        min-height:       {c['scrollbar_handle_min']}px;
        margin:           {c['scrollbar_handle_margin']};
    }}
    QScrollBar::handle:horizontal {{
        background-color: {c['scrollbar_handle_bg']};
        border-radius:    {c['scrollbar_handle_radius']};
        min-width:        {c['scrollbar_handle_min']}px;
        margin:           {c['scrollbar_handle_margin']};
    }}
    QScrollBar::handle:vertical:hover,
    QScrollBar::handle:horizontal:hover {{
        background-color: {c['scrollbar_handle_bg_hover']};
    }}
    QScrollBar::handle:vertical:pressed,
    QScrollBar::handle:horizontal:pressed {{
        background-color: {c['scrollbar_handle_bg_pressed']};
    }}
    QScrollBar::add-line, QScrollBar::sub-line,
    QScrollBar::add-page, QScrollBar::sub-page {{
        background: {c['scrollbar_line_bg']};
        border:     {c['scrollbar_line_border']};
        height:     {c['scrollbar_line_height']};
        width:      {c['scrollbar_line_width']};
    }}

    QTreeWidget QScrollBar:vertical {{
        border:           {c['scrollbar_border']};
        background-color: {c['scrollbar_track_bg']};
        width:            {c['scrollbar_width']}px;
        margin:           {c['scrollbar_margin']};
    }}
    QTreeWidget QScrollBar:horizontal {{
        border:           {c['scrollbar_border']};
        background-color: {c['scrollbar_track_bg']};
        height:           {c['scrollbar_width']}px;
        margin:           {c['scrollbar_margin']};
    }}
    QTreeWidget QScrollBar::handle:vertical {{
        background-color: {c['scrollbar_handle_bg']};
        border-radius:    {c['scrollbar_handle_radius']};
        min-height:       {c['scrollbar_handle_min']}px;
        margin:           {c['scrollbar_handle_margin']};
    }}
    QTreeWidget QScrollBar::handle:horizontal {{
        background-color: {c['scrollbar_handle_bg']};
        border-radius:    {c['scrollbar_handle_radius']};
        min-width:        {c['scrollbar_handle_min']}px;
        margin:           {c['scrollbar_handle_margin']};
    }}
    QTreeWidget QScrollBar::handle:vertical:hover,
    QTreeWidget QScrollBar::handle:horizontal:hover {{
        background-color: {c['scrollbar_handle_bg_hover']};
    }}
    QTreeWidget QScrollBar::handle:vertical:pressed,
    QTreeWidget QScrollBar::handle:horizontal:pressed {{
        background-color: {c['scrollbar_handle_bg_pressed']};
    }}
    QTreeWidget QScrollBar::add-line, QTreeWidget QScrollBar::sub-line,
    QTreeWidget QScrollBar::add-page, QTreeWidget QScrollBar::sub-page {{
        background: {c['scrollbar_line_bg']};
        border:     {c['scrollbar_line_border']};
        height:     {c['scrollbar_line_height']};
        width:      {c['scrollbar_line_width']};
    }}

    /* ===========================================================================
       S3  QSCROLLAREA
       =========================================================================== */

    QScrollArea,
    QScrollArea > QWidget,
    QScrollArea > QWidget > QWidget {{
        background-color: {c['scrollarea_bg']};
        border:           {c['scrollarea_border']};
    }}

    /* ===========================================================================
       S4a  QLABEL
       =========================================================================== */

    QLabel {{
        font-family: {c['label_font_family']};
        font-size:   {c['label_font_size']};
        font-weight: {c['label_font_weight']};
        color:            {c['label_color']};
        font-weight:      {c['label_font_weight']};
        background-color: {c['label_bg']};
        border:           {c['label_border']};
        outline:          {c['label_outline']};
    }}

    /* ===========================================================================
       S4b  QRADIOBUTTON
       =========================================================================== */

    QRadioButton {{
        font-family: {c['radio_font_family']};
        font-size:   {c['radio_font_size']};
        font-weight: {c['radio_font_weight']};
        spacing:          {c['radio_spacing']}px;
        color:            {c['radio_widget_color']};
        background-color: {c['radio_widget_bg']};
        border:           {c['radio_widget_border']};
        outline:          {c['radio_widget_outline']};
    }}
    QRadioButton::indicator {{
        width:            {c['radio_indicator_size']}px;
        height:           {c['radio_indicator_size']}px;
        border-top:       {c['radio_border_top']};
        border-right:     {c['radio_border_right']};
        border-bottom:    {c['radio_border_bottom']};
        border-left:      {c['radio_border_left']};
        border-radius:    {c['radio_indicator_radius']};
        background-color: {c['radio_indicator_bg']};
    }}
    QRadioButton::indicator:hover {{
        border-top:    {c['radio_border_top_hover']};
        border-right:  {c['radio_border_right_hover']};
        border-bottom: {c['radio_border_bottom_hover']};
        border-left:   {c['radio_border_left_hover']};
    }}
    QRadioButton::indicator:checked {{
        border-top:       {c['radio_border_top_checked']};
        border-right:     {c['radio_border_right_checked']};
        border-bottom:    {c['radio_border_bottom_checked']};
        border-left:      {c['radio_border_left_checked']};
        image: {c['radio_checked']};
    }}

    /* ===========================================================================
       S5  QLINEEDIT
       =========================================================================== */

    QLineEdit {{
        font-family: {c['lineedit_font_family']};
        font-size:   {c['lineedit_font_size']};
        font-weight: {c['lineedit_font_weight']};
        background-color:           {c['lineedit_bg']};
        color:                      {c['lineedit_color']};
        border-top:                 {c['lineedit_border_top']};
        border-right:               {c['lineedit_border_right']};
        border-bottom:              {c['lineedit_border_bottom']};
        border-left:                {c['lineedit_border_left']};
        border-radius:              {c['lineedit_radius']};
        padding:                    {c['lineedit_padding']};
        min-height:                 {c['lineedit_min_height']}px;
        min-width:                  {c['lineedit_min_width']}px;
        selection-background-color: {c['lineedit_selection_bg']};
    }}
    QLineEdit:hover {{
        background-color: {c['lineedit_bg_hover']};
        border-top:    {c['lineedit_border_top_hover']};
        border-right:  {c['lineedit_border_right_hover']};
        border-bottom: {c['lineedit_border_bottom_hover']};
        border-left:   {c['lineedit_border_left_hover']};
        border-radius: {c['lineedit_radius']};
    }}
    QLineEdit:focus {{
        background-color: {c['lineedit_bg_focus']};
        border-top:      {c['lineedit_border_top_focus']};
        border-right:    {c['lineedit_border_right_focus']};
        border-bottom:   {c['lineedit_border_bottom_focus']};
        border-left:     {c['lineedit_border_left_focus']};
        border-radius:   {c['lineedit_radius']};
        outline:         {c['lineedit_outline']};
        color:           {c['lineedit_color_focus']};
    }}
    QLineEdit:read-only {{
        background-color: {c['lineedit_bg_readonly']};
        color:            {c['lineedit_color']};
        border-top:    {c['lineedit_border_top_ro']};
        border-right:  {c['lineedit_border_right_ro']};
        border-bottom: {c['lineedit_border_bottom_ro']};
        border-left:   {c['lineedit_border_left_ro']};
    }}
    QLineEdit:disabled {{
        background-color: {c['lineedit_bg_disabled']};
        color:            {c['lineedit_color_disabled']};
    }}

    /* ── S5 CardWidget Header sub-section: QLineEdit#CardTitle ── */
    QLineEdit#CardTitle {{
        font-family: {c['lineedit_card_header_font_family']};
        font-size:   {c['lineedit_card_header_font_size']};
        font-weight: {c['lineedit_card_header_font_weight']};
        background-color:           {c['lineedit_card_header_bg']};
        color:                      {c['lineedit_card_header_color']};
        border-top:                 {c['lineedit_card_header_border_top']};
        border-right:               {c['lineedit_card_header_border_right']};
        border-bottom:              {c['lineedit_card_header_border_bottom']};
        border-left:                {c['lineedit_card_header_border_left']};
        border-radius:              {c['lineedit_card_header_radius']};
        font-size:                  {c['lineedit_card_header_font_size']};
        padding:                    {c['lineedit_card_header_padding']};
        min-height:                 {c['lineedit_card_header_min_height']}px;
        selection-background-color: {c['lineedit_card_header_selection_bg']};
    }}
    QLineEdit#CardTitle::placeholder {{
        color: {c['lineedit_card_header_placeholder']};
    }}

    /* ===========================================================================
       S6  QCOMBOBOX & DROPDOWN
       =========================================================================== */

    QComboBox {{
        font-family: {c['combobox_font_family']};
        font-size:   {c['combobox_font_size']};
        font-weight: {c['combobox_font_weight']};
        background-color:           {c['combobox_bg']};
        color:                      {c['combobox_color']};
        border-top:                 {c['combobox_border_top']};
        border-right:               {c['combobox_border_right']};
        border-bottom:              {c['combobox_border_bottom']};
        border-left:                {c['combobox_border_left']};
        border-radius:              {c['combobox_radius']};
        padding:                    {c['combobox_padding']};
        min-height:                 {c['combobox_min_height']}px;
        min-width:                  {c['combobox_min_width']}px;
        selection-background-color: {c['combobox_selection_bg']};
    }}
    QComboBox:hover {{
        border-top:    {c['combobox_border_top_hover']};
        border-right:  {c['combobox_border_right_hover']};
        border-bottom: {c['combobox_border_bottom_hover']};
        border-left:   {c['combobox_border_left_hover']};
        border-radius: {c['combobox_radius']};
        background-color: {c['combobox_bg_hover']};
    }}
    QComboBox:focus {{
        border-top:    {c['combobox_border_top_focus']};
        border-right:  {c['combobox_border_right_focus']};
        border-bottom: {c['combobox_border_bottom_focus']};
        border-left:   {c['combobox_border_left_focus']};
        border-radius: {c['combobox_radius']};
        outline:       {c['combobox_outline']};
        background-color: {c['combobox_bg_focus']};
    }}
    QComboBox::drop-down {{
        subcontrol-origin:   padding;
        subcontrol-position: top right;
        width:               {c['combobox_arrow_area_width']}px;
        border-left:         {c['combobox_arrow_area_border']};
    }}
    QComboBox::drop-down:hover {{
        border-left:         {c['combobox_arrow_area_border_hover']};
    }}
    QComboBox::drop-down:focus {{
        border-left:         {c['combobox_arrow_area_border_focus']};
    }}
    QComboBox::down-arrow    {{ image: {c['combobox_arrow_down_img']}; width: {c['combobox_arrow_size']}px; height: {c['combobox_arrow_size']}px; }}
    QComboBox::down-arrow:on {{ image: {c['combobox_arrow_up_img']};   width: {c['combobox_arrow_size']}px; height: {c['combobox_arrow_size']}px; }}
    QComboBox QAbstractItemView {{
        font-family: {c['combobox_popup_font_family']};
        font-size:   {c['combobox_popup_font_size']};
        font-weight: {c['combobox_popup_font_weight']};
        background-color:           {c['combobox_popup_bg']};
        color:                      {c['combobox_popup_color']};
        border-top:                 {c['combobox_popup_border_top']};
        border-right:               {c['combobox_popup_border_right']};
        border-bottom:              {c['combobox_popup_border_bottom']};
        border-left:                {c['combobox_popup_border_left']};
        border-radius:              {c['combobox_popup_radius']};
        selection-background-color: {c['combobox_popup_selection_bg']};
        outline:                    {c['combobox_popup_outline']};
        padding:                    {c['combobox_popup_padding']};
    }}
    QComboBox QAbstractItemView::item {{
        font-family: {c['combobox_item_font_family']};
        font-size:   {c['combobox_item_font_size']};
        font-weight: {c['combobox_item_font_weight']};
        min-height:    {c['combobox_item_min_height']}px;
        padding:       {c['combobox_item_padding']};
        border-radius: {c['combobox_item_radius']};
    }}
    QComboBox QAbstractItemView::item:hover {{
        background-color: {c['combobox_item_bg_hover']};
        color:            {c['combobox_item_color_hover']};
    }}
    QComboBox QAbstractItemView::item:selected {{
        background-color: {c['combobox_item_bg_selected']};
        color:            {c['combobox_item_color_selected']};
    }}

    /* ── S6 CardWidget Header sub-section: QComboBox#CardTitle ── */
    QComboBox#CardTitle {{
        font-family: {c['combobox_card_header_font_family']};
        font-size:   {c['combobox_card_header_font_size']};
        font-weight: {c['combobox_card_header_font_weight']};
        background-color: {c['combobox_card_header_bg']};
        color:            {c['combobox_card_header_color']};
        border-top:       {c['combobox_card_header_border_top']};
        border-right:     {c['combobox_card_header_border_right']};
        border-bottom:    {c['combobox_card_header_border_bottom']};
        border-left:      {c['combobox_card_header_border_left']};
        font-weight:      {c['combobox_card_header_font_weight']};
        font-size:        {c['combobox_card_header_font_size']};
        padding:          {c['combobox_card_header_padding']};
        min-height:       {c['combobox_card_header_min_height']}px;
    }}
    QComboBox#CardTitle QLineEdit {{
        font-family: {c['combobox_card_header_font_family']};
        font-size:   {c['combobox_card_header_font_size']};
        font-weight: {c['combobox_card_header_font_weight']};
        background-color: {c['combobox_card_header_edit_bg']};
        color:            {c['combobox_card_header_edit_color']};
        border-top:       {c['combobox_card_header_edit_border_top']};
        border-right:     {c['combobox_card_header_edit_border_right']};
        border-bottom:    {c['combobox_card_header_edit_border_bottom']};
        border-left:      {c['combobox_card_header_edit_border_left']};
        padding:          {c['combobox_card_header_padding']};
        font-size:        {c['combobox_card_header_font_size']};
    }}
    QComboBox#CardTitle::drop-down {{
        border: {c['combobox_card_header_dd_border']};
    }}
    QComboBox#CardTitle::down-arrow {{
        width:  {c['combobox_card_header_arrow_width']};
        height: {c['combobox_card_header_arrow_height']};
    }}

    /* ===========================================================================
       S7a  QDATEEDIT
       =========================================================================== */

    QDateEdit {{
        font-family: {c['dateedit_font_family']};
        font-size:   {c['dateedit_font_size']};
        font-weight: {c['dateedit_font_weight']};
        background-color: {c['dateedit_bg']};
        color:            {c['dateedit_color']};
        border-top:       {c['dateedit_border_top']};
        border-right:     {c['dateedit_border_right']};
        border-bottom:    {c['dateedit_border_bottom']};
        border-left:      {c['dateedit_border_left']};
        border-radius:    {c['dateedit_radius']};
        padding:          {c['dateedit_padding']};
        min-height:       {c['dateedit_min_height']}px;
        min-width:        {c['dateedit_min_width']}px;
        selection-background-color: {c['dateedit_selection_bg']};

    }}
    QDateEdit:hover {{
        border-top:    {c['dateedit_border_top_hover']};
        border-right:  {c['dateedit_border_right_hover']};
        border-bottom: {c['dateedit_border_bottom_hover']};
        border-left:   {c['dateedit_border_left_hover']};
        border-radius: {c['dateedit_radius']};
        background-color: {c['dateedit_bg_hover']};
    }}
    QDateEdit:focus {{
        border-top:    {c['dateedit_border_top_focus']};
        border-right:  {c['dateedit_border_right_focus']};
        border-bottom: {c['dateedit_border_bottom_focus']};
        border-left:   {c['dateedit_border_left_focus']};
        border-radius: {c['dateedit_radius']};
        outline:       {c['dateedit_outline']};
        color:         {c['dateedit_color_focus']};
        background-color: {c['dateedit_bg_focus']};
    }}
    QDateEdit::drop-down {{
        width:          {c['dateedit_arrow_area_width']}px;
        border:         {c['dateedit_arrow_area_border']};
    }}
    QDateEdit::down-arrow {{
        width: {c['dateedit_arrow_size']}px;
        height: {c['dateedit_arrow_size']}px;
    }}

    /* ===========================================================================
       S8  QCHECKBOX
       =========================================================================== */

    QCheckBox {{
        font-family: {c['checkbox_font_family']};
        font-size:   {c['checkbox_font_size']};
        font-weight: {c['checkbox_font_weight']};
        spacing:          {c['checkbox_spacing']}px;
        color:            {c['checkbox_widget_color']};
        background-color: {c['checkbox_widget_bg']};
        border:           {c['checkbox_widget_border']};
        outline:          {c['checkbox_widget_outline']};
    }}
    QCheckBox::indicator {{
        width:         {c['checkbox_indicator_size']}px;
        height:        {c['checkbox_indicator_size']}px;
        border-top:    {c['checkbox_indicator_border_top']};
        border-right:  {c['checkbox_indicator_border_right']};
        border-bottom: {c['checkbox_indicator_border_bottom']};
        border-left:   {c['checkbox_indicator_border_left']};
        border-radius: {c['checkbox_indicator_radius']};
        background-color: {c['checkbox_indicator_bg']};
    }}
    QCheckBox::indicator:hover {{
        border-top:    {c['checkbox_indicator_border_top_hover']};
        border-right:  {c['checkbox_indicator_border_right_hover']};
        border-bottom: {c['checkbox_indicator_border_bottom_hover']};
        border-left:   {c['checkbox_indicator_border_left_hover']};
    }}
    QCheckBox::indicator:checked {{
        background-color: {c['checkbox_indicator_bg_checked']};
        border-top:       {c['checkbox_indicator_border_top_checked']};
        border-right:     {c['checkbox_indicator_border_right_checked']};
        border-bottom:    {c['checkbox_indicator_border_bottom_checked']};
        border-left:      {c['checkbox_indicator_border_left_checked']};
        image:            {c['checkbox_indicator_img_checked']};
    }}
    QCheckBox::indicator:indeterminate {{
        background-color: {c['checkbox_indicator_bg_indeterminate']};
        border-top:       {c['checkbox_indicator_border_top_indeterminate']};
        border-right:     {c['checkbox_indicator_border_right_indeterminate']};
        border-bottom:    {c['checkbox_indicator_border_bottom_indeterminate']};
        border-left:      {c['checkbox_indicator_border_left_indeterminate']};
        image:            {c['checkbox_indicator_img_indeterminate']};
    }}

    /* ===========================================================================
       S9  QGROUPBOX
       =========================================================================== */

    QGroupBox {{
        font-family: {c['groupbox_font_family']};
        font-size:   {c['groupbox_font_size']};
        font-weight: {c['groupbox_font_weight']};
        background-color: {c['groupbox_bg']};
        border-top:       {c['groupbox_border_top']};
        border-right:     {c['groupbox_border_right']};
        border-bottom:    {c['groupbox_border_bottom']};
        border-left:      {c['groupbox_border_left']};
        border-radius:    {c['groupbox_radius']};
        margin-top:       {c['groupbox_margin_top']};
        padding:          {c['groupbox_padding']};
        font-weight:      {c['groupbox_font_weight']};
        font-size:        {c['groupbox_font_size']};
        color:            {c['groupbox_color']};
    }}
    QGroupBox::title {{
        font-family: {c['groupbox_title_font_family']};
        font-size:   {c['groupbox_title_font_size']};
        font-weight: {c['groupbox_title_font_weight']};
        subcontrol-origin:   {c['groupbox_title_subcontrol_origin']};
        subcontrol-position: {c['groupbox_title_subcontrol_pos']};
        left:                {c['groupbox_title_left']};
        top:                 {c['groupbox_title_top']};
        padding:             {c['groupbox_title_padding']};
        color:               {c['groupbox_title_color']};
        background-color:    {c['groupbox_title_bg']};
    }}

    /* ===========================================================================
       S10  QPUSHBUTTON — BASE
       =========================================================================== */

    QPushButton {{
        font-family: {c['btn_font_family']};
        font-size:   {c['btn_font_size']};
        font-weight: {c['btn_font_weight']};
        background-color: {c['btn_bg']};
        color:            {c['btn_color']};
        border-top:       {c['btn_border_top']};
        border-right:     {c['btn_border_right']};
        border-bottom:    {c['btn_border_bottom']};
        border-left:      {c['btn_border_left']};
        border-radius:    {c['btn_radius']};
        padding:          {c['btn_padding']};
        min-height:       {c['btn_min_height']}px;
        min-width:        {c['btn_min_width']}px;
    }}
    QPushButton:hover {{
        background-color: {c['btn_bg_hover']};
        color:            {c['btn_color_hover']};
    }}
    QPushButton:pressed {{
        background-color: {c['btn_bg_pressed']};
        color:            {c['btn_color_pressed']};
    }}
    QPushButton:disabled {{
        background-color: {c['btn_bg_disabled']};
        color:            {c['btn_color_disabled']};
    }}

    /* ===========================================================================
       S11  QPUSHBUTTON — NAMED ACTION BUTTONS
       =========================================================================== */

    /* -- Danger buttons (LIMPIAR, ELIMINAR) -- */
    QPushButton[text="LIMPIAR"],
    QPushButton[text="ELIMINAR"] {{
        background-color: {c['btn_danger_bg']};
        color:            {c['btn_danger_color']};
        border-top:       {c['btn_danger_border_top']};
        border-right:     {c['btn_danger_border_right']};
        border-bottom:    {c['btn_danger_border_bottom']};
        border-left:      {c['btn_danger_border_left']};
        border-radius:    {c['btn_danger_radius']};
        padding:          {c['btn_danger_padding']};
        min-height:       {c['btn_danger_min_height']}px;
        min-width:        {c['btn_danger_min_width']}px;
    }}
    QPushButton[text="LIMPIAR"]:hover,
    QPushButton[text="ELIMINAR"]:hover {{
        background-color: {c['btn_danger_bg_hover']};
        color:            {c['btn_danger_color_hover']};
        border-top:       {c['btn_danger_border_top_hover']};
        border-right:     {c['btn_danger_border_right_hover']};
        border-bottom:    {c['btn_danger_border_bottom_hover']};
        border-left:      {c['btn_danger_border_left_hover']};
    }}

    /* -- role="danger" -- */
    QPushButton[role="danger"] {{
        background-color: {c['btn_role_danger_bg']};
        color:            {c['btn_role_danger_color']};
        border-top:       {c['btn_role_danger_border_top']};
        border-right:     {c['btn_role_danger_border_right']};
        border-bottom:    {c['btn_role_danger_border_bottom']};
        border-left:      {c['btn_role_danger_border_left']};
        border-radius:    {c['btn_role_danger_radius']};
        padding:          {c['btn_role_danger_padding']};
        min-height:       {c['btn_role_danger_min_height']}px;
        min-width:        {c['btn_role_danger_min_width']}px;
    }}
    QPushButton[role="danger"]:hover {{
        background-color: {c['btn_role_danger_bg_hover']};
        color:            {c['btn_role_danger_color_hover']};
        border-top:       {c['btn_role_danger_border_top_hover']};
        border-right:     {c['btn_role_danger_border_right_hover']};
        border-bottom:    {c['btn_role_danger_border_bottom_hover']};
        border-left:      {c['btn_role_danger_border_left_hover']};
    }}

    /* -- role="cesiones-danger" -- */
    QPushButton[role="cesiones-danger"] {{
        background-color: {c['btn_ces_danger_bg']};
        color:            {c['btn_ces_danger_color']};
        border-top:       {c['btn_ces_danger_border_top']};
        border-right:     {c['btn_ces_danger_border_right']};
        border-bottom:    {c['btn_ces_danger_border_bottom']};
        border-left:      {c['btn_ces_danger_border_left']};
        border-radius:    {c['btn_ces_danger_radius']};
        padding:          {c['btn_ces_danger_padding']};
        min-height:       {c['btn_ces_danger_height']}px;
        max-height:       {c['btn_ces_danger_height']}px;
    }}
    QPushButton[role="cesiones-danger"]:hover {{
        background-color: {c['btn_ces_danger_bg_hover']};
        color:            {c['btn_ces_danger_color_hover']};
        border-top:       {c['btn_ces_danger_border_top_hover']};
        border-right:     {c['btn_ces_danger_border_right_hover']};
        border-bottom:    {c['btn_ces_danger_border_bottom_hover']};
        border-left:      {c['btn_ces_danger_border_left_hover']};
    }}

    /* -- role="cesiones-neutral" -- */
    QPushButton[role="cesiones-neutral"] {{
        background-color: {c['btn_ces_neutral_bg']};
        color:            {c['btn_ces_neutral_color']};
        border-top:       {c['btn_ces_neutral_border_top']};
        border-right:     {c['btn_ces_neutral_border_right']};
        border-bottom:    {c['btn_ces_neutral_border_bottom']};
        border-left:      {c['btn_ces_neutral_border_left']};
        border-radius:    {c['btn_ces_neutral_radius']};
        padding:          {c['btn_ces_neutral_padding']};
        min-height:       {c['btn_ces_neutral_height']}px;
        max-height:       {c['btn_ces_neutral_height']}px;
    }}
    QPushButton[role="cesiones-neutral"]:hover {{
        background-color: {c['btn_ces_neutral_bg_hover']};
    }}

    /* -- role="quitar" (icon trash pill) -- */
    QPushButton[role="quitar"] {{
        background-color: {c['btn_quitar_icon_bg']};
        border-top:       {c['btn_quitar_icon_border_top']};
        border-right:     {c['btn_quitar_icon_border_right']};
        border-bottom:    {c['btn_quitar_icon_border_bottom']};
        border-left:      {c['btn_quitar_icon_border_left']};
        border-radius:    {c['btn_quitar_icon_radius']};
        padding:          {c['btn_quitar_icon_padding']};
        min-width:        {c['btn_quitar_icon_size']}px;
        max-width:        {c['btn_quitar_icon_size']}px;
        min-height:       {c['btn_quitar_icon_size']}px;
        max-height:       {c['btn_quitar_icon_size']}px;
    }}
    QPushButton[role="quitar"]:hover {{
        background-color: {c['btn_quitar_icon_bg_hover']};
    }}

    /* -- role="excel-icon" -- */
    QPushButton[role="excel-icon"] {{
        background-color: {c['btn_excel_icon_bg']};
        border-top:       {c['btn_excel_icon_border_top']};
        border-right:     {c['btn_excel_icon_border_right']};
        border-bottom:    {c['btn_excel_icon_border_bottom']};
        border-left:      {c['btn_excel_icon_border_left']};
        border-radius:    {c['btn_excel_icon_radius']};
        padding:          {c['btn_excel_icon_padding']};
        min-width:        {c['btn_excel_icon_size']}px;
        max-width:        {c['btn_excel_icon_size']}px;
        min-height:       {c['btn_excel_icon_size']}px;
        max-height:       {c['btn_excel_icon_size']}px;
    }}
    QPushButton[role="excel-icon"]:hover {{
        background-color: {c['btn_excel_icon_bg_hover']};
    }}

    /* -- role="excel-text" -- */
    QPushButton[role="excel-text"] {{
        font-family: {c['btn_excel_text_font_family']};
        font-size:   {c['btn_excel_text_font_size']};
        font-weight: {c['btn_excel_text_font_weight']};
        background-color: {c['btn_excel_text_bg']};
        color:            {c['btn_excel_text_color']};
        border-top:       {c['btn_excel_text_border_top']};
        border-right:     {c['btn_excel_text_border_right']};
        border-bottom:    {c['btn_excel_text_border_bottom']};
        border-left:      {c['btn_excel_text_border_left']};
        border-radius:    {c['btn_excel_text_radius']};
        padding:          {c['btn_excel_text_padding']};
        min-height:       {c['btn_excel_text_height']}px;
    }}
    QPushButton[role="excel-text"]:hover {{
        background-color: {c['btn_excel_text_bg_hover']};
    }}

    /* -- role="download" -- */
    QPushButton[role="download"] {{
        font-family: {c['btn_download_font_family']};
        font-size:   {c['btn_download_font_size']};
        font-weight: {c['btn_download_font_weight']};
        background-color: {c['btn_download_bg']};
        color:            {c['btn_download_color']};
        border-top:       {c['btn_download_border_top']};
        border-right:     {c['btn_download_border_right']};
        border-bottom:    {c['btn_download_border_bottom']};
        border-left:      {c['btn_download_border_left']};
        border-radius:    {c['btn_download_radius']};
        padding:          {c['btn_download_padding']};
        min-height:       {c['btn_download_height']}px;
    }}
    QPushButton[role="download"]:hover {{
        background-color: {c['btn_download_bg_hover']};
        color:            {c['btn_download_color_hover']};
        border-top:       {c['btn_download_border_top_hover']};
        border-right:     {c['btn_download_border_right_hover']};
        border-bottom:    {c['btn_download_border_bottom_hover']};
        border-left:      {c['btn_download_border_left_hover']};
    }}

    /* -- role="endtable-view" -- */
    QPushButton[role="endtable-view"] {{
        background-color: {c['btn_endtable_view_bg']};
        border-top:       {c['btn_endtable_view_border_top']};
        border-right:     {c['btn_endtable_view_border_right']};
        border-bottom:    {c['btn_endtable_view_border_bottom']};
        border-left:      {c['btn_endtable_view_border_left']};
        border-radius:    {c['btn_endtable_view_radius']};
        padding:          {c['btn_endtable_view_padding']};
        min-width:        {c['btn_endtable_view_size']}px;
        max-width:        {c['btn_endtable_view_size']}px;
        min-height:       {c['btn_endtable_view_size']}px;
        max-height:       {c['btn_endtable_view_size']}px;
    }}
    QPushButton[role="endtable-view"]:hover {{ background-color: {c['btn_endtable_view_bg_hover']}; }}

    /* -- role="endtable-edit" -- */
    QPushButton[role="endtable-edit"] {{
        background-color: {c['btn_endtable_edit_bg']};
        border-top:       {c['btn_endtable_edit_border_top']};
        border-right:     {c['btn_endtable_edit_border_right']};
        border-bottom:    {c['btn_endtable_edit_border_bottom']};
        border-left:      {c['btn_endtable_edit_border_left']};
        border-radius:    {c['btn_endtable_edit_radius']};
        padding:          {c['btn_endtable_edit_padding']};
        min-width:        {c['btn_endtable_edit_size']}px;
        max-width:        {c['btn_endtable_edit_size']}px;
        min-height:       {c['btn_endtable_edit_size']}px;
        max-height:       {c['btn_endtable_edit_size']}px;
    }}
    QPushButton[role="endtable-edit"]:hover {{ background-color: {c['btn_endtable_edit_bg_hover']}; }}

    /* -- role="endtable-import" -- */
    QPushButton[role="endtable-import"] {{
        background-color: {c['btn_endtable_import_bg']};
        border-top:       {c['btn_endtable_import_border_top']};
        border-right:     {c['btn_endtable_import_border_right']};
        border-bottom:    {c['btn_endtable_import_border_bottom']};
        border-left:      {c['btn_endtable_import_border_left']};
        border-radius:    {c['btn_endtable_import_radius']};
        padding:          {c['btn_endtable_import_padding']};
        min-width:        {c['btn_endtable_import_size']}px;
        max-width:        {c['btn_endtable_import_size']}px;
        min-height:       {c['btn_endtable_import_size']}px;
        max-height:       {c['btn_endtable_import_size']}px;
    }}
    QPushButton[role="endtable-import"]:hover {{
        background-color: {c['btn_endtable_import_bg_hover']};
    }}

    /* -- QUITAR POLIZA / QUITAR ASEGURADO -- */
    QPushButton[text^="QUITAR POLIZA"],
    QPushButton[text^="QUITAR ASEGURADO"] {{
        background-color: {c['btn_quitar_text_bg']};
        color:            {c['btn_quitar_text_color']};
        border-top:       {c['btn_quitar_text_border_top']};
        border-right:     {c['btn_quitar_text_border_right']};
        border-bottom:    {c['btn_quitar_text_border_bottom']};
        border-left:      {c['btn_quitar_text_border_left']};
        border-radius:    {c['btn_quitar_text_radius']};
        padding:          {c['btn_quitar_text_padding']};
        min-width:        {c['btn_quitar_text_min_width']};
        min-height:       {c['btn_quitar_text_min_height']}px;
    }}
    QPushButton[text^="QUITAR POLIZA"]:hover,
    QPushButton[text^="QUITAR ASEGURADO"]:hover {{
        background-color: {c['btn_quitar_text_bg_hover']};
        color:            {c['btn_quitar_text_color_hover']};
        border-top:       {c['btn_quitar_text_border_top_hover']};
        border-right:     {c['btn_quitar_text_border_right_hover']};
        border-bottom:    {c['btn_quitar_text_border_bottom_hover']};
        border-left:      {c['btn_quitar_text_border_left_hover']};
    }}

    /* -- role="accordion" -- */
    QPushButton[role="accordion"] {{
        background-color: {c['btn_accordion_bg']};
        border-top:       {c['btn_accordion_border_top']};
        border-right:     {c['btn_accordion_border_right']};
        border-bottom:    {c['btn_accordion_border_bottom']};
        border-left:      {c['btn_accordion_border_left']};
        border-radius:    {c['btn_accordion_radius']};
        padding:          {c['btn_accordion_padding']};
        icon-size:        {c['btn_accordion_size']};
        color:            {c['btn_accordion_color']};
        min-width:        {c['btn_accordion_size']};
        min-height:       {c['btn_accordion_size']};
    }}
    QPushButton[role="accordion"]:hover {{
        background-color: {c['btn_accordion_bg_hover']};
        border-color:     {c['btn_accordion_border_color_hover']};
    }}
    QPushButton[role="accordion"]:checked {{
        background-color: {c['btn_accordion_bg_checked']};
        border-color:     {c['btn_accordion_border_color_checked']};
    }}
    QPushButton[role="accordion"]:checked:hover {{
        background-color: {c['btn_accordion_bg_hover']};
        border-color:     {c['btn_accordion_border_color_hover']};
    }}

    /* -- role="format-selector" -- */
    QPushButton[role="format-selector"] {{
        font-family: {c['btn_format_font_family']};
        font-size:   {c['btn_format_font_size']};
        font-weight: {c['btn_format_font_weight']};
        background-color: {c['btn_format_bg']};
        border-top:       {c['btn_format_border_top']};
        border-right:     {c['btn_format_border_right']};
        border-bottom:    {c['btn_format_border_bottom']};
        border-left:      {c['btn_format_border_left']};
        border-radius:    {c['btn_format_radius']};
        padding:          {c['btn_format_padding']};
        min-width:        {c['btn_format_min_width']}px;
        color:            {c['btn_format_color']};
        font-weight:      {c['btn_format_font_weight']};
        icon-size:        {c['btn_format_icon_size']}px;
        text-align:       {c['btn_format_text_align']};
    }}
    QPushButton[role="format-selector"]:hover {{
        background-color: {c['btn_format_bg_hover']};
        border-color:     {c['btn_format_border_color_hover']};
    }}
    QPushButton[role="format-selector"]:checked {{
        background-color: {c['btn_format_bg_checked']};
        border-color:     {c['btn_format_border_color_checked']};
        color:            {c['btn_format_color_checked']};
        font-weight:      {c['btn_format_font_weight_checked']};
    }}
    QPushButton[role="format-selector"]:checked:hover {{
        background-color: {c['btn_format_bg_checked_hover']};
    }}

    /* -- role="manual-item" -- */
    QPushButton[role="manual-item"] {{
        font-family: {c['btn_manual_font_family']};
        font-size:   {c['btn_manual_font_size']};
        font-weight: {c['btn_manual_font_weight']};
        background-color: {c['btn_manual_bg']};
        border-top:       {c['btn_manual_border_top']};
        border-right:     {c['btn_manual_border_right']};
        border-bottom:    {c['btn_manual_border_bottom']};
        border-left:      {c['btn_manual_border_left']};
        border-radius:    {c['btn_manual_radius']};
        padding:          {c['btn_manual_padding']};
        color:            {c['btn_manual_color']};
        text-align:       {c['btn_manual_text_align']};
        min-height:       {c['btn_manual_min_height']}px;
    }}
    QPushButton[role="manual-item"]:hover {{
        background-color: {c['btn_manual_bg_hover']};
        border-color:     {c['btn_manual_border_color_hover']};
    }}
    QPushButton[role="manual-item"]:checked {{
        background-color: {c['btn_manual_bg_checked']};
        border-color:     {c['btn_manual_border_color_checked']};
        color:            {c['btn_manual_color_checked']};
        font-weight:      {c['btn_manual_font_weight_checked']};
    }}
    QPushButton[role="manual-item"]:disabled {{
        background-color: {c['btn_manual_bg_disabled']};
        border-color:     {c['btn_manual_border_color_disabled']};
        color:            {c['btn_manual_color_disabled']};
        font-weight:      {c['btn_manual_font_weight_disabled']};
    }}

    /* -- role="manual-fixed" -- */
    QPushButton[role="manual-fixed"] {{
        font-family: {c['btn_manual_fixed_font_family']};
        font-size:   {c['btn_manual_fixed_font_size']};
        font-weight: {c['btn_manual_fixed_font_weight']};
        background-color: {c['btn_manual_fixed_bg']};
        border-top:       {c['btn_manual_fixed_border_top']};
        border-right:     {c['btn_manual_fixed_border_right']};
        border-bottom:    {c['btn_manual_fixed_border_bottom']};
        border-left:      {c['btn_manual_fixed_border_left']};
        border-radius:    {c['btn_manual_fixed_radius']};
        padding:          {c['btn_manual_fixed_padding']};
        color:            {c['btn_manual_fixed_color']};
        font-weight:      {c['btn_manual_fixed_font_weight']};
        text-align:       {c['btn_manual_fixed_text_align']};
        min-height:       {c['btn_manual_fixed_min_height']}px;
    }}
    QPushButton[role="manual-fixed"]:disabled {{
        background-color: {c['btn_manual_fixed_bg_disabled']};
        border-top:       {c['btn_manual_fixed_border_top_disabled']};
        border-right:     {c['btn_manual_fixed_border_right_disabled']};
        border-bottom:    {c['btn_manual_fixed_border_bottom_disabled']};
        border-left:      {c['btn_manual_fixed_border_left_disabled']};
        color:            {c['btn_manual_fixed_color_disabled']};
        font-weight:      {c['btn_manual_fixed_font_weight_disabled']};
    }}

    /* -- role="config-gear" -- */
    QPushButton[role="config-gear"] {{
        background-color: {c['btn_gear_bg']};
        border-top:       {c['btn_gear_border_top']};
        border-right:     {c['btn_gear_border_right']};
        border-bottom:    {c['btn_gear_border_bottom']};
        border-left:      {c['btn_gear_border_left']};
        border-radius:    {c['btn_gear_radius']};
        padding:          {c['btn_gear_padding']};
    }}
    QPushButton[role="config-gear"]:hover   {{ background-color: {c['btn_gear_bg_hover']}; }}
    QPushButton[role="config-gear"]:checked {{ background-color: {c['btn_gear_bg_checked']}; }}

    /* -- role="col-action" -- */
    QPushButton[role="col-action"] {{
        background-color: {c['btn_col_action_bg']};
        border-top:       {c['btn_col_action_border_top']};
        border-right:     {c['btn_col_action_border_right']};
        border-bottom:    {c['btn_col_action_border_bottom']};
        border-left:      {c['btn_col_action_border_left']};
        border-radius:    {c['btn_col_action_radius']};
        padding:          {c['btn_col_action_padding']};
    }}
    QPushButton[role="col-action"]:hover {{ background-color: {c['btn_col_action_bg_hover']}; }}

    /* -- role="col-action-danger" -- */
    QPushButton[role="col-action-danger"] {{
        background-color: {c['btn_col_danger_bg']};
        border-top:       {c['btn_col_danger_border_top']};
        border-right:     {c['btn_col_danger_border_right']};
        border-bottom:    {c['btn_col_danger_border_bottom']};
        border-left:      {c['btn_col_danger_border_left']};
        border-radius:    {c['btn_col_danger_radius']};
        padding:          {c['btn_col_danger_padding']};
        color:            {c['btn_col_danger_color']};
    }}
    QPushButton[role="col-action-danger"]:hover {{
        background-color: {c['btn_col_danger_bg_hover']};
        border-color:     {c['btn_col_danger_border_color_hover']};
    }}

    /* ===========================================================================
       S12  QTREEWIDGET
       =========================================================================== */

    QTreeWidget {{
        font-family: {c['tree_font_family']};
        font-size:   {c['tree_font_size']};
        font-weight: {c['tree_font_weight']};
        background-color:           {c['tree_bg']};
        alternate-background-color: {c['tree_alt_row_bg']};
        color:                      {c['tree_color']};
        border-top:                 {c['tree_border_top']};
        border-right:               {c['tree_border_right']};
        border-bottom:              {c['tree_border_bottom']};
        border-left:                {c['tree_border_left']};
        border-radius:              {c['tree_radius']};
        gridline-color:             {c['tree_gridline']};
        outline:                    {c['tree_outline']};
    }}
    QTreeWidget::item {{
        font-family: {c['tree_item_font_family']};
        font-size:   {c['tree_item_font_size']};
        font-weight: {c['tree_item_font_weight']};
        min-height:    {c['tree_item_min_height']}px;
        padding:       {c['tree_item_padding']};
        border-top:    {c['tree_item_border_top']};
        border-right:  {c['tree_item_border_right']};
        border-bottom: {c['tree_item_border_bottom']};
        border-left:   {c['tree_item_border_left']};
    }}
    QTreeWidget::item:!selected {{ border-bottom: {c['tree_item_border_bottom']}; }}
    QTreeWidget::item:hover     {{ background-color: {c['tree_item_bg_hover']}; color: {c['tree_item_color_hover']}; }}
    QTreeWidget::item:selected  {{
        background-color: {c['tree_item_bg_selected']};
        color:            {c['tree_item_color_selected']};
    }}
    QTreeWidget QHeaderView {{ border: {c['tree_header_border']}; }}
    QTreeWidget QHeaderView::section {{
        font-family: {c['tree_header_font_family']};
        font-size:   {c['tree_header_font_size']};
        font-weight: {c['tree_header_font_weight']};
        background-color: {c['tree_header_section_bg']};
        color:            {c['tree_header_section_color']};
        font-weight:      {c['tree_header_font_weight']};
        border-top:       {c['tree_header_section_border_top']};
        border-right:     {c['tree_header_section_border_right']};
        border-bottom:    {c['tree_header_section_border_bottom']};
        border-left:      {c['tree_header_section_border_left']};
        padding:          {c['tree_header_section_padding']};
        min-height:       {c['tree_header_section_min_height']}px;
    }}
    QTreeWidget QHeaderView::section:last,
    QTreeWidget QHeaderView::section:last-child,
    QTreeWidget QHeaderView::section:only-child {{ border-right: {c['tree_header_last_border_right']}; }}

    /* QTableWidget headers (EndorsementEditDialog) */
    QTableWidget QHeaderView::section:horizontal {{
        font-family: {c['table_hdr_hz_font_family']};
        font-size:   {c['table_hdr_hz_font_size']};
        font-weight: {c['table_hdr_hz_font_weight']};
        background-color: {c['table_hdr_hz_bg']};
        color:            {c['table_hdr_hz_color']};
        font-weight:      {c['table_hdr_hz_font_weight']};
        padding:          {c['table_hdr_hz_padding']};
        border-top:       {c['table_hdr_hz_border_top']};
        border-right:     {c['table_hdr_hz_border_right']};
        border-bottom:    {c['table_hdr_hz_border_bottom']};
        border-left:      {c['table_hdr_hz_border_left']};
    }}
    QTableWidget QHeaderView::section:vertical {{
        font-family: {c['table_hdr_vt_font_family']};
        font-size:   {c['table_hdr_vt_font_size']};
        font-weight: {c['table_hdr_vt_font_weight']};
        background-color: {c['table_hdr_vt_bg']};
        color:            {c['table_hdr_vt_color']};
        padding:          {c['table_hdr_vt_padding']};
        border-top:       {c['table_hdr_vt_border_top']};
        border-right:     {c['table_hdr_vt_border_right']};
        border-bottom:    {c['table_hdr_vt_border_bottom']};
        border-left:      {c['table_hdr_vt_border_left']};
        min-width:        {c['table_vertical_header_width']}px;
        max-width:        {c['table_vertical_header_width']}px;
    }}

    /* ===========================================================================
       S13  NAVBAR
       =========================================================================== */

    #NavBar {{
        background-color: {c['navbar_bg']};
        border-top:       {c['navbar_border_top']};
        border-right:     {c['navbar_border_right']};
        border-bottom:    {c['navbar_border_bottom']};
        border-left:      {c['navbar_border_left']};
        min-height:       {c['navbar_min_height']}px;
        max-height:       {c['navbar_max_height']}px;
    }}

    /* ===========================================================================
       S14  CARDWIDGET
       =========================================================================== */

    #CardHeader {{
        background-color: {c['card_header_bg']};
        min-height:       {c['card_header_min_height']}px;
        max-height:       {c['card_header_max_height']}px;
        padding:          {c['card_header_padding']};
        border-radius:    {c['card_header_radius']};
        border-top:       {c['card_header_border_top']};
        border-right:     {c['card_header_border_right']};
        border-bottom:    {c['card_header_border_bottom']};
        border-left:      {c['card_header_border_left']};
    }}
    #CardTitle {{
        font-family: {c['card_title_font_family']};
        font-size:   {c['card_title_font_size']};
        font-weight: {c['card_title_font_weight']};
        color:            {c['card_title_color']};
        font-weight:      {c['card_title_font_weight']};
    }}
    #CardToggle {{
        font-family: {c['card_toggle_font_family']};
        font-size:   {c['card_toggle_font_size']};
        font-weight: {c['card_toggle_font_weight']};
        color:            {c['card_toggle_color']};
        background-color: {c['card_toggle_bg']};
    }}
    #CardToggle:hover {{
        background-color: {c['card_toggle_bg_hover']};
    }}
    #CardBody {{
        background-color: {c['card_body_bg']};
        border-top:       {c['card_body_border_top']};
        border-right:     {c['card_body_border_right']};
        border-bottom:    {c['card_body_border_bottom']};
        border-left:      {c['card_body_border_left']};
        border-radius:    {c['card_body_radius']};
        padding:          {c['card_body_padding']};
    }}

    /* ===========================================================================
       S15  CUSTOMMESSAGEBOX
       =========================================================================== */

    #MsgFrame {{
        background-color: {c['msg_frame_bg']};
        border-top:       {c['msg_frame_border_top']};
        border-right:     {c['msg_frame_border_right']};
        border-bottom:    {c['msg_frame_border_bottom']};
        border-left:      {c['msg_frame_border_left']};
        border-radius:    {c['msg_frame_radius']};
    }}
    #MsgTitleBar {{
        background-color: {c['msg_titlebar_bg']};
        border-radius:    {c['msg_titlebar_radius']};
        min-height:       {c['msg_titlebar_min_height']}px;
        max-height:       {c['msg_titlebar_max_height']}px;
    }}
    #MsgTitle {{
        font-family: {c['msg_title_font_family']};
        font-size:   {c['msg_title_font_size']};
        font-weight: {c['msg_title_font_weight']};
        color:            {c['msg_title_color']};
        font-weight:      {c['msg_title_font_weight']};
        font-size:        {c['msg_title_font_size']};
        background-color: {c['msg_title_bg']};
    }}
    #MsgBody {{
        background-color: {c['msg_body_bg']};
        border-radius:    {c['msg_body_radius']};
        padding:          {c['msg_body_padding']};
    }}
    #MsgText {{
        font-family: {c['msg_text_font_family']};
        font-size:   {c['msg_text_font_size']};
        font-weight: {c['msg_text_font_weight']};
        color:            {c['msg_text_color']};
        font-weight:      {c['msg_text_font_weight']};
        font-size:        {c['msg_text_font_size']};
        background-color: {c['msg_text_bg']};
    }}
    #MsgBtnPrimary {{
        font-family: {c['msg_btn_primary_font_family']};
        font-size:   {c['msg_btn_primary_font_size']};
        font-weight: {c['msg_btn_primary_font_weight']};
        background-color: {c['msg_btn_primary_bg']};
        color:            {c['msg_btn_primary_color']};
        font-weight:      {c['msg_btn_primary_font_weight']};
        border-top:       {c['msg_btn_primary_border_top']};
        border-right:     {c['msg_btn_primary_border_right']};
        border-bottom:    {c['msg_btn_primary_border_bottom']};
        border-left:      {c['msg_btn_primary_border_left']};
        border-radius:    {c['msg_btn_primary_radius']};
        padding:          {c['msg_btn_primary_padding']};
        min-width:        {c['msg_btn_primary_min_width']}px;
        min-height:       {c['msg_btn_primary_min_height']}px;
    }}
    #MsgBtnPrimary:hover {{ background-color: {c['msg_btn_primary_bg_hover']}; }}
    #MsgBtnSecondary {{
        font-family: {c['msg_btn_secondary_font_family']};
        font-size:   {c['msg_btn_secondary_font_size']};
        font-weight: {c['msg_btn_secondary_font_weight']};
        background-color: {c['msg_btn_secondary_bg']};
        color:            {c['msg_btn_secondary_color']};
        font-weight:      {c['msg_btn_primary_font_weight']};
        border-top:       {c['msg_btn_secondary_border_top']};
        border-right:     {c['msg_btn_secondary_border_right']};
        border-bottom:    {c['msg_btn_secondary_border_bottom']};
        border-left:      {c['msg_btn_secondary_border_left']};
        border-radius:    {c['msg_btn_secondary_radius']};
        padding:          {c['msg_btn_secondary_padding']};
        min-width:        {c['msg_btn_secondary_min_width']}px;
        min-height:       {c['msg_btn_secondary_min_height']}px;
    }}
    #MsgBtnSecondary:hover {{ background-color: {c['msg_btn_secondary_bg_hover']}; }}

    /* ===========================================================================
       S16  CESIONES / ENDORSEMENTTABLECARD
       =========================================================================== */

    #EndorsementCard {{
        background-color: {c['endcard_bg']};
        border-top:       {c['endcard_border_top']};
        border-right:     {c['endcard_border_right']};
        border-bottom:    {c['endcard_border_bottom']};
        border-left:      {c['endcard_border_left']};
        border-radius:    {c['endcard_radius']};
    }}
    #EndorsementCard QLabel {{
        font-family: {c['endcard_label_font_family']};
        font-size:   {c['endcard_label_font_size']};
        font-weight: {c['endcard_label_font_weight']};
        color:      {c['endcard_label_color']};
        background: {c['endcard_label_bg']};
    }}
    #EndorsementCard QCheckBox {{
        color:      {c['endcard_checkbox_color']};
        background: {c['endcard_checkbox_bg']};
    }}

    #InsuredGroupHeader {{
        background-color: {c['insured_hdr_bg']};
        border-top:       {c['insured_hdr_border_top']};
        border-right:     {c['insured_hdr_border_right']};
        border-bottom:    {c['insured_hdr_border_bottom']};
        border-left:      {c['insured_hdr_border_left']};
        border-radius:    {c['insured_hdr_radius']};
    }}
    #InsuredGroupHeader QLabel {{
        font-family: {c['insured_hdr_label_font_family']};
        font-size:   {c['insured_hdr_label_font_size']};
        font-weight: {c['insured_hdr_label_font_weight']};
        color:       {c['insured_hdr_label_color']};
        font-weight: {c['insured_hdr_label_fw']};
        background:  {c['insured_hdr_label_bg']};
    }}
    #InsuredGroupHeader #CardToggle {{
        color: {c['insured_hdr_toggle_color']};
    }}
    #InsuredGroupBody {{
        background-color: {c['insured_body_bg']};
        border-top:       {c['insured_body_border_top']};
        border-right:     {c['insured_body_border_right']};
        border-bottom:    {c['insured_body_border_bottom']};
        border-left:      {c['insured_body_border_left']};
        padding:          {c['insured_body_padding']};
    }}

    /* ── GroupEditor config panel ── */
    #ConfigPanel {{
        background-color: {c['config_panel_bg']};
        border-top:       {c['config_panel_border_top']};
        border-right:     {c['config_panel_border_right']};
        border-bottom:    {c['config_panel_border_bottom']};
        border-left:      {c['config_panel_border_left']};
    }}

    /* ── Toolbar buttons (Garantías editor) ── */
    #ToolbarButton {{
        font-family: {c['toolbar_btn_font_family']};
        font-size:   {c['toolbar_btn_font_size']};
        font-weight: {c['toolbar_btn_font_weight']};
        background-color: {c['toolbar_btn_bg']};
        color:            {c['toolbar_btn_color']};
        border-top:       {c['toolbar_btn_border_top']};
        border-right:     {c['toolbar_btn_border_right']};
        border-bottom:    {c['toolbar_btn_border_bottom']};
        border-left:      {c['toolbar_btn_border_left']};
        border-radius:    {c['toolbar_btn_radius']};
        padding:          {c['toolbar_btn_padding']};
        min-width:        {c['toolbar_btn_width']}px;
        min-height:       {c['toolbar_btn_height']}px;
        font-weight:      {c['toolbar_btn_font_weight']};
    }}
    #ToolbarButton:hover {{ background-color: {c['toolbar_btn_bg_hover']}; }}

    /* ── QTextEdit (Garantías editor) ── */
    QTextEdit {{
        font-family: {c['textedit_font_family']};
        font-size:   {c['textedit_font_size']};
        font-weight: {c['textedit_font_weight']};
        background-color: {c['textedit_bg']};
        color:            {c['textedit_color']};
        border-top:       {c['textedit_border_top']};
        border-right:     {c['textedit_border_right']};
        border-bottom:    {c['textedit_border_bottom']};
        border-left:      {c['textedit_border_left']};
        border-radius:    {c['textedit_radius']};
    }}

    /* ===========================================================================
       S17  APPTITLEBAR (CustomDialog frameless titlebar)
       =========================================================================== */

    #AppTitleBar {{
        background-color: {c['titlebar_bg']};
        min-height:       {c['titlebar_min_height']}px;
        max-height:       {c['titlebar_max_height']}px;
    }}
    #AppTitleLabel {{
        font-family: {c['titlebar_label_font_family']};
        font-size:   {c['titlebar_label_font_size']};
        font-weight: {c['titlebar_label_font_weight']};
        color:            {c['titlebar_label_color']};
        font-weight:      {c['titlebar_label_font_weight']};
        font-size:        {c['titlebar_label_font_size']};
        background-color: {c['titlebar_label_bg']};
    }}
    QPushButton[role="titlebar-min"],
    QPushButton[role="titlebar-max"] {{
        background-color: {c['btn_titlebar_bg']};
        color:            {c['btn_titlebar_color']};
        border-top:       {c['btn_titlebar_border_top']};
        border-right:     {c['btn_titlebar_border_right']};
        border-bottom:    {c['btn_titlebar_border_bottom']};
        border-left:      {c['btn_titlebar_border_left']};
        font-size:        {c['btn_titlebar_font_size']};
        min-width:        {c['titlebar_btn_width']}px;
        max-width:        {c['titlebar_btn_width']}px;
        min-height:       {c['titlebar_btn_height']}px;
        max-height:       {c['titlebar_btn_height']}px;
        border-radius:    {c['btn_titlebar_radius']};
        padding:          {c['btn_titlebar_padding']};
    }}
    QPushButton[role="titlebar-min"]:hover,
    QPushButton[role="titlebar-max"]:hover {{
        background-color: {c['btn_titlebar_bg_hover']};
    }}
    QPushButton[role="titlebar-close"] {{
        background-color: {c['btn_titlebar_close_bg']};
        color:            {c['btn_titlebar_close_color']};
        border-top:       {c['btn_titlebar_close_border_top']};
        border-right:     {c['btn_titlebar_close_border_right']};
        border-bottom:    {c['btn_titlebar_close_border_bottom']};
        border-left:      {c['btn_titlebar_close_border_left']};
        font-size:        {c['btn_titlebar_close_font_size']};
        min-width:        {c['titlebar_btn_width']}px;
        max-width:        {c['titlebar_btn_width']}px;
        min-height:       {c['titlebar_btn_height']}px;
        max-height:       {c['titlebar_btn_height']}px;
        border-radius:    {c['btn_titlebar_close_radius']};
        padding:          {c['btn_titlebar_close_padding']};
    }}
    QPushButton[role="titlebar-close"]:hover   {{ background-color: {c['btn_titlebar_close_bg_hover']}; }}
    QPushButton[role="titlebar-close"]:pressed {{ background-color: {c['btn_titlebar_close_bg_pressed']}; }}

    /* ===========================================================================
       S18  MISCELLANEOUS / PAGE-SPECIFIC
       =========================================================================== */

    #InstructionLabel {{
        font-family: {c['instruction_label_font_family']};
        font-size:   {c['instruction_label_font_size']};
        font-weight: {c['instruction_label_font_weight']};
        color:       {c['instruction_label_color']};
        font-size:   {c['instruction_label_font_size']};
        font-weight: {c['instruction_label_font_weight']};
    }}

    /* ── QTabWidget — Cesiones Individual mode ── */
    QTabWidget::pane {{
        border-top:    {c['tab_pane_border_top']};
        border-right:  {c['tab_pane_border_right']};
        border-bottom: {c['tab_pane_border_bottom']};
        border-left:   {c['tab_pane_border_left']};
        margin:        {c['tab_pane_margin']};
        padding:       {c['tab_pane_padding']};
        background:    {c['tab_pane_bg']};
        top:           {c['tab_pane_top_offset']};
    }}
    QTabWidget {{
        margin:  {c['tab_widget_margin']};
        padding: {c['tab_widget_padding']};
    }}
    QTabBar::tab {{
        font-family: {c['tab_font_family']};
        font-size:   {c['tab_font_size']};
        font-weight: {c['tab_font_weight']};
        background-color:        {c['tab_bg']};
        color:                   {c['tab_color']};
        border-top:              {c['tab_border_top']};
        border-right:            {c['tab_border_right']};
        border-bottom:           {c['tab_border_bottom']};
        border-left:             {c['tab_border_left']};
        border-top-left-radius:  {c['tab_radius_tl']};
        border-top-right-radius: {c['tab_radius_tr']};
        padding:                 {c['tab_padding']};
        min-height:              {c['tab_min_height']}px;
        margin-right:            {c['tab_margin_right']};
    }}
    QTabBar::tab:selected {{
        font-family: {c['tab_selected_font_family']};
        font-size:   {c['tab_selected_font_size']};
        font-weight: {c['tab_selected_font_weight']};
        background-color: {c['tab_selected_bg']};
        color:            {c['tab_selected_color']};
        font-weight:      {c['tab_selected_font_weight']};
    }}
    QTabBar::tab:!selected {{
        background-color: {c['tab_inactive_bg']};
        color:            {c['tab_inactive_color']};
        margin-top:       {c['tab_inactive_top_margin']};
    }}
    QTabBar::tab:hover:!selected {{
        background-color: {c['tab_inactive_hover_bg']};
        color:            {c['tab_inactive_hover_color']};
    }}

    /* ── CardWidget inside QTabWidget — suppress side borders ── */
    QTabWidget QWidget#CardBody {{
        border-top:    {c['tab_cardbody_border_top']};
        border-right:  {c['tab_cardbody_border_right']};
        border-bottom: {c['tab_cardbody_border_bottom']};
        border-left:   {c['tab_cardbody_border_left']};
    }}
    QTabWidget QWidget#CardHeader {{
        border-radius: {c['tab_cardheader_radius']};
    }}

    """

    # Convert url() to absolute paths when running from PyInstaller bundle
    try:
        import re as _re, os as _os
        from helpers import resource_path as _rp
        def _abs_url(m):
            rel = m.group(1)
            try:
                abs_path = _rp(rel).replace('\\', '/')
                return f'url({abs_path})'
            except Exception:
                return m.group(0)
        qss = _re.sub(r'url\((imgs/[^)]+)\)', _abs_url, qss)
    except Exception:
        pass
    return qss
