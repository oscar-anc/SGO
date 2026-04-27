# coding: utf-8
"""
theme.py — Tema Vivaldi Dark 4.x con QSS estático de doble paleta.

ESTRATEGIA ANTI-PARPADEO:
  build_qss() se llama UNA SOLA VEZ al arranque.
  El QSS incluye reglas para ambas empresas usando el selector
  de propiedad dinámica [empresa="RRGG"] y [empresa="Transportes"].

  Para cambiar el acento al seleccionar empresa, en Python se hace:
      main_window.setProperty("empresa", "RRGG")
      main_window.style().polish(main_window)

  Esto recalcula solo las reglas afectadas por la propiedad — sin
  regenerar el string QSS, sin setStyleSheet(), sin parpadeo.

REGLA DE TIPOS (sin excepciones):
  int  → valores que van a Python: setFixedSize, setFixedHeight,
          setContentsMargins, resize, QSize, o a QSS como {c[k]}px
  str  → valores que van directo en QSS con px/pt ya incluidos
"""

from PySide6.QtGui import QPalette, QColor

# ─────────────────────────────────────────────────────────────────────────────
# PALETA BASE — Vivaldi Dark 4.x
# ─────────────────────────────────────────────────────────────────────────────
QSSD: dict = {

    # ── Fondos ────────────────────────────────────────────────────────────────
    'app_bg':        '#2e2f37',
    'surface_raised':'#363740',
    'surface':       '#3d3e48',
    'surface_alt':   '#44454d',

    # ── Texto ─────────────────────────────────────────────────────────────────
    'text_primary':     '#d3d9e3',
    'text_on_dark':     '#d3d9e3',
    'text_muted':       '#8a93a8',
    'text_disabled':    '#56575f',
    'text_placeholder': '#5e6270',
    'text_on_accent':   '#ffffff',
    'text_label':       '#9199aa',

    # ── Constantes CSS ────────────────────────────────────────────────────────
    'css_none':        'none',
    'css_transparent': 'transparent',
    'css_image_none':  'none',
    'css_outline_none':'none',
    'align_left':      'left',
    'align_center':    'center',
    'fw_bold':         'bold',
    'fw_normal':       'normal',

    # ── Acentos RRGG ──────────────────────────────────────────────────────────
    'accent_rrgg':       '#6590fd',
    'accent_rrgg_dark':  '#4a72e8',
    'accent_rrgg_light': '#252d4a',

    # ── Acentos Transportes ───────────────────────────────────────────────────
    'accent_trans':       '#56b4a0',
    'accent_trans_dark':  '#3d9484',
    'accent_trans_light': '#1b3030',

    # ── Acento activo (alias — para uso en Python, ej. combo_item_hover) ─────
    # Se actualiza en Python cuando cambia empresa pero NO se usa en el QSS
    # estático (allí se usan los selectores [empresa="X"]).
    'accent':       '#6590fd',
    'accent_dark':  '#4a72e8',
    'accent_light': '#252d4a',

    # ── Bordes ────────────────────────────────────────────────────────────────
    'border_input':       '#4a4b56',
    'border_block':       '#42434d',

    # ── TitleBar ──────────────────────────────────────────────────────────────
    'titlebar_bg':               '#26272e',
    'titlebar_btn_text':         '#d3d9e3',
    'titlebar_btn_hover_bg':     '#6590fd',
    'titlebar_close_hover_bg':   '#c42b1c',
    'titlebar_close_pressed_bg': '#a01e10',

    # ── Bloques ───────────────────────────────────────────────────────────────
    'block_header_text': '#9199aa',
    'block_body_bg':     '#363740',
    'block_body_border': '#42434d',

    # ── Botones grandes (estado neutro — seleccionado usa [empresa]) ──────────
    'btn_linea_bg':       '#3d3e48',
    'btn_linea_border':   '#4a4b56',
    'btn_linea_text':     '#9199aa',
    'btn_linea_hover_bg': '#44454d',

    # ── Radio-cards L2 (estado neutro) ────────────────────────────────────────
    'radio_opt_bg':       '#3d3e48',
    'radio_opt_border':   '#4a4b56',
    'radio_opt_hover_bg': '#44454d',
    'radio_dot_border':   '#5e6270',

    # ── Botón Agregar ─────────────────────────────────────────────────────────
    'btn_add_row_disabled_text':   '#56575f',
    'btn_add_row_disabled_border': '#42434d',

    # ── Botón Eliminar ────────────────────────────────────────────────────────
    'btn_del_bg':        '#3d3e48',
    'btn_del_border':    '#4a4b56',
    'btn_del_icon':      '#8a93a8',
    'btn_del_hover_bg':  '#3a2020',

    # ── Botón secundario / paste ──────────────────────────────────────────────
    'btn_secondary_bg':     '#3d3e48',
    'btn_secondary_border': '#4a4b56',
    'btn_secondary_text':   '#d3d9e3',
    'btn_secondary_hover':  '#44454d',
    'btn_paste_bg':         '#3d3e48',
    'btn_paste_border':     '#4a4b56',
    'btn_paste_text':       '#9199aa',
    'btn_paste_hover_bg':   '#44454d',

    # ── QComboBox dropdown ────────────────────────────────────────────────────
    'combo_dropdown_bg':     '#3d3e48',
    'combo_dropdown_border': '#4a4b56',

    # ── Scrollbar ─────────────────────────────────────────────────────────────
    'scrollbar_track':          '#2e2f37',
    'scrollbar_handle':         '#4a4b56',
    'scrollbar_handle_radius':  '3px',
    'scrollbar_margin':         '1px',

    # ── Asunto ────────────────────────────────────────────────────────────────
    'asunto_bg':          '#3d3e48',
    'asunto_border':      '#4a4b56',
    'asunto_char_normal': '#8a93a8',
    'asunto_char_warn':   '#e5a550',
    'asunto_char_over':   '#e06c75',

    # ── Vista previa ──────────────────────────────────────────────────────────
    'preview_bg':         '#2e2f37',
    'preview_border':     '#42434d',
    'preview_empty_text': '#56575f',

    # ── CustomMessageBox ──────────────────────────────────────────────────────
    'msg_titlebar_bg':  '#26272e',
    'msg_titlebar_text':'#d3d9e3',
    'msg_body_bg':      '#363740',
    'msg_body_text':    '#d3d9e3',
    'msg_border':       '#42434d',
    'msg_icon_color':   '#e5a550',
    'msg_btn_ok_text':  '#ffffff',

    # ── Inline warn/error ─────────────────────────────────────────────────────
    'inline_warn_bg':      '#3a3020',
    'inline_warn_border':  '#e5a550',
    'inline_warn_text':    '#e5a550',
    'inline_error_bg':     '#3a2020',
    'inline_error_border': '#e06c75',
    'inline_error_text':   '#e06c75',

    # ── Tipografía ────────────────────────────────────────────────────────────
    'font_family':      'Segoe UI',
    'font_size_base':   '9pt',
    'font_size_button': '9pt',
    'font_size_small':  '8pt',
    'font_size_label':  '8pt',
    'font_size_nav':    '11px',

    # ── Border radius (str CSS) ───────────────────────────────────────────────
    'radius_input':        '6px',
    'radius_combo':        '6px',
    'radius_btn':          '6px',
    'radius_btn_linea':    '6px',
    'radius_btn_add':      '6px',
    'radius_btn_del':      '6px',
    'radius_radio_opt':    '6px',
    'radius_block':        '8px',
    'radius_msg':          '8px',
    'radius_msg_titlebar': '8px 8px 0 0',
    'radius_msg_body':     '0 0 8px 8px',
    'radius_msg_btn':      '6px',
    'radius_preview':      '6px',
    'radius_asunto':       '6px',
    'radius_zero':         '0px',

    # ── Border widths (str CSS) ───────────────────────────────────────────────
    'border_1px': '1px',

    # ── Letter spacing ────────────────────────────────────────────────────────
    'block_label_letter_spacing': '0.5px',

    # ── Padding (str CSS shorthand) ───────────────────────────────────────────
    'padding_input':         '6px 10px',
    'padding_btn_linea':     '8px 14px',
    'padding_btn_add':       '5px 12px',
    'padding_btn_primary':   '8px 18px',
    'padding_btn_secondary': '8px 12px',
    'padding_btn_paste':     '6px 12px',
    'padding_msg_btn':       '8px 20px',
    'padding_zero_h':        '0px',

    # =========================================================================
    # SIZING — int (Python + QSS como {c[k]}px)
    # =========================================================================
    'titlebar_height':       36,   # Python setFixedHeight
    'titlebar_fixed_height': 36,   # alias
    'titlebar_btn_width':    36,   # Python setFixedSize(36, 36)

    'input_min_height':  28,
    'combo_min_height':  28,
    'combo_arrow_width': 22,
    'combo_item_height': 26,
    'combo_arrow_size':  12,

    'btn_linea_min_height':     48,
    'btn_del_size':             28,
    'btn_add_min_height':       26,
    'btn_primary_min_height':   34,
    'btn_primary_min_width':    140,
    'btn_secondary_min_height': 34,
    'btn_paste_min_height':     28,
    'msg_btn_min_height':       34,
    'msg_btn_min_width':        110,

    'scrollbar_width':      7,
    'scrollbar_handle_min': 28,

    'msg_box_min_width': 400,
    'msg_box_max_width': 460,

    # =========================================================================
    # LAYOUT — int y tuples (Python only)
    # =========================================================================
    'app_min_width':      800,
    'app_min_height':     600,
    'app_default_width':  920,
    'app_default_height': 860,
    'preview_panel_width': 400,   # px que se suman al abrir preview

    'margins_app_root':       (0, 0, 0, 0),
    'spacing_app_root':       0,
    'margins_titlebar_inner': (12, 0, 4, 0),
    'spacing_titlebar':       8,
    'titlebar_logo_size':     (20, 20),

    'margins_scroll_content': (14, 14, 14, 14),
    'spacing_scroll_content': 10,

    'margins_block_outer':    (0, 0, 0, 0),
    'spacing_block_body':     8,

    'btn_linea_icon_size':    (20, 20),
    'btn_linea_spacing':      8,

    'radio_opt_grid_cols':    2,
    'radio_opt_grid_spacing': 8,
    'radio_opt_min_height':   44,

    'spacing_datos_fields':      8,
    'spacing_field_inline':      8,

    'dyn_row_spacing':        8,

    'msg_icon_circle_size':   (40, 40),
    'margins_msg_titlebar':   (14, 0, 6, 0),
    'spacing_msg_titlebar':   8,
    'margins_msg_body':       (20, 16, 20, 14),
    'spacing_msg_body':       14,
    'margins_msg_buttons':    (0, 6, 0, 0),

    'preview_min_height': 220,
    'margins_preview':    (0, 0, 0, 0),
}


