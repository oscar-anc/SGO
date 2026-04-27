# coding: utf-8
"""
theme.py — Gestión centralizada de tema y colores.

Todos los selectores QSS, colores, dimensiones, márgenes, paddings,
tipografía y tamaños de widget se definen aquí como variables.
Cambiar un valor aquí actualiza instantáneamente toda la app.

Estructura de secciones:
  QSSD → diccionario de variables (colores, tipografía, bordes, tamaños, layout)
  build_qss() → genera el string QSS final interpolando las variables

Grupos de variables:
  Colores     → app_bg, text_*, surface_*, accent_*, border_*, btn_*
  Tipografía  → font_family, font_size_*, fw_*
  Bordes      → border_width_*, radius_*
  Padding     → padding_*
  Tamaños     → *_min_height, *_min_width, *_size, *_height, *_width
  Layout Py   → margins_*, spacing_* (tuplas usadas en Python, no en QSS)

Convenciones de nomenclatura:
  widget_parte_estado   → ej. btn_primary_hover, input_border_focus
  Sin slash, solo guiones bajos.
  Valores de px sin sufijo cuando se usan en QSS como {c['key']}px.
  Valores con sufijo CSS cuando van directamente: '1px', '7px 10px', etc.
"""

from PySide6.QtGui import QPalette, QColor