def build_qss() -> str:
    """
    Genera el QSS ESTÁTICO con doble paleta de acento.
    Llamar UNA SOLA VEZ al arranque con app.setStyleSheet(build_qss()).

    Para cambiar acento:
        window.setProperty("empresa", "RRGG")   # o "Transportes"
        window.style().polish(window)
    """
    c = QSSD

    # Valores de acento por empresa — usados en los selectores [empresa="X"]
    RRGG  = dict(acc='#6590fd', dark='#4a72e8', light='#252d4a')
    TRANS = dict(acc='#56b4a0', dark='#3d9484', light='#1b3030')

    def accent_rules(sel: str, a: dict) -> str:
        """Genera todas las reglas de acento para un selector de empresa."""
        return f"""
    /* ── Acento: {sel} ───────────────────────────────────────────────── */
    {sel} QPushButton[role="btn-linea"][selected="true"],
    {sel} QPushButton[role="btn-tpl-l1"][selected="true"] {{
        background-color: {a['acc']};
        color:            #ffffff;
        border-color:     {a['acc']};
    }}
    {sel} QFrame[role="radio-opt"][selected="true"] {{
        background-color: {a['light']};
        border-color:     {a['acc']};
    }}
    {sel} QFrame[role="radio-opt"] QRadioButton::indicator:checked {{
        border-color: {a['acc']};
        background:   {a['acc']};
    }}
    {sel} QLineEdit:hover,
    {sel} QLineEdit:focus   {{ border-color: {a['acc']}; }}
    {sel} QComboBox:hover,
    {sel} QComboBox:focus   {{ border-color: {a['acc']}; }}
    {sel} QLineEdit {{ selection-background-color: {a['acc']}; }}
    {sel} QComboBox {{ selection-background-color: {a['acc']}; }}
    {sel} QComboBox QAbstractItemView::item:hover    {{ background-color: {a['acc']}; color: #ffffff; }}
    {sel} QComboBox QAbstractItemView::item:selected {{ background-color: {a['dark']}; color: #ffffff; }}
    {sel} QPushButton[role="btn-add-row"] {{
        color:        {a['acc']};
        border-color: {a['acc']};
    }}
    {sel} QPushButton[role="btn-add-row"]:hover {{ background-color: {a['light']}; }}
    {sel} QPushButton[role="btn-primary"] {{
        background-color: {a['acc']};
    }}
    {sel} QPushButton[role="btn-primary"]:hover   {{ background-color: {a['dark']}; }}
    {sel} QPushButton[role="btn-primary"]:pressed {{ background-color: {a['dark']}; }}
    {sel} QPushButton[role="btn-linea"]:hover,
    {sel} QPushButton[role="btn-tpl-l1"]:hover {{ border-color: {a['acc']}; }}
    {sel} QRadioButton::indicator:checked {{ border-color: {a['acc']}; background: {a['acc']}; }}
    {sel} #MsgBtnOk              {{ background-color: {a['acc']}; }}
    {sel} #MsgBtnOk:hover        {{ background-color: {a['dark']}; }}
    {sel} QScrollBar::handle:vertical:hover,
    {sel} QScrollBar::handle:horizontal:hover {{ background: {a['acc']}; }}
    """

    return f"""

    /* ===================================================================
       S01  RESET GLOBAL
       =================================================================== */
    QWidget {{
        background-color: {c['app_bg']};
        color:            {c['text_primary']};
        font-family:      "{c['font_family']}";
        font-size:        {c['font_size_base']};
        font-weight:      {c['fw_normal']};
        outline:          {c['css_none']};
    }}

    /* ===================================================================
       S02  SCROLL AREA
       =================================================================== */
    QScrollArea {{ background-color: {c['app_bg']}; border: {c['css_none']}; }}
    QScrollArea > QWidget > QWidget {{ background-color: {c['app_bg']}; }}

    /* ===================================================================
       S03  BLOQUES
       =================================================================== */
    #BlockWidget {{
        background-color: {c['block_body_bg']};
        border:           {c['border_1px']} solid {c['block_body_border']};
        border-radius:    {c['radius_block']};
    }}
    #SLabel {{
        color:          {c['block_header_text']};
        font-size:      {c['font_size_small']};
        font-weight:    {c['fw_bold']};
        letter-spacing: {c['block_label_letter_spacing']};
        background:     {c['css_transparent']};
    }}
    #FieldLabel {{
        color:       {c['text_label']};
        font-size:   {c['font_size_label']};
        font-weight: {c['fw_normal']};
        background:  {c['css_transparent']};
    }}

    /* ===================================================================
       S04  QLINEEDIT
       =================================================================== */
    QLineEdit {{
        background-color: {c['surface']};
        color:            {c['text_primary']};
        border:           {c['border_1px']} solid {c['border_input']};
        border-radius:    {c['radius_input']};
        padding:          {c['padding_input']};
        min-height:       {c['input_min_height']}px;
    }}
    QLineEdit:disabled {{
        background-color: {c['surface_alt']};
        color:            {c['text_disabled']};
        border-color:     {c['border_input']};
    }}
    QLineEdit#AsuntoEdit {{
        background-color: {c['asunto_bg']};
        border:           {c['border_1px']} solid {c['asunto_border']};
        border-radius:    {c['radius_asunto']};
    }}

    /* ===================================================================
       S05  QCOMBOBOX
       =================================================================== */
    QComboBox {{
        background-color: {c['surface']};
        color:            {c['text_primary']};
        border:           {c['border_1px']} solid {c['border_input']};
        border-radius:    {c['radius_combo']};
        padding:          {c['padding_input']};
        min-height:       {c['combo_min_height']}px;
    }}
    QComboBox:disabled {{ background-color: {c['surface_alt']}; color: {c['text_disabled']}; }}
    QComboBox::drop-down {{ border: {c['css_none']}; width: {c['combo_arrow_width']}px; }}
    QComboBox::down-arrow {{ width: {c['combo_arrow_size']}px; height: {c['combo_arrow_size']}px; image: {c['css_image_none']}; }}
    QComboBox QAbstractItemView {{
        background-color: {c['combo_dropdown_bg']};
        color:            {c['text_primary']};
        border:           {c['border_1px']} solid {c['combo_dropdown_border']};
        border-radius:    {c['radius_zero']};
        outline:          {c['css_outline_none']};
        padding:          2px;
    }}
    QComboBox QAbstractItemView::item {{ min-height: {c['combo_item_height']}px; padding: 3px 8px; color: {c['text_primary']}; }}

    /* ===================================================================
       S06  BOTONES GRANDES (estado neutro — seleccionado via [empresa])
       =================================================================== */
    QPushButton[role="btn-linea"],
    QPushButton[role="btn-tpl-l1"] {{
        background-color: {c['btn_linea_bg']};
        color:            {c['btn_linea_text']};
        border:           {c['border_1px']} solid {c['btn_linea_border']};
        border-radius:    {c['radius_btn_linea']};
        font-weight:      {c['fw_bold']};
        font-size:        {c['font_size_button']};
        text-align:       {c['align_center']};
    }}
    QPushButton[role="btn-linea"] {{
        padding:    {c['padding_btn_linea']};
        min-height: {c['btn_linea_min_height']}px;
    }}
    QPushButton[role="btn-tpl-l1"] {{
        padding:    6px 12px;
        min-height: 42px;
    }}
    QPushButton[role="btn-linea"]:hover,
    QPushButton[role="btn-tpl-l1"]:hover {{ background-color: {c['btn_linea_hover_bg']}; }}
    QPushButton[role="btn-linea"]:disabled,
    QPushButton[role="btn-tpl-l1"]:disabled {{
        background-color: {c['btn_linea_bg']};
        color:            {c['text_disabled']};
        border-color:     {c['border_input']};
    }}

    /* ===================================================================
       S07  RADIO-CARDS L2
       =================================================================== */
    QFrame[role="radio-opt"] {{
        background-color: {c['radio_opt_bg']};
        border:           {c['border_1px']} solid {c['radio_opt_border']};
        border-radius:    {c['radius_radio_opt']};
    }}
    QFrame[role="radio-opt"]:hover {{ background-color: {c['radio_opt_hover_bg']}; }}
    QFrame[role="radio-opt"] QRadioButton {{
        background-color: {c['css_transparent']};
        color:            {c['text_primary']};
        font-size:        {c['font_size_button']};
        font-weight:      {c['fw_bold']};
        spacing:          8px;
    }}
    QFrame[role="radio-opt"] QRadioButton::indicator {{
        width: 13px; height: 13px; border-radius: 7px;
        border: 2px solid {c['radio_dot_border']}; background: {c['surface']};
    }}

    /* ===================================================================
       S08  BOTÓN AGREGAR FILA (estado neutro — color via [empresa])
       =================================================================== */
    QPushButton[role="btn-add-row"] {{
        background-color: {c['css_transparent']};
        border:           {c['border_1px']} dashed {c['border_input']};
        border-radius:    {c['radius_btn_add']};
        padding:          {c['padding_btn_add']};
        min-height:       {c['btn_add_min_height']}px;
        font-size:        {c['font_size_button']};
        text-align:       {c['align_left']};
    }}
    QPushButton[role="btn-add-row"]:disabled {{
        color:        {c['btn_add_row_disabled_text']};
        border-color: {c['btn_add_row_disabled_border']};
        background:   {c['css_transparent']};
    }}

    /* ===================================================================
       S09  BOTÓN ELIMINAR FILA
       =================================================================== */
    QPushButton[role="btn-del-row"] {{
        background-color: {c['btn_del_bg']};
        border:           {c['border_1px']} solid {c['btn_del_border']};
        border-radius:    {c['radius_btn_del']};
        min-width:  {c['btn_del_size']}px; max-width:  {c['btn_del_size']}px;
        min-height: {c['btn_del_size']}px; max-height: {c['btn_del_size']}px;
        padding:    {c['padding_zero_h']};
    }}
    QPushButton[role="btn-del-row"]:hover {{
        background-color: {c['btn_del_hover_bg']};
        border-color:     {c['inline_error_border']};
    }}

    /* ===================================================================
       S10  BOTONES DE ACCIÓN
       =================================================================== */
    QPushButton[role="btn-primary"] {{
        color:         #ffffff;
        border:        {c['css_none']};
        border-radius: {c['radius_btn']};
        padding:       {c['padding_btn_primary']};
        min-height:    {c['btn_primary_min_height']}px;
        min-width:     {c['btn_primary_min_width']}px;
        font-weight:   {c['fw_bold']};
        font-size:     {c['font_size_button']};
    }}
    QPushButton[role="btn-secondary"] {{
        background-color: {c['btn_secondary_bg']};
        color:            {c['btn_secondary_text']};
        border:           {c['border_1px']} solid {c['btn_secondary_border']};
        border-radius:    {c['radius_btn']};
        padding:          {c['padding_btn_secondary']};
        min-height:       {c['btn_secondary_min_height']}px;
        font-size:        {c['font_size_button']};
    }}
    QPushButton[role="btn-secondary"]:hover {{ background-color: {c['btn_secondary_hover']}; }}

    QPushButton[role="btn-paste"] {{
        background-color: {c['btn_paste_bg']};
        color:            {c['btn_paste_text']};
        border:           {c['border_1px']} solid {c['btn_paste_border']};
        border-radius:    {c['radius_btn']};
        padding:          {c['padding_btn_paste']};
        min-height:       {c['btn_paste_min_height']}px;
        font-size:        {c['font_size_button']};
    }}
    QPushButton[role="btn-paste"]:hover {{ background-color: {c['btn_paste_hover_bg']}; }}

    /* ===================================================================
       S11  TITLEBAR
       =================================================================== */
    #AppTitleBar {{ background-color: {c['titlebar_bg']}; min-height: {c['titlebar_height']}px; max-height: {c['titlebar_height']}px; }}
    #AppTitleLabel {{ color: {c['text_on_dark']}; font-weight: {c['fw_bold']}; font-size: {c['font_size_button']}; background: {c['css_transparent']}; }}
    QPushButton[role="titlebar-min"],
    QPushButton[role="titlebar-max"] {{
        background-color: {c['css_transparent']}; color: {c['titlebar_btn_text']};
        border: {c['css_none']}; font-size: {c['font_size_nav']};
        min-width: {c['titlebar_btn_width']}px; max-width: {c['titlebar_btn_width']}px;
        min-height: {c['titlebar_height']}px; max-height: {c['titlebar_height']}px;
        border-radius: {c['radius_zero']}; padding: {c['padding_zero_h']};
    }}
    QPushButton[role="titlebar-min"]:hover,
    QPushButton[role="titlebar-max"]:hover {{ background-color: {c['titlebar_btn_hover_bg']}; }}
    QPushButton[role="titlebar-close"] {{
        background-color: {c['css_transparent']}; color: {c['titlebar_btn_text']};
        border: {c['css_none']}; font-size: {c['font_size_nav']};
        min-width: {c['titlebar_btn_width']}px; max-width: {c['titlebar_btn_width']}px;
        min-height: {c['titlebar_height']}px; max-height: {c['titlebar_height']}px;
        border-radius: {c['radius_zero']}; padding: {c['padding_zero_h']};
    }}
    QPushButton[role="titlebar-close"]:hover   {{ background-color: {c['titlebar_close_hover_bg']}; }}
    QPushButton[role="titlebar-close"]:pressed {{ background-color: {c['titlebar_close_pressed_bg']}; }}

    /* ===================================================================
       S12  MESSAGEBOX
       =================================================================== */
    #MsgFrame {{ background-color: {c['msg_body_bg']}; border: {c['border_1px']} solid {c['msg_border']}; border-radius: {c['radius_msg']}; }}
    #MsgTitleBar {{ background-color: {c['msg_titlebar_bg']}; border-radius: {c['radius_msg_titlebar']}; }}
    #MsgTitleLabel {{ color: {c['msg_titlebar_text']}; font-weight: {c['fw_bold']}; font-size: {c['font_size_button']}; background: {c['css_transparent']}; }}
    #MsgBody {{ background-color: {c['msg_body_bg']}; border-radius: {c['radius_msg_body']}; }}
    #MsgBodyText {{ color: {c['msg_body_text']}; font-size: {c['font_size_base']}; background: {c['css_transparent']}; }}
    #MsgBtnOk {{
        color: {c['msg_btn_ok_text']}; border: {c['css_none']}; border-radius: {c['radius_msg_btn']};
        padding: {c['padding_msg_btn']}; min-height: {c['msg_btn_min_height']}px;
        min-width: {c['msg_btn_min_width']}px; font-weight: {c['fw_bold']};
    }}

    /* ===================================================================
       S13  SCROLLBAR
       =================================================================== */
    QScrollBar:vertical {{ background: {c['scrollbar_track']}; width: {c['scrollbar_width']}px; border: {c['css_none']}; border-radius: {c['scrollbar_handle_radius']}; }}
    QScrollBar::handle:vertical {{ background: {c['scrollbar_handle']}; border-radius: {c['scrollbar_handle_radius']}; min-height: {c['scrollbar_handle_min']}px; margin: {c['scrollbar_margin']}; }}
    QScrollBar::handle:vertical:pressed {{ background: #4a4b56; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
    QScrollBar:horizontal {{ background: {c['scrollbar_track']}; height: {c['scrollbar_width']}px; border: {c['css_none']}; border-radius: {c['scrollbar_handle_radius']}; }}
    QScrollBar::handle:horizontal {{ background: {c['scrollbar_handle']}; border-radius: {c['scrollbar_handle_radius']}; min-width: {c['scrollbar_handle_min']}px; margin: {c['scrollbar_margin']}; }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}

    /* ===================================================================
       S14  MISC
       =================================================================== */
    QToolTip {{ background-color: {c['surface_alt']}; color: {c['text_primary']}; border: {c['border_1px']} solid {c['border_block']}; border-radius: 4px; padding: 4px 8px; font-size: {c['font_size_small']}; }}
    #InlineWarn  {{ background-color: {c['inline_warn_bg']};  border-left: 3px solid {c['inline_warn_border']};  border-radius: 0 4px 4px 0; color: {c['inline_warn_text']};  font-size: {c['font_size_small']}; padding: 6px 10px; }}
    #InlineError {{ background-color: {c['inline_error_bg']}; border-left: 3px solid {c['inline_error_border']}; border-radius: 0 4px 4px 0; color: {c['inline_error_text']}; font-size: {c['font_size_small']}; padding: 6px 10px; }}
    #PreviewContainer {{ background-color: {c['preview_bg']}; border: {c['border_1px']} solid {c['preview_border']}; border-radius: {c['radius_preview']}; }}
    QFrame[frameShape="4"] {{ background-color: {c['border_block']}; border: {c['css_none']}; max-height: 1px; }}
    QRadioButton {{ background-color: {c['css_transparent']}; color: {c['text_primary']}; font-size: {c['font_size_base']}; spacing: 6px; }}
    QRadioButton::indicator {{ width: 13px; height: 13px; border-radius: 7px; border: 2px solid {c['radio_dot_border']}; background: {c['surface']}; }}

    /* ===================================================================
       S15  PALETAS DE ACENTO POR EMPRESA
       Reglas generadas para [empresa="RRGG"] y [empresa="Transportes"].
       No se regeneran — se activan con setProperty() + polish().
       =================================================================== */
    {accent_rules('[empresa="RRGG"]',       RRGG)}
    {accent_rules('[empresa="Transportes"]', TRANS)}

    /* Default (sin empresa seleccionada): sin acento marcado */
    QWidget:not([empresa]) QPushButton[role="btn-primary"] {{ background-color: #4a4b56; }}

    """


def get_palette() -> QPalette:
    c = QSSD
    p = QPalette()
    p.setColor(QPalette.Window,          QColor(c['app_bg']))
    p.setColor(QPalette.WindowText,      QColor(c['text_primary']))
    p.setColor(QPalette.Base,            QColor(c['surface']))
    p.setColor(QPalette.AlternateBase,   QColor(c['surface_alt']))
    p.setColor(QPalette.Text,            QColor(c['text_primary']))
    p.setColor(QPalette.Button,          QColor(c['btn_linea_bg']))
    p.setColor(QPalette.ButtonText,      QColor(c['text_primary']))
    p.setColor(QPalette.Highlight,       QColor(c['accent_rrgg']))
    p.setColor(QPalette.HighlightedText, QColor('#ffffff'))
    p.setColor(QPalette.ToolTipBase,     QColor(c['surface_alt']))
    p.setColor(QPalette.ToolTipText,     QColor(c['text_primary']))
    p.setColor(QPalette.PlaceholderText, QColor(c['text_placeholder']))
    p.setColor(QPalette.Disabled, QPalette.Text,       QColor(c['text_disabled']))
    p.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(c['text_disabled']))
    return p