QSSD = {
    # =========================================================================
    # COLOUR VARIABLES
    # Cambia un color aquí → todas las reglas QSS que lo referencian se actualizan.
    # =========================================================================

    # ── Fondo de la aplicación ────────────────────────────────────────────────
    # Usado por: QWidget (reset global), QScrollArea viewport, ventana principal
    'app_bg':                       '#f0f3f6',

    # ── Texto ─────────────────────────────────────────────────────────────────
    # text_primary       → QLabel, QLineEdit, QComboBox en toda la app
    # text_on_dark       → texto sobre fondos oscuros (headers de bloque, titlebar)
    # text_disabled      → cualquier widget con setEnabled(False)
    # text_placeholder   → placeholder de QLineEdit / QComboBox
    # text_on_accent     → texto sobre fondo de color accent (botones seleccionados)
    # text_muted         → texto secundario, hints, instrucciones
    # text_label         → etiquetas de campo (QLabel encima de inputs)
    'text_primary':                 '#4f5f6f',
    'text_on_dark':                 '#FFFFFF',
    'text_disabled':                '#a1b1c2',
    'text_placeholder':             '#a1b1c2',
    'text_on_accent':               '#FFFFFF',
    'text_muted':                   '#8a9bae',
    'text_label':                   '#6b7c8d',

    # ── Superficies ───────────────────────────────────────────────────────────
    # surface      → fondo estándar de inputs (QLineEdit, QComboBox)
    # surface_alt  → fondo alternativo (filas pares de tabla, inputs read-only)
    # surface_card → fondo del cuerpo de cada bloque/card de sección
    'surface':                      '#FFFFFF',
    'surface_alt':                  '#e1ecf7',
    'surface_card':                 '#FFFFFF',

    # ── Constantes CSS ────────────────────────────────────────────────────────
    # Valores fijos usados en reglas QSS — centralizados para cambio global
    'css_none':                     'none',
    'css_transparent':              'transparent',
    'css_solid':                    'solid',
    'css_zero':                     '0',
    'css_outline_none':             'none',
    'css_image_none':               'none',

    # ── Constantes de alineación ──────────────────────────────────────────────
    'align_left':                   'left',
    'align_center':                 'center',
    'align_right':                  'right',

    # ── Constantes de peso tipográfico ────────────────────────────────────────
    'fw_bold':                      'bold',
    'fw_normal':                    'normal',

    # ── Constantes de bordes por lado ─────────────────────────────────────────
    'border_top_none':              'none',
    'border_bottom_none':           'none',
    'border_left_none':             'none',
    'border_right_none':            'none',

    # ── Alias y constantes estructurales ──────────────────────────────────────
    'margin_zero':                  '0',
    'block_header_min_height':      '36',   # min-height del header de cada bloque (px str)

    # ── Acento RRGG (azul) ────────────────────────────────────────────────────
    # accent_rrgg        → color principal de la línea RRGG
    # accent_rrgg_dark   → variante oscura para hover/pressed sobre accent
    # accent_rrgg_light  → tint muy claro para hover sobre fondo blanco
    'accent_rrgg':                  '#0078d4',
    'accent_rrgg_dark':             '#005a9e',
    'accent_rrgg_light':            '#e6f1fb',

    # ── Acento Transportes (verde) ────────────────────────────────────────────
    # accent_trans       → color principal de la línea Transportes
    # accent_trans_dark  → variante oscura para hover/pressed
    # accent_trans_light → tint muy claro para hover sobre fondo blanco
    'accent_trans':                 '#107c10',
    'accent_trans_dark':            '#0a5c0a',
    'accent_trans_light':           '#eaf3de',

    # ── Acento genérico (alias — se sobreescribe en Python según línea activa) ─
    # accent       → color activo según empresa seleccionada
    # accent_dark  → variante oscura del activo
    # accent_light → tint claro del activo
    'accent':                       '#0078d4',
    'accent_dark':                  '#005a9e',
    'accent_light':                 '#e6f1fb',

    # ── Bordes de inputs ──────────────────────────────────────────────────────
    # border_input       → QLineEdit, QComboBox en reposo
    # border_input_hover → al pasar el mouse
    # border_input_focus → al hacer foco (clic / teclado)
    # border_block       → borde del contenedor de cada sección/bloque
    'border_input':                 '#C8D0D8',
    'border_input_hover':           '#0078d4',
    'border_input_focus':           '#0078d4',
    'border_block':                 '#dce6f0',

    # ── Barra de título de la ventana ─────────────────────────────────────────
    # titlebar_bg             → fondo del CustomTitleBar
    # titlebar_btn_text       → color de íconos de Min/Max/Close en reposo
    # titlebar_btn_hover_bg   → fondo hover de botones Min/Max
    # titlebar_btn_pressed_bg → fondo pressed de botones Min/Max
    # titlebar_close_hover_bg / pressed_bg → botón Cerrar (familia roja)
    'titlebar_bg':                  '#1e2d3d',
    'titlebar_btn_text':            '#FFFFFF',
    'titlebar_btn_hover_bg':        '#0078d4',
    'titlebar_btn_pressed_bg':      '#005a9e',
    'titlebar_close_hover_bg':      '#e81123',
    'titlebar_close_pressed_bg':    '#c50f1f',

    # ── Bloques / secciones de formulario ─────────────────────────────────────
    # Cada sección del formulario progresivo es un "bloque" con header y body.
    # block_header_bg    → fondo de la barra superior del bloque (label de sección)
    # block_header_text  → texto del label de sección
    # block_body_bg      → fondo del cuerpo del bloque
    # block_body_border  → borde del contenedor del bloque
    'block_header_bg':              '#f0f3f6',
    'block_header_text':            '#6b7c8d',
    'block_body_bg':                '#FFFFFF',
    'block_body_border':            '#dce6f0',

    # ── Botón línea de negocio / modo envío (pushbuttons grandes) ─────────────
    # btn_linea_bg         → fondo en reposo (sin seleccionar)
    # btn_linea_border     → borde en reposo
    # btn_linea_text       → texto/ícono en reposo
    # btn_linea_hover_bg   → fondo al hacer hover
    # btn_linea_sel_bg     → fondo cuando está seleccionado (activo)
    # btn_linea_sel_text   → texto/ícono cuando está seleccionado
    'btn_linea_bg':                 '#f5f7fa',
    'btn_linea_border':             '#C8D0D8',
    'btn_linea_text':               '#4f5f6f',
    'btn_linea_hover_bg':           '#e8f0f8',
    'btn_linea_sel_bg':             '#0078d4',    # se sobreescribe en Python según empresa
    'btn_linea_sel_text':           '#FFFFFF',
    'btn_linea_sel_border':         '#0078d4',

    # ── RadioButton tipo pill (opciones L2 de plantilla) ──────────────────────
    # radio_opt_bg         → fondo de cada opción en reposo
    # radio_opt_border     → borde en reposo
    # radio_opt_hover_bg   → fondo al hover
    # radio_opt_sel_bg     → fondo cuando está seleccionada
    # radio_opt_sel_border → borde cuando está seleccionada
    'radio_opt_bg':                 '#f5f7fa',
    'radio_opt_border':             '#C8D0D8',
    'radio_opt_hover_bg':           '#e8f0f8',
    'radio_opt_sel_bg':             '#e6f1fb',    # tint del accent, se ajusta en Python
    'radio_opt_sel_border':         '#0078d4',
    'radio_dot_border':             '#C8D0D8',
    'radio_dot_sel_border':         '#0078d4',
    'radio_dot_sel_fill':           '#0078d4',

    # ── Botón Agregar fila (dashed outline) ───────────────────────────────────
    # btn_add_row_text    → texto e ícono del botón "Agregar póliza / endoso"
    # btn_add_row_border  → borde dashed
    # btn_add_row_hover   → fondo al hover
    # btn_add_row_disabled_text → texto cuando se alcanza el máximo
    'btn_add_row_text':             '#0078d4',
    'btn_add_row_border':           '#0078d4',
    'btn_add_row_hover_bg':         '#e6f1fb',
    'btn_add_row_disabled_text':    '#a1b1c2',
    'btn_add_row_disabled_border':  '#dce6f0',

    # ── Botón Eliminar fila (ícono tacho) ─────────────────────────────────────
    # btn_del_bg          → fondo en reposo
    # btn_del_border      → borde en reposo
    # btn_del_icon        → color del ícono tacho en reposo
    # btn_del_hover_bg    → fondo al hover
    # btn_del_hover_icon  → color del ícono al hover
    'btn_del_bg':                   '#f5f7fa',
    'btn_del_border':               '#dce6f0',
    'btn_del_icon':                 '#8a9bae',
    'btn_del_hover_bg':             '#fce8ed',
    'btn_del_hover_icon':           '#c42b1c',

    # ── Botón primario (Abrir en Outlook) ─────────────────────────────────────
    # btn_primary_bg      → fondo en reposo (accent de empresa)
    # btn_primary_hover   → fondo al hover
    # btn_primary_text    → texto del botón
    'btn_primary_bg':               '#0078d4',
    'btn_primary_hover':            '#005a9e',
    'btn_primary_text':             '#FFFFFF',

    # ── Botón secundario (Limpiar) ────────────────────────────────────────────
    # btn_secondary_bg     → fondo en reposo
    # btn_secondary_border → borde
    # btn_secondary_text   → texto
    # btn_secondary_hover  → fondo al hover
    'btn_secondary_bg':             '#FFFFFF',
    'btn_secondary_border':         '#C8D0D8',
    'btn_secondary_text':           '#4f5f6f',
    'btn_secondary_hover':          '#f0f3f6',

    # ── Botón Pegar datos del portapapeles ────────────────────────────────────
    # btn_paste_bg    → fondo en reposo (variante suave)
    # btn_paste_hover → fondo al hover
    # btn_paste_text  → texto e ícono
    'btn_paste_bg':                 '#f5f7fa',
    'btn_paste_border':             '#C8D0D8',
    'btn_paste_text':               '#4f5f6f',
    'btn_paste_hover_bg':           '#e1ecf7',

    # ── QComboBox popup dropdown ───────────────────────────────────────────────
    'combo_dropdown_bg':            '#FFFFFF',
    'combo_dropdown_border':        '#96989a',
    'combo_item_hover_bg':          '#0078d4',
    'combo_item_hover_text':        '#FFFFFF',
    'combo_item_sel_bg':            '#1e2d3d',
    'combo_item_sel_text':          '#FFFFFF',

    # ── Scrollbar ─────────────────────────────────────────────────────────────
    'scrollbar_track':              '#f0f3f6',
    'scrollbar_handle':             '#ced6dc',
    'scrollbar_handle_hover':       '#959fa9',
    'scrollbar_handle_pressed':     '#4f5f6f',

    # ── Campo de asunto editable ──────────────────────────────────────────────
    # asunto_char_normal  → color del contador de caracteres en reposo
    # asunto_char_warn    → color cuando supera 80 caracteres (ámbar)
    # asunto_char_over    → color cuando supera 100 caracteres (rojo)
    'asunto_char_normal':           '#8a9bae',
    'asunto_char_warn':             '#9d5a00',
    'asunto_char_over':             '#c42b1c',
    'asunto_bg':                    '#f5f7fa',
    'asunto_border':                '#C8D0D8',

    # ── Vista previa del correo ───────────────────────────────────────────────
    # preview_bg      → fondo del contenedor de vista previa
    # preview_border  → borde del contenedor
    # preview_empty   → color del texto cuando está vacío
    'preview_bg':                   '#f5f7fa',
    'preview_border':               '#dce6f0',
    'preview_empty_text':           '#a1b1c2',

    # ── CustomMessageBox de advertencia Outlook ───────────────────────────────
    # msg_titlebar_bg    → barra de título del diálogo
    # msg_titlebar_text  → texto de la barra de título
    # msg_body_bg        → fondo del cuerpo del diálogo
    # msg_body_text      → texto del cuerpo
    # msg_border         → borde del diálogo completo
    # msg_icon_bg        → fondo circular del ícono de advertencia
    # msg_icon_color     → color del ícono SVG de advertencia
    # msg_btn_ok_bg      → botón "Entendido" en reposo
    # msg_btn_ok_hover   → botón "Entendido" al hover
    # msg_btn_ok_text    → texto del botón "Entendido"
    'msg_titlebar_bg':              '#1e2d3d',
    'msg_titlebar_text':            '#FFFFFF',
    'msg_body_bg':                  '#FFFFFF',
    'msg_body_text':                '#4f5f6f',
    'msg_border':                   '#dce6f0',
    'msg_icon_bg':                  '#fff4ce',
    'msg_icon_color':               '#9d5a00',
    'msg_btn_ok_bg':                '#0078d4',
    'msg_btn_ok_hover':             '#005a9e',
    'msg_btn_ok_text':              '#FFFFFF',

    # ── Advertencia / error inline ────────────────────────────────────────────
    # Usado en el paste de portapapeles cuando el JSON no es válido
    'inline_warn_bg':               '#fff4ce',
    'inline_warn_border':           '#f0a500',
    'inline_warn_text':             '#9d5a00',
    'inline_error_bg':              '#fde7e9',
    'inline_error_border':          '#c42b1c',
    'inline_error_text':            '#c42b1c',

    # =========================================================================
    # TYPOGRAPHY VARIABLES
    # =========================================================================

    # ── Familia y tamaño de fuente ────────────────────────────────────────────
    # font_family     → aplicado globalmente a QWidget
    # font_size_base  → heredado por todos los widgets salvo excepciones
    'font_family':                  'Segoe UI',
    'font_size_base':               '9pt',
    'font_size_button':             '9pt',       # QPushButton label
    'font_size_small':              '8pt',       # labels de sección, hints
    'font_size_label':              '8pt',       # etiquetas de campo (encima de input)
    'font_size_large':              '11pt',      # títulos de bloque, msg titlebar
    'font_size_nav':                '11px',      # fuente en barra de título
    'font_size_preview':            '9pt',       # texto dentro de la vista previa

    # ── Pesos tipográficos ────────────────────────────────────────────────────
    'text_primary_bold':            'normal',    # labels generales de la app
    'block_label_bold':             'bold',      # etiqueta de sección (SLABEL)
    'btn_primary_font_weight':      'bold',      # botones primarios
    'btn_linea_font_weight':        'bold',      # botones de línea / modo envío
    'msg_titlebar_text_bold':       'bold',      # título del CustomMessageBox
    'msg_body_text_bold':           'normal',    # cuerpo del CustomMessageBox

    # =========================================================================
    # BORDER VARIABLES
    # Valores CSS: '1px', '2px', '0px'
    # =========================================================================

    # ── Anchos de borde ───────────────────────────────────────────────────────
    'border_width_input':           '1px',   # QLineEdit
    'border_width_combo':           '1px',   # QComboBox caja principal
    'border_width_combo_dropdown':  '1px',   # popup de QComboBox
    'border_width_block':           '1px',   # borde del bloque/sección
    'border_width_btn_linea':       '1px',   # botones grandes de línea/modo
    'border_width_btn_add':         '1px',   # botón Agregar (dashed)
    'border_width_btn_del':         '1px',   # botón Eliminar fila
    'border_width_btn_secondary':   '1px',   # botón Limpiar
    'border_width_msg':             '1px',   # CustomMessageBox borde
    'border_width_asunto':          '1px',   # campo de asunto editable
    'border_width_preview':         '1px',   # contenedor de vista previa

    # ── Border radius ─────────────────────────────────────────────────────────
    'radius_input':                 '4px',   # QLineEdit
    'radius_combo':                 '4px',   # QComboBox
    'radius_btn':                   '6px',   # QPushButton genérico
    'radius_btn_linea':             '8px',   # botones grandes de línea/modo
    'radius_btn_add':               '6px',   # botón Agregar fila
    'radius_btn_del':               '6px',   # botón Eliminar fila
    'radius_radio_opt':             '6px',   # contenedor de opción radio
    'radius_block':                 '10px',  # contenedor de cada bloque/sección
    'radius_msg':                   '10px',  # CustomMessageBox completo
    'radius_msg_titlebar':          '10px 10px 0 0',   # solo esquinas superiores
    'radius_msg_body':              '0 0 10px 10px',   # solo esquinas inferiores
    'radius_msg_btn':               '6px',   # botón dentro del CustomMessageBox
    'radius_preview':               '6px',   # contenedor de vista previa
    'radius_asunto':                '4px',   # campo de asunto editable
    'radius_zero':                  '0px',
    'radius_tab_inactive':          '2px',

    # =========================================================================
    # PADDING VARIABLES (QSS)
    # Shorthand CSS: '7px 10px' = vertical 7 / horizontal 10
    # =========================================================================

    'padding_input':                '7px 10px',     # QLineEdit / QComboBox
    'padding_btn':                  '8px 18px',     # QPushButton genérico
    'padding_btn_linea':            '14px 20px',    # botones grandes línea/modo
    'padding_btn_add':              '6px 14px',     # botón Agregar fila
    'padding_btn_primary':          '9px 20px',     # botón Abrir en Outlook
    'padding_btn_secondary':        '9px 14px',     # botón Limpiar
    'padding_btn_paste':            '7px 14px',     # botón Pegar portapapeles
    'padding_block_body':           '14px 18px',    # cuerpo de cada bloque
    'padding_block_header':         '0px',          # sin padding en label de sección
    'padding_msg_body':             '24px',         # cuerpo del CustomMessageBox
    'padding_msg_btn':              '9px 24px',     # botón del CustomMessageBox
    'padding_combo':                '4px 8px',      # alternate combo
    'padding_header_sec':           '4px 8px',      # QHeaderView section
    'padding_zero_h':               '0px',

    # =========================================================================
    # SIZING VARIABLES (QSS)
    # Sin sufijo 'px' — se agrega en el template QSS como {c['key']}px
    # =========================================================================

    # ── Inputs ────────────────────────────────────────────────────────────────
    'input_min_height':             '30',    # QLineEdit min-height
    'combo_min_height':             '30',    # QComboBox min-height
    'combo_arrow_width':            '24',    # ancho del área de flecha del dropdown
    'combo_item_height':            '28',    # altura de cada ítem del dropdown
    'combo_arrow_size':             '14',    # tamaño de la flecha dropdown (px)

    # ── Botones ───────────────────────────────────────────────────────────────
    'btn_min_height':               '32',    # QPushButton min-height estándar
    'btn_linea_min_height':         '64',    # botones grandes línea/modo envío
    'btn_del_size':                 '30',    # botón Eliminar fila (cuadrado)
    'btn_add_min_height':           '28',    # botón Agregar fila min-height
    'btn_primary_min_height':       '36',    # botón Abrir en Outlook
    'btn_primary_min_width':        '160',   # botón Abrir en Outlook min-width
    'btn_secondary_min_height':     '36',    # botón Limpiar
    'btn_paste_min_height':         '30',    # botón Pegar portapapeles
    'msg_btn_min_height':           '36',    # botón dentro del CustomMessageBox
    'msg_btn_min_width':            '120',   # ancho mínimo botón del diálogo

    # ── Scrollbar ─────────────────────────────────────────────────────────────
    'scrollbar_width':              '8',     # ancho/alto del QScrollBar
    'scrollbar_handle_min':         '30',    # min-height del handle
    'scrollbar_handle_radius':      '4px',   # radio del handle
    'scrollbar_margin':             '1px',   # margen del handle respecto al track

    # ── Misc ──────────────────────────────────────────────────────────────────
    'titlebar_height':              '36',    # altura del CustomTitleBar
    'titlebar_btn_width':           '36',    # ancho de botones Min/Max/Close
    'msg_min_width':                '400',   # ancho mínimo del CustomMessageBox
    'block_label_letter_spacing':   '0.6px', # espaciado entre letras del slabel

    # =========================================================================
    # LAYOUT & SIZE VARIABLES (Python)
    # Usados directamente en código Python — NOT en build_qss().
    # Tuples → desempaquetar con *QSSD['key']
    # Integers → usar directamente como valores px
    # =========================================================================

    # ── Ventana principal ──────────────────────────────────────────────────────
    'app_min_width':                760,
    'app_min_height':               600,
    'app_default_width':            860,
    'app_default_height':           900,
    'margins_app_root':             (0, 0, 0, 0),
    'spacing_app_root':             0,

    # ── TitleBar de la ventana ─────────────────────────────────────────────────
    'titlebar_fixed_height':        36,
    'titlebar_logo_size':           (22, 22),
    'margins_titlebar_inner':       (12, 0, 4, 0),
    'spacing_titlebar':             8,

    # ── Scroll area principal (contenedor del formulario progresivo) ───────────
    'margins_scroll_content':       (16, 16, 16, 16),
    'spacing_scroll_content':       10,

    # ── Bloque / sección individual del formulario ────────────────────────────
    # margins_block_outer → margen externo del bloque (separación entre bloques)
    # margins_block_body  → padding interno del cuerpo del bloque
    # spacing_block_body  → spacing del QVBoxLayout interno del bloque
    'margins_block_outer':          (0, 0, 0, 0),
    'spacing_block_body':           10,

    # ── Grilla de botones grandes (Línea de negocio / Modo de envío) ──────────
    # btn_linea_grid_cols → número de columnas en el QHBoxLayout
    # btn_linea_icon_size → tamaño del QSvgWidget dentro del botón
    'btn_linea_icon_size':          (24, 24),
    'btn_linea_spacing':            8,

    # ── Grilla de opciones L2 (radiobutton cards) ─────────────────────────────
    # Implementada con QGridLayout de 2 columnas
    'radio_opt_grid_cols':          2,
    'radio_opt_grid_spacing':       8,
    'radio_opt_min_height':         52,

    # ── Sección de campos de datos del despacho ───────────────────────────────
    'margins_datos_section':        (0, 0, 0, 0),
    'spacing_datos_fields':         10,       # vertical gap entre filas de campos
    'spacing_field_inline':         10,       # horizontal gap entre campos en una fila
    'field_label_margin_bottom':    4,        # margen inferior de la QLabel de campo

    # ── Filas dinámicas (agregar póliza / endoso / declaración) ───────────────
    'dyn_row_spacing':              10,       # gap entre columnas de la fila dinámica
    'dyn_row_margin_bottom':        8,        # margen inferior de cada fila dinámica

    # ── CustomMessageBox Outlook ──────────────────────────────────────────────
    'msg_box_min_width':            420,
    'msg_box_max_width':            480,
    'msg_icon_circle_size':         (44, 44),
    'margins_msg_titlebar':         (16, 0, 8, 0),
    'spacing_msg_titlebar':         8,
    'margins_msg_body':             (24, 20, 24, 16),
    'spacing_msg_body':             16,
    'margins_msg_buttons':          (0, 8, 0, 0),
    'spacing_msg_buttons':          8,

    # ── Área de vista previa ──────────────────────────────────────────────────
    'preview_min_height':           200,      # altura mínima del QWebEngineView
    'margins_preview':              (0, 0, 0, 0),
}


def build_qss() -> str:
    """
    Genera el string QSS completo interpolando todas las variables de QSSD.
    Retorna el QSS listo para aplicar con app.setStyleSheet(build_qss()).
    """
    c = QSSD
    qss = f"""

    /* =========================================================================
       S01  RESET GLOBAL
       Aplica a todo QWidget — fondo, texto y fuente base de la app
       ========================================================================= */

    QWidget {{
        background-color: {c['app_bg']};
        color:            {c['text_primary']};
        font-family:      "{c['font_family']}";
        font-size:        {c['font_size_base']};
        font-weight:      {c['text_primary_bold']};
    }}

    /* =========================================================================
       S02  QSCROLLAREA — contenedor principal del formulario progresivo
       ========================================================================= */

    QScrollArea {{
        background-color: {c['app_bg']};
        border:           {c['css_none']};
    }}
    QScrollArea > QWidget > QWidget {{
        background-color: {c['app_bg']};
    }}

    /* =========================================================================
       S03  BLOQUES DE SECCIÓN
       #BlockWidget → contenedor de cada sección del formulario progresivo
       #BlockBody   → cuerpo interno del bloque
       ========================================================================= */

    #BlockWidget {{
        background-color: {c['block_body_bg']};
        border:           {c['border_width_block']} solid {c['block_body_border']};
        border-radius:    {c['radius_block']};
    }}

    /* SLABEL — etiqueta de sección (texto uppercase pequeño) */
    #SLabel {{
        color:       {c['block_header_text']};
        font-size:   {c['font_size_small']};
        font-weight: {c['block_label_bold']};
    }}

    /* =========================================================================
       S04  ETIQUETAS DE CAMPO
       QLabel encima de cada input (Nombre contratante, CIA, Ramo, etc.)
       ========================================================================= */

    #FieldLabel {{
        color:       {c['text_label']};
        font-size:   {c['font_size_label']};
        font-weight: {c['fw_normal']};
    }}

    /* =========================================================================
       S05  QLINEEDIT
       Inputs de texto: Contratante, Contacto, Nro. Póliza, Vigencia, etc.
       ========================================================================= */

    QLineEdit {{
        background-color: {c['surface']};
        color:            {c['text_primary']};
        border:           {c['border_width_input']} solid {c['border_input']};
        border-radius:    {c['radius_input']};
        padding:          {c['padding_input']};
        min-height:       {c['input_min_height']}px;
        selection-background-color: {c['accent']};
    }}
    QLineEdit:hover {{
        border-color: {c['border_input_hover']};
    }}
    QLineEdit:focus {{
        border-color: {c['border_input_focus']};
    }}
    QLineEdit:disabled {{
        background-color: {c['surface_alt']};
        color:            {c['text_disabled']};
        border-color:     {c['border_input']};
    }}
    QLineEdit::placeholder {{
        color: {c['text_placeholder']};
    }}

    /* Campo de asunto editable (diferenciado visualmente) */
    QLineEdit#AsuntoEdit {{
        background-color: {c['asunto_bg']};
        border:           {c['border_width_asunto']} solid {c['asunto_border']};
        border-radius:    {c['radius_asunto']};
        font-size:        {c['font_size_base']};
        padding:          {c['padding_input']};
    }}

    /* =========================================================================
       S06  QCOMBOBOX
       Dropdowns: CIA, Ramo
       ========================================================================= */

    QComboBox {{
        background-color: {c['surface']};
        color:            {c['text_primary']};
        border:           {c['border_width_combo']} solid {c['border_input']};
        border-radius:    {c['radius_combo']};
        padding:          {c['padding_input']};
        min-height:       {c['combo_min_height']}px;
        selection-background-color: {c['accent']};
    }}
    QComboBox:hover {{
        border-color: {c['border_input_hover']};
    }}
    QComboBox:focus {{
        border-color: {c['border_input_focus']};
    }}
    QComboBox:disabled {{
        background-color: {c['surface_alt']};
        color:            {c['text_disabled']};
    }}
    QComboBox::drop-down {{
        border:     {c['css_none']};
        width:      {c['combo_arrow_width']}px;
    }}
    QComboBox::down-arrow {{
        width:  {c['combo_arrow_size']}px;
        height: {c['combo_arrow_size']}px;
        image:  {c['css_image_none']};
    }}
    QComboBox QAbstractItemView {{
        background-color: {c['combo_dropdown_bg']};
        border:           {c['border_width_combo_dropdown']} solid {c['combo_dropdown_border']};
        border-radius:    {c['css_zero']};
        outline:          {c['css_outline_none']};
        padding:          2px;
    }}
    QComboBox QAbstractItemView::item {{
        min-height: {c['combo_item_height']}px;
        padding:    4px 8px;
        color:      {c['text_primary']};
    }}
    QComboBox QAbstractItemView::item:hover {{
        background-color: {c['combo_item_hover_bg']};
        color:            {c['combo_item_hover_text']};
    }}
    QComboBox QAbstractItemView::item:selected {{
        background-color: {c['combo_item_sel_bg']};
        color:            {c['combo_item_sel_text']};
    }}

    /* =========================================================================
       S07  BOTONES GRANDES — LÍNEA DE NEGOCIO Y MODO DE ENVÍO
       QPushButton[role="btn-linea"] → RRGG / Transportes / Correo nuevo / Responder a todos
       ========================================================================= */

    QPushButton[role="btn-linea"] {{
        background-color: {c['btn_linea_bg']};
        color:            {c['btn_linea_text']};
        border:           {c['border_width_btn_linea']} solid {c['btn_linea_border']};
        border-radius:    {c['radius_btn_linea']};
        padding:          {c['padding_btn_linea']};
        min-height:       {c['btn_linea_min_height']}px;
        font-weight:      {c['btn_linea_font_weight']};
        font-size:        {c['font_size_button']};
        text-align:       {c['align_center']};
    }}
    QPushButton[role="btn-linea"]:hover {{
        background-color: {c['btn_linea_hover_bg']};
    }}
    QPushButton[role="btn-linea"][selected="true"] {{
        background-color: {c['btn_linea_sel_bg']};
        color:            {c['btn_linea_sel_text']};
        border-color:     {c['btn_linea_sel_border']};
    }}

    /* =========================================================================
       S08  BOTONES DE PLANTILLA L1 — Póliza / Endoso / Declaración mensual
       QPushButton[role="btn-tpl-l1"] → igual estética que btn-linea pero compacto
       ========================================================================= */

    QPushButton[role="btn-tpl-l1"] {{
        background-color: {c['btn_linea_bg']};
        color:            {c['btn_linea_text']};
        border:           {c['border_width_btn_linea']} solid {c['btn_linea_border']};
        border-radius:    {c['radius_btn_linea']};
        padding:          10px 16px;
        min-height:       52px;
        font-weight:      {c['btn_linea_font_weight']};
        font-size:        {c['font_size_button']};
        text-align:       {c['align_center']};
    }}
    QPushButton[role="btn-tpl-l1"]:hover {{
        background-color: {c['btn_linea_hover_bg']};
    }}
    QPushButton[role="btn-tpl-l1"][selected="true"] {{
        background-color: {c['btn_linea_sel_bg']};
        color:            {c['btn_linea_sel_text']};
        border-color:     {c['btn_linea_sel_border']};
    }}

    /* =========================================================================
       S09  OPCIONES RADIO L2 — tarjetas de selección de subtipo
       QFrame[role="radio-opt"] → contenedor de cada opción
       ========================================================================= */

    QFrame[role="radio-opt"] {{
        background-color: {c['radio_opt_bg']};
        border:           1px solid {c['radio_opt_border']};
        border-radius:    {c['radius_radio_opt']};
    }}
    QFrame[role="radio-opt"]:hover {{
        background-color: {c['radio_opt_hover_bg']};
        border-color:     {c['border_input_hover']};
    }}
    QFrame[role="radio-opt"][selected="true"] {{
        background-color: {c['radio_opt_sel_bg']};
        border-color:     {c['radio_opt_sel_border']};
    }}

    /* QRadioButton dentro de las tarjetas L2 */
    QFrame[role="radio-opt"] QRadioButton {{
        background-color: {c['css_transparent']};
        color:            {c['text_primary']};
        font-size:        {c['font_size_button']};
        font-weight:      {c['fw_bold']};
        spacing:          8px;
    }}
    QFrame[role="radio-opt"] QRadioButton::indicator {{
        width:         14px;
        height:        14px;
        border-radius: 7px;
        border:        2px solid {c['radio_dot_border']};
        background:    {c['surface']};
    }}
    QFrame[role="radio-opt"] QRadioButton::indicator:checked {{
        border-color:  {c['radio_dot_sel_border']};
        background:    {c['radio_dot_sel_fill']};
    }}

    /* =========================================================================
       S10  BOTÓN AGREGAR FILA (dashed outline)
       QPushButton[role="btn-add-row"] → Agregar póliza / endoso / declaración
       ========================================================================= */

    QPushButton[role="btn-add-row"] {{
        background-color: {c['css_transparent']};
        color:            {c['btn_add_row_text']};
        border:           {c['border_width_btn_add']} dashed {c['btn_add_row_border']};
        border-radius:    {c['radius_btn_add']};
        padding:          {c['padding_btn_add']};
        min-height:       {c['btn_add_min_height']}px;
        font-size:        {c['font_size_button']};
        font-weight:      {c['fw_bold']};
        text-align:       {c['align_left']};
    }}
    QPushButton[role="btn-add-row"]:hover {{
        background-color: {c['btn_add_row_hover_bg']};
    }}
    QPushButton[role="btn-add-row"]:disabled {{
        color:        {c['btn_add_row_disabled_text']};
        border-color: {c['btn_add_row_disabled_border']};
        background:   {c['css_transparent']};
    }}

    /* =========================================================================
       S11  BOTÓN ELIMINAR FILA (ícono tacho)
       QPushButton[role="btn-del-row"] → eliminar fila dinámica de póliza/endoso
       ========================================================================= */

    QPushButton[role="btn-del-row"] {{
        background-color: {c['btn_del_bg']};
        border:           {c['border_width_btn_del']} solid {c['btn_del_border']};
        border-radius:    {c['radius_btn_del']};
        min-width:        {c['btn_del_size']}px;
        max-width:        {c['btn_del_size']}px;
        min-height:       {c['btn_del_size']}px;
        max-height:       {c['btn_del_size']}px;
        padding:          {c['padding_zero_h']};
    }}
    QPushButton[role="btn-del-row"]:hover {{
        background-color: {c['btn_del_hover_bg']};
        border-color:     {c['inline_error_border']};
    }}

    /* =========================================================================
       S12  BOTONES DE ACCIÓN (barra inferior)
       btn-primary  → Abrir en Outlook
       btn-secondary → Limpiar
       btn-paste    → Pegar datos del portapapeles
       ========================================================================= */

    QPushButton[role="btn-primary"] {{
        background-color: {c['btn_primary_bg']};
        color:            {c['btn_primary_text']};
        border:           {c['css_none']};
        border-radius:    {c['radius_btn']};
        padding:          {c['padding_btn_primary']};
        min-height:       {c['btn_primary_min_height']}px;
        min-width:        {c['btn_primary_min_width']}px;
        font-weight:      {c['btn_primary_font_weight']};
        font-size:        {c['font_size_button']};
    }}
    QPushButton[role="btn-primary"]:hover {{
        background-color: {c['btn_primary_hover']};
    }}
    QPushButton[role="btn-primary"]:pressed {{
        background-color: {c['accent_dark']};
    }}

    QPushButton[role="btn-secondary"] {{
        background-color: {c['btn_secondary_bg']};
        color:            {c['btn_secondary_text']};
        border:           {c['border_width_btn_secondary']} solid {c['btn_secondary_border']};
        border-radius:    {c['radius_btn']};
        padding:          {c['padding_btn_secondary']};
        min-height:       {c['btn_secondary_min_height']}px;
        font-size:        {c['font_size_button']};
    }}
    QPushButton[role="btn-secondary"]:hover {{
        background-color: {c['btn_secondary_hover']};
    }}

    QPushButton[role="btn-paste"] {{
        background-color: {c['btn_paste_bg']};
        color:            {c['btn_paste_text']};
        border:           1px solid {c['btn_paste_border']};
        border-radius:    {c['radius_btn']};
        padding:          {c['padding_btn_paste']};
        min-height:       {c['btn_paste_min_height']}px;
        font-size:        {c['font_size_button']};
    }}
    QPushButton[role="btn-paste"]:hover {{
        background-color: {c['btn_paste_hover_bg']};
    }}

    /* =========================================================================
       S13  CUSTOMTITLEBAR
       Barra de título personalizada de la ventana principal
       ========================================================================= */

    #AppTitleBar {{
        background-color: {c['titlebar_bg']};
        min-height:       {c['titlebar_height']}px;
        max-height:       {c['titlebar_height']}px;
    }}
    #AppTitleLabel {{
        color:            {c['text_on_dark']};
        font-weight:      {c['fw_bold']};
        font-size:        {c['font_size_button']};
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

    /* =========================================================================
       S14  CUSTOMmessagebox — advertencia al abrir Outlook
       #MsgFrame     → contenedor completo del diálogo
       #MsgTitleBar  → barra de título del diálogo
       #MsgBody      → cuerpo del diálogo
       #MsgBtnOk     → botón "Entendido"
       ========================================================================= */

    #MsgFrame {{
        background-color: {c['msg_body_bg']};
        border:           {c['border_width_msg']} solid {c['msg_border']};
        border-radius:    {c['radius_msg']};
    }}
    #MsgTitleBar {{
        background-color: {c['msg_titlebar_bg']};
        border-radius:    {c['radius_msg_titlebar']};
    }}
    #MsgTitleLabel {{
        color:       {c['msg_titlebar_text']};
        font-weight: {c['msg_titlebar_text_bold']};
        font-size:   {c['font_size_button']};
        background:  {c['css_transparent']};
    }}
    #MsgBody {{
        background-color: {c['msg_body_bg']};
        border-radius:    {c['radius_msg_body']};
    }}
    #MsgBodyText {{
        color:       {c['msg_body_text']};
        font-size:   {c['font_size_base']};
        font-weight: {c['msg_body_text_bold']};
        background:  {c['css_transparent']};
    }}
    #MsgBtnOk {{
        background-color: {c['msg_btn_ok_bg']};
        color:            {c['msg_btn_ok_text']};
        border:           {c['css_none']};
        border-radius:    {c['radius_msg_btn']};
        padding:          {c['padding_msg_btn']};
        min-height:       {c['msg_btn_min_height']}px;
        min-width:        {c['msg_btn_min_width']}px;
        font-weight:      {c['fw_bold']};
        font-size:        {c['font_size_button']};
    }}
    #MsgBtnOk:hover {{
        background-color: {c['msg_btn_ok_hover']};
    }}

    /* =========================================================================
       S15  QSCROLLBAR — scroll del formulario principal
       ========================================================================= */

    QScrollBar:vertical {{
        background:    {c['scrollbar_track']};
        width:         {c['scrollbar_width']}px;
        border:        {c['css_none']};
        border-radius: {c['scrollbar_handle_radius']};
    }}
    QScrollBar::handle:vertical {{
        background:    {c['scrollbar_handle']};
        border-radius: {c['scrollbar_handle_radius']};
        min-height:    {c['scrollbar_handle_min']}px;
        margin:        {c['scrollbar_margin']};
    }}
    QScrollBar::handle:vertical:hover {{
        background: {c['scrollbar_handle_hover']};
    }}
    QScrollBar::handle:vertical:pressed {{
        background: {c['scrollbar_handle_pressed']};
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: {c['css_zero']}px;
    }}
    QScrollBar:horizontal {{
        background:    {c['scrollbar_track']};
        height:        {c['scrollbar_width']}px;
        border:        {c['css_none']};
        border-radius: {c['scrollbar_handle_radius']};
    }}
    QScrollBar::handle:horizontal {{
        background:    {c['scrollbar_handle']};
        border-radius: {c['scrollbar_handle_radius']};
        min-width:     {c['scrollbar_handle_min']}px;
        margin:        {c['scrollbar_margin']};
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {c['scrollbar_handle_hover']};
    }}
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {{
        width: {c['css_zero']}px;
    }}

    /* =========================================================================
       S16  TOOLTIP
       ========================================================================= */

    QToolTip {{
        background-color: {c['titlebar_bg']};
        color:            {c['text_on_dark']};
        border:           1px solid {c['border_block']};
        border-radius:    4px;
        padding:          4px 8px;
        font-size:        {c['font_size_small']};
    }}

    /* =========================================================================
       S17  ADVERTENCIA INLINE (paste portapapeles)
       #InlineWarn  → fondo ámbar para error de parseo de portapapeles
       #InlineError → fondo rojo para error crítico
       ========================================================================= */

    #InlineWarn {{
        background-color: {c['inline_warn_bg']};
        border-left:      3px solid {c['inline_warn_border']};
        border-radius:    0 4px 4px 0;
        color:            {c['inline_warn_text']};
        font-size:        {c['font_size_small']};
        padding:          6px 10px;
    }}
    #InlineError {{
        background-color: {c['inline_error_bg']};
        border-left:      3px solid {c['inline_error_border']};
        border-radius:    0 4px 4px 0;
        color:            {c['inline_error_text']};
        font-size:        {c['font_size_small']};
        padding:          6px 10px;
    }}

    /* =========================================================================
       S18  VISTA PREVIA DEL CORREO
       #PreviewContainer → QFrame que envuelve el QWebEngineView
       ========================================================================= */

    #PreviewContainer {{
        background-color: {c['preview_bg']};
        border:           {c['border_width_preview']} solid {c['preview_border']};
        border-radius:    {c['radius_preview']};
    }}

    """
    return qss


def get_palette() -> QPalette:
    """
    Retorna un QPalette alineado con la paleta de colores del tema.
    Aplicar con app.setPalette(get_palette()) junto con build_qss().
    """
    c = QSSD
    palette = QPalette()
    palette.setColor(QPalette.Window,          QColor(c['app_bg']))
    palette.setColor(QPalette.WindowText,      QColor(c['text_primary']))
    palette.setColor(QPalette.Base,            QColor(c['surface']))
    palette.setColor(QPalette.AlternateBase,   QColor(c['surface_alt']))
    palette.setColor(QPalette.Text,            QColor(c['text_primary']))
    palette.setColor(QPalette.Button,          QColor(c['btn_linea_bg']))
    palette.setColor(QPalette.ButtonText,      QColor(c['text_primary']))
    palette.setColor(QPalette.Highlight,       QColor(c['accent']))
    palette.setColor(QPalette.HighlightedText, QColor(c['text_on_accent']))
    palette.setColor(QPalette.ToolTipBase,     QColor(c['titlebar_bg']))
    palette.setColor(QPalette.ToolTipText,     QColor(c['text_on_dark']))
    palette.setColor(QPalette.PlaceholderText, QColor(c['text_placeholder']))
    return palette
